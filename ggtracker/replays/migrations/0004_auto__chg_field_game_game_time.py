# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Game.game_time'
        db.alter_column('replays_game', 'game_time', self.gf('django.db.models.fields.DateTimeField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'Game.game_time'
        db.alter_column('replays_game', 'game_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.date(2012, 1, 30)))


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
            'character_code': ('django.db.models.fields.IntegerField', [], {}),
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
            'win': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
