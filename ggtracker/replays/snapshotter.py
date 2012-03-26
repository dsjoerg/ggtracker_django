import StringIO
import string

# warning! copied from armyfun.js
units = {
    'zealot': [100,0],
    'sentry': [50,100],
    'stalker': [125,50],
    'hightemplar': [50,150],
    'darktemplar': [125,125],
    'immortal': [250,100],
    'colossus': [300,200],
    'archon': [175,275],
    'observer': [25,75],
    'warpprism': [200,0],
    'phoenix': [150,100],
    'voidray': [250,150],
    'carrier': [350,250],
    'interceptor': [25,0],
    'mothership': [400,400],
    'photoncannon': [150,0],
    'marine': [50,0],
    'marauder': [100,25],
    'reaper': [50,50],
    'ghost': [200,100],
    'hellion': [100,0],
    'siegetank': [150,125],
    'thor': [300,200],
    'viking': [150,75],
    'medivac': [100,100],
    'banshee': [150,100],
    'raven': [100,200],
    'battlecruiser': [400,300],
    'planetaryfortress': [150,150],
    'missileturret': [100,0],
    'queen': [150,0],
    'zergling': [25,0],
    'baneling': [25,25],
    'roach': [75,25],
    'overseer': [50,50],
    'hydralisk': [100,50],
    'spinecrawler': [100,0],
    'sporecrawler': [75,0],
    'mutalisk': [100,100],
    'corruptor': [150,100],
    'broodlord': [150,150],
    'broodling': [0,0],
    'infestor': [100,150],
   'infestedterran': [0,0],
    'ultralisk': [300,200],
    'nydusworm': [100,100],
}


def frame_to_time(frame):
	minutes = frame / (60*16);
	seconds = (frame/16) % 60;
	frames = frame % 16
	return "%02d:%02d.%02d" % (minutes, seconds, frames)

no_train = {}
no_suitable_train = {}

# the given object needs to be matched to its birth frame.  look for
# it, and if we can find it, set its birth_frame attribute
# accordingly.
def find_and_set_birth_frame(obj, now_frame):
	if not hasattr(obj, "player"):
		return
	trained_unmatched = obj.player.trained_unmatched
	unittype = obj.__class__.__name__.lower()
	if not (unittype in trained_unmatched):
		no_train_count = no_train.setdefault(unittype, 0)
		no_train_count = no_train_count + 1
		no_train[unittype] = no_train_count
#		print "Erk, couldnt find any train events for %s" % unittype
		return

	trained_unmatched_list = trained_unmatched[unittype]

	#
	# we want the LAST train event that was BEFORE this selection
	# event.
	#
	# trained_unmatched_list is in reverse order, i.e. the first
	# item on the list is the last unmatched train event.
	#
	# we want that event, unless it is AFTER our selection event,
	# in case we want an older one.
	#
	train_event = None
	try: train_event = (event for event in trained_unmatched_list if event.frame < now_frame).next()
	except StopIteration: pass

	if train_event is not None:
		trained_unmatched_list.remove(train_event)
		setattr(obj, "birth_frame", train_event.frame)
#		print "Hooray! %s %s was born at %d." % (unittype, hex(obj.id), train_event.frame)
	else:
		no_suitable_train_count = no_suitable_train.setdefault(unittype, 0)
		no_suitable_train_count = no_suitable_train_count + 1
		no_suitable_train[unittype] = no_suitable_train_count
#		print "Couldnt find a suitable train event for %s" % unittype


# returns a map from player to javascript string representation of
# that players army.
def armyjs_map(replay):
	player_to_army = {}

	for player in replay.players:
		lastobjs = None
		for frame in sorted(player.get_selection().keys()):
			for theobj in player.get_selection()[frame]:
				if not hasattr(theobj, "birth_frame"):
					find_and_set_birth_frame(theobj, frame);
			
			# each thing selected in the previous
			# selection survived at least until this
			# selection
			if lastobjs is not None:
				for theobj in lastobjs:
					theobj.last_selected = frame
			lastobjs = player.get_selection()[frame]

		# currently selected objects survived until the end of the game
		# right?
		for obj in player.get_selection().current:
			obj.last_selected = replay.frames


	for obj in replay.objects.values():
		if not hasattr(obj, "first_selected"):
			continue
		firstseen = obj.first_selected
		lastseen = obj.last_selected
#		if hasattr(obj, "last_removed"):
#			lastseen = max(lastseen, obj.last_removed)
		if hasattr(obj, "birth_frame"):
			firstseen = min(firstseen, obj.birth_frame)
		if obj.first_selected > lastseen:
			print " HEY first_selected is after lastseen! ",
		obj.firstseen = firstseen
		obj.lastseen = lastseen


	for player in replay.players:
		result = StringIO.StringIO()
		print >>result, "[ ",
		for obj in replay.objects.values():
			if not hasattr(obj, "player"):
				continue
			if obj.player != player:
				continue
			if not hasattr(obj, "first_selected"):
				continue
			unittype = obj.__class__.__name__.lower()
			clean_unittype = string.replace(unittype, " (burrowed)", "");
			clean_unittype = string.replace(clean_unittype, " (sieged)", "");
			if clean_unittype not in units:
				continue
			print >>result, "['%s', %d, %d], " % (unittype, obj.firstseen, obj.lastseen),
		print >>result, "]",
		finalstring = result.getvalue()
		result.close()
		player_to_army[player] = finalstring

#	print "no_train: %s" % no_train
#	print "no_suitable_train: %s" % no_suitable_train

	return player_to_army


def armyjs(replay):
	result = StringIO.StringIO()

	print >>result, "numplayers = %d;" % len(replay.players)
	print >>result, ""

	# currently selected objects survived until the end of the game
	# right?
	for player in replay.players:
		lastobjs = None
		for frame in sorted(player.get_selection().keys()):
			if lastobjs is not None:
				for theobj in lastobjs:
					theobj.last_selected = frame
			lastobjs = player.get_selection()[frame]
		for obj in player.get_selection().current:
			obj.last_selected = replay.frames

	for obj in replay.objects.values():
		if not hasattr(obj, "first_selected"):
			continue
		lastseen = obj.last_selected
		if hasattr(obj, "last_removed"):
			lastseen = max(lastseen, obj.last_removed)
		if obj.first_selected > lastseen:
			print " HEY first_selected is after lastseen! ",
		obj.lastseen = lastseen


	print >>result, "armies = {"
	for player in replay.players:
		print >>result, "%d: [ " % player.pid
		for obj in replay.objects.values():
			if not hasattr(obj, "player"):
				continue
			if obj.player != player:
				continue
			if not hasattr(obj, "first_selected"):
				continue
			print >>result, "['%s', %d, %d], " % (obj.__class__.__name__.lower(), obj.first_selected, obj.lastseen)
		print >>result, "],"
	print >>result, "};"
	finalstring = result.getvalue()
	result.close()
	return finalstring

def doit(replay):
	army_history = {}
#	print "hi"

	# currently selected objects survived until the end of the game
	# right?
	for player in replay.players:
#		for hotkey, hotkey_selection in player.hotkeys.iteritems():
#			for obj in hotkey_selection.current:
#				obj.last_selected = replay.frames
#				print "obj %s survived in hotkey %s" % (obj, hotkey)
		for obj in player.get_selection().current:
			obj.last_selected = replay.frames
#			print "obj %s survived in selection" % obj
		lastobjs = None
		for frame in sorted(player.get_selection().keys()):
			if lastobjs is not None:
				for theobj in lastobjs:
					theobj.last_selected = frame
			lastobjs = player.get_selection()[frame]

	for obj in replay.objects.values():
#		print "Looking at obj %s" % obj,
		if not hasattr(obj, "first_selected"):
#			print " was never selected."
			continue

#		if hasattr(obj, "first_hotkeyed_out"):
#			print "was first hotkeyed out at %s" % frame_to_time(obj.first_hotkeyed_out),
		# getting hotkeyed out means the unit is definitely
		# not alive.  however we dont need this, since we are
		# using more conservative criteria to establish active
		# army lifetime -- first and last selected time.

		lastseen = obj.last_selected
		if hasattr(obj, "last_removed"):
			lastseen = max(lastseen, obj.last_removed)
#			print "was last removed from a selection at %s" % frame_to_time(obj.last_removed),
		if obj.first_selected > lastseen:
			print " HEY first_selected is after lastseen! ",
#		print "was first_sel %s last_sel %s ." % (frame_to_time(obj.first_selected), frame_to_time(obj.last_selected))
		obj.lastseen = lastseen


		for frame in range(0, replay.frames, 16*60):
			# the logic below is ignoring last_removed,
			# and ignoring hotkey groups or selections
			# that it may have remained in following the
			# last selection/removal
			if (obj.first_selected <= frame and frame <= lastseen):
				frame_armies =  army_history.get(frame, {})
				army_history[frame] = frame_armies

				frame_army = frame_armies.get(obj.player.pid, {})
				frame_armies[obj.player.pid] = frame_army

				frame_army_set_for_type = frame_army.get(obj.__class__.__name__, set([]))
				frame_army[obj.__class__.__name__] = frame_army_set_for_type

				frame_army_set_for_type.add(obj)

#				print "did obj %s in frame %d, set is now %s" % (obj, frame, frame_army_set_for_type)



	if False:
		for frame in range(0, replay.frames, 16*60):
			print "=============== %s ===============" % frame_to_time(frame)
			for player in replay.players:
				print "---- %-20s -----" % player.name
				frame_armies = army_history.get(frame, {})
				frame_army = frame_armies.get(player.pid, {})
#			print "frame_army: %s" % frame_army
				for classname, frame_army_set in frame_army.iteritems():
					print "%3d %s" % (len(frame_army_set), classname)

	print "armies = {"
	for player in replay.players:
		print "%d: [" % player.pid
		for obj in replay.objects.values():
			if not hasattr(obj, "player"):
				continue
			if obj.player != player:
				continue
			if not hasattr(obj, "first_selected"):
				continue
			print "[%d, '%s', %d, %d]" % (obj.id, obj.__class__.__name__.lower(), obj.first_selected, obj.lastseen)
		print "],"
	print "}"
