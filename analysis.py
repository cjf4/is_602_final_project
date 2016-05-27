import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

d = pd.read_csv('pbp-2015-output.csv')



#filter out non 'traditional' plays
d_reg = d[d.PAT == False]
d_reg = d_reg[d_reg.ReversedPlay == False]
d_reg = d_reg[d_reg.Punt == False]
d_reg = d_reg[d_reg.Kickoff == False]
d_reg = d_reg[d_reg.DeadPlay == False]



reg_play_list = ('PASS','RUSH','SACK','SCRAMBLE')
d_reg = d_reg[d_reg.PlayType.isin(reg_play_list)]

#focus only on home offense plays
h_off = d_reg[d.OffenseTeam == d.Home]



grouped_plays = h_off.groupby('PlayType')

plays_by_count = grouped_plays.PlayType.count()

plt.figure(1)
plays_by_count.plot(kind='bar')
plt.show()

h_off_lead = h_off[h_off.HomeDeficit > 8]
h_off_trail = h_off[h_off.HomeDeficit < -8]

lead_groupings = h_off_lead.groupby('PlayType')
trail_groupings = h_off_trail.groupby('PlayType')

plt.figure(2)
lead_play_count = lead_groupings.PlayType.count()
lead_play_count.plot(kind='bar')
plt.show()

plt.figure(3)

trail_play_count = trail_groupings.PlayType.count()
trail_play_count.plot(kind='bar')
plt.show()
