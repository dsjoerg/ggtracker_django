from sc2reader.events import *

# TODO: Once the sc2reader:new_data branch is finished we won't need this.
army_values = {
    #Protoss
        #Gateways
        'zealot': [100,0,2],
        'sentry': [50,100,2],
        'stalker': [125,50,2],
        'hightemplar': [50,150,2],
        'darktemplar': [125,125,2],

        #Robotics Bay
        'immortal': [250,100,4],
        'colossus': [300,200,6],
        'observer': [25,75,1],
        'warpprism': [200,0,2],

        #Stargate
        'phoenix': [150,100,2],
        'voidray': [250,150,2],
        'carrier': [350,250,6],
        'interceptor': [25,0,0],

        #Other
        'mothership': [400,400,6],
        'archon': [175,275,4],        # Can't know the cost, split the difference.
        'photoncannon': [150,0,0],    # Are we counting defensive structures here?

    #Terran
        #Barracks
        'marine': [50,0,1],
        'marauder': [100,25,2],
        'reaper': [50,50,2],
        'ghost': [200,100,2],

        #Facotry
        'hellion': [100,0,2],
        'siegetank': [150,125,2],
        'thor': [300,200,6],

        #Starport
        'viking': [150,75,2],
        'medivac': [100,100,2],
        'banshee': [150,100,3],
        'raven': [100,200,2],
        'battlecruiser': [400,300,6],

        #Other - TODO: No Bunker?
        'planetaryfortress': [150,150,0],
        'missileturret': [100,0,0],

    #Zerg
        #Hatchery - TODO: No Overlord (it is a transport)
        'queen': [150,0,2],
        'zergling': [25,0,.5],
        'baneling': [25,25,.5],
        'roach': [75,25,2],

        #Lair
        'overseer': [50,50,0],
        'hydralisk': [100,50,2],
        'mutalisk': [100,100,2],
        'corruptor': [150,100,2],
        'infestor': [100,150,2],
        'infestedterran': [0,0,0],

        #Hive
        'broodlord': [150,150,4],
        'broodling': [0,0,0],
        'ultralisk': [300,200,6],

        #Other
        'spinecrawler': [100,0,0],
        'sporecrawler': [75,0,0],
        'nydusworm': [100,100,0],
}

terran_training = set([
    'Marine','Reaper','Marauder','Ghost',                       #Barracks
    'Hellion','Siege Tank','Thor',                              #Factory
    'Medivac','Viking','Banshee','Raven','Battlecruiser'        #Starport
])

protoss_training = set([
    'Zealot','Stalker','Sentry','High Templar','Dark Templar'   #Gateway
    'Warp Prism','Observer','Colossus','Immortal',              #Robotics Bay
    'Phoenix','Carrier','Void Ray',                             #Stargate
    'Mothership','Archon'                                       #Nexus/Other
])


zerg_training = set([
    'Overlord','Queen','Zergling','Baneling','Roach',           #Hatchery
    'Overseer','Hydralisk','Infestor','Mutalisk','Corruptor',   #Lair
    'Ultralisk','Broodlord'                                     #Hive
])

# NOTE: Doesn't include worker training right now, we don't use it!
train_commands = zerg_training | protoss_training | terran_training


def APMTracker(replay):
    """Just the straight up simple non-camera action APM"""
    efilter = lambda event: event.is_player_action
    for player in replay.players:
        player.aps = defaultdict(int)
        player.apm = defacultdict(int)
        for event in filter(efilter, player.events):
            player.aps[event.second] += 1
            player.apm[event.second/60] += 1
        player.avg_apm = sum(player.apm.values())/minutes

def WWPMTracker(replay, ww_length, workers=set(["Probe", "Drone", "SCV"])):
    """A worker wave are defined as a set of worker built commands within the
    specified ww_length time window."""
    efilter = lambda e: isinstance(e, AbilityEvent) and e.ability in workers
    for player in replay.players:
        player.wwpm = defaultdict(int)
        last_worker_built = -ww_length
        for event in filter(efilter, player.events):
            if (event.framestamp - last_worker_built) > ww_length:
                last_worker_built = framestamp
                event.player.wwpm[event.second/60] += 1

def ActivityTracker(replay):
    """Unit activity marks the first and last times a unit is explicitly
    interacted with by any of the players and/or observers"""
    def mark_activity(obj,framestamp):
        if obj.first_activity == None:
            obj.first_activity = framestamp
        obj.last_activity = framestamp

    # Initialize all objects
    for obj in replay.objects:
        obj.first_activity = None
        obj.last_activity=None

    # Mark Selection Activity - Include Observers
    efilter = lambda e: isinstance(e, SelectionEvent) or isinstance(e, HotkeyEvent)
    for person in replay.people:
        for event in filter(efilter, replay.events):
            # Mark all currently selected units
            for obj in event.selected:
                mark_activity(obj, framestamp)

            #Also mark all previously (just before now) selected units
            for obj in person.selections[event.framestamp-1][0x0A].objects:
                mark_activity(obj, framestamp)

        # The last set of units seleced is alive till the end
        for obj in person.selections[replay.frames].objects:
            mark_activity(obj, replay.frames)

    # Mark Ability Target Activity
    efilter = lambda e: isinstance(e, TargetAbilityEvent)
    for event in filter(efilter, replay.events):
        mark_activity(event.target, framestamp)

def OwnershipTracker(replay):
    """The ownership tracker uses a variety of game engine constraints to
    establish definite ownership of units."""
    # TODO: Work out shared ownership
    # TODO: Account for non-player owned (neutral) objects
    # TODO: A race-based analysis would be more effecitve in many cases (TvZ)
    def mark_ownership(objects, player):
        for obj in objects:
            obj.owner = player
            player.units.add(obj)

    # Initialize all objects
    mark_ownership(replay.objects, None)

    # Only loop over players since no one else can own anything
    for player in replay.players:
        player.units = set()

        # A player can only select more than one unit at a time when selecting her own units
        efilter = lambda e: isinstance(e, SelectionEvent) or isinstance(e, HotkeyEvent)
        for event in filter(efilter, player.events):
            selection = player.selections[event.framestamp][0x0A]
            if len(selection.objects) > 1:
                mark_ownership(selection.objects, player)

        # A player can only issue orders to her own units
        efilter = lambda e: isinstance(e, AbilityEvent)
        for event in filter(efilter, player.events):
            mark_ownership(player.selections[event.framestamp][0x0A], player)


def TrainingTracker(replay):
    """Tracks each train command with no regard for spam or the action's
    success. Useful for determining when selected units have been birthed."""
    # TODO: Make an attempt to handle cancels?
    efilter = lambda e: isinstance(e, AbilityEvent) and e.ability in train_commands
    for player in replay.players:
        player.train_commands = defaultdict(list)
        for event in filter(efilter, player.events):
            unit_name = ability_name.lower().replace(' ','')
            player.train_commands[smooshed_ability].append(event.framestamp)


def LifeSpanTracker(replay):
    """Tracks the birth and death of each unit to the best of it's abilities"""
    # TODO: Birth could be much smarter here by using player training commands
    # TODO: Death is obviously taking a very pessimistic view; most units don't
    #        die immediately after their last selection...
    for unit in replay.objects:
        unit.birth = unit.first_activity
        unit.death = unit.last_activity

    # Make a second pass using training information
    for player in replay.players:

        # Make a copy using a reversed deque for performance
        unmatched_train_commands = dict()
        for command, frame_list in player.train_commands.items():
            unmatched_train_commands[command] = deque(sorted(frame_list,reverse=True))

        # Work through the units from last activity to first activity and match
        # them with the most recent train command. This results in the most
        # conservative guesses on our part.
        for unit in sorted(player.units, key=lambda u: u.birth, reverse=true):
            try:
                unit_name = unit.__class__.__name__.lower().replace(' ','')

                # Remove all commands that happened after this point in time
                # TODO: they were probably spam, we could use that information elsewhere
                unit_build_times = unmatched_train_commands[unit_name]
                while(unit_build_times[0] >= unit.first_activity):
                    unit_build_times.pop_left()

                # Get the first build time before the unit's first_activity
                unit.birth = unit_build_times.pop_left()

            except IndexError as e:
                # A build time wasn't found for this unit?!?!
                # TODO: What's the logging mechanism here?
                pass