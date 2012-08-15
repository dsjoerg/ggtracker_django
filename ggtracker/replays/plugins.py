import re, math
from collections import defaultdict, deque
from sc2reader.events import *
from sc2reader.plugins.utils import plugin

FRAMES_PER_SECOND = 16

# TODO: Once the sc2reader:new_data branch is finished we won't need this.
# Include buildings for ownership tracking but don't include them in army tracking
unit_data = {'Protoss':[
    (True,'probe', [50,0,1]),
    (True,'zealot', [100,0,2]),
    (True,'sentry', [50,100,2]),
    (True,'stalker', [125,50,2]),
    (True,'hightemplar', [50,150,2]),
    (True,'darktemplar', [125,125,2]),
    (True,'immortal', [250,100,4]),
    (True,'colossus', [300,200,6]),
    (True,'archon', [175,275,4]), # Can't know the cost, split the difference.
    (True,'observer', [25,75,1]),
    (True,'warpprism', [200,0,2]),
    (True,'phoenix', [150,100,2]),
    (True,'voidray', [250,150,2]),
    (True,'carrier', [350,250,6]),
    (True,'mothership', [400,400,6]),
    (True,'photoncannon', [150,0,0]),
    #(True,'interceptor', [25,0,0]), # This is technically a army unit

],'Terran':[
    (True,'scv', [50,0,1]),
    (True,'marine', [50,0,1]),
    (True,'marauder', [100,25,2]),
    (True,'reaper', [50,50,2]),
    (True,'ghost', [200,100,2]),
    (True,'hellion', [100,0,2]),
    (True,'siegetank', [150,125,2]),
    (True,'thor', [300,200,6]),
    (True,'viking', [150,75,2]),
    (True,'medivac', [100,100,2]),
    (True,'banshee', [150,100,3]),
    (True,'raven', [100,200,2]),
    (True,'battlecruiser', [400,300,6]),
    (True,'planetaryfortress', [150,150,0]),
    (True,'missileturret', [100,0,0]),

],'Zerg':[
    # Cumulative costs, including drone costs
    (True,'drone', [50,0,1]),
    (True,'zergling', [25,0,.5]),
    (True,'queen', [150,0,2]),
    (True,'baneling', [50,25,.5]),
    (True,'roach', [75,25,2]),
    (True,'overlord', [100,0,0]),
    (True,'overseer', [150,50,0]),
    (True,'hydralisk', [100,50,2]),
    (True,'spinecrawler', [150,0,0]),
    (True,'sporecrawler', [125,0,0]),
    (True,'mutalisk', [100,100,2]),
    (True,'corruptor', [150,100,2]),
    (True,'broodlord', [300,250,4]),
    (True,'broodling', [0,0,0]),
    (True,'infestor', [100,150,2]),
    (True,'infestedterran', [0,0,0]),
    (True,'ultralisk', [300,200,6]),
    (True,'nydusworm', [100,100,0]),
]}



ARMY_MAP, ARMY_INFO, UNITS  = {}, {}, {}
for race, unit_list in unit_data.items():
    UNITS[race] = list()
    for index, (army, name, info) in enumerate(unit_list):
        if army:
            ARMY_MAP[name] = index
            ARMY_INFO[name] = info
        UNITS[race].append(name)

MAX_NUM_UNITS = max(len(filter(lambda u: u[0], unit_list)) for unit_list in unit_data.values())

@plugin
def WWPMTracker(replay, ww_length_frames, workers=set(["TrainProbe", "TrainDrone", "TrainSCV"])):
    """ Implements:
            player.wwpm = dict[minute] = count

            Where distict waves are counted by ignoring all train commands for
            ww_length_frames frames after the inital train command.

        Requires: None
    """
    efilter = lambda e: isinstance(e, AbilityEvent) and e.ability_name in workers
    for player in replay.players:
        player.wwpm = defaultdict(int)
        last_worker_built = -ww_length_frames
        for event in filter(efilter, player.events):
            if (event.frame - last_worker_built) > ww_length_frames:
                last_worker_built = event.frame
                event.player.wwpm[event.second/60] += 1

@plugin
def ActivityTracker(replay):
    """ Implements:
            obj.first_activity = framestamp
            obj.last_activity = framestamp

            Where obj includes all objects including critters, resources, and
            neutral buildings (Xel'Naga) and activity is defined as any time
            the unit is selected by any person (players and observers) or the
            is the target of an ability.

        Requires: SelectionTracker
    """
    def mark_activity(obj,frame):
        if obj.first_activity == None:
            obj.first_activity = frame
        obj.last_activity = frame

    # Initialize all objects
    for obj in replay.objects.values():
        obj.first_activity = None
        obj.last_activity=None

    # Mark Selection Activity - Include Observers
    efilter = lambda e: isinstance(e, SelectionEvent) or isinstance(e, HotkeyEvent)
    for person in replay.people:
        for event in filter(efilter, person.events):
            # Mark all currently selected units
            for obj in event.selected:
                mark_activity(obj, event.frame)

            #Also mark all previously (just before now) selected units
            for obj in person.selection[event.frame-1][0x0A].objects:
                mark_activity(obj, event.frame)

        # The last set of units seleced is alive till the end
        for obj in person.selection[replay.frames][0x0A].objects:
            mark_activity(obj, replay.frames)

    # Mark Ability Target Activity
    efilter = lambda e: isinstance(e, TargetAbilityEvent) and e.target
    for event in filter(efilter, replay.events):
        mark_activity(event.target, event.frame)

@plugin
def OwnershipTracker(replay):
    """ Implements:
            player.units = set(unit objects)
            unit.owner = player object

            Where ownership is determined by race for non-mirrored 1v1s and by
            applying a series of game engine constraints for all other cases:

                1) Only units you own can be commanded
                2) Multi-unit selections can only be of your own units

            These rules break when sharing control in team games, to mitigate
            this ownership can only be set once after which point it is locked.

        Requires: SelectionTracker
    """
    # TODO: Account for non-player owned (neutral) objects
    # TODO: We can possibly mop up a few more units by checking for
    #       any single race player and doing mass assignment. This
    #       could work in FFA, 2v2, etc for a subset of players.
    # TODO: We can also use bad owner events + race rules in many team games.

    # Initialize all objects
    for unit in replay.objects.values():
        unit.owner = None

    # A race-based analysis is more efficient and effective in 1v1 cases.
    if replay.real_type=='1v1':
        # we can't assume what the pid's will be
        player1 = replay.team[1].players[0]
        player2 = replay.team[2].players[0]
        p1_race, p2_race = player1.play_race, player2.play_race

        # if the races are different then ownership is easy
        if p1_race != p2_race:
            p1_units, race1_units = set(), UNITS[p1_race]
            p2_units, race2_units = set(), UNITS[p2_race]
            for obj in replay.objects.values():
                obj_race = getattr(obj, 'race', None)
                if obj_race == p1_race:
                    obj.owner = player1
                    p1_units.add(obj)
                elif obj_race == p2_race:
                    obj.owner = player2
                    p2_units.add(obj)
                else:
                    "Must be neutral unit."

            player1.units = p1_units
            player2.units = p2_units
            return
    # Cut out here if the above conditions applied
    # Otherwise do the more complicated logic below

    # Only loop over players since no one else can own anything
    for player in replay.players:
        player_units = set()
        player_selection = player.selection
        play_race = player.play_race

        # Don't assign ownership to off race units
        # First owner stays owner to keep shared control game events
        # from double counting ownership in team games
        def mark_ownership(objects, player):
            unit_check = lambda obj: obj.owner == None and getattr(obj, 'race', None) == play_race
            for obj in filter(unit_check, objects):
                obj.owner = player
                player_units.add(obj)

        # A player can only select more than one unit at a time when selecting her own units
        # WARNING: Also shared control units, can't detect that though
        efilter = lambda e: isinstance(e, SelectionEvent) or isinstance(e, HotkeyEvent)
        for event in filter(efilter, player.events):
            current_selection = player_selection[event.frame][0x0A].objects
            if len(current_selection) > 1:
                mark_ownership(current_selection, player)

        # A player can only issue orders to her own units
        # WARNING: Also a shared control unit, can't detect that though
        efilter = lambda e: isinstance(e, AbilityEvent)
        for event in filter(efilter, player.events):
            mark_ownership(player_selection[event.frame][0x0A].objects, player)

        player.units = player_units

@plugin
def TrainingTracker(replay):
    """ Implements:
            player.train_commands = dict[unit_name] = list(framestamps)

            Does not attempt to filter out spammed events.

        Requires: None
    """
    # TODO: Make an attempt to handle cancels?
    # TODO: This should also include infested terrans maybe?
    efilter = lambda e: hasattr(e,'ability') and hasattr(e.ability, 'build_unit')
    for player in replay.players:
        train_commands = defaultdict(list)
        for event in filter(efilter, player.events):
            train_commands[event.ability.build_unit.name].append(event.frame)
        player.train_commands = train_commands

@plugin
def LifeSpanTracker(replay):
    """ Implements:
            unit.birth = framestamp
            unit.death = framestamp

            Where birth is the framestamp of the closest corresponding unit
            build event before the unit's first_activity and death is the
            unit's last_activity point.

            If a prior build event cannot be found then the unit either
                A) is not actually owned by this player or
                B) is a starting unit, apply unit.birth=1 for first frame

        Requires: TrainingTracker, ActivityTracker, OwnershipTracker
    """
    # TODO: Death is obviously taking a very pessimistic view; most units don't
    # die immediately after their last selection...
    for unit in replay.objects.values():
        unit.birth = unit.first_activity
        unit.death = unit.last_activity

    # Make a second pass using training information
    for player in replay.players:

        # Make a copy using a reversed deque for performance
        unmatched_train_commands = dict()
        for unit_name, frame_list in player.train_commands.items():
            unmatched_train_commands[unit_name.lower()] = deque(sorted(frame_list,reverse=True))

        # Work through the units from last activity to first activity and match
        # them with the most recent train command. This results in the most
        # conservative guesses on our part.
        zergling_parity = True
        auto_units = set(['broodling','interceptor'])
        start_units = set(['probe','drone','overlord','scv'])
        for unit in sorted(player.units, key=lambda u: u.birth, reverse=True):
            name = unit.name.lower()
            if name in ARMY_INFO:
                # Find the best guess for a matching train command
                build_time = False
                if name in unmatched_train_commands:
                    # Use the first build_time before the first_activity
                    unit_build_times = unmatched_train_commands[name]
                    while len(unit_build_times) > 0:
                        build_time = unit_build_times.popleft()
                        if build_time <= unit.first_activity:
                            break
                    else:
                        build_time = False

                if build_time:
                    unit.birth = build_time

                    # Zerglings always come in twos so push it back on for the twin
                    if name == 'zergling':
                        zergling_parity = not zergling_parity
                        if not zergling_parity:
                            unit_build_times.appendleft(build_time)

                elif name in start_units:
                    unit.birth = 1

                elif name in auto_units:
                    pass

                else:
                    print "Bad ownership for {}: {} selected without matching train command".format(player, name)


@plugin
def ArmyTracker(replay):
    """ Implements:
            player.total_army = dict[UnitNum] = count
            player.army_by_minute = dict[minute][UnitNum] = count

            Where UnitNum is the ordering number specified in ARMY_MAP and
            army_by_minute count represents the total known to be alive at
            that minute mark of the game.

        Requires: OwnershipTracker, LifeSpanTracker
    """
    # Chop off trailing seconds since we use floor below
    replayMinutesCompleted = replay.frames/960
    for player in replay.players:
        player.total_army = [0] * MAX_NUM_UNITS
        player.army_by_minute = list()
        for i in range(0, replayMinutesCompleted+1):
            player.army_by_minute.append([0] * MAX_NUM_UNITS)

        for unit in player.units:

            unitnum = ARMY_MAP.get(unit.name.lower(), None)
            if unitnum == None:
                continue

            player.total_army[unitnum] += 1

            # This understates the army strength by rounding birth up and death down
            firstMinuteInArmy = int(math.ceil(unit.birth/960.0))
            lastMinuteInArmy = unit.death/960

            # Mark the unit strength for the whole time range
            for i in range(firstMinuteInArmy, lastMinuteInArmy+1):
                player.army_by_minute[i][unitnum] += 1


def setup():
    import sc2reader
    from sc2reader.plugins.replay import APMTracker, SelectionTracker

    # Register all the sc2reader plugins; order matters!
    sc2reader.register_plugin('Replay',APMTracker())
    sc2reader.register_plugin('Replay',SelectionTracker())
    sc2reader.register_plugin('Replay',WWPMTracker(ww_length_frames=3 * FRAMES_PER_SECOND))
    sc2reader.register_plugin('Replay',TrainingTracker())

    # These require Selection Tracking
    sc2reader.register_plugin('Replay',ActivityTracker())
    sc2reader.register_plugin('Replay',OwnershipTracker())

    #Also requires Training and Ownership Tracking
    sc2reader.register_plugin('Replay',LifeSpanTracker())
    sc2reader.register_plugin('Replay',ArmyTracker())


if __name__ == '__main__':
    import sys, sc2reader
    setup()
    for filename in sys.argv[1:]:
        try:
            #replay = sc2reader.load_replay(filename,verbose=True, load_level=1)
            #if replay.category == 'Ladder':
            replay = sc2reader.load_replay(filename, verbose=True, debug=True)
            """
            for event in replay.events:
                if event.pid == 2:
                    if isinstance(event, AbilityEvent) or isinstance(event, SelectionEvent) or isinstance(event, HotkeyEvent):
                        print event
                        if isinstance(event, SelectionEvent) or isinstance(event, HotkeyEvent):
                            print "\t",event.player.selection[event.frame][10]
                        if getattr(event, 'bytes', None):
                            print "\t", event.bytes.encode('hex')
                        print
            """

            #else:
            #    print "Skipped {} game {}; {}".format(replay.category, replay.map_name, filename)

        except Exception as e:
            raise
            #print "[FATAL] {}\n{}".format(filename, str(e))
