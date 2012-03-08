# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Game', fields ['category']
        db.create_index('replays_game', ['category'])

        # Adding index on 'Game', fields ['average_league']
        db.create_index('replays_game', ['average_league'])

        # Adding index on 'Game', fields ['game_type']
        db.create_index('replays_game', ['game_type'])

        # Adding index on 'Game', fields ['release_string']
        db.create_index('replays_game', ['release_string'])

        # Adding index on 'PlayerInGame', fields ['chosen_race']
        db.create_index('replays_playeringame', ['chosen_race'])

        # Adding index on 'PlayerInGame', fields ['race']
        db.create_index('replays_playeringame', ['race'])

        # Adding index on 'BuildNode', fields ['action']
        db.create_index('replays_buildnode', ['action'])

        # Adding index on 'BuildNode', fields ['depth']
        db.create_index('replays_buildnode', ['depth'])

        # Adding index on 'Sc2RanksCache', fields ['bnet_url']
        db.create_index('replays_sc2rankscache', ['bnet_url'])

        # Adding index on 'Player', fields ['bnet_id']
        db.create_index('replays_player', ['bnet_id'])

        # Adding index on 'Player', fields ['name']
        db.create_index('replays_player', ['name'])

        # Adding index on 'Player', fields ['region']
        db.create_index('replays_player', ['region'])

        # Adding index on 'Player', fields ['subregion']
        db.create_index('replays_player', ['subregion'])

        # Adding index on 'Player', fields ['gateway']
        db.create_index('replays_player', ['gateway'])

        # Adding index on 'Replay', fields ['dropsc_id']
        db.create_index('replays_replay', ['dropsc_id'])

        # Adding index on 'PlayerInGameMinute', fields ['minute']
        db.create_index('replays_playeringameminute', ['minute'])

        # Adding index on 'Map', fields ['s2ma_hash']
        db.create_index('replays_map', ['s2ma_hash'])

        # Adding index on 'Map', fields ['name']
        db.create_index('replays_map', ['name'])

        # Adding index on 'PlayerLeague', fields ['num_players']
        db.create_index('replays_playerleague', ['num_players'])

        # Adding index on 'PlayerLeague', fields ['league']
        db.create_index('replays_playerleague', ['league'])

        # Adding index on 'PlayerLeague', fields ['fav_race']
        db.create_index('replays_playerleague', ['fav_race'])

        # Adding index on 'PlayerLeague', fields ['is_best']
        db.create_index('replays_playerleague', ['is_best'])

        # Adding index on 'PlayerLeague', fields ['is_random']
        db.create_index('replays_playerleague', ['is_random'])


    def backwards(self, orm):
        
        # Removing index on 'PlayerLeague', fields ['is_random']
        db.delete_index('replays_playerleague', ['is_random'])

        # Removing index on 'PlayerLeague', fields ['is_best']
        db.delete_index('replays_playerleague', ['is_best'])

        # Removing index on 'PlayerLeague', fields ['fav_race']
        db.delete_index('replays_playerleague', ['fav_race'])

        # Removing index on 'PlayerLeague', fields ['league']
        db.delete_index('replays_playerleague', ['league'])

        # Removing index on 'PlayerLeague', fields ['num_players']
        db.delete_index('replays_playerleague', ['num_players'])

        # Removing index on 'Map', fields ['name']
        db.delete_index('replays_map', ['name'])

        # Removing index on 'Map', fields ['s2ma_hash']
        db.delete_index('replays_map', ['s2ma_hash'])

        # Removing index on 'PlayerInGameMinute', fields ['minute']
        db.delete_index('replays_playeringameminute', ['minute'])

        # Removing index on 'Replay', fields ['dropsc_id']
        db.delete_index('replays_replay', ['dropsc_id'])

        # Removing index on 'Player', fields ['gateway']
        db.delete_index('replays_player', ['gateway'])

        # Removing index on 'Player', fields ['subregion']
        db.delete_index('replays_player', ['subregion'])

        # Removing index on 'Player', fields ['region']
        db.delete_index('replays_player', ['region'])

        # Removing index on 'Player', fields ['name']
        db.delete_index('replays_player', ['name'])

        # Removing index on 'Player', fields ['bnet_id']
        db.delete_index('replays_player', ['bnet_id'])

        # Removing index on 'Sc2RanksCache', fields ['bnet_url']
        db.delete_index('replays_sc2rankscache', ['bnet_url'])

        # Removing index on 'BuildNode', fields ['depth']
        db.delete_index('replays_buildnode', ['depth'])

        # Removing index on 'BuildNode', fields ['action']
        db.delete_index('replays_buildnode', ['action'])

        # Removing index on 'PlayerInGame', fields ['race']
        db.delete_index('replays_playeringame', ['race'])

        # Removing index on 'PlayerInGame', fields ['chosen_race']
        db.delete_index('replays_playeringame', ['chosen_race'])

        # Removing index on 'Game', fields ['release_string']
        db.delete_index('replays_game', ['release_string'])

        # Removing index on 'Game', fields ['game_type']
        db.delete_index('replays_game', ['game_type'])

        # Removing index on 'Game', fields ['average_league']
        db.delete_index('replays_game', ['average_league'])

        # Removing index on 'Game', fields ['category']
        db.delete_index('replays_game', ['category'])


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
            'game_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
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
            'bnet_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'character_code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'gateway': ('django.db.models.fields.CharField', [], {'max_length': '5', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
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
