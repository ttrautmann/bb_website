from django.db import models
from django.utils import timezone
import pandas as pd

# Create your models here.
class Player(models.Model):
    player_name = models.CharField(max_length=15)
    image_url = models.CharField(max_length=200)
    def __unicode__(self):
        return self.player_name

class Throw(models.Model):
    player = models.ForeignKey(Player)
    result = models.IntegerField()
    event_time = models.DateTimeField(default=timezone.now)
    round = models.IntegerField(default=0)
    def __unicode__(self):
        return (self.player.player_name+ '  '+str(self.event_time.strftime("%d/%m/%y %H:%M"))+ ' Punkte: '+str(self.result)+ ' Runde: '+str(self.round))
    def get_pd(self):
        return pd.DataFrame([self.player.player_name, self.event_time, self.result, self.round])

class DailyLoser(models.Model):
    day = models.DateTimeField()
    loser = models.ForeignKey(Player)
    round = models.IntegerField(default=0)
    def __unicode__(self):
        return (str(self.day)+' Loser:'+ str(self.loser))
    def get_pd(self):
        return pd.DataFrame([self.loser.player_name, self.day, self.round])

class Gladiator(models.Model):
    day = models.DateTimeField()
    gladiator = models.ForeignKey(Player)
    points = models.FloatField()
    round = models.IntegerField(default=0)
    def __unicode__(self):
        return (str(self.day) + ' ' + str(self.gladiator) + ' ' + str(self.points))
    def get_pd(self):
        return pd.DataFrame([self.gladiator.player_name, self.day, self.points, self.round])