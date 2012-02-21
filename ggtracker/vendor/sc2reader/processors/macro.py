from __future__ import absolute_import

from datetime import datetime
import string

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
'Warp Prism',
'Observer',
'Colossus',
'Immortal',
'Phoenix',
'Carrier',
'Void Ray',
'Zergling',
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
    if theAbility in ["Gateway", "Forge", "Cybernetics Core", "Robotics Facility", "Pylon", "Nexus", "Fleet Beacon", "Twilight Council", "Photon Cannon", "Assimilator", "Stargate", "Dark Shrine", "Robotics Bay"]:
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

WORKER_PRODUCE_SECONDS = 17
WORKER_SPAM_MARGIN_SECONDS = 3
WORKER_PRODUCE_SPACING_SECONDS = WORKER_SPAM_MARGIN_SECONDS
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

def Macro(replay):

    # start with a clean slate
    lwb = {}

    try:
        data = config.build_data[replay.build]
    except KeyError:
        # If we don't have data for this version, we can't do any more.
        return replay

    for player in replay.players:
        player.wpm_arr = defaultdict(int)

    # Gather data for WPM measurements
    for event in replay.events:
        if event.is_local and event.is_player_action and isinstance(event, AbilityEvent) and data.ability_known(event.ability):
            ability_name = data.ability(event.ability)
            player = event.player
            if not player.is_observer:
                if ability_name in ["Probe", "Drone", "Train SCV"]:
                    if worker_built_no_spam(player, event.second, lwb):
                        curwpm = getattr(player, "wpm", 0)
                        setattr(player, "wpm", curwpm + 1)
                        minute = event.second/60
                        player.wpm_arr[minute] += 1
                elif IsBuildEvent(ability_name) or IsTrainEvent(ability_name):
                    curbo = getattr(player, "bo", "")
                    setattr(player, "bo", curbo + data.ability(event.ability) + "|")
                if IsTrainEvent(ability_name):
                    curtrained = getattr(player, "trained", {})
                    curtrained[ability_name] = curtrained.setdefault(ability_name, 0) + 1
                    setattr(player, "trained", curtrained)
                
                    


    # Average the WPM for actual players
    for player in replay.players:
        if player.events:
            event_minutes = player.events[-1].second/60.0
            if event_minutes:
                curwpm = getattr(player, "wpm", 0)
                setattr(player, "wpm", curwpm / event_minutes)

    return replay
