import pandas as pd
import numpy as np

#load the data
d = pd.read_csv('pbp-2015.csv')

#sort by game, than sequentially
#reset the index so the index is chronologically sequential
d = d.sort_values(by=['GameId','Quarter','Minute','Second'], ascending = [True, True, False, False]).reset_index(drop=True)

#get date list
date_list = pd.to_datetime(d.GameDate.values)


#import date to week conversion table
w = pd.read_csv('nfl_2015_week_dates.csv')

w.start = pd.to_datetime(w.start)
w.end = pd.to_datetime(w.end)

(date_list[0] >= w.start[0]) and (date_list[0] <= w.end[0])

# build up week list to attach to df
week_list = []
for date in date_list:
    for i in range(17):
        if (date >= w.start[i]) and (date <= w.end[i]):
            week_list.append(i+1)
            break

d['week'] = week_list


#identify home and away teams for each game

sched = pd.read_csv('2015_sched.csv')

#this array will hold every matchup. aligned with each play
home_team = []
away_team = []

#loop through each play, get the defensive team and week number
#than use those two things to look up what game it came from
#put it in the array
for row_index in range(len(d)):
    r_def = d.DefenseTeam.ix[row_index,:]
    r_week = d.week.ix[row_index,:]
    game = sched.ix[((sched.Away==r_def) | (sched.Home==r_def)) & (sched.week==r_week)]
    home_team.append(game.Home.values[0])
    away_team.append(game.Away.values[0])

d['Home'] = home_team
d['Away'] = away_team

#see if the play was a dead ball foul and add a boolean
noplay = d.Description.str.contains("NO PLAY")
d['DeadPlay'] = noplay

reversed_play = d.Description.str.contains("PLAY WAS REVERSED")
d['ReversedPlay'] = reversed_play

extra_point = d.Description.str.contains("EXTRA POINT IS GOOD")
d['PAT'] = extra_point

field_goal = d.Description.str.contains("FIELD GOAL IS GOOD")
d['FG'] = field_goal

safety = d.Description.str.contains("SAFETY")
d['Safety'] = safety

punt = d.Description.str.contains("PUNT")
d['Punt'] = punt

kick_off = d.Description.str.contains("KICKS")
d['Kickoff'] = kick_off



#build up scoring arrays

scoring_td = []
for row_index in range(len(d)):
    if d.ReversedPlay.ix[row_index,:] != True and d.IsNoPlay.ix[row_index,:] != 1:
        if d.IsTouchdown.ix[row_index,:] == 1:
            scoring_td.append(6)
        else:
            scoring_td.append(0)
    else:
        scoring_td.append(0)

scoring_2p = []
for row_index in range(len(d)):
    if d.ReversedPlay.ix[row_index,:] != True and d.IsNoPlay.ix[row_index,:] != 1:
        if d.IsTwoPointConversionSuccessful.ix[row_index,:] == 1:
            scoring_2p.append(2)
        else:
            scoring_2p.append(0)
    else:
        scoring_2p.append(0)


scoring_ep = []
for row_index in range(len(d)):
    if d.ReversedPlay.ix[row_index,:] != True and d.IsNoPlay.ix[row_index,:] != 1:
        if d.PAT.ix[row_index,:] == True:
            scoring_ep.append(1)
        else:
            scoring_ep.append(0)
    else:
        scoring_ep.append(0)


scoring_fg = []
for row_index in range(len(d)):
    if d.ReversedPlay.ix[row_index,:] != True and d.IsNoPlay.ix[row_index,:] != 1:
        if d.FG.ix[row_index,:] == True:
            scoring_fg.append(3)
        else:
            scoring_fg.append(0)
    else:
        scoring_fg.append(0)


scoring_safety = []
for row_index in range(len(d)):
    if d.ReversedPlay.ix[row_index,:] != True and d.IsNoPlay.ix[row_index,:] != 1:
        if d.Safety.ix[row_index,:] == True:
            scoring_safety.append(2)
        else:
            scoring_safety.append(0)
    else:
        scoring_safety.append(0)


#combine scoring arrays into all scoring types

scoring_play = []

for i in range(len(scoring_td)):
    scoring_play.append(scoring_td[i] + scoring_2p[i] + scoring_ep[i] + scoring_fg[i] + scoring_safety[i])

d['ScoringPlay'] = scoring_play


current_game = 2015091000
home_score = []
away_score = []

cg_home_score = []
cg_away_score = []

cg_home_running_score = 0
cg_away_running_score = 0

cg_home_running_list = []
cg_away_running_list = []

home_running = []
away_running = []


for row_index in range(len(d)):
    #check and see if the current row is a new game
    #if it is, update the current game id
    #append the game scores
    #reset the game scores
    offense_is_away = None
    if d.OffenseTeam.ix[row_index,:] == d.Away.ix[row_index,:]:
        offense_is_away = True
    else:
        offense_is_away = False
    if d.GameId.ix[row_index,:] != current_game:
        current_game = d.GameId.ix[row_index,:]
        home_score.append(cg_home_score)
        away_score.append(cg_away_score)
        cg_home_score = []
        cg_away_score = []
    if d.ScoringPlay.ix[row_index,:] == 0:
        cg_away_score.append(0)
        cg_home_score.append(0)
    elif d.ScoringPlay.ix[row_index,:] == 3:
        if offense_is_away:
            cg_away_score.append(3)
            cg_home_score.append(0)
        else:
            cg_away_score.append(0)
            cg_home_score.append(3)
    elif d.ScoringPlay.ix[row_index,:] == 1:
        if offense_is_away:
            cg_away_score.append(1)
            cg_home_score.append(0)
        else:
            cg_away_score.append(0)
            cg_home_score.append(1)
    elif d.ScoringPlay.ix[row_index,:] == 2:
        if d.IsTwoPointConversionSuccessful.ix[row_index,:] == 1:
            if offense_is_away:
                cg_away_score.append(2)
                cg_home_score.append(0)
            else:
                cg_away_score.append(0)
                cg_home_score.append(2)
        else:
            if offense_is_away:
                cg_away_score.append(0)
                cg_home_score.append(2)
            else:
                cg_away_score.append(2)
                cg_home_score.append(0)
    elif d.ScoringPlay.ix[row_index,:] == 6:
        if d.Kickoff.ix[row_index,:] or d.Punt.ix[row_index,:] or (d.IsFumble.ix[row_index,:] == 1) or (d.IsInterception.ix[row_index,:] == 1):
            if offense_is_away:
                cg_away_score.append(0)
                cg_home_score.append(6)
            else:
                cg_away_score.append(6)
                cg_home_score.append(0)
        else:
            if offense_is_away:
                cg_away_score.append(6)
                cg_home_score.append(0)
            else:
                cg_away_score.append(0)
                cg_home_score.append(6)


home_score.append(cg_home_score)
away_score.append(cg_away_score)

flat_home_score = [item for sublist in home_score for item in sublist]
flat_away_score = [item for sublist in away_score for item in sublist]

d['AwayScore'] = flat_away_score
d['HomeScore'] = flat_home_score

current_game_2 = 2015091000
play_num = []
cg_play_num =[]
play = 1

for row_index in range(len(d)):
    if d.GameId.ix[row_index,:] != current_game_2:
        current_game_2 = d.GameId.ix[row_index,:]
        play_num.append(cg_play_num)
        cg_play_num = []
        play = 1
    cg_play_num.append(play)
    play += 1

play_num.append(cg_play_num)

d['PlayNum'] = [item for sublist in play_num for item in sublist]

games = d.groupby('GameId')
games.aggregate(np.sum)

running_away_score = 0
running_home_score = 0

running_away_score_list = []
running_home_score_list = []


for play in range(len(d)):
    if d.PlayNum.ix[play,:] == 1:
        running_home_score = 0
        running_away_score = 0
    else:
        running_home_score += d.HomeScore.ix[play,:]
        running_away_score += d.AwayScore.ix[play,:]
    running_away_score_list.append(running_away_score)
    running_home_score_list.append(running_home_score)

d['RunningHomeScore'] = running_home_score_list
d['RunningAwayScore'] = running_away_score_list

home_def = []

for play in range(len(d)):
    home_def.append(d.RunningHomeScore.ix[play,:] - d.RunningAwayScore.ix[play,:])

d['HomeDeficit'] = home_def
d.to_csv('pbp-2015-output.csv')
