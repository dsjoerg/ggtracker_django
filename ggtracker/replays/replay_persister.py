import Image
import hashlib
import boto
import sc2reader
import StringIO
import pytz
from s2gs_persister import *
from buildnodes import *

from models import *
from snapshotter import *

from datetime import datetime
from datetime import timedelta
from pytz import timezone
from django.conf import settings
from boto.s3.key import Key

import plugins
plugins.setup()

class ReplayPersister():

      def __init__(self):
            self.replaybucket = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                                                settings.AWS_SECRET_ACCESS_KEY)\
                                                .lookup(settings.REPLAYS_BUCKET_NAME)
            self.buildnodes = BuildNodes()

      def get_file_from_s3(self, s3key):
            k = Key(self.replaybucket)
            k.key = s3key
            stringio = StringIO.StringIO()
            k.get_contents_to_file(stringio)
            return stringio

      # this function gets called when uploading through the
      # ruby-served page
      def upload_from_ruby(self, id, sender_subdomain):
            replayDB = Replay.objects.get(id__exact=id)
            replaystringio = self.get_file_from_s3("%s.SC2Replay" % replayDB.md5hash)
            replay = sc2reader.load_replay(replaystringio)

            first_player = getOrCreatePlayer(replay.players[0])
            endtime = datetime.utcfromtimestamp(replay.unix_timestamp)
            gamesecs = replay.length.seconds
            realsecs = gamesecs / 1.4
            starttime = endtime - timedelta(seconds=realsecs)
            utc = pytz.utc
            eastern = timezone('US/Eastern')
            utc_starttime = utc.localize(starttime)
            loc_starttime = utc_starttime.astimezone(eastern)
            gameDBs = S2GSPersister.games_with_player_and_start(first_player, loc_starttime)
            print "Game started at %(starttime)s, lasted %(realsecs)i real seconds and %(gamesecs)i game seconds" % {"starttime": loc_starttime, "realsecs": realsecs, "gamesecs": gamesecs}

            if len(list(gameDBs)) == 1:
                  # this could either be a reupload of a replay,
                  # or we only had the s2gs before.
                  # set the new subdomain only if it used to be blank
                  #
                  gameDB = gameDBs[0]
                  if not gameDB.subdomain:
                        gameDB.subdomain = sender_subdomain 
                  gameDB.replay = replayDB
            elif len(list(gameDBs)) > 1:
                  print "Oooh, more than one game found for replay %(replay_id)i. Game IDs:" % {"replay_id": int(id)}
                  for gameDB in gameDBs:
                        print gameDB.id
            else:
                  # make a new game record
                  gameDB = Game(replay=replayDB, subdomain=sender_subdomain)

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
            replaystringio.close()
            
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
            
            replay = vendor.sc2reader.read_file(stringio, processors=[Macro], apply=True)
            populateGameFromReplay(replay, gameDB)
            for player in replay.players:
                  self.buildnodes.populate_build(gameDB, player)



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
            if playerDB.name is None or playerDB.name == "":
                  playerDB.name = player.name
                  playerDB.save()
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
            k = Key(bucket)
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

            # if there are any PIGs for this game, blow them away.
            # we have all the interesting PIG data in our replay
            pigsDB = PlayerInGame.objects.filter(player=playerDB, game=gameDB)
            pigsDB.delete()

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
