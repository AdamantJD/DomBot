import ccxt
import talib
import numpy as np
import time
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

# Set up exchange instance
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True,
})

# Set up trading parameters
risk = 0.1
leverage = 10
lookback_periods = [100, 200]
take_profit = 0.441
stop_loss = 1
max_position_size = 0.05
ema_periods = [10, 20]
rsi_period = 14
stoch_periods = (14, 3, 3)
bollinger_period = 20

def get_indicator_values(data, ema_periods, rsi_period, stoch_periods, bollinger_period):
    close_prices = np.array([item[4] for item in data])
    ema_values = {period: talib.EMA(close_prices, timeperiod=period) for period in ema_periods}
    rsi_values = talib.RSI(close_prices, timeperiod=rsi_period)
    stoch_values = talib.STOCH(high, low, close_prices, stoch_periods[0], stoch_periods[1], stoch_periods[2])
    bollinger_values = talib.BBANDS(close_prices, timeperiod=bollinger_period)
    return ema_values, rsi_values, stoch_values, bollinger_values

def enter_trade(symbol, position_size, direction, current_price):
    try:
        if direction == 'long':
            order = exchange.create_market_buy_order(symbol, position_size)
        elif direction == 'short':
            order = exchange.create_market_sell_order(symbol, position_size)
        return order
    except Exception as e:
        print(f"Error entering {direction} trade for {symbol}: {e}")
        return None

def exit_trade(symbol, position_size, direction):
    try:
        if direction == 'long':
            order = exchange.create_market_sell_order(symbol, position_size)
        elif direction == 'short':
            order = exchange.create_market_buy_order(symbol, position_size)
        return order
    except Exception as e:
        print(f"Error exiting trade for {symbol}: {e}")
        return None

# Main trading loop
while True:
    for symbol in exchange.markets:
        # Get OHLCV data
        data = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=lookback_periods[1])
        high = np.array([item[2] for item in data])
        low = np.array([item[3] for item in data])
        ema_values, rsi_values, stoch_values, bollinger_values = get_indicator_values(data, ema_periods, rsi_period, stoch_periods, bollinger_period)
        
        direction = None
        if ema_values[10][-1] > ema_values[20][-1] and ema_values[10][-2] <= ema_values[20][-2]:
            direction = 'long'
        elif ema_values[10][-1] < ema_values[20][-1] and ema_values[10][-2] >= ema_values[20][-2]:
            direction = 'short'
        
        if direction:
            signal = False # Initialize signal variable
            if rsi_values[-1] < 30 and direction == 'long':
                signal = True
            elif rsi_values[-1] > 70 and direction == 'short':
                signal = True
            
            if signal:
            # Calculate position size
                position_size = max_position_size * risk / stop_loss

            # Get current price
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['ask'] if direction == 'long' else ticker['bid']

            # Enter trade
            order = enter_trade(symbol, position_size, direction, current_price)
            if order:
                print(f"Entered {direction} trade for {symbol} with position size {position_size}")

                # Monitor trade
                in_trade = True
                entry_price = current_price
                while in_trade:
                    time.sleep(60)
                    ticker = exchange.fetch_ticker(symbol)
                    current_price = ticker['ask'] if direction == 'long' else ticker['bid']

                    # Calculate profit/loss
                    pnl = (current_price - entry_price) / entry_price if direction == 'long' else (entry_price - current_price) / entry_price

                    # Exit conditions
                    if pnl >= take_profit:
                        exit_order = exit_trade(symbol, position_size, direction)  # Add direction as an argument
                        if exit_order:
                            print(f"Exited {direction} trade for {symbol} with profit")
                        in_trade = False
                    elif pnl <= -stop_loss:
                        exit_order = exit_trade(symbol, position_size, direction)  # Add direction as an argument
                        if exit_order:
                            print(f"Exited {direction} trade for {symbol} with loss")
                        in_trade = False

    # Sleep before starting the next loop
    time.sleep(60)

