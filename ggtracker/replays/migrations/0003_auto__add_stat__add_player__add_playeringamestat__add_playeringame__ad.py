# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Stat'
        db.create_table('replays_stat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('replays', ['Stat'])

        # Adding model 'Player'
        db.create_table('replays_player', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('gateway', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('subregion', self.gf('django.db.models.fields.IntegerField')()),
            ('bnet_id', self.gf('django.db.models.fields.IntegerField')()),
            ('character_code', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('replays', ['Player'])

        # Adding model 'PlayerInGameStat'
        db.create_table('replays_playeringamestat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['replays.Game'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['replays.Player'])),
            ('stat', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['replays.Stat'])),
            ('stat_value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('replays', ['PlayerInGameStat'])

        # Adding model 'PlayerInGame'
        db.create_table('replays_playeringame', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['replays.Game'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['replays.Player'])),
            ('team', self.gf('django.db.models.fields.IntegerField')()),
            ('chosen_race', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('race', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('win', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('replays', ['PlayerInGame'])

        # Adding field 'Game.game_time'
        db.add_column('replays_game', 'game_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.date(2012, 1, 30)), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'Stat'
        db.delete_table('replays_stat')

        # Deleting model 'Player'
        db.delete_table('replays_player')

        # Deleting model 'PlayerInGameStat'
        db.delete_table('replays_playeringamestat')

        # Deleting model 'PlayerInGame'
        db.delete_table('replays_playeringame')

        # Deleting field 'Game.game_time'
        db.delete_column('replays_game', 'game_time')


    models = {
        'replays.game': {
            'Meta': {'object_name': 'Game'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'game_time': ('django.db.models.fields.DateTimeField', [], {}),
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
