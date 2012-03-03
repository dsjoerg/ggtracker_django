# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Replay.dropsc_id'
        db.add_column('replays_replay', 'dropsc_id', self.gf('django.db.models.fields.IntegerField')(max_length=255, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Replay.dropsc_id'
        db.delete_column('replays_replay', 'dropsc_id')


    models = {
        'replays.buildnode': {
            'Meta': {'object_name': 'BuildNode'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.BuildNode']", 'null': 'True', 'blank': 'True'})
        },
        'replays.game': {
            'Meta': {'object_name': 'Game'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'duration_seconds': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'game_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'game_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Map']"}),
            'release_string': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'replay': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Replay']"}),
            'winning_team': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'replays.map': {
            'Meta': {'object_name': 'Map'},
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            's2ma_hash': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'})
        },
        'replays.player': {
            'Meta': {'object_name': 'Player'},
            'bnet_id': ('django.db.models.fields.IntegerField', [], {}),
            'character_code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'sc2ranks_info': ('django.db.models.fields.CharField', [], {'max_length': '50000', 'null': 'True'}),
            'sc2ranks_retrieved': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'subregion': ('django.db.models.fields.IntegerField', [], {})
        },
        'replays.playeringame': {
            'Meta': {'object_name': 'PlayerInGame'},
            'apm': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'apm_by_minute': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'chosen_race': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Player']"}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
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
            'minute': ('django.db.models.fields.IntegerField', [], {}),
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
            'fav_race': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_best': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_random': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'league': ('django.db.models.fields.IntegerField', [], {}),
            'num_players': ('django.db.models.fields.IntegerField', [], {}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Player']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        'replays.replay': {
            'Meta': {'object_name': 'Replay'},
            'dropsc_id': ('django.db.models.fields.IntegerField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'md5hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        },
        'replays.sc2ranks': {
            'Meta': {'object_name': 'Sc2Ranks'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'replays.sc2rankscache': {
            'Meta': {'object_name': 'Sc2RanksCache'},
            'bnet_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
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
