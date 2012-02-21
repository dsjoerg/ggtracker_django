# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Sc2Ranks'
        db.create_table('replays_sc2ranks', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['replays.Player'])),
            ('sc2ranks_info', self.gf('django.db.models.fields.CharField')(max_length=10000, null=True)),
            ('sc2ranks_retrieved', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('replays', ['Sc2Ranks'])

        # Adding field 'PlayerInGame.apm'
        db.add_column('replays_playeringame', 'apm', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'PlayerInGame.wpm'
        db.add_column('replays_playeringame', 'wpm', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'PlayerInGame.apm_by_minute'
        db.add_column('replays_playeringame', 'apm_by_minute', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True), keep_default=False)

        # Adding field 'PlayerInGame.wpm_by_minute'
        db.add_column('replays_playeringame', 'wpm_by_minute', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True), keep_default=False)

        # Deleting field 'Stat.description'
        db.delete_column('replays_stat', 'description')

        # Deleting field 'Stat.name'
        db.delete_column('replays_stat', 'name')

        # Deleting field 'PlayerInGameString.stat_value'
        db.delete_column('replays_playeringamestring', 'stat_value')

        # Deleting field 'PlayerInGameString.stat'
        db.delete_column('replays_playeringamestring', 'stat_id')

        # Deleting field 'PlayerInGameString.player_in_game'
        db.delete_column('replays_playeringamestring', 'player_in_game_id')

        # Deleting field 'PlayerInGameStat.stat_value'
        db.delete_column('replays_playeringamestat', 'stat_value')

        # Deleting field 'PlayerInGameStat.stat'
        db.delete_column('replays_playeringamestat', 'stat_id')

        # Deleting field 'PlayerInGameStat.player_in_game'
        db.delete_column('replays_playeringamestat', 'player_in_game_id')


    def backwards(self, orm):
        
        # Deleting model 'Sc2Ranks'
        db.delete_table('replays_sc2ranks')

        # Deleting field 'PlayerInGame.apm'
        db.delete_column('replays_playeringame', 'apm')

        # Deleting field 'PlayerInGame.wpm'
        db.delete_column('replays_playeringame', 'wpm')

        # Deleting field 'PlayerInGame.apm_by_minute'
        db.delete_column('replays_playeringame', 'apm_by_minute')

        # Deleting field 'PlayerInGame.wpm_by_minute'
        db.delete_column('replays_playeringame', 'wpm_by_minute')

        # User chose to not deal with backwards NULL issues for 'Stat.description'
        raise RuntimeError("Cannot reverse this migration. 'Stat.description' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Stat.name'
        raise RuntimeError("Cannot reverse this migration. 'Stat.name' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'PlayerInGameString.stat_value'
        raise RuntimeError("Cannot reverse this migration. 'PlayerInGameString.stat_value' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'PlayerInGameString.stat'
        raise RuntimeError("Cannot reverse this migration. 'PlayerInGameString.stat' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'PlayerInGameString.player_in_game'
        raise RuntimeError("Cannot reverse this migration. 'PlayerInGameString.player_in_game' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'PlayerInGameStat.stat_value'
        raise RuntimeError("Cannot reverse this migration. 'PlayerInGameStat.stat_value' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'PlayerInGameStat.stat'
        raise RuntimeError("Cannot reverse this migration. 'PlayerInGameStat.stat' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'PlayerInGameStat.player_in_game'
        raise RuntimeError("Cannot reverse this migration. 'PlayerInGameStat.player_in_game' and its values cannot be restored.")


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
