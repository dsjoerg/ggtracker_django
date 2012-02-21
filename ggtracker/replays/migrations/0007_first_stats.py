# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from replays.models import Stat

class Migration(DataMigration):

    def forwards(self, orm):
        avg_apm = Stat(name="avg_apm", description="average APM until the player leaves")
        avg_apm.save()

        wpm = Stat(name="wpm", description="average Workers Per Minute until the player leaves")
        wpm.save()

    def backwards(self, orm):
        pass


    models = {
        'replays.game': {
            'Meta': {'object_name': 'Game'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'game_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'release_string': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'winning_team': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'replays.player': {
            'Meta': {'object_name': 'Player'},
            'bnet_id': ('django.db.models.fields.IntegerField', [], {}),
            'character_code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'subregion': ('django.db.models.fields.IntegerField', [], {})
        },
        'replays.playeringame': {
            'Meta': {'object_name': 'PlayerInGame'},
            'chosen_race': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Player']"}),
            'race': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'team': ('django.db.models.fields.IntegerField', [], {}),
            'win': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'replays.playeringamestat': {
            'Meta': {'object_name': 'PlayerInGameStat'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Player']"}),
            'stat': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Stat']"}),
            'stat_value': ('django.db.models.fields.FloatField', [], {})
        },
        'replays.stat': {
            'Meta': {'object_name': 'Stat'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['replays']
