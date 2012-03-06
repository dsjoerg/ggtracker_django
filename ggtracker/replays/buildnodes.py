import StringIO
import boto
import vendor.sc2reader

from boto.s3.key import Key
from django.conf import settings
from models import *
from vendor.sc2reader.processors.macro import Macro

class BuildNodes():

      def __init__(self):
            print "connecting to bucket %s" % settings.REPLAYS_BUCKET_NAME
            self.replaybucket = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                                                settings.AWS_SECRET_ACCESS_KEY)\
                                                .lookup(settings.REPLAYS_BUCKET_NAME)

      def get_file_from_s3(self, s3key):
            print "retrieving key = %s" % s3key
            k = Key(self.replaybucket)
            k.key = s3key
            stringio = StringIO.StringIO()
            k.get_contents_to_file(stringio)
            return stringio

      def get_replay_file_for_game_id(self, id):
            game = Game.objects.get(id__exact=id)
            replay = game.replay
            file = self.get_file_from_s3(game.replay.s3key())
            return file

      def destroy_build_for_game(self, game):
            PlayerInGameBuild.objects.filter(player_in_game__game__exact=game).delete()

      def populate_build(self, game, player):
            pig = PlayerInGame.objects.get(player__bnet_id__exact=player.uid, game__exact=game)
            if not hasattr(player, "bo"):
                  return

            builtitems = player.bo.lower().split("|")

            current_node, created = BuildNode.objects.get_or_create(parent=None, action=pig.race.lower())
            PlayerInGameBuild(player_in_game=pig, buildnode=current_node, when_seconds=0).save()

            for builtitem in builtitems[0:25]:
                  current_node, created = BuildNode.objects.get_or_create(parent=current_node, action=builtitem)
                  PlayerInGameBuild(player_in_game=pig, buildnode=current_node, when_seconds=0).save()

      def populate_bo_for_game(self, id):
            game = Game.objects.get(id__exact=id)
            self.destroy_build_for_game(game)

            file = self.get_replay_file_for_game_id(id)
            replay = vendor.sc2reader.read_file(file, processors=[Macro])

            for player in replay.players:
                  self.populate_build(game, player)
