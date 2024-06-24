import os
from dotenv import load_dotenv
import requests
import time
from discord import Intents, Client, TextChannel
from discord.ext import tasks
import datetime
import pandas as pd
import pandas_ta as ta

import os
TOKEN=os.getenv("TOKEN")
intents = Intents.default()
intents.message_content = True

client = Client(intents=intents)

last_warning_time=0

def get_kline_data(symbol, interval, start=None, end=None, category="linear", limit=200):
    url = "https://api.bybit.com/v5/market/kline"
    
    params = {
        "symbol": symbol,
        "interval": interval,
        "category": category,
        "limit": limit
    }
    if start:
        params["start"] = start
    if end:
        params["end"] = end

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['retCode'] == 0:
            return data['result']['list']
        else:
            print(f"Error: {data['retMsg']}")
    else:
        print(f"HTTP Error: {response.status_code}")

    return None

# chooses first channel on which bot has permisions 
def get_default_channel(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            return channel
    return None


@tasks.loop(seconds=5) 
async def check_rsi():

    global last_warning_time

    number_pulled_records=100

    end_time = int(time.time() * 1000)
    start_time = end_time - (number_pulled_records* 60 * 60 * 1000)  

    symbol = "SOLUSDT"
    interval = "60"  # 1-hour interval
  
    kline_data = get_kline_data(symbol, interval, start=start_time, end=end_time)
   

    if kline_data:
       
        timestamps = [int(candle[0]) for candle in kline_data]
        open_prices = [float(candle[1]) for candle in kline_data]
        high_prices = [float(candle[2]) for candle in kline_data]
        low_prices = [float(candle[3]) for candle in kline_data]
        close_prices = [float(candle[4]) for candle in kline_data]
        volumes = [float(candle[5]) for candle in kline_data]

        timestamps.reverse()
        open_prices.reverse()
        high_prices.reverse()
        low_prices.reverse()
        close_prices.reverse()
        volumes.reverse()

        dates = [datetime.datetime.fromtimestamp(ts / 1000) for ts in timestamps]

        # Create a DataFrame
        data = pd.DataFrame({
            'Date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': volumes
        })

        # pandas_ta library is used to calculate relative strength index
        data['RSI'] = ta.rsi(data['Close'], length=14)

        # getting data from the last record 
        latest_RSI=data.iloc[-1, -1]
        latest_price=data.iloc[-1, -3]
        

        for guild in client.guilds:
            channel = get_default_channel(guild)
            if channel:
                
                # await channel.send(f"Latest {symbol} price: {latest_price} USDT, RSI={latest_RSI}")
                current_time = time.time()
                
                if latest_RSI>70 and current_time-last_warning_time>=3600:    # waiting until an hour passes since last message to avoid spam
                    last_warning_time = current_time
                    await channel.send(f"RSI for SOLUSDT is over 70")

                if latest_RSI<30 and current_time-last_warning_time>=3600:
                    last_warning_time = current_time
                    await channel.send(f"RSI for SOLUSDT is under 30")


@client.event
async def on_ready():
    print(f'{client.user} is now running!')
    check_rsi.start()  


def main():
    client.run(TOKEN)

if __name__ == '__main__':
    main()