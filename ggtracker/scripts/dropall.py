#!/usr/bin/env python

import sys
import os
sys.path.append("ggtracker")

django_settings_module = 'settings'
os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module

from replays.models import *

for game in Game.objects.all():
    game.delete()

for player in Player.objects.all():
    player.delete()

# WARNING: Amazon S3 bucket ids are invalidated by this!
for replay in Replay.objects.all():
    replay.delete()
