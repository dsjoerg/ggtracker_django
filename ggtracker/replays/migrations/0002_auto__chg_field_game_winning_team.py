# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Game.winning_team'
        db.alter_column('replays_game', 'winning_team', self.gf('django.db.models.fields.IntegerField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'Game.winning_team'
        db.alter_column('replays_game', 'winning_team', self.gf('django.db.models.fields.IntegerField')(default=0))


    models = {
        'replays.game': {
            'Meta': {'object_name': 'Game'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'release_string': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'winning_team': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['replays']
