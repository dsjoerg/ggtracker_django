# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Sc2RanksCache'
        db.create_table('replays_sc2rankscache', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['replays.Player'])),
            ('bnet_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True)),
            ('sc2ranks_info', self.gf('django.db.models.fields.CharField')(max_length=10000, null=True)),
            ('sc2ranks_retrieved', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('replays', ['Sc2RanksCache'])

        # Deleting field 'Sc2Ranks.bnet_url'
        db.delete_column('replays_sc2ranks', 'bnet_url')

        # Deleting field 'Sc2Ranks.sc2ranks_info'
        db.delete_column('replays_sc2ranks', 'sc2ranks_info')

        # Deleting field 'Sc2Ranks.player'
        db.delete_column('replays_sc2ranks', 'player_id')

        # Deleting field 'Sc2Ranks.sc2ranks_retrieved'
        db.delete_column('replays_sc2ranks', 'sc2ranks_retrieved')


    def backwards(self, orm):
        
        # Deleting model 'Sc2RanksCache'
        db.delete_table('replays_sc2rankscache')

        # Adding field 'Sc2Ranks.bnet_url'
        db.add_column('replays_sc2ranks', 'bnet_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True), keep_default=False)

        # Adding field 'Sc2Ranks.sc2ranks_info'
        db.add_column('replays_sc2ranks', 'sc2ranks_info', self.gf('django.db.models.fields.CharField')(max_length=10000, null=True), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'Sc2Ranks.player'
        raise RuntimeError("Cannot reverse this migration. 'Sc2Ranks.player' and its values cannot be restored.")

        # Adding field 'Sc2Ranks.sc2ranks_retrieved'
        db.add_column('replays_sc2ranks', 'sc2ranks_retrieved', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)


    models = {
        'replays.game': {
            'Meta': {'object_name': 'Game'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'duration_seconds': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'game_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'game_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'map': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['replays.Map']"}),
            'md5hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'release_string': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'winning_team': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'replays.map': {
            'Meta': {'object_name': 'Map'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'replays.player': {
            'Meta': {'object_name': 'Player'},
            'bnet_id': ('django.db.models.fields.IntegerField', [], {}),
            'character_code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'sc2ranks_info': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True'}),
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
        'replays.playeringamestat': {
            'Meta': {'object_name': 'PlayerInGameStat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'replays.playeringamestring': {
            'Meta': {'object_name': 'PlayerInGameString'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'sc2ranks_info': ('django.db.models.fields.CharField', [], {'max_length': '10000', 'null': 'True'}),
            'sc2ranks_retrieved': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'replays.stat': {
            'Meta': {'object_name': 'Stat'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['replays']
