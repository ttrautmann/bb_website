import pandas as pd
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Player(models.Model):
    '''Model for storing all players'''
    player_name = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    image_url = models.CharField(max_length=200)

    def __str__(self):
        return self.player_name


@python_2_unicode_compatible
class Throw(models.Model):
    '''Model for storing all throws'''
    RESULT_CHOICES = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
    )
    player = models.ForeignKey(Player)
    result = models.IntegerField(choices=RESULT_CHOICES, blank=False, null=False)
    event_time = models.DateTimeField(default=timezone.now)
    round = models.PositiveSmallIntegerField(default=1)

    class Meta:
        get_latest_by = 'event_time'

    def __str__(self):
        return u'{:%y-%m-%d-%H-%M}_{:2}_{:15}_{}'.format(self.event_time,
                                                         self.round,
                                                         self.player,
                                                         self.result)

    def get_pd(self):
        return pd.DataFrame([self.player.player_name, self.event_time, self.result, self.round])


@python_2_unicode_compatible
class DailyLoser(models.Model):
    '''Model for storing daily losers'''
    day = models.DateTimeField()
    loser = models.ForeignKey(Player)
    round = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return u'{:%y-%m-%d}_{:15}'.format(self.day, self.loser)

    def get_pd(self):
        return pd.DataFrame([self.loser.player_name, self.day, self.round])


@python_2_unicode_compatible
class Gladiator(models.Model):
    '''Model for storing gladiators'''
    day = models.DateTimeField()
    gladiator = models.ForeignKey(Player)
    points = models.FloatField()
    round = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return u'{:%y-%m-%d}_{:15}_{}'.format(self.day, self.loser, self.points)

    def get_pd(self):
        return pd.DataFrame([self.gladiator.player_name, self.day, self.points, self.round])