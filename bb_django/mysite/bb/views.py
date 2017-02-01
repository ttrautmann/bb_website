#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.utils import timezone
import pandas as pd
import numpy as np
from .models import Throw, Player, DailyLoser, Gladiator


class Statistics:
    def __init__(self, throw_objects, loser_objects, gladiator_objects):
        self.throw_objects = throw_objects
        self.loser_objects = loser_objects
        self.gladiator_objects = gladiator_objects
        self.statisticsdict = {}
        self.get_statistics()

    def get_statistics(self):
        throw_df = pd.concat([x.get_pd() for x in self.throw_objects], axis=1)
        throw_df.index = ['name', 'date', 'result', 'round']
        loser_df = pd.concat([x.get_pd() for x in self.loser_objects], axis=1)
        loser_df.index = ['name', 'date', 'round']
        gladiator_df = pd.concat([x.get_pd() for x in self.gladiator_objects], axis=1)
        gladiator_df.index = ['name', 'date', 'result', 'round']
        throw_df_plays = throw_df.copy().T
        plays_total = len(throw_df_plays.groupby(by='date').count())
        self.statisticsdict['TotalPlays'] = plays_total
        # Plays
        throw_df_plays.date = [x.date() for x in throw_df_plays.date]
        plays_df = throw_df_plays.groupby(by=['name', 'date']
                                          ).sum().groupby(level='name').count().sort_values(by='result', ascending=0)
        plays_df.columns = ['rel_plays', 'plays']
        plays = plays_df.loc[:, 'plays']
        plays_ranks = plays.rank(method='min', ascending=False).astype(int)
        self.statisticsdict['plays'] = [x for x in zip(plays_ranks, plays.index, plays)]
        # relative plays
        plays_df.loc[:, 'rel_plays'] = plays_df.loc[:, 'plays']/plays_total
        rel_plays = plays_df.loc[:, 'rel_plays']
        rel_plays_ranks = rel_plays.rank(method='min', ascending=False).astype(int)
        self.statisticsdict['relativePlays'] = [x for x in zip(rel_plays_ranks, rel_plays.index, rel_plays)]
        # losses
        losses_df = loser_df.T.groupby(by='name').count().sort_values(by='round', ascending=0)
        losses = losses_df.iloc[:, 1]
        losses_rank = losses.rank(method='min', ascending=False).astype(int)
        self.statisticsdict['losses'] = [x for x in zip( losses_rank, losses.index, losses)]
        # relative losses
        rel_losses_df = pd.concat([plays_df.plays, losses_df.iloc[:, 1]], axis=1).replace(to_replace=np.nan, value=0)
        rel_losses_unsorted = rel_losses_df.loc[:, 'round']/rel_losses_df.loc[:, 'plays']
        rel_losses_sorted = rel_losses_unsorted.sort_values(axis=0, ascending=False)
        rel_losses = rel_losses_sorted.round(2)
        rel_los_ranks = rel_losses.rank(method='min', ascending=False).astype(int)
        self.statisticsdict['relativeLosses'] = [x for x in zip(rel_los_ranks, rel_losses.index, rel_losses)]
        # longest pointstreak and losingstreak
        pointstreak_df = throw_df_plays.sort_values(by=['name', 'date'])
        pointstreak_dict = {}
        zerostreak_dict = {}
        for player in throw_df_plays.loc[:, 'name'].unique():
            player_row = pointstreak_df.loc[:, 'name'] == player
            point_str = ''.join(str(x) for x in pointstreak_df.loc[:, 'result'][player_row])
            longest_pointstreak = max([len(x) for x in point_str.replace('0', ',').split(',')])
            longest_zerostreak = max([len(x) for x in point_str.replace('1', ','
                                                                        ).replace('2', ','
                                                                                  ).replace('3', ',').split(',')])
            pointstreak_dict[player] = longest_pointstreak
            zerostreak_dict[player] = longest_zerostreak
        pointstreak_sorted = pd.Series(pointstreak_dict).sort_values(axis=0, ascending=False)
        pointstreak_ranks = pointstreak_sorted.rank(method='min', ascending=False).astype(int)
        zerostreak_sorted = pd.Series(zerostreak_dict).sort_values(axis=0, ascending=False)
        zerostreak_ranks = zerostreak_sorted.rank(method='min', ascending=False).astype(int)
        self.statisticsdict['pointstreak'] = [x for x in zip(pointstreak_ranks,
                                                             pointstreak_sorted.index, pointstreak_sorted)]
        self.statisticsdict['zerostreak'] = [x for x in zip(zerostreak_ranks,
                                                            zerostreak_sorted.index, zerostreak_sorted)]
        # gladiator
        gladiator_points_df = gladiator_df.T.groupby(by='name').sum().sort_values(by='result', ascending=0)
        gladiator_points = gladiator_points_df.loc[:, 'result']
        glad_ranks = gladiator_points.rank(method='min', ascending=False).astype(int)
        self.statisticsdict['gladiatorPoints'] = [x for x in zip(glad_ranks,
                                                                 gladiator_points.index, gladiator_points)]
        # fluktuationsmonster
        throw_df_plays.result = throw_df_plays.loc[:, 'result'].apply(int)
        stderivation = throw_df_plays.loc[:, ['name', 'result']].groupby(by='name').std().replace(np.nan,0)
        stderivation_sorted = stderivation.sort_values(by='result', ascending=0)
        std_ranks = [int(x) for x in stderivation_sorted.rank(method='min', ascending=False).values]
        self.statisticsdict['stdev'] = [x for x in zip(std_ranks,
                                                       stderivation_sorted.index,
                                                       [round(x, 2) for x in stderivation_sorted.values])]
        # durchschnittspunktzahl
        mean = throw_df_plays.loc[:, ['name', 'result']].groupby(by='name').mean()
        mean_sorted = mean.sort_values(by='result', ascending=0)
        mean_ranks = [int(x) for x in mean_sorted.rank(method='min', ascending=False).values]
        self.statisticsdict['mean'] = [x for x in zip(mean_ranks,
                                                      mean_sorted.index, [round(x, 2) for x in mean_sorted.values])]
        # angeber
        three_point_df = throw_df_plays.loc[:, ['name', 'result']].copy()
        three_point_ix = [i for i, x in enumerate(throw_df_plays.loc[:, 'result']) if x == 3]
        three_point_df_n = three_point_df.iloc[three_point_ix, :].groupby(by='name').count()
        three_point_df_sorted = three_point_df_n.sort_values(by='result', ascending=0)
        if len(three_point_df_n) > 0:
            three_point_ranks = [int(x) for x in three_point_df_sorted.rank(method='min',ascending=False).values]
            self.statisticsdict['threePoints'] = [x for x in zip(three_point_ranks,
                                                                 three_point_df_sorted.index,
                                                                 [int(x) for x in three_point_df_sorted.values])]
        # Nachsitzer
        second_round = throw_df_plays.loc[:, ['name', 'round']].copy()
        second_round_ix = [i for i, x in enumerate(throw_df_plays.loc[:, 'round']) if x == 2]
        second_round_df = second_round.iloc[second_round_ix, :].groupby(by='name').count()
        second_round_sorted = second_round_df.sort_values(by='round', ascending=0)
        ranks = [int(x) for x in second_round_sorted.rank(method='min', ascending=False).values]
        self.statisticsdict['secondRound'] = [x for x in zip(ranks,
                                                             second_round_sorted.index,
                                                             [int(x) for x in second_round_sorted.values])]

        # Norm guy by Mathias Seibert
        norm_guy = []
        norm_names = pd.DataFrame(index=pd.DataFrame(self.statisticsdict['mean']).iloc[:, 1])
        stat_keys = self.statisticsdict.keys()
        stat_keys.remove('TotalPlays')
        for key in stat_keys:
            temp = pd.DataFrame(self.statisticsdict[key])
            temp.columns = ['rank', 'name', 'result']
            temp.set_index('name', inplace=True)
            temp = norm_names.join(temp)
            temp.replace(np.nan, 0, inplace=True)
            score = np.sqrt((temp.result - np.median(temp.result))**2)
            score_norm = score / score.max()
            norm_guy.append(score_norm)
        norm_guy_result_df = pd.concat(norm_guy, axis=1).mean(axis=1).sort_values()
        norm_guy_result_df = 1 - norm_guy_result_df
        norm_guy_ranks = [int(x) for x in norm_guy_result_df.rank(method='min', ascending=False).values]
        self.statisticsdict['norm_guy'] = [x for x in zip(norm_guy_ranks,
                                                          norm_guy_result_df.index,
                                                          [round(x, 2) for x in norm_guy_result_df.values])]
        # Get Cake Guy
        relevant_categories = self.statisticsdict.keys()
        relevant_categories.remove('TotalPlays')
        relevant_categories.remove('relativePlays')
        winner_categorie = relevant_categories[np.random.random_integers(0, len(relevant_categories)-1)]
        categorie_dict = {
            'plays': u'Basketballjunkie',
            'losses': u'Kaffegott',
            'relativeLosses': u'Angestellter des Wasserkochers',
            'pointstreak': u'Goldenes Händchen',
            'zerostreak': u'Tennisarm',
            'stdev': u'Fluktuationsmonster',
            'mean': u'Solider Typ',
            'gladiatorPoints': u'Gladiator',
            'threePoints': u'Angeber',
            'secondRound': u'Nachsitzer',
            'norm_guy': u'Regular every day normal guy'
        }
        temp_df = pd.DataFrame(self.statisticsdict[winner_categorie])
        temp_df.columns = ['rank', 'name', 'result']
        rank1 = sum([x for x in temp_df['rank'] if x == 1])
        if rank1 > 1:
            cake_baker = temp_df.name[np.random.randint(0, rank1 - 1)]
        else:
            cake_baker = temp_df.name[0]
        self.statisticsdict['mrcake'] = (categorie_dict[winner_categorie], cake_baker)


def index(request):
    latest_throws_list = Throw.objects.filter(event_time__gte=timezone.now().date())
    if len(latest_throws_list) > 0:
        throws_df = pd.concat([x.get_pd() for x in latest_throws_list], axis=1)
        throws_df.index = ['name', 'date', 'result', 'round']
        already_played = [Player.objects.get(player_name=x).id for x in throws_df.loc['name', :]]
    else:
        already_played = []
    context_dict = {
        'latest_throws_list': latest_throws_list,
        'players': [x for x in Player.objects.all() if x.id not in already_played],
        'scores': range(4),
        'day': timezone.now().date(),
        'round_nr': 2
    }
    if len(latest_throws_list) > 1:
        context_dict['show_eval_button'] = 1

    template = loader.get_template('bb/index.html')
    context = RequestContext(request, context_dict)
    return HttpResponse(template.render(context))


def detail(request, throw_id):
    throw = get_object_or_404(Throw, pk=throw_id)
    return render(request, 'bb/detail.html', {'throw': throw})


def input(request):
    input_player = get_object_or_404(Player, pk=request.POST['player'])
    new_throw = Throw(result=request.POST['score'], event_time=timezone.now(), player=input_player, round=1)
    new_throw.save()
    return HttpResponseRedirect('/bb/')


def next_round(request, round_nr):
    # Test if first round was the only one
    eval_day = timezone.now().date()
    throws_list_filter = Throw.objects.filter(event_time__gte=eval_day, round=str(int(round_nr)-1))
    if len(Throw.objects.filter(event_time__gte=eval_day, round=round_nr)) > 0:
        return HttpResponseRedirect('/bb/')
    if len(throws_list_filter) == 0:
        return HttpResponseRedirect('/bb/')
    else:
        throws_df = pd.concat([x.get_pd() for x in throws_list_filter], axis=1)
        throws_df.index = ['name', 'date', 'result', 'round']
        nr_of_player_next_round = sum(throws_df.loc['result', :].values == min(throws_df.loc['result', :].values))
        final_round_trigger = nr_of_player_next_round == 1
        if final_round_trigger:
            last_round = throws_df.T
            loser = [x[0] for x in last_round.values if x[2] == last_round.result.min()]
            gladiator_1 = [x[0] for x in last_round.values if x[2] != last_round.result.min() and x[2] == 1]
            gladiator_15 = [x[0] for x in last_round.values if x[2] != last_round.result.min() and x[2] == 2]
            gladiator_2 = [x[0] for x in last_round.values if x[2] != last_round.result.min() and x[2] == 3]
            loser_da = DailyLoser(day=eval_day,
                                  loser=get_object_or_404(Player, player_name=loser[0]),
                                  round=int(round_nr)-1)
            loser_da.save()

            if len(gladiator_1) > 0:
                for x in gladiator_1:
                    gladiator_da = Gladiator(day=eval_day,
                                             gladiator=get_object_or_404(Player, player_name=x),
                                             points=1, round=int(round_nr)-1)
                    gladiator_da.save()

            if len(gladiator_15) > 0:
                for x in gladiator_15:
                    gladiator_da = Gladiator(day=eval_day,
                                             gladiator=get_object_or_404(Player, player_name=x),
                                             points=1.5, round=int(round_nr)-1)
                    gladiator_da.save()

            if len(gladiator_2) > 0:
                for x in gladiator_2:
                    gladiator_da = Gladiator(day=eval_day,
                                             gladiator=get_object_or_404(Player, player_name=x),
                                             points=2, round=int(round_nr)-1)
                    gladiator_da.save()
            return HttpResponseRedirect('/bb/')
        else:
            new_round_nr = int(round_nr)+1
            next_round_player = throws_df.iloc[0,
                                               throws_df.loc['result', :].values == min(throws_df.loc['result',
                                                                                        :].values)]
            next_players = [Player.objects.get(player_name=x) for x in next_round_player]
            template = loader.get_template('bb/round_input.html')
            context = RequestContext(request, {
                'players': next_players,
                'scores': range(4),
                'day': timezone.now().date(),
                'round_nr': new_round_nr,
                'round_nr_display': new_round_nr-1
            })
            return HttpResponse(template.render(context))


def next_round_input(request, round_nr):
    eval_day = timezone.now().date()
    throws_list_filter = Throw.objects.filter(event_time__gte=eval_day, round=str(int(round_nr)-2))
    throws_df = pd.concat([x.get_pd() for x in throws_list_filter], axis=1)
    throws_df.index = ['name', 'date', 'result', 'round']
    next_round_player = throws_df.iloc[0, throws_df.loc['result', :].values == min(throws_df.loc['result', :].values)]
    next_players = [Player.objects.get(player_name=x).id for x in next_round_player]
    for playerid in next_players:
        input_player = get_object_or_404(Player, pk=playerid)
        new_throw = Throw(result=request.POST[str(playerid)],
                          event_time=timezone.now(),
                          player=input_player,
                          round=int(round_nr)-1)
        new_throw.save()
    return HttpResponseRedirect('/bb/round/'+str(round_nr)+'/')


def month_stat(request, year, month):
    monthly_throws = Throw.objects.filter(event_time__year=year, event_time__month=month)
    monthly_loser = DailyLoser.objects.filter(day__year=year, day__month=month)
    monthly_gladiator = Gladiator.objects.filter(day__year=year, day__month=month)
    if len(monthly_loser) == 0:
        return HttpResponseRedirect('/bb/')
    else:
        context_dict = Statistics(monthly_throws, monthly_loser, monthly_gladiator).statisticsdict
        context_dict['year'] = year
        context_dict['month'] = month
        template = loader.get_template('bb/monthly_stats.html')
        context = RequestContext(request, context_dict)
        return HttpResponse(template.render(context))


def year_stat(request, year):
    yearly_throws = Throw.objects.filter(event_time__year=year)
    yearly_loser = DailyLoser.objects.filter(day__year=year)
    yearly_gladiator = Gladiator.objects.filter(day__year=year)
    if len(yearly_loser) == 0:
        return HttpResponseRedirect('/bb/')
    else:
        context_dict = Statistics(yearly_throws, yearly_loser, yearly_gladiator).statisticsdict
        context_dict['year'] = year
        template = loader.get_template('bb/monthly_stats.html')
        context = RequestContext(request, context_dict)
        return HttpResponse(template.render(context))


def player_stat(request, player):
    player_throws = Throw.objects.filter(player__player_name=player)
    player_loser = DailyLoser.objects.filter(loser__player_name=player)
    player_gladiator = Gladiator.objects.filter(gladiator__player_name=player)
    if len(player_loser) == 0:
        return HttpResponseRedirect('/bb/')
    else:
        context_dict = Statistics(player_throws, player_loser, player_gladiator).statisticsdict
        context_dict['player_name'] = player
        template = loader.get_template('bb/player_stats.html')
        context = RequestContext(request, context_dict)
        return HttpResponse(template.render(context))
