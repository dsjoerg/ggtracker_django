from __future__ import absolute_import

from datetime import datetime
import string
import re

from collections import defaultdict

from sc2reader.constants import REGIONS, LOCALIZED_RACES
from sc2reader.objects import Player, Message, Color, Observer, Team, Packet, AbilityEvent
from sc2reader.utils import windows_to_unix
from sc2reader import config

def IsTrainEvent(theAbility):
    if string.find(theAbility, "Train") != -1:
        return True
    if string.find(theAbility, "Warp in") != -1:
        return True
    if theAbility in ['Marine',
'Reaper',
'Ghost',
'Marauder',
'Siege Tank',
'Thor',
'Hellion',
'Medivac',
'Banshee',
'Raven',
'Battlecruiser',
'Viking',
'Warp Prism',
'Observer',
'Colossus',
'Immortal',
'Phoenix',
'Carrier',
'Void Ray',
'Zergling',
'Overlord',
'Queen',
'Hydralisk',
'Mutalisk',
'Ultralisk',
'Roach',
'Infestor',
'Corruptor',
'Mothership',
]:
        return True

def IsBuildEvent(theAbility):
    if theAbility in ["Gateway", "Forge", "Cybernetics Core", "Robotics Facility", "Pylon", "Nexus", "Fleet Beacon", "Twilight Council", "Photon Cannon", "Assimilator", "Stargate", "Dark Shrine", "Robotics Bay", "Templar Archives"]:
        return True
    if theAbility in ['Command Center', 'Supply Depot', 'Barracks', 'Engineering Bay', 'Missile Turret', 'Bunker', 'Refinery', 'Sensor Tower', 'Ghost Academy', 'Factory', 'Starport', 'Armory', 'Fusion Core']:
        return True
    if theAbility in [
'Hatchery',
'Spawning Pool',
'Evolution Chamber',
'Hydralisk Den',
'Spire',
'Ultralisk Cavern',
'Extractor',
'Infestation Pit',
'Nydus Network',
'Baneling Nest',
'Roach Warren',
'Spine Crawler',
'Spore Crawler',
]:
        return True
    return False

def IsImportantResearchEvent(theAbility):
    if theAbility in ["Blink", "Warp Gate", "Psionic Storm", "Extended Thermal Lance"]:
        return True
    if theAbility in ['Stimpack', "Combat Shields", "Siege Tech", "Infernal Pre-igniter", "Cloaking Field"]:
        return True
    if theAbility in ['Evolve Burrow', 'Evolve Metabolic Boost', 'Evolve Adrenal Glands', 'Evolve Neural Parasite']:
        return True
    return False

WORKER_PRODUCE_SECONDS = 17
WORKER_SPAM_MARGIN_SECONDS = 3
WORKER_PRODUCE_SPACING_SECONDS = WORKER_SPAM_MARGIN_SECONDS
UNIT_PRODUCE_SPACING_SECONDS = 3
# its a tough call, but lets recognize every worker-creation command
# every three seconds. if we make it any shorter, then real spam is
# going to pollute the stats. but if we make it any longer, then
# legitimate queuing of worker construction is going to get blocked.
# so after three seconds, its much less likely to be spam.

def worker_built_no_spam(player, when_seconds, lwb):
    if player in lwb:
        if (when_seconds - lwb[player]) > WORKER_PRODUCE_SPACING_SECONDS:
            lwb[player] = when_seconds
            return True
    else:
        lwb[player] = when_seconds
        return True
    return False

def unit_built_no_spam(player, unit, when_seconds, lub):
    if unit != "Overlord":
        return True

    if player in lub:
        if unit in lub[player]:
            if (when_seconds - lub[player][unit]) > UNIT_PRODUCE_SPACING_SECONDS:
                lub[player][unit] = when_seconds
                return True
        else:
            lub[player][unit] = when_seconds
            return True
    else:
        lub[player] = {}
        lub[player][unit] = when_seconds
        return True
    return False

def Macro(replay):

    # start with a clean slate
    lwb = {}
    lub = {}

    try:
        data = config.build_data[replay.build]
    except KeyError:
        # If we don't have data for this version, we can't do any more.
        return replay

    for person in replay.people:
        person.wpm_arr = defaultdict(int)
        person.apm_arr = defaultdict(int)
        person.trained_unmatched = {}

    # Gather data for WPM measurements
    for event in replay.events:
        if event.is_local and event.is_player_action and not event.player.is_observer:
            player = event.player
            minute = event.second/60
            player.apm_arr[minute] += 1
            
        if event.is_local and event.is_player_action and isinstance(event, AbilityEvent) and data.ability_known(event.ability):
            ability_name = data.ability(event.ability)
            clean_ability = re.sub("^Warp in ", "", ability_name)
            clean_ability = re.sub("^Train ", "", clean_ability)
#            print "ability_name = %s, clean_ability = %s" % (ability_name, clean_ability)
            player = event.player
            if not player.is_observer:
                if ability_name in ["Probe", "Drone", "Train SCV"]:
                    if worker_built_no_spam(player, event.second, lwb):
                        curwpm = getattr(player, "wpm", 0)
                        setattr(player, "wpm", curwpm + 1)
                        minute = event.second/60
                        player.wpm_arr[minute] += 1
                elif IsBuildEvent(ability_name) or IsTrainEvent(ability_name) or IsImportantResearchEvent(ability_name):
                    if unit_built_no_spam(player, clean_ability, event.second, lub):
                        curbo = getattr(player, "bo", "")
                        setattr(player, "bo", curbo + clean_ability + "|")

                if IsTrainEvent(ability_name):
                        trained_unmatched = getattr(player, "trained_unmatched", {})
                        smooshed_ability = clean_ability.lower().translate(None, ' ')
                        trained_unmatched_list = trained_unmatched.setdefault(smooshed_ability, [])
                        # keep the list in reverse order, i.e first item on the list is the last train event.
                        trained_unmatched_list.insert(0, event)
                        trained_unmatched[smooshed_ability] = trained_unmatched_list
                        setattr(player, "trained_unmatched", trained_unmatched)
                    


    # Average the WPM for actual players
    for player in replay.players:
        if player.events:
            event_minutes = player.events[-1].second/60.0
            if event_minutes:
                curwpm = getattr(player, "wpm", 0)
                setattr(player, "wpm", curwpm / event_minutes)

    return replay
