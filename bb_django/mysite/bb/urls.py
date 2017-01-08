from django.conf.urls import  url

from bb import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
        # ex: /polls/5/
    #url(r'^(?P<throw_id>\d+)/$', views.detail, name='detail'),
    url(r'^input/$', views.input, name='input'),
    #url(r'^dailyeval/$', views.daily_evaluation, name='daily_evaluation'),
    url(r'^stats/(?P<year>\d+)/(?P<month>\d+)$', views.month_stat, name="month_stat"),
    url(r'^stats/(?P<year>\d+)/$', views.year_stat, name="year_stat"),
    url(r'^round/(?P<round_nr>\d+)/$', views.next_round, name="next_round"),
    url(r'^round/(?P<round_nr>\d+)/input/$', views.next_round_input, name="next_round_input"),
    ]