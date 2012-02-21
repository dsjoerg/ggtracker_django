# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        db.delete_table('replays_game')

        # Adding model 'Game'
        db.create_table('replays_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('release_string', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('winning_team', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('replays', ['Game'])


    def backwards(self, orm):
        
        # Deleting model 'Game'
        db.delete_table('replays_game')


    models = {
        'replays.game': {
            'Meta': {'object_name': 'Game'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'release_string': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'winning_team': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['replays']
