import ccxt
import talib
import numpy as np
import time
import os
import logging
import concurrent.futures
from datetime import datetime
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
timeframe = '1m'
num_candles = 30
risk = 0.1
leverage = 3
lookback_periods = [100, 200]
take_profit = 0.441
stop_loss = 1
max_position_size = 0.05
position_size = 100
# ema_periods = [10, 20]
ema_periods = [5, 10]
rsi_period = 14
stoch_periods = (14, 3, 3)
bollinger_period = 20

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

def get_futures_symbols():
    futures_symbols = []
    exchange_info = exchange.fapiPublic_get_exchangeinfo()
    for symbol_info in exchange_info['symbols']:
        futures_symbols.append(symbol_info['symbol'])
    print(futures_symbols)
    return futures_symbols

def process_symbol(symbol):
    # Get OHLCV data
    data = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=num_candles)

    # Log market data
    market_data_logger.debug(f"{symbol} OHLCV data: {data}")

    high = np.array([item[2] for item in data])
    low = np.array([item[3] for item in data])
    ema_values, rsi_values, stoch_values, bollinger_values = get_indicator_values(data, high, low, ema_periods, rsi_period, stoch_periods, bollinger_period)

    direction = None
    if ema_values[5][-1] > ema_values[10][-1] and ema_values[5][-2] <= ema_values[10][-2]:
        direction = 'long'
    elif ema_values[5][-1] < ema_values[10][-1] and ema_values[5][-2] >= ema_values[10][-2]:
        direction = 'short'

    if direction:
        # Get current price
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['ask'] if direction == 'long' else ticker['bid']
        
        signal = False  # Initialize signal variable
        if rsi_values[-1] < 45 and direction == 'long':
            signal = True
        elif rsi_values[-1] > 55 and direction == 'short':
            signal = True

        if signal:
            # Calculate the 0.382 Fibonacci level
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=num_candles)
            high_price = np.max([candle[2] for candle in ohlcv])  # Get the highest price
            low_price = np.min([candle[3] for candle in ohlcv])   # Get the lowest price
            fib_382 = low_price + (high_price - low_price) * 0.382  # calculate the 0.382 fibonacci level

            if direction == 'long':
                order_side = 'buy'
            else:
                order_side = 'sell'

            limit_price = fib_382
            limit_price = exchange.price_to_precision(symbol, limit_price)

            print(f"Placing {order_side} limit order for {symbol} with size {position_size} at price {limit_price}")
            try:
                order = exchange.create_limit_order(symbol, order_side, position_size, limit_price)
                print(f"{datetime.now()} {symbol} {order_side} limit order placed at {limit_price}, size: {position_size}")
            except Exception as e:
                print(f"{datetime.now()} {symbol} Error placing {order_side} limit order: {e}")
                logging.error(f"Error placing limit order for {symbol}: {e}")

            other_logger.debug(f"{symbol} signal: {signal}")
            logging.info(f"Attempting to execute trade for {symbol} at price {limit_price} with position size {position_size}")  # Log the trading pair
            time.sleep(timeframe_seconds)

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

import concurrent.futures

def process_symbols():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Get valid futures trading pairs
        valid_futures_symbols = get_futures_symbols()

        # Filter out invalid trading pairs from your list of USDT pairs
        symbols_to_process = [symbol for symbol in exchange.markets if symbol.endswith('/USDT') and symbol.replace("/", "") in valid_futures_symbols]
        executor.map(process_symbol, symbols_to_process)

timeframe_seconds = int(timeframe[:-1]) * 60 if timeframe.endswith('m') else int(timeframe[:-1]) * 60 * 60  # Initialize last trade time
while True:
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
        time.sleep(timeframe_seconds)
        continue

    process_symbols()

    # Sleep for 60 seconds before starting the next loop
    time.sleep(timeframe_seconds)
