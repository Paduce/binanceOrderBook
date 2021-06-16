from secret import API,Private
import bokeh.plotting as bk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as anim
from binance.client import Client
import webbrowser
import tempfile
import seaborn as sns
import datetime
import time

def open_file(dataFrame):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = tmp.name+'.html'
    dataFrame.to_html(path)
    webbrowser.open("file://"+path)


client = Client(API,Private)
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
book = client.get_order_book(symbol = 'BTCUSDT',limit = 5000)
global df
df = pd.DataFrame()
bids = book['bids']
asks = book['asks']
bids_prices = [t[0] for t in bids]
bids_volume = [t[1] for t in bids]
asks_prices = [t[0] for t in asks]
asks_volume = [t[1] for t in asks]
time = client.get_server_time()['serverTime']/1000
df['Bid Price'] = bids_prices
df['Bid Volume'] = bids_volume
df['Ask Price'] = asks_prices
df['Ask Volume'] = asks_volume
df = df.astype('float64')
df['time'] = time
class Depth(object):
    def __init__(self,init):
        self.state = init
        self.price = [(self.state.iloc[0,0] + self.state.iloc[2,0])/2]
    def anim(self):
        book = client.get_order_book(symbol='BTCUSDT', limit=5000)
        time = client.get_server_time()['serverTime'] / 1000
        dfnew = pd.DataFrame()
        bids = book['bids']
        asks = book['asks']
        bids_prices = [t[0] for t in bids]
        bids_volume = [t[1] for t in bids]
        asks_prices = [t[0] for t in asks]
        asks_volume = [t[1] for t in asks]
        dfnew['Bid Price'] = bids_prices
        dfnew['Bid Volume'] = bids_volume
        dfnew['Ask Price'] = asks_prices
        dfnew['Ask Volume'] = asks_volume
        dfnew = dfnew.astype('float64')
        dfnew['time'] = time
        self.state = pd.concat([self.state, dfnew], ignore_index=True)
        self.price.append((self.state[self.state['time'] == time].iloc[0,0] +
                       self.state[self.state['time'] == time].iloc[2,0])/2)
        if len(self.state) > 200*5000:
            self.state = self.state.iloc[len(self.state) - 200*5000 :,:]
            self.price = self.price[len(self.price) - 200: ]

    def plott(self,i):
        self.anim()
        ax1.clear()
        plt.hist2d(x=self.state['time'], y=self.state['Bid Price'], weights=self.state['Bid Volume'],
                   bins = (len(self.state['time'].unique()),100), cmap = 'magma')

        plt.hist2d(x=self.state['time'], y=self.state['Ask Price'], weights=self.state['Ask Volume'],
                   bins = (len(self.state['time'].unique()),100), cmap = 'magma')

        ticks = ax1.get_xticks()
        ticks = [ticks[i] for i in range(0, len(ticks), int(np.ceil(len(ticks) / 10)))]
        ax1.set_xticks(ticks)
        ax1.set_xticklabels([datetime.datetime.fromtimestamp(i).strftime('%H:%M:%S') for i in ticks])
        plt.xticks(rotation=45)
        plt.ylim(min(self.state['Bid Price']),max(self.state['Ask Price']))
        plt.plot(self.state['time'].unique(),self.price)


init = df
animation = Depth(df)
ani = anim.FuncAnimation(fig, animation.plott, interval=5000)
plt.show()