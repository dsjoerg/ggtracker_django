from __future__ import absolute_import

import re
from collections import defaultdict

from sc2reader.objects import AbilityEvent
from sc2reader import config

worker_abilities = set(["Probe", "Drone", "SCV"])

# NOTE: Added gateway units
train_abilities = set(['Marine','Reaper','Marauder','Ghost','Hellion','Siege Tank','Thor','Medivac','Banshee','Raven','Battlecruiser','Viking','Zealot','Stalker','Sentry','High Templar','Dark Templar','Warp Prism','Observer','Colossus','Immortal','Phoenix','Carrier','Void Ray','Zergling','Overlord','Queen','Hydralisk','Mutalisk','Ultralisk','Roach','Infestor','Corruptor','Mothership'])

# TODO: Don't include addons, intentional?
build_abilities = set(["Gateway", "Forge", "Cybernetics Core", "Robotics Facility", "Pylon", "Nexus", "Fleet Beacon", "Twilight Council", "Photon Cannon", "Assimilator", "Stargate", "Dark Shrine", "Robotics Bay", "Templar Archives",'Command Center', 'Supply Depot', 'Barracks', 'Engineering Bay', 'Missile Turret', 'Bunker', 'Refinery', 'Sensor Tower', 'Ghost Academy', 'Factory', 'Starport', 'Armory', 'Fusion Core','Hatchery','Spawning Pool','Evolution Chamber','Hydralisk Den','Spire','Ultralisk Cavern','Extractor','Infestation Pit','Nydus Network','Baneling Nest','Roach Warren','Spine Crawler','Spore Crawler')

# TODO: Don't include Charge, building upgrades, and general 1/1/1 upgrades, intentional?
research_abilities = set(["Blink", "Warp Gate", "Psionic Storm", "Extended Thermal Lance",'Stimpack', "Combat Shields", "Siege Tech", "Infernal Pre-igniter", "Cloaking Field", 'Evolve Burrow', 'Evolve Metabolic Boost', 'Evolve Adrenal Glands', 'Evolve Neural Parasite'])

# These events are included in the build orders...
important_events = train_abilities | build_abilities | research_abilities

# its a tough call, but lets recognize every worker-creation command
# every three seconds. if we make it any shorter, then real spam is
# going to pollute the stats. but if we make it any longer, then
# legitimate queuing of worker construction is going to get blocked.
# so after three seconds, its much less likely to be spam.
WORKER_PRODUCE_SECONDS = 17
WORKER_SPAM_MARGIN_SECONDS = 3
WORKER_PRODUCE_SPACING_SECONDS = WORKER_SPAM_MARGIN_SECONDS
UNIT_PRODUCE_SPACING_SECONDS = 3

def Macro(replay):
    # If we don't have data for this version, we can't do anything
    if replay.build not in config.build_data:
        return replay
    else:
        data = config.build_data[replay.build]

    # We don't want observer actions, so only track players
    # Computers don't have actions either, so they'll be lightweight
    for player in replay.players:
        wpm = 0
        build_order = ""
        trained_unmatched = defaultdict(list)
        wpm_arr = defaultdict(int)
        apm_arr = defaultdict(int)

        # start with a clean slate
        lub = {} # last unit built
        lwb = None # last worker built

        # Only includes actions local to that player, perfect
        for event in player.events:

            # Exclude Camera and Uknown Events
            if event.is_player_action:
                minute = event.second/60

                # Increment the APM
                apm_arr[minute] += 1

                # Do addtional processing for known ability events
                if isinstance(event, AbilityEvent) and data.ability_known(event.ability):
                    # Inconsistencies in the data file need to be cleaned up
                    ability_name = re.sub("^(Warp in|Train )","", data.ability(event.ability))

                    if ability_name in worker_abilities:
                        # Special case for first pass then check for worker spacing
                        if lwb != None and (event.second-lwb) > WORKER_PRODUCE_SPACING_SECONDS:
                            wpm += 1
                            wpm_arr[minute] += 1
                            lwb = event.second

                    # Important events should be added to the build orders
                    elif ability_name in important_events:

                        # TODO: What the hell? Only rate limit overlords? *Confusion*
                        if unit != "Overlord":
                            build_order += ability_name+"|"

                        # Special case for first pass then check for unit spacing
                        elif unit not in lub or ((event.seconds - lub[unit]) > UNIT_PRODUCE_SPACING_SECONDS):
                            lub[unit] = event.seconds
                            build_order += ability_name+"|"

                        # TODO: What the hell is this doing?
                        if IsTrainEvent(ability_name):
                            # TODO: smooshed_ability...huh? Also, why the reversed order?
                            # keep the list in reverse order, i.e first item on the list is the last train event.
                            smooshed_ability = ability_name.lower().translate(None, ' ')
                            trained_unmatched[smooshed_ability].insert(0, event)

        # Assign as player variables...
        player.wpm_arr = wpm_arr
        player.apm_arr = apm_arr
        player.build_order = build_order
        player.trained_unmatched = trained_unmatched

        # Average the WPM, we're probably going to get rid of this one
        player.wpm = wpm/minute

    return replay
