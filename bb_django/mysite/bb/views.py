#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import numpy as np
import pandas as pd
from django.db import models
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.utils import timezone

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
        plays_df.loc[:, 'rel_plays'] = plays_df.loc[:, 'plays'] / plays_total
        rel_plays = plays_df.loc[:, 'rel_plays']
        rel_plays_ranks = rel_plays.rank(method='min', ascending=False).astype(int)
        self.statisticsdict['relativePlays'] = [x for x in zip(rel_plays_ranks, rel_plays.index, rel_plays)]
        # losses
        losses_df = loser_df.T.groupby(by='name').count().sort_values(by='round', ascending=0)
        losses = losses_df.iloc[:, 1]
        losses_rank = losses.rank(method='min', ascending=False).astype(int)
        self.statisticsdict['losses'] = [x for x in zip(losses_rank, losses.index, losses)]
        # relative losses
        rel_losses_df = pd.concat([plays_df.plays, losses_df.iloc[:, 1]], axis=1).replace(to_replace=np.nan, value=0)
        rel_losses_unsorted = rel_losses_df.loc[:, 'round'] / rel_losses_df.loc[:, 'plays']
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
        stderivation = throw_df_plays.loc[:, ['name', 'result']].groupby(by='name').std()
        stderivation_sorted = stderivation.sort_values(by='result', ascending=0)
        std_ranks = [int(x) for x in stderivation_sorted.rank(method='min', ascending=False).values]
        self.statisticsdict['stdev'] = [x for x in zip(std_ranks,
                                                       stderivation_sorted.index,
                                                       [round(x[0], 2) for x in stderivation_sorted.values])]
        # durchschnittspunktzahl
        mean = throw_df_plays.loc[:, ['name', 'result']].groupby(by='name').mean()
        mean_sorted = mean.sort_values(by='result', ascending=0)
        mean_ranks = [int(x) for x in mean_sorted.rank(method='min', ascending=False).values]
        self.statisticsdict['mean'] = [x for x in zip(mean_ranks,
                                                      mean_sorted.index, [round(x[0], 2) for x in mean_sorted.values])]
        # angeber
        three_point_df = throw_df_plays.loc[:, ['name', 'result']].copy()
        three_point_ix = [i for i, x in enumerate(throw_df_plays.loc[:, 'result']) if x == 3]
        three_point_df_n = three_point_df.iloc[three_point_ix, :].groupby(by='name').count()
        three_point_df_sorted = three_point_df_n.sort_values(by='result', ascending=0)
        if len(three_point_df_n) > 0:
            three_point_ranks = [int(x) for x in three_point_df_sorted.rank(method='min', ascending=False).values]
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
        stat_keys = list(self.statisticsdict.keys())
        stat_keys.remove('TotalPlays')
        for key in stat_keys:
            temp = pd.DataFrame(self.statisticsdict[key])
            temp.columns = ['rank', 'name', 'result']
            temp.set_index('name', inplace=True)
            temp = norm_names.join(temp)
            temp.replace(np.nan, 0, inplace=True)
            score = np.sqrt((temp.result - np.median(temp.result)) ** 2)
            score_norm = score / score.max()
            norm_guy.append(score_norm)
        norm_guy_result_df = pd.concat(norm_guy, axis=1).mean(axis=1).sort_values()
        norm_guy_result_df = 1 - norm_guy_result_df
        norm_guy_ranks = [int(x) for x in norm_guy_result_df.rank(method='min', ascending=False).values]
        self.statisticsdict['norm_guy'] = [x for x in zip(norm_guy_ranks,
                                                          norm_guy_result_df.index,
                                                          [round(x, 2) for x in norm_guy_result_df.values])]
        # Get Cake Guy
        relevant_categories = list(self.statisticsdict.keys())
        relevant_categories.remove('TotalPlays')
        relevant_categories.remove('relativePlays')
        winner_categorie = relevant_categories[np.random.random_integers(0, len(relevant_categories) - 1)]
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


def game_list(request):
    '''creates the view for the list of throws'''
    # get throws from last 30 days and group by date and make group count of throws
    latest_games = (Throw.objects.filter(event_time__gte=timezone.now().date() - datetime.timedelta(days=30)).
                    extra(select={'date': 'date(event_time)'}).
                    values('date').
                    order_by('-date').
                    annotate(n=models.Count("pk")))
    # is today in selection?
    exist_game_today = latest_games.filter(event_time__date=timezone.now().date())
    return render(request, 'bb/game_list.html', {'games': latest_games,
                                                 'exist_game_today': exist_game_today})


def next_round(request, round_nr):
    '''creates the view for all throws in a round'''
    # turn to integer as can be passed from template
    round_nr = int(round_nr)
    # get today's date
    eval_day = timezone.now().date()
    if round_nr == 1:
        # get all currently active players
        active_players = Player.objects.filter(is_active=True)
    else:
        # get players from last round
        last_round = Throw.objects.filter(event_time__date=eval_day, round=round_nr - 1)
        # get last rounds lowest score
        lowest_score = last_round.aggregate(models.Min('result'))['result__min']
        # get all player objects by a list of last rounds' players with lowest score
        active_players = Player.objects.filter(
            id__in=list(last_round.filter(result=lowest_score).values_list('player', flat=True)))

        if len(active_players) == 1:
            # if only player is left, sync other model entries loser and gladiator
            # TODO: remove redundancy
            # get last rounds loser
            loser_da = DailyLoser(day=eval_day,
                                  loser=active_players[0],
                                  round=round_nr - 1)
            loser_da.save()
            # get all last rounds' players with not lowest score
            glad_players = last_round.exclude(result=lowest_score).values('player', 'result')
            for glad_player in glad_players:
                gladiator_da = Gladiator(day=eval_day,
                                         gladiator=Player.objects.get(id=glad_player['player']),
                                         points=1 + (glad_player['result'] - 1) * 0.5,
                                         round=round_nr - 1)
                gladiator_da.save()
            # redirect to index view
            return redirect('game_list')

    # make factory of modelformsets
    # use only field result, scale by length of active players
    RoundFormSet = modelformset_factory(Throw, fields=('result',), extra=len(active_players))
    if request.method == 'POST':
        formset = RoundFormSet(request.POST)
        if formset.is_valid():
            # save commits to instance
            form_entries = formset.save(commit=False)
            for form, player in zip(form_entries, active_players):
                # now add player and round_nr to instance
                form.player = player
                form.round = round_nr
                form.save()
            # redirect to this view reloaded with advanced round number
            return redirect('next_round', round_nr + 1)
    else:
        # populate formset with today's throws for specific round
        formset = RoundFormSet(queryset=Throw.objects.filter(event_time__date=eval_day, round=round_nr))
    return render(request, 'bb/round_input.html',
                  {'formset': formset, 'player_list': active_players, 'round_nr': round_nr})


def month_stat(request, year, month=None):
    event_time_kwargs = {'event_time__year': year}
    day_kwargs = {'day__year': year}
    if month:
        event_time_kwargs['event_time__month'] = month
        day_kwargs['day__month'] = month

    monthly_throws = Throw.objects.filter(**event_time_kwargs)
    monthly_loser = DailyLoser.objects.filter(**day_kwargs)
    monthly_gladiator = Gladiator.objects.filter(**day_kwargs)
    if not monthly_loser:
        # redirect to index view
        return redirect('game_list')
    else:
        context_dict = Statistics(monthly_throws, monthly_loser, monthly_gladiator).statisticsdict
        context_dict['year'] = year
        context_dict['month'] = month
        return render(request, 'bb/monthly_stats.html', context_dict)


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
