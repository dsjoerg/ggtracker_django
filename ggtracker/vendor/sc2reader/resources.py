from __future__ import absolute_import

import zlib
import pprint
import hashlib
from datetime import datetime
import time
from StringIO import StringIO
from collections import defaultdict, deque

import urllib2
from mpyq import MPQArchive

from sc2reader import utils
from sc2reader import readers, data
from sc2reader.objects import Player, Observer, Team, PlayerSummary, Graph
from sc2reader.constants import REGIONS, LOCALIZED_RACES, GAME_SPEED_FACTOR, GAME_SPEED_CODES, RACE_CODES, PLAYER_TYPE_CODES, TEAM_COLOR_CODES, GAME_FORMAT_CODES, GAME_TYPE_CODES, DIFFICULTY_CODES


class Resource(object):
    def __init__(self, file_object, filename=None, **options):
        self.opt = utils.AttributeDict(options)
        self.filename = filename or getattr(file_object,'name','Unavailable')

        file_object.seek(0)
        self.filehash = hashlib.sha256(file_object.read()).hexdigest()
        file_object.seek(0)

class GameSummary(Resource):
    base_url_template = 'http://{0}.depot.battle.net:1119/{1}.{2}'
    url_template = 'http://{0}.depot.battle.net:1119/{1}.s2gs'

    stats_keys = [
        'R',
        'U',
        'S',
        'O',
        'AUR',
        'RCR',
        'WC',
        'UT',
        'KUC',
        'SB',
        'SRC',
        ]

    #: Game speed
    game_speed = str()

    #: Game length (real-time)
    real_length = int()

    #: Game length (in-game)
    game_length = int()

    #: A dictionary of Lobby properties
    lobby_properties = dict()

    #: A dictionary of Lobby player properties
    lobby_player_properties = dict()

    #: Game completion time
    time = int()

    #: Players, a dict of :class`PlayerSummary` from the game
    players = dict()

    #: Teams, a dict of pids
    teams = dict()

    #: Winners, a list of the pids of the winning players
    winners = list()

    #: Build orders, a dict of build orders indexed by player id
    build_orders = dict()

    #: Map image urls
    image_urls = list()

    #: Map localization urls
    localization_urls = dict()

    def __init__(self, summary_file, filename=None, **options):
        super(GameSummary, self).__init__(summary_file, filename,**options)

        self.team = dict()
        self.teams = list()
        self.players = list()
        self.winners = list()
        self.player = dict()
        self.build_orders = dict()
        self.image_urls = list()
        self.localization_urls = dict()
        self.lobby_properties = dict()
        self.lobby_player_properties = dict()

        # The first 16 bytes appear to be some sort of compression header
        buffer = utils.ReplayBuffer(zlib.decompress(summary_file.read()[16:]))

        # TODO: Is there a fixed number of entries?
        # TODO: Maybe the # of parts is recorded somewhere?
        self.parts = list()
        while buffer.left:
            self.parts.append(buffer.read_data_struct())

        # Parse basic info
        self.game_speed = GAME_SPEED_CODES[''.join(reversed(self.parts[0][0][1]))]

        # time struct looks like this:
        # { 0: 11987, 1: 283385849, 2: 1334719793L}
        # 0, 1 might be an adjustment of some sort
        self.unknown_time = self.parts[0][2][2]

        # this one is alone as a unix timestamp
        self.time = self.parts[0][8]

        # in seconds
        self.game_length = utils.Length(seconds=self.parts[0][7])
        self.real_length = utils.Length(seconds=self.parts[0][7]/GAME_SPEED_FACTOR[self.game_speed])

        self.load_lobby_properties()
        self.load_player_info()
        self.load_player_graphs()
        self.load_map_data()
        self.load_player_builds()

    def load_player_builds(self):
        # Parse build orders
        bo_structs = [x[0] for x in self.parts[5:]]
        bo_structs.append(self.parts[4][0][3:])

        # This might not be the most effective way, but it works
        for pid, p in self.player.items():
            bo = list()
            for bo_struct in bo_structs:
                for order in bo_struct:

                    if order[0][1] >> 24 == 0x01:
                        # unit
                        parsed_order = utils.get_unit(order[0][1])
                    elif order[0][1] >> 24 == 0x02:
                        # research
                        parsed_order = utils.get_research(order[0][1])

                    for entry in order[1][p.pid]:
                        bo.append({
                                'supply' : entry[0],
                                'total_supply' : entry[1]&0xff,
                                'time' : (entry[2] >> 8) / 16,
                                'order' : parsed_order,
                                'build_index' : entry[1] >> 16,
                                })
            bo.sort(key=lambda x: x['build_index'])
            self.build_orders[p.pid] = bo

    def load_map_data(self):
        # Parse map localization data
        for l in self.parts[0][6][8]:
            lang = l[0]
            urls = list()
            for hash in l[1]:
                parsed_hash = utils.parse_hash(hash)
                if not parsed_hash['server']:
                    continue
                urls.append(self.base_url_template.format(parsed_hash['server'], parsed_hash['hash'], parsed_hash['type']))

            self.localization_urls[lang] = urls

        # Parse map images
        for hash in self.parts[0][6][7]:
            parsed_hash = utils.parse_hash(hash)
            self.image_urls.append(self.base_url_template.format(parsed_hash['server'], parsed_hash['hash'], parsed_hash['type']))

    def load_player_graphs(self):
        # Parse graph and stats stucts, for each player
        for pid, p in self.player.items():
#            print type(pid), type(p)
            # Graph stuff
            xy = [(o[2], o[0]) for o in self.parts[4][0][2][1][p.pid]]
            p.army_graph = Graph([], [], xy_list=xy)

            xy = [(o[2], o[0]) for o in self.parts[4][0][1][1][p.pid]]
            p.income_graph = Graph([], [], xy_list=xy)

            # Stats stuff
            stats_struct = self.parts[3][0]
            # The first group of stats is located in parts[3][0]
            for i in range(len(stats_struct)):
                p.stats[self.stats_keys[i]] = stats_struct[i][1][p.pid][0][0]
            # The last piece of stats is in parts[4][0][0][1]
            p.stats[self.stats_keys[len(stats_struct)]] = self.parts[4][0][0][1][p.pid][0][0]

    def load_player_info(self):
        # Parse player structs, 16 is the maximum amount of players
        for i in range(16):
            # Check if player, skip if not
            if self.parts[0][3][i][2] == '\x00\x00\x00\x00':
                continue

            player_struct = self.parts[0][3][i]

            player = PlayerSummary(player_struct[0][0])
            player.race = RACE_CODES[''.join(reversed(player_struct[2]))]

            # TODO: Grab team id from lobby_player_properties
            player.teamid = 0

            player.is_winner = (player_struct[1][0] == 0)
            if player.is_winner:
                self.winners.append(player.pid)

            # Is the player an ai?
            if type(player_struct[0][1]) == type(int()):
                player.is_ai = True
            else:
                player.is_ai = False

                player.bnetid = player_struct[0][1][0][3]
                player.subregion = player_struct[0][1][0][2]

                # int
                player.unknown1 = player_struct[0][1][0]
                # {0:long1, 1:long2}
                # Example:
                # { 0: 3405691582L, 1: 11402158793782460416L}
                player.unknown2 = player_struct[0][1][1]

            self.players.append(player)
            self.player[player.pid] = player

            if not player.teamid in self.teams:
                self.team[player.teamid] = list()
            self.team[player.teamid].append(player.pid)
        self.teams = [self.team[tid] for tid in sorted(self.team.keys())]

    def load_lobby_properties(self):
        #Monster function used to parse lobby properties in GameSummary
        #
        # The definition of each lobby property is in data[0][5] with the structure
        #
        # id = def[0][1] # The unique property id
        # vals = def[1]  # A list with the values the property can be
        # reqs = def[3]  # A list of requirements the property has
        # dflt = def[8]  # The default value(s) of the property
        #                this is a single entry for a global property
        #                and a list() of entries for a player property

        # The def-values is structured like this
        #
        # id = `the index in the vals list`
        # name = v[0]    # The name of the value

        # The requirement structure looks like this
        #
        # id = r[0][1][1] # The property id of this requirement
        # vals = r[1]     # A list of names of valid values for this requirement

        ###
        # The values of each property is in data[0][6][6] with the structure
        #
        # id = v[0][1]  # The property id of this value
        # vals = v[1]   # The value(s) of this property
        #                this is a single entry for a global property
        #                and a list() of entries for a player property

        ###
        # A value-entry looks like this
        #
        # index = v[0]  # The index in the def.vals array representing the value
        # unknown = v[1]

        # TODO: this indirection is confusing, fix at some point..
        data = self.parts

        # First get the definitions in data[0][5]
        defs = dict()
        for d in data[0][5]:
            k = d[0][1]
            defs[k] = {
                'id':k,
                'vals':d[1],
                'reqs':d[3],
                'dflt':d[8],
                'lobby_prop':type(d[8]) == type(dict())
                }
        vals = dict()

        # Get the values in data[0][6][6]
        for v in data[0][6][6]:
            k = v[0][1]
            vals[k] = {
                'id':k,
                'vals':v[1]
                }

        lobby_ids = [k for k in defs if defs[k]['lobby_prop']]
        lobby_ids.sort()
        player_ids = [k for k in defs if not defs[k]['lobby_prop']]
        player_ids.sort()

        left_lobby = deque([k for k in defs if defs[k]['lobby_prop']])

        lobby_props = dict()
        # We cycle through all property values 'til we're done
        while len(left_lobby) > 0:
            propid = left_lobby.popleft()
            can_be_parsed = True
            active = True
            # Check the requirements
            for req in defs[propid]['reqs']:
                can_be_parsed = can_be_parsed and (req[0][1][1] in lobby_props)
                # Have we parsed all req-fields?
                if not can_be_parsed:
                    break
                # Is this requirement fullfilled?
                active = active and (lobby_props[req[0][1][1]] in req[1])

            if not can_be_parsed:
                # Try parse this later
                left_lobby.append(propid)
                continue
            if not active:
                # Ok, so the reqs weren't fullfilled, don't use this property
                continue
            # Nice! We've parsed a property
            lobby_props[propid] = defs[propid]['vals'][vals[propid]['vals'][0]][0]

        player_props = [dict() for pid in range(16)]
        # Parse each player separately (this is required :( )
        for pid in range(16):
            left_players = deque([a for a in player_ids])
            player = dict()

            # Use this to avoid an infinite loop
            last_success = 0
            max = len(left_players)
            while len(left_players) > 0 and not (last_success > max+1):
                last_success += 1
                propid = left_players.popleft()
                can_be_parsed = True
                active = True
                for req in defs[propid]['reqs']:
                    #req is a lobby prop
                    if req[0][1][1] in lobby_ids:
                        active = active and (req[0][1][1] in lobby_props) and (lobby_props[req[0][1][1]] in req[1])
                    #req is a player prop
                    else:
                        can_be_parsed = can_be_parsed and (req[0][1][1] in player)
                        if not can_be_parsed:
                            break
                        active = active and (player[req[0][1][1]] in req[1])

                if not can_be_parsed:
                    left_players.append(propid)
                    continue
                last_success = 0
                if not active:
                    continue
                player[propid] = defs[propid]['vals'][vals[propid]['vals'][pid][0]][0]

            player_props[pid] = player

        self.lobby_props = lobby_props
        self.player_props = player_props

    def __str__(self):
        return "{} - {} {}".format(time.ctime(self.time),self.game_length,
                                         'v'.join(''.join(self.players[p].race[0] for p in self.teams[tid]) for tid in self.teams))

