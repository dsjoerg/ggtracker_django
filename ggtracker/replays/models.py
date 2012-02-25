from django.db import models

class Replay(models.Model):
    md5hash = models.CharField(max_length=32, db_index=True)

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.md5hash)

class Map(models.Model):
    name = models.CharField(max_length=255)
    s2ma_hash = models.CharField(max_length=255, null=True)
    gateway = models.CharField(max_length=5, null=True)

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.name)

class Game(models.Model):
    replay = models.ForeignKey('Replay')
    game_time = models.DateTimeField(null=True)
    release_string = models.CharField(max_length=255)
    winning_team = models.IntegerField(null=True)
    map = models.ForeignKey('Map')
    game_type = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    duration_seconds = models.IntegerField(null=True)

    def __unicode__(self):
        return '(%d) %s' % (self.id, self.map.name)

class Player(models.Model):
    name = models.CharField(max_length=255)
    gateway = models.CharField(max_length=5)
    region = models.CharField(max_length=5)
    subregion = models.IntegerField()
    bnet_id = models.IntegerField()
    character_code = models.IntegerField(null=True)
    sc2ranks_info = models.CharField(max_length=50000, null=True)
    sc2ranks_retrieved = models.DateTimeField(null=True)

    def __unicode__(self):
        return '(%d) %s / %s' % (self.id, self.name, self.gateway)

class Sc2RanksCache(models.Model):
    player = models.ForeignKey('Player')
    bnet_url = models.CharField(max_length=255, null=True)
    sc2ranks_info = models.CharField(max_length=50000, null=True)
    sc2ranks_retrieved = models.DateTimeField(null=True)

    def __unicode__(self):
        return '(%d) %s %s' % (self.id, self.player.name, self.sc2ranks_retrieved)

class PlayerLeague(models.Model):
    player = models.ForeignKey('Player')
    num_players = models.IntegerField()
    is_random = models.BooleanField()
    league = models.IntegerField()
    rank = models.IntegerField()
    is_best = models.BooleanField()
    fav_race = models.CharField(max_length=1)

    def __unicode__(self):
        return '(%d) %s %iv%i league %i' % (self.id, self.player.name, self.num_players, self.num_players, self.league)
    

class PlayerInGame(models.Model):
    game = models.ForeignKey('Game')
    player = models.ForeignKey('Player')
    team = models.IntegerField()
    chosen_race = models.CharField(max_length=1)
    race = models.CharField(max_length=1)
    win = models.NullBooleanField()
    apm = models.FloatField(null=True)
    wpm = models.FloatField(null=True)
    apm_by_minute = models.CharField(max_length=1000, null=True)
    wpm_by_minute = models.CharField(max_length=1000, null=True)

    def __unicode__(self):
        return '(%d) %s / %s' % (self.id, self.game.filename, self.player.name)

class Stat(models.Model):
    pass

class PlayerInGameStat(models.Model):
    pass

class PlayerInGameString(models.Model):
    pass

class Sc2Ranks(models.Model):
    pass
