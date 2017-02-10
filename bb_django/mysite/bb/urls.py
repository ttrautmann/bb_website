from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.game_list, name='game_list'),
    url(r'^round/(?P<round_nr>\d+)/$', views.next_round, name="next_round"),
    #url(r'^dailyeval/$', views.daily_evaluation, name='daily_evaluation'),
    url(r'^stats/(?P<year>\d+)/(?P<month>\d+)$', views.month_stat, name="month_stat"),
    url(r'^stats/(?P<year>\d+)/$', views.month_stat, name="month_stat"),
    ]