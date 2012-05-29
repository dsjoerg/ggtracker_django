from django.db import models

class Replay(models.Model):
    md5hash = models.CharField(max_length=32, db_index=True)
    dropsc_id = models.IntegerField(max_length=255, null=True, blank=True, db_index=True)
    source = models.CharField(max_length=64, db_index=True, null=True, blank=True)

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.md5hash)

    def s3key(self):
        return '%s.SC2Replay' % self.md5hash


class Map(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    s2ma_hash = models.CharField(max_length=255, null=True, db_index=True)
    gateway = models.CharField(max_length=5, null=True)

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.name)

class Game(models.Model):
    replay = models.ForeignKey('Replay', null=True)
    game_time = models.DateTimeField(null=True, db_index=True)
    upload_time = models.DateTimeField(null=True, db_index=True)
    release_string = models.CharField(max_length=255, db_index=True, null=True)
    winning_team = models.IntegerField(null=True, blank=True)
    map = models.ForeignKey('Map', null=True)
    game_type = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    duration_seconds = models.IntegerField(null=True)
    average_league = models.IntegerField(null=True, blank=True, db_index=True)
    processed_time = models.DateTimeField(null=True, db_index=True)
    subdomain = models.CharField(max_length=50, db_index=True, default='')

    def __unicode__(self):
        return '(%d)' % (self.id)

class Player(models.Model):
    name = models.CharField(null=True, blank=True, max_length=255, db_index=True, default='')
    gateway = models.CharField(max_length=5, db_index=True)
    region = models.CharField(null=True, blank=True, max_length=5, db_index=True, default='')
    subregion = models.IntegerField(db_index=True)
    bnet_id = models.IntegerField(db_index=True)
    character_code = models.IntegerField(null=True, blank=True)
    sc2ranks_info = models.CharField(max_length=50000, null=True)
    sc2ranks_retrieved = models.DateTimeField(null=True)
    avg_wpmx10 = models.IntegerField(null=True)
    best_league = models.IntegerField(null=True, db_index=True)
    num_games = models.IntegerField(null=True, db_index=True)
    best_rank = models.IntegerField(null=True)
    best_race = models.CharField(max_length=1, null=True, db_index=True)
    best_num_players = models.IntegerField(null=True)
    best_is_random = models.NullBooleanField()
    s2gs_last_retrieved_at = models.DateTimeField(null=True)

    def __unicode__(self):
        return '(%d) %s / %s' % (self.id, '' if self.name is None else self.name, self.gateway)

class Sc2RanksCache(models.Model):
    player = models.ForeignKey('Player')
    bnet_url = models.CharField(max_length=255, null=True, db_index=True)
    sc2ranks_info = models.CharField(max_length=50000, null=True)
    sc2ranks_retrieved = models.DateTimeField(null=True)

    def __unicode__(self):
        return '(%d) %s %s' % (self.id, self.player.name, self.sc2ranks_retrieved)

class PlayerLeague(models.Model):
    player = models.ForeignKey('Player')
    num_players = models.IntegerField(db_index=True)
    is_random = models.BooleanField(db_index=True)
    league = models.IntegerField(db_index=True)
    rank = models.IntegerField()
    is_best = models.BooleanField(db_index=True)
    fav_race = models.CharField(max_length=1, db_index=True)

    def __unicode__(self):
        return '(%d) %s %iv%i league %i' % (self.id, self.player.name, self.num_players, self.num_players, self.league)
    

class PlayerInGame(models.Model):
    game = models.ForeignKey('Game')
    player = models.ForeignKey('Player')
    team = models.IntegerField()
    chosen_race = models.CharField(max_length=1, db_index=True)
    race = models.CharField(max_length=1, db_index=True)
    win = models.NullBooleanField()
    apm = models.FloatField(null=True)
    wpm = models.FloatField(null=True)
    apm_by_minute = models.CharField(max_length=1000, null=True)
    wpm_by_minute = models.CharField(max_length=1000, null=True)
    color = models.CharField(max_length=6, null=True, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    armies_by_frame = models.CharField(max_length=1000000, blank=True, null=True)

    def __unicode__(self):
        return '(%d) %s / %s' % (self.id, self.game.map.name, self.player.name)

class PlayerInGameMinute(models.Model):
    player_in_game = models.ForeignKey('PlayerInGame')
    minute = models.IntegerField(db_index=True)
    wpm = models.IntegerField()
    apm = models.IntegerField()


class BuildNode(models.Model):
    parent = models.ForeignKey('BuildNode', null=True, blank=True)
    action = models.CharField(max_length=50, db_index=True)
    depth = models.IntegerField(null=True, blank=True, db_index=True)

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.action)


class PlayerInGameBuild(models.Model):
    player_in_game = models.ForeignKey('PlayerInGame')
    buildnode = models.ForeignKey('BuildNode')
    when_seconds = models.IntegerField()

    def __unicode__(self):
        return '(%d)' % (self.id)


class IdentifiedBuild(models.Model):
    buildnode = models.ForeignKey('BuildNode', null=True, blank=True)
    race = models.CharField(max_length=1, db_index=True)
    name = models.CharField(max_length=300)
    url = models.CharField(max_length=500)

    def __unicode__(self):
        return '(%s)' % (self.name)


class Stat(models.Model):
    pass

class PlayerInGameStat(models.Model):
    pass

class PlayerInGameString(models.Model):
    pass

class Sc2Ranks(models.Model):
    pass

class GameSummary(models.Model):
  # sha1 is 40 bytes, doubling up just in case.
  s2gs_hash = models.CharField(max_length=80, db_index=True)

  realm = models.CharField(max_length=2, db_index=True)
  game = models.ForeignKey('Game', null=True, blank=True)

  first_seen_at = models.DateTimeField(null=True, db_index=True)
  first_retrieved_at = models.DateTimeField(null=True, db_index=True)
  status = models.IntegerField(null=False, blank=False, db_index=True, default=0)
  league = models.IntegerField(db_index=True, null=True, blank=True)
  

class Graph(models.Model):
    pass

class GraphPoint(models.Model):
    graph = models.ForeignKey('Graph')
    graph_seconds = models.IntegerField(null=False, blank=False)
    graph_value = models.IntegerField(null=False, blank=False)

class PlayerSummary(models.Model):
    game = models.ForeignKey('Game')
    player = models.ForeignKey('Player')
    build_order = models.ForeignKey('BuildOrder')
    army_graph = models.ForeignKey('Graph', related_name='+')
    income_graph = models.ForeignKey('Graph', related_name='+')
    resources = models.IntegerField(null=False, blank=False)
    units = models.IntegerField(null=False, blank=False)
    structures = models.IntegerField(null=False, blank=False)
    overview = models.IntegerField(null=False, blank=False)
    average_unspent_resources = models.IntegerField(null=False, blank=False)
    resource_collection_rate = models.IntegerField(null=False, blank=False)
    workers_created = models.IntegerField(null=False, blank=False)
    units_trained = models.IntegerField(null=False, blank=False)
    killed_unit_count = models.IntegerField(null=False, blank=False)
    structures_built = models.IntegerField(null=False, blank=False)
    structures_razed_count = models.IntegerField(null=False, blank=False)

class Item(models.Model):
    name = models.CharField(max_length=64, db_index=True)

class BuildOrder(models.Model):
    pass

class BuildOrderItem(models.Model):
    build_order = models.ForeignKey('BuildOrder')
    built_item = models.ForeignKey('Item')
    build_seconds = models.IntegerField(null=False, blank=False)
    supply = models.IntegerField(null=False, blank=False)
    total_supply = models.IntegerField(null=False, blank=False)
