import pandas as pd
import numpy as np
import datetime
from django.shortcuts import get_object_or_404
from bb.models import Throw, Player, DailyLoser, Gladiator

#bbdataset=pd.read_csv("C:\\Users\\yemmit\\Documents\\bb\\datenbasis\\BB-Mappe.csv", sep=';')
#bbdataset=pd.read_csv("H:\\BB-Mappe.csv", sep=';')
bbdataset=pd.read_csv("N:\\temp\\tim\\privat\\datenbasis\\BB-Mappe_ergz.csv", sep=';', dtype=str)
bbdataset_with0=bbdataset.replace(to_replace=np.nan, value='')

for x,date_str in enumerate(bbdataset.iloc[:,0]):
    player_i=0
    for player in bbdataset.columns[1:]:
        player_i+=1
        throw_list=bbdataset.ix[x,player]
        if type(throw_list) == type('str'):
            throw_list=throw_list.replace(',','')
            throw_i=0
            for throwround in range(len(throw_list)):
                throw_i+=1
                event_time=datetime.datetime(int(date_str[-4:]), int(date_str[3:5]), int(date_str[:2]),0,throw_i, player_i)
                input_player = get_object_or_404(Player, player_name=player)
                new_throw = Throw(result=int(throw_list[throwround]), event_time=event_time, player=input_player, round=throw_i)
                new_throw.save()
    throwround_lens = [len(z.replace(',','')) for z in bbdataset_with0.ix[x, 1:]]
    if max(throwround_lens) > 0:
        last_round_ix=[q+1 for q,z in enumerate(throwround_lens) if z==max(throwround_lens)]
        last_round_points=[int(z[-1]) for z in bbdataset_with0.iloc[x,last_round_ix]]
        loser = bbdataset.columns[[last_round_ix[q] for q, z in enumerate(last_round_points) if z == min(last_round_points)][0]]
        loser_da = DailyLoser(day=datetime.date(int(date_str[-4:]), int(date_str[3:5]), int(date_str[:2])),
                              loser=get_object_or_404(Player, player_name=loser), round=max(throwround_lens))
        loser_da.save()
        gladiator1_ix = [last_round_ix[q] for q, z in enumerate(last_round_points) if z > min(last_round_points) and z == 1]
        if len(gladiator1_ix) > 0:
            gladiator1 = bbdataset.columns[gladiator1_ix]
            for gladiator in gladiator1:
                gladiator_da = Gladiator(day=datetime.date(int(date_str[-4:]), int(date_str[3:5]), int(date_str[:2])),
                                     gladiator=get_object_or_404(Player, player_name=gladiator),
                                     points=1, round=max(throwround_lens))
                gladiator_da.save()
        gladiator15_ix=[last_round_ix[q] for q, z in enumerate(last_round_points) if z > min(last_round_points) and z == 2]
        if len(gladiator15_ix) > 0:
            gladiator15 = bbdataset.columns[gladiator15_ix]
            for gladiator in gladiator15:
                gladiator_da = Gladiator(day=datetime.date(int(date_str[-4:]), int(date_str[3:5]), int(date_str[:2])),
                                         gladiator=get_object_or_404(Player, player_name=gladiator),
                                         points=1.5, round=max(throwround_lens))
                gladiator_da.save()
        gladiator2_ix=[last_round_ix[q] for q, z in enumerate(last_round_points) if z > min(last_round_points) and z == 3]
        if len(gladiator2_ix) > 0:
            gladiator2 = bbdataset.columns[gladiator2_ix]
            for gladiator in gladiator2:
                gladiator_da = Gladiator(day=datetime.date(int(date_str[-4:]), int(date_str[3:5]), int(date_str[:2])),
                                         gladiator=get_object_or_404(Player, player_name=gladiator),
                                         points=2, round=max(throwround_lens))
                gladiator_da.save()