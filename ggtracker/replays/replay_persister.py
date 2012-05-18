# Built-ins
import json
import Image
import hashlib
from datetime import datetime
from cStringIO import StringIO

# 3rd party
import boto
import sc2reader

# Local
from models import *
#from buildnodes import *
from django.conf import settings

import replay_processors


# Register all the sc2reader plugins; order matters!
sc2reader.register_plugin('Replay',replay_processors.APMTracker)
sc2reader.register_plugin('Replay',replay_processors.WWPMTracker)
sc2reader.register_plugin('Replay',replay_processors.TrainingTracker)
sc2reader.register_plugin('Replay',sc2reader.plugins.replay.SelectionTracker)
# These require Selection Tracking
sc2reader.register_plugin('Replay',replay_processors.ActivityTracker)
sc2reader.register_plugin('Replay',replay_processors.OwnershipTracker)
#Also requires Training and Ownership Tracking
sc2reader.register_plugin('Replay',replay_processors.LifeSpanTracker)

def armyjs_map(replay):
    """Creates a map of player => json array of army units in this format:
        [ [unit type, birth, death], [unit type, birth, death], ... ]
    """
    army_map = dict()
    for player in replay.players:
        player_army = list()
        for unit in player.units:
            unit_type = unit.__class__.__name__.lower()
            unit_type = re.replace(' \((burrowed|sieged)\)', '', unit_type)
            if unit_type in replay_processors.army_values:
                player_army.append(unit_type, unit.birth, unit.death)
        army_map[player] = json.dumps(player_army)
    return army_map

class ReplayPersister():

      def __init__(self):
            self.replaybucket = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                                                settings.AWS_SECRET_ACCESS_KEY)\
                                                .lookup(settings.REPLAYS_BUCKET_NAME)
            #self.buildnodes = BuildNodes()

      def get_replay_file(self, s3_key):
            replay_file = StringIO()
            key = boto.s3.Key(self.replaybucket, s3_key)
            return key.get_contents_to_file(replay_file)

      # this function gets called when uploading through the
      # ruby-served page
      def upload_from_ruby(self, id, sender_subdomain):
            replayDB = Replay.objects.get(id__exact=id)
            s3_key = "{0}.SC2Replay".format(replayDB.md5hash)
            replay_file = self.get_replay_file(s3_key)

            # delete any Game data associated with this replay
            gameDBs = Game.objects.filter(replay__id__exact=id)

            # TODO: There should be a better way to die here
            assert gameDBs.count() <= 1

            if gameDBs.count() == 1:
                  # make a new game record, but with the same ID as the old one
                  # set the new subdomain only if it used to be blank
                  gameDB = gameDBs[0]
                  subdomain = gameDB.subdomain if gameDB.subdomain else sender_subdomain
                  oldID = gameDB.id
                  gameDB.delete()
                  gameDB = Game(id=oldID, replay=replayDB, subdomain=subdomain)
            else:
                  # make a new game record
                  gameDB = Game(replay=replayDB, subdomain=sender_subdomain)

            # parse the replay into memory
            replay = sc2reader.load_replay(replay_file)

            # write it out to the DB
            populateGameFromReplay(replay, gameDB)

#
# 20120427 dont populate buildnodes for now. Why slow down every users upload
# for processing that isnt ready for prime-time?  We can go back and reprocess
# replays later once weve figured out how we really want to do it.
#
#            for player in replay.players:
#                  print "populating for %s" % player.name
#                  self.buildnodes.populate_build(gameDB, player)

            #release this memory
            replay_file.close()

            return True

      # this function gets called when uploading through the
      # django-served page
      def upload_complete(self, filename, stringio):
            m = hashlib.md5()
            m.update(stringio.getvalue())
            hash = m.hexdigest()
            gameDBs = Game.objects.filter(md5hash__exact=hash)
            assert gameDBs.count() <= 1
            if gameDBs.count() == 1:
                  gameDB = gameDBs[0]
                  gameDB.delete()

            gameDB = Game(md5hash=hash, filename=filename)

            replay = sc2reader.load_replay(stringio)
            populateGameFromReplay(replay, gameDB)
            #for player in replay.players:
            #    self.buildnodes.populate_build(gameDB, player)



def winning_team(replay):
    winning_team = 0
    for team in replay.teams:
#        print "team", dir(team)
        if hasattr(team, "result"):
            if team.result == "Win":
                winning_team = team.number
    return winning_team

def createPlayer(player):
      playerDB = Player(name=player.name)
      playerDB.gateway = player.gateway
      playerDB.region = player.region
      playerDB.subregion = player.subregion
      playerDB.bnet_id = player.uid
      playerDB.save()
      return playerDB

def didPlayerWin(player):
      if player.team.result == "Win":
            return True
      elif player.team.result == "Loss":
            return False
      else:
            return None

def getStatArr(player, replay, stat):
      theArr = [0] * (replay.length.seconds/60 + 1)
      for minute,statvalue in getattr(player, stat + "_arr").items():
            theArr[minute] = statvalue
      return theArr

def getWPMArr(player, replay):
      theArr = [0] * (replay.length.seconds/60 + 1)
      for minute,workers in player.wpm_arr.items():
            theArr[minute] = workers
      return theArr

def getOrCreatePlayer(player):
      playerDBs = Player.objects.filter(bnet_id__exact=player.uid,
                                        gateway__exact=player.gateway,
                                        subregion__exact=player.subregion)
      assert playerDBs.count() <= 1
      if playerDBs.count() == 1:
            playerDB = playerDBs[0]
      else:
            playerDB = createPlayer(player)

      return playerDB

MAPHEIGHT = 100

def getOrCreateMap(replay):
      mapDBs = Map.objects.filter(s2ma_hash__exact=replay.map.hash)

      assert mapDBs.count() <= 1
      if mapDBs.count() == 1:
            mapDB = mapDBs[0]
      else:
            mapDB = Map(name=replay.map.name, s2ma_hash=replay.map.hash, gateway=replay.map.gateway)
            mapDB.save()

            # retrieve s2ma from battlenet, extract image
            replay.map.load()
            mapsio = StringIO.StringIO(replay.map.minimap)
            im = Image.open(mapsio)
            cropped = im.crop(im.getbbox())
            cropsize = cropped.size

            # resize height to MAPHEIGHT, and compute new width that
            # would preserve aspect ratio
            newwidth = int(cropsize[0] * (float(MAPHEIGHT) / cropsize[1]))
            finalsize = (newwidth, MAPHEIGHT)
            resized = cropped.resize(finalsize, Image.ANTIALIAS)

            # write cropped resized minimap image to a string as a png
            finalIO = StringIO.StringIO()
            resized.save(finalIO, "png")

            # store that in S3
            bucket = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                                     settings.AWS_SECRET_ACCESS_KEY)\
                                     .lookup(settings.MINIMAP_BUCKET_NAME)
            k = boto.s3.Key(bucket)
            k.key = "%s_%i.png" % (replay.map.hash, MAPHEIGHT)
            k.set_contents_from_string(finalIO.getvalue())

            # clean up
            finalIO.close()

      return mapDB

def populateGameFromReplay(replay, gameDB):
      mapDB = getOrCreateMap(replay)
      gameDB.map = mapDB
      gameDB.release_string = replay.release_string
      gameDB.game_time = datetime.utcfromtimestamp(replay.unix_timestamp)
      gameDB.winning_team = winning_team(replay)
      gameDB.game_type = replay.type
      gameDB.category = replay.category
      gameDB.duration_seconds = replay.length.seconds
      gameDB.save()

      player_to_army = armyjs_map(replay)
      for player in replay.players:
            playerDB = getOrCreatePlayer(player)

            pigDB = PlayerInGame(game=gameDB, player=playerDB)
            pigDB.team = player.team.number
            pigDB.chosen_race = player.pick_race[0]
            pigDB.race = player.play_race[0]
            pigDB.win = didPlayerWin(player)
            pigDB.color = player.color.hex
            pigDB.pid = player.pid
            pigDB.armies_by_frame = player_to_army[player]

            if hasattr(player, "avg_apm"):
                  pigDB.apm = player.avg_apm
            if hasattr(player, "wpm"):
                  pigDB.wpm = player.wpm
            if hasattr(player, "wpm_arr"):
                  pigDB.wpm_by_minute = getWPMArr(player, replay)
            if hasattr(player, "apm_arr"):
                  pigDB.apm_by_minute = getStatArr(player, replay, "apm")

            pigDB.save()
