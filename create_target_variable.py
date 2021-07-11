from re import L
from statistics import mode
from xml.etree.ElementPath import prepare_predicate
from scipy.signal import find_peaks,peak_prominences
import pandas as pd 
import plotly.graph_objects as go 
import plotly.express as px
import numpy as np 
import ta.trend as td


#len 
lenn = 400
# get the symbol
symbol = 'ETHUSDT'
#get time steps 
time = '15m'

# read the raw data
data = pd.read_csv(f'data/{symbol}-{time}-data.csv')
data.set_index('timestamp',inplace=True)

# get the closing price and compute 7 periods moving average (MA)
price = data[['close']].close.rolling(7).mean()
index_to_drop = price.index[0:6]
price = price.drop(index_to_drop)

price_dpo = td.DPOIndicator(price,20).dpo()


# Compute peaks and valleys
peaks, _ = find_peaks(price_dpo)
valleys, _ = find_peaks(price_dpo*-1)

# get prominences
prominences_peaks = peak_prominences(price_dpo, peaks)[0]
prominences_valleys = peak_prominences(price_dpo*-1, valleys)[0]

# Prominences 
p_valley_val = pd.Series(prominences_valleys)
p_valley_val.index = price.index[valleys] 
p_valley_val.name = 'peak_prominence'


p_peak_val = pd.Series(prominences_peaks)
p_peak_val.index = price.index[peaks] 
p_peak_val.name = 'peak_prominence'


# peak and valley status
valleys_val = pd.Series(np.repeat(2,len(valleys)))
valleys_val.index = price.index[valleys] 
valleys_val.name = 'valley_status'

peaks_val = pd.Series(np.repeat(1,len(peaks)))
peaks_val.index = price.index[peaks] 
peaks_val.name = 'peak_status'

df = pd.concat([price,price_dpo,peaks_val,valleys_val,p_valley_val,p_peak_val],axis=1)
df.fillna(0,inplace=True)
df.head(100)
df.columns
df['action'] = df.peak_status+df.valley_status

# statistics about the dataset 
df.head()
df.action.value_counts()


data_out = data.join(df.drop('close',axis=1))
data_out.head()

# write to disk
data_out.to_csv(f'data/{symbol}-{time}-data_with_target.csv')


# fig = go.Figure()
# fig.add_trace(go.Scatter(x=price_dpo.index,y=price_dpo))
# fig.add_trace(go.Scatter(x=price_dpo.index[peaks][l1_bool],
#                          y=price_dpo.iloc[peaks][l1_bool],
#                          mode='markers',name='peaks'))
# fig.add_trace(go.Scatter(x=price_dpo.index[valleys][l2_bool],
#                          y=price_dpo.iloc[valleys][l2_bool],
#                          mode='markers',name='valleys'))
# fig.show()




