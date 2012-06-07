import boto
import vendor.sc2reader
import StringIO
import pytz

from django.conf import settings
from boto.s3.key import Key
from datetime import datetime, timedelta
from django.db.models import F
from pytz import timezone

from models import *

class S2GSPersister():

      def __init__(self):
            self.replaybucket = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                                                settings.AWS_SECRET_ACCESS_KEY)\
                                                .lookup(settings.REPLAYS_BUCKET_NAME)

      def get_file_from_s3(self, s3key):
            k = Key(self.replaybucket)
            k.key = s3key
            stringio = StringIO.StringIO()
            k.get_contents_to_file(stringio)
            return stringio

      def saveBuildOrder(self, boDB, build_order):
            for boitem in build_order:
                  itemDB, created = Item.objects.get_or_create(name=boitem['order']['name'])
                  boitemDB = BuildOrderItem(build_order=boDB,
                                            built_item=itemDB,
                                            build_seconds=boitem['time'],
                                            supply=boitem['supply'],
                                            total_supply=boitem['total_supply'])
                  boitemDB.save()

      def saveGraph(self, graphDB, graph):
            for time,value in zip(graph.times, graph.values):
                  gpDB = GraphPoint(graph=graphDB,
                                    graph_seconds=time,
                                    graph_value=value)
                  gpDB.save()

      # race = s2gs.player[0].race
      # chosen_race = s2gs.player_props[1][3001]
      # who won = s2gs.player[0].is_winner
      # team = int(s2gs.player_props[0][2002].replace("\x00","").replace("T",""))  but depending on game mode, it may not be 2002. see constants.py
      def createOrCheckPIG(self, playerDB, gameDB, s2gsplayer, s2gs):
            pigsDB = PlayerInGame.objects.filter(player=playerDB, game=gameDB)
            assert pigsDB.count() <= 1
            if pigsDB.count() == 1:
                  failedmatches = list()
                  if pigsDB[0].team != s2gsplayer.teamid:
                        failedmatches.append("team")
                  if pigsDB[0].race != s2gsplayer.race[0]:
                        failedmatches.append("race")
                  if pigsDB[0].chosen_race != s2gs.player_props[s2gsplayer.pid][3001][0]:
                        failedmatches.append("chosen_race")
                  if pigsDB[0].win != s2gsplayer.is_winner:
                        failedmatches.append("is_winner")

                  if len(failedmatches) > 0:
                        print "%(failures)s didnt match between s2gs and db. game=%(gameid)i, s2gs=%(s2gs)s" % \
                            {"gameid": gameDB.id,
                             "s2gs": s2gs.filehash,
                             "failures": " ".join(failedmatches)}
                        #TODO alert a human for real
            else:
                  pigDB = PlayerInGame(player=playerDB,
                                       game=gameDB,
                                       team=s2gsplayer.teamid,
                                       race=s2gsplayer.race[0],
                                       chosen_race=s2gs.player_props[s2gsplayer.pid][3001][0],
                                       win=s2gsplayer.is_winner)
                  pigDB.save()

      # find any games that had the given player and started within 15 seconds of the given time,
      # which is a datetime localized to US Eastern time.
      @staticmethod
      def games_with_player_and_start(player, loc_starttime):
            #
            # Game.game_time is the end time of the replay.  We compute the games start time
            # by translating its duration_seconds into real time (we assume Faster!),
            # and then comparing to the given loc_starttime.
            #
            queryString = "SELECT DISTINCT g.* from replays_game g, replays_playeringame pig, replays_player p "
            queryString = queryString + "where (game_time - (INTERVAL '1 second' * duration_seconds/1.4)) - '%(starttime)s' between INTERVAL '-15 seconds' and INTERVAL '15 seconds'" % {"starttime": loc_starttime}
            queryString = queryString + " AND g.id = pig.game_id "
            queryString = queryString + " AND p.id = pig.player_id "
            queryString = queryString + " AND p.bnet_id = %(bnet_id)i " % {"bnet_id": player.bnet_id}
            queryString = queryString + " AND p.subregion = %(subregion)i " % {"subregion": player.subregion}
            games = Game.objects.raw(queryString)
            return games


      def upload(self, id):
            gameSummaryDB = GameSummary.objects.get(id__exact=id)
            s2gsio = self.get_file_from_s3("s2gs/%s.s2gs" % gameSummaryDB.s2gs_hash)

            s2gs = vendor.sc2reader.resources.GameSummary(s2gsio)

            players = list()
            for player in s2gs.players:
                  if not player.is_ai:
                        print "Looking for player ", player.bnetid, player.subregion
                        playerQ = Player.objects.filter(gateway__exact="us")
                        playerQ = playerQ.filter(bnet_id__exact=player.bnetid)
                        playerQ = playerQ.filter(subregion__exact=player.subregion)
                        assert playerQ.count() <= 1
                        theplayer = None
                        if playerQ.count() == 1:
                              theplayer = playerQ[0]
                              print "Found player", theplayer
                        else:
                              theplayer = Player(gateway="us", bnet_id=player.bnetid, subregion=player.subregion)
                              theplayer.save()
                              print "created player", theplayer
                        players.append([theplayer, player])

            endtime = datetime.utcfromtimestamp(s2gs.time)
            starttime = endtime - s2gs.real_length
            utc = pytz.utc
            eastern = timezone('US/Eastern')
            utc_starttime = utc.localize(starttime)
            loc_starttime = utc_starttime.astimezone(eastern)
            print "Game started at %(starttime)s, lasted %(realsecs)i real seconds and %(gamesecs)i game seconds" % {"starttime": loc_starttime, "realsecs": s2gs.real_length.seconds, "gamesecs": s2gs.game_length.seconds}

            games = games_with_player_and_start(players[0][0], loc_starttime)

            thegame = None
            if len(list(games)) == 0:
                  thegame = Game(game_time=endtime, upload_time=datetime.now(), game_type=s2gs.game_type(), duration_seconds=s2gs.game_length.seconds)
                  thegame.save()
            elif len(list(games)) > 1:
                  print "Oooh, more than one game found for gamesummary %(gamesummary_id)i" % {"gamesummary_id": id}
            else:
                  thegame = games[0]

            print "got the game!", thegame
            gameSummaryDB.game = thegame
            gameSummaryDB.save()

            for [player, s2gsplayer] in players:
                  print "Hi! ", player, s2gsplayer

                  # create PlayerInGame records if necessary
                  self.createOrCheckPIG(player, thegame, s2gsplayer, s2gs)
                  # TODO if it already exists, check and see if its fields match what we expect
                  
                  # blow away playersummary for this player and game
                  playersummariesDB = PlayerSummary.objects.filter(player__exact=player, game__exact=thegame)
                  assert playersummariesDB.count() <= 1
                  if playersummariesDB.count() == 1:
                        psDB = playersummariesDB[0]
                        print "deleting ", psDB
                        psDB.build_order.delete()
                        psDB.army_graph.delete()
                        psDB.income_graph.delete()
                        psDB.delete()

                  bo = BuildOrder()
                  bo.save()
                  army_graph = Graph()
                  army_graph.save()
                  income_graph = Graph()
                  income_graph.save()

                  # save s2gs data for this player
                  psDB = PlayerSummary(game=thegame, player=player, build_order=bo, army_graph=army_graph, income_graph=income_graph,
                                       resources=s2gsplayer.stats['R'],
                                       units=s2gsplayer.stats['U'],
                                       structures=s2gsplayer.stats['S'],
                                       overview=s2gsplayer.stats['O'],
                                       average_unspent_resources=s2gsplayer.stats['AUR'],
                                       resource_collection_rate=s2gsplayer.stats['RCR'],
                                       workers_created=s2gsplayer.stats['WC'],
                                       units_trained=s2gsplayer.stats['UT'],
                                       killed_unit_count=s2gsplayer.stats['KUC'],
                                       structures_built=s2gsplayer.stats['SB'],
                                       structures_razed_count=s2gsplayer.stats['SRC'])
                  psDB.save()

                  self.saveBuildOrder(bo, s2gs.build_orders[s2gsplayer.pid])
                  self.saveGraph(army_graph, s2gsplayer.army_graph)
                  self.saveGraph(income_graph, s2gsplayer.income_graph)

                  pass

            return True

# TODO scenarios to confirm work properly.
#      how about a test suite?
# nothing then s2gs
# replay then s2gs
# s2gs then replays
# s2gs then s2gs
# s2gs and replay then s2gs
# s2gs and replay then replay
# what if the replay is an MLG replay?
