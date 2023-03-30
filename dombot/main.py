import ccxt
import talib
import numpy as np
import time
import os
import requests
import logging
import concurrent.futures
import threading
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
API_ENDPOINT = os.getenv('API_ENDPOINT')

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up exchange instance
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    }
)

exchange.load_markets()
markets = exchange.markets.keys()

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
trade_timeout = 60  # 1 minute

# Set up logging for market data
market_data_logger = logging.getLogger('market_data_logger')
market_data_logger.setLevel(logging.DEBUG)
market_data_logger.propagate = False  # Prevent propagation of market_data_logger messages

# Add a file handler to write logs to the market_data.log file
file_handler = logging.FileHandler('market_data.log')
file_handler.setLevel(logging.DEBUG)
market_data_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(market_data_formatter)
market_data_logger.addHandler(file_handler)

# Set up logging for all other events
other_logger = logging.getLogger('other_logger')
other_logger.setLevel(logging.DEBUG)

# Set up a StreamHandler to output other logs to the console
other_handler = logging.StreamHandler()
other_handler.setLevel(logging.INFO)  # Only log messages with INFO level or higher to the console
other_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
other_handler.setFormatter(other_formatter)
other_logger.addHandler(other_handler)

# Add a file handler to write logs to the other.log file
file_handler = logging.FileHandler('other.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(other_formatter)
other_logger.addHandler(file_handler)

def get_indicator_values(data, high, low, ema_periods, rsi_period, stoch_periods, bollinger_period):
    close_prices = np.array([item[4] for item in data])
    ema_values = {period: np.full_like(close_prices, np.nan) for period in ema_periods}
    rsi_values = np.full_like(close_prices, np.nan)
    stoch_values = np.full((len(close_prices), 2), np.nan)
    bollinger_values = np.full((len(close_prices), 3), np.nan)
    
    for period in ema_periods:
        if len(close_prices) >= period:
            ema_values[period] = talib.EMA(close_prices, timeperiod=period)
    
    if len(close_prices) >= rsi_period:
        rsi_values = talib.RSI(close_prices, timeperiod=rsi_period)
    
    if len(close_prices) >= stoch_periods[0]:
        stoch_values = talib.STOCH(high, low, close_prices, *stoch_periods)
    
    if len(close_prices) >= bollinger_period:
        upper, middle, lower = talib.BBANDS(close_prices, timeperiod=bollinger_period)
        bollinger_values[:, 0] = upper
        bollinger_values[:, 1] = middle
        bollinger_values[:, 2] = lower
    
    return ema_values, rsi_values, stoch_values, bollinger_values


def get_futures_balance():
    for i in range(5):
        try:
            balance = exchange.fapiPrivate_get_balance()
            other_logger.debug(f"Raw futures balance response: {balance}")
            for entry in balance:
                if entry['asset'] == 'USDT':
                    usdt_balance = float(entry['balance'])
                    print(f"USDT balance: {usdt_balance}")
                    return usdt_balance
        except ccxt.NetworkError as e:
            other_logger.error(f"Error fetching futures balance: {e}")
            time.sleep(5 * (i + 1))
        except ccxt.ExchangeError as e:
            other_logger.error(f"Exchange error fetching futures balance: {e}")
            time.sleep(5 * (i + 1))
    logging.warning("Failed to fetch futures balance after multiple attempts.")
    return None



def enter_trade(symbol, position_size, direction, current_price):
    for i in range(5):
        try:
            # Round position size to nearest valid size
            position_size = exchange.amount_to_precision(symbol, position_size)
            
            if direction == 'long':
                order = exchange.create_market_buy_order(symbol, position_size)
            elif direction == 'short':
                order = exchange.create_market_sell_order(symbol, position_size)
            other_logger.debug(f"Market order response for {symbol}: {order}")
            logging.info(f"Placed {direction} order for {symbol} with position size {position_size} and current price {current_price}")
            return order
        except Exception as e:
            logging.error(f"Error entering {direction} trade for {symbol}: {e}")
            time.sleep(5 * (i + 1))
    logging.error(f"Failed to enter {direction} trade for {symbol} after multiple attempts.")
    return None
    
def exit_trade(symbol, position_size, direction):
    for i in range(5):
        try:
            if direction == 'long':
                order = exchange.create_market_sell_order(symbol, position_size)
            elif direction == 'short':
                order = exchange.create_market_buy_order(symbol, position_size)
            other_logger.debug(f"Exit order response for {symbol}: {order}")
            
            # Log trade exit
            if order:
                logging.info(f"Exited {direction} trade for {symbol} with position size {position_size}")
            
            return order
        except Exception as e:
            logging.error(f"Error exiting {direction} trade for {symbol}: {e}")
            time.sleep(5 * (i + 1))
    
    logging.error(f"Failed to exit {direction} trade for {symbol} after multiple attempts.")
    return None

def process_symbol(symbol):
    # Get OHLCV data
    data = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=lookback_periods[1])

    # Log market data
    market_data_logger.debug(f"{symbol} OHLCV data: {data}")

    high = np.array([item[2] for item in data])
    low = np.array([item[3] for item in data])
    ema_values, rsi_values, stoch_values, bollinger_values = get_indicator_values(data, high, low, ema_periods, rsi_period, stoch_periods, bollinger_period)

    direction = None
    if ema_values[10][-1] > ema_values[20][-1] and ema_values[10][-2] <= ema_values[20][-2]:
        direction = 'long'
    elif ema_values[10][-1] < ema_values[20][-1] and ema_values[10][-2] >= ema_values[20][-2]:
        direction = 'short'

    if direction:
        signal = False  # Initialize signal variable
        if rsi_values[-1] < 30 and direction == 'long':
            signal = True
        elif rsi_values[-1] > 70 and direction == 'short':
            signal = True

        if signal:
            other_logger.debug(f"{symbol} signal: {signal}")
            logging.info(f"Attempting to execute trade for {symbol}")  # Log the trading pair

            # Get current futures balance
            balance = None
            for attempt in range(3):    
                balance = get_futures_balance()
                if balance is not None:
                    break
                else:
                    time.sleep(5 * (attempt + 1))

            if balance is None:
                logging.warning("Skipping trade due to failure to obtain balance.")
                return

            # Get current price
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['ask'] if direction == 'long' else ticker['bid']

            # Calculate position size
            symbol_info = exchange.markets[symbol]
            minimum_trade_value = symbol_info['limits']['cost']['min']
            minimum_position_size = minimum_trade_value / current_price
            position_size = max(minimum_position_size, 0.01 * balance)
            position_size = exchange.amount_to_precision(symbol, position_size, 'CEILING')

            # Enter trade
            order = enter_trade(symbol, position_size, direction, current_price)
            if order:
                logging.info(f"Entered {direction} trade for {symbol} with position size {position_size}")

                # Monitor trade
                in_trade = True
                entry_time = time.time()
                entry_price = current_price
                while in_trade:
                    time.sleep(5)
                    ticker = exchange.fetch_ticker(symbol)
                    current_price = ticker['ask'] if direction == 'long' else ticker['bid']

                    # Calculate profit/loss
                    pnl = (current_price - entry_price) / entry_price if direction == 'long' else (entry_price - current_price) / entry_price

                    # Exit conditions
                    if pnl >= take_profit:
                        exit_order = exit_trade(symbol, position_size, direction)
                        if exit_order:
                            logging.info(f"Exited {direction} trade for {symbol} with profit")
                        in_trade = False
                    elif pnl <= -stop_loss:
                        exit_order = exit_trade(symbol, position_size, direction)
                        if exit_order:
                            logging.info(f"Exited {direction} trade for {symbol} with loss")
                        in_trade = False

                    # Timeout exit condition
                    if time.time() - entry_time >= trade_timeout:
                        exit_order = exit_trade(symbol, position_size, direction)
                        if exit_order:
                            logging.info(f"Exited {direction} trade for {symbol} due to timeout")
                        in_trade = False

import concurrent.futures

def process_symbols():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        symbols_to_process = [symbol for symbol in exchange.markets if symbol.endswith('/USDT')]
        executor.map(process_symbol, symbols_to_process)

last_trade_time = time.time() - 60  # Initialize last trade time
while True:
    process_symbols()

    # Sleep for 60 seconds before starting the next loop
    time.sleep(60)
