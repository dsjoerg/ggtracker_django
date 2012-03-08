# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Game', fields ['game_time']
        db.create_index('replays_game', ['game_time'])

        # Adding field 'Player.avg_wpmx10'
        db.add_column('replays_player', 'avg_wpmx10', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Player.best_league'
        db.add_column('replays_player', 'best_league', self.gf('django.db.models.fields.IntegerField')(null=True, db_index=True), keep_default=False)

        # Adding field 'Player.num_games'
        db.add_column('replays_player', 'num_games', self.gf('django.db.models.fields.IntegerField')(null=True, db_index=True), keep_default=False)

        # Adding field 'Player.best_rank'
        db.add_column('replays_player', 'best_rank', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Player.best_race'
        db.add_column('replays_player', 'best_race', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, db_index=True), keep_default=False)

        # Adding field 'Player.best_num_players'
        db.add_column('replays_player', 'best_num_players', self.gf('django.db.models.fields.IntegerField')(null=True), keep_default=False)

        # Adding field 'Player.best_is_random'
        db.add_column('replays_player', 'best_is_random', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Removing index on 'Game', fields ['game_time']
        db.delete_index('replays_game', ['game_time'])

        # Deleting field 'Player.avg_wpmx10'
        db.delete_column('replays_player', 'avg_wpmx10')

        # Deleting field 'Player.best_league'
        db.delete_column('replays_player', 'best_league')

        # Deleting field 'Player.num_games'
        db.delete_column('replays_player', 'num_games')

        # Deleting field 'Player.best_rank'
        db.delete_column('replays_player', 'best_rank')

        # Deleting field 'Player.best_race'
        db.delete_column('replays_player', 'best_race')

        # Deleting field 'Player.best_num_players'
        db.delete_column('replays_player', 'best_num_players')

        # Deleting field 'Player.best_is_random'
        db.delete_column('replays_player', 'best_is_random')


    models = {
        'replays.buildnode': {
            'Meta': {'object_name': 'BuildNode'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'depth': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.BuildNode']", 'null': 'True', 'blank': 'True'})
        },
        'replays.game': {
            'Meta': {'object_name': 'Game'},
            'average_league': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'duration_seconds': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'game_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'game_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Map']"}),
            'release_string': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'replay': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Replay']"}),
            'winning_team': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'replays.identifiedbuild': {
            'Meta': {'object_name': 'IdentifiedBuild'},
            'buildnode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.BuildNode']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'replays.map': {
            'Meta': {'object_name': 'Map'},
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            's2ma_hash': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'})
        },
        'replays.player': {
            'Meta': {'object_name': 'Player'},
            'avg_wpmx10': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'best_is_random': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'best_league': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'best_num_players': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'best_race': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'db_index': 'True'}),
            'best_rank': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'bnet_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'character_code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'num_games': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_index': 'True'}),
            'sc2ranks_info': ('django.db.models.fields.CharField', [], {'max_length': '50000', 'null': 'True'}),
            'sc2ranks_retrieved': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'subregion': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'replays.playeringame': {
            'Meta': {'object_name': 'PlayerInGame'},
            'apm': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'apm_by_minute': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'chosen_race': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Player']"}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'team': ('django.db.models.fields.IntegerField', [], {}),
            'win': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'wpm': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'wpm_by_minute': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'})
        },
        'replays.playeringamebuild': {
            'Meta': {'object_name': 'PlayerInGameBuild'},
            'buildnode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.BuildNode']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player_in_game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.PlayerInGame']"}),
            'when_seconds': ('django.db.models.fields.IntegerField', [], {})
        },
        'replays.playeringameminute': {
            'Meta': {'object_name': 'PlayerInGameMinute'},
            'apm': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'minute': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'player_in_game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.PlayerInGame']"}),
            'wpm': ('django.db.models.fields.IntegerField', [], {})
        },
        'replays.playeringamestat': {
            'Meta': {'object_name': 'PlayerInGameStat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'replays.playeringamestring': {
            'Meta': {'object_name': 'PlayerInGameString'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'replays.playerleague': {
            'Meta': {'object_name': 'PlayerLeague'},
            'fav_race': ('django.db.models.fields.CharField', [], {'max_length': '1', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_best': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_random': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'league': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'num_players': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Player']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        'replays.replay': {
            'Meta': {'object_name': 'Replay'},
            'dropsc_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        },
        'replays.sc2ranks': {
            'Meta': {'object_name': 'Sc2Ranks'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'replays.sc2rankscache': {
            'Meta': {'object_name': 'Sc2RanksCache'},
            'bnet_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Player']"}),
            'sc2ranks_info': ('django.db.models.fields.CharField', [], {'max_length': '50000', 'null': 'True'}),
            'sc2ranks_retrieved': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'replays.stat': {
            'Meta': {'object_name': 'Stat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['replays']
