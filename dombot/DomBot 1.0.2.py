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
risk = 0.1 # Risk as a percentage of account balance
leverage = 10 # Leverage to use for trading
lookback_periods = [100, 200] # Lookback periods for multiple timeframes
take_profit = 0.441 # Target take-profit level (0.441 for 44.1% Fibonacci level)
stop_loss = 1 # Risk-reward ratio for stop loss (1 for 1:1)
max_position_size = 0.05 # Maximum position size as a percentage of equity
ema_periods = [10, 20] # EMA periods for EMA crossover strategy

# Get current ticker price
ticker = exchange.fetch_ticker(symbol)
current_price = ticker['last']

# Main trading loop
while True:
    for symbol in exchange.markets:
        # Get OHLCV data for multiple timeframes
        timeframe_data = {}
        for period in lookback_periods:
            data = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=period)
            timeframe_data[period] = data
        close_prices = {k: np.array([item[4] for item in v]) for k, v in timeframe_data.items()}
        
        # Calculate Fibonacci levels for multiple timeframes
        fib_levels = {}
        for period, prices in close_prices.items():
            fib_levels[period] = talib.FIB(prices, 0.382, 0.5, 0.441)
            
        # Calculate EMAs for EMA crossover strategy
        ema_values = {}
        for period in ema_periods:
            ema_values[period] = talib.EMA(close_prices[100], timeperiod=period)
        
        # Check for bullish EMA crossover on the 15-minute timeframe
        if ema_values[10][-1] > ema_values[20][-1] and ema_values[10][-2] <= ema_values[20][-2]:
            # Calculate position size based on risk, leverage, and equity
            equity = exchange.fetch_balance()['total']['USDT']
            max_equity_exposure = equity * max_position_size
            max_position_size_usd = max_equity_exposure / (leverage * close_prices[100][-1])
            balance = exchange.fetch_balance()['total']['USDT']
            position_size = min(max_position_size_usd, balance * risk / (leverage * close_prices[100][-1]))
            
            # Place limit buy order
            buy_price = close_prices[100][-1]
            order = exchange.create_limit_buy_order(symbol, position_size, buy_price)
            
            # Set take-profit level and stop-loss level
            take_profit_price = buy_price * (1 + take_profit)
            stop_loss_price = buy_price * (1 - stop_loss)
            
        # Check for bearish EMA crossover on the 15-minute timeframe
        elif ema_values[10][-1] < ema_values[20][-1] and ema_values[10][-2] >= ema_values[20][-2]:
            # Calculate position size based on risk, leverage, and equity
            equity = exchange.fetch_balance()['total']['USDT']
            max_equity_exposure = equity * max_position_size
            max_position_size_usd = max_equity_exposure / (leverage * close_prices[100][-1])
            balance = exchange.fetch_balance()['total']['USDT']
            position_size = min(max_position_size_usd, balance * risk / (leverage * close_prices[100][-1]))
            
            # Place limit buy order
            buy_price = close_prices[100][-1]
            order = exchange.create_limit_buy_order(symbol, position_size, buy_price)
            
            # Set take-profit level and stop-loss level
            take_profit_price = buy_price * (1 + take_profit)
            stop_loss_price = buy_price * (1 - stop_loss)
            
        # Check for bearish EMA crossover on the 15-minute timeframe
        elif ema_values[10][-1] < ema_values[20][-1] and ema_values[10][-2] >= ema_values[20][-2]:
            # Calculate position size based on risk, leverage, and equity
            equity = exchange.fetch_balance()['total']['USDT']
            max_equity_exposure = equity * max_position_size
            max_position_size_usd = max_equity_exposure / (leverage * close_prices[100][-1])
            balance = exchange.fetch_balance()['total']['USDT']
            
            position_size = min(max_position_size_usd, balance * risk / (leverage * close_prices[100][-1]))
            
            # Place limit sell order
            sell_price = close_prices[100][-1]
            order = exchange.create_limit_sell_order(symbol, position_size, sell_price)
            
            # Set take-profit level and stop-loss level
            take_profit_price = sell_price * (1 - take_profit)
            stop_loss_price = sell_price * (1 + stop_loss)
            
        # Check if take-profit level is hit
        if 'id' in order and current_price >= take_profit_price:
            # Place market sell order
            order = exchange.create_market_sell_order(symbol, position_size)
    
        # Check if stop-loss level is hit
        elif 'id' in order and current_price <= stop_loss_price:
            # Place market sell order
            order = exchange.create_market_sell_order(symbol, position_size)
    
        # Check if current price crosses down 0.5 Fibonacci level on the 1-hour timeframe
        elif current_price < fib_levels[200][-1]:
            # Cancel limit order and place market sell order
            exchange.cancel_order(order['id'], symbol)
            order = exchange.create_market_sell_order(symbol, position_size)
            
            # Calculate position size based on risk, leverage, and equity
            equity = exchange.fetch_balance()['total']['USDT']
            max_equity_exposure = equity * max_position_size
            max_position_size_usd = max_equity_exposure / (leverage * fib_levels[200][-2])
            balance = exchange.fetch_balance()['total']['USDT']
            position_size = min(max_position_size_usd, balance * risk / (leverage * fib_levels[200][-2]))
            
            # Place limit sell order
            sell_price = fib_levels[200][-2] * current_price / fib_levels[200][-1]
            order = exchange.create_limit_sell_order(symbol, position_size, sell_price)
            
            # Set take-profit level and stop-loss level
            take_profit_price = fib_levels[200][-3] * current_price / fib_levels[200][-2]
            stop_loss_price = sell_price * (1 + stop_loss)
        
        # Check for bearish divergence on the 15-minute timeframe
        if talib.CDLDIVERGENCE(close_prices[100], talib.MACD(close_prices[100])[0], talib.MACD(close_prices[100])[1], talib.MACD(close_prices[100])[2])[-1] == -1:
            # Calculate position size based on risk, leverage, and equity
            equity = exchange.fetch_balance()['total']['USDT']
            max_equity_exposure = equity * max_position_size
            max_position_size_usd = max_equity_exposure / (leverage * close_prices[100][-1])
            balance = exchange.fetch_balance()['total']['USDT']
            position_size = min(max_position_size_usd, balance * risk / (leverage * close_prices[100][-1]))
            
            # Place limit sell order
            sell_price = close_prices[100][-1]
            order = exchange.create_limit_sell_order(symbol, position_size, sell_price)
            
            # Set take-profit level and stop-loss level
            take_profit_price = sell_price * (1 - take_profit)
            stop_loss_price = sell_price * (1 + stop_loss)
            
        # Check for bullish divergence on the 15-minute timeframe
        elif talib.CDLDIVERGENCE(close_prices[100], talib.MACD(close_prices[100])[1], talib.MACD(close_prices[100])[0], talib.MACD(close_prices[100])[2])[-1] == 1:
            # Calculate position size based on risk, leverage, and equity
            equity = exchange.fetch_balance()['total']['USDT']
            max_equity_exposure = equity * max_position_size
            max_position_size_usd = max_equity_exposure / (leverage * close_prices[100][-1])
            balance = exchange.fetch_balance()['total']['USDT']
            position_size = min(max_position_size_usd, balance * risk / (leverage * close_prices[100][-1]))
            
            # Place limit buy order
            buy_price = close_prices[100][-1]
            order = exchange.create_limit_buy_order(symbol, position_size, buy_price)

            # Get current price
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
    
            # Check if take-profit level is hit
            if 'id' in order and current_price >= take_profit_price:
                # Place market sell order
                order = exchange.create_market_sell_order(symbol, position_size)
                
            # Check if stop-loss level is hit
            elif 'id' in order and current_price <= stop_loss_price:
                # Place market sell order
                order = exchange.create_market_sell_order(symbol, position_size)
            
            # Set take-profit level and stop-loss level
            take_profit_price = buy_price * (1 + take_profit)
            stop_loss_price = buy_price * (1 - stop_loss)
            
        # Check if take-profit level is hit
        if 'id' in order and current_price >= take_profit_price:
            # Place market sell order
            order = exchange.create_market_sell_order(symbol, position_size)
    
        # Check if stop-loss level is hit
        elif 'id' in order and current_price <= stop_loss_price:
            # Place market sell order
            order = exchange.create_market_sell_order(symbol, position_size)
    
        # Check if current price crosses up 0.5 Fibonacci level on the 1-hour timeframe
        elif current_price > fib_levels[200][0]:
            # Cancel limit order and place market buy order
            exchange.cancel_order(order['id'], symbol)
            order = exchange.create_market_buy_order(symbol, position_size)
            
            # Calculate position size based on risk, leverage, and equity
            equity = exchange.fetch_balance()['total']['USDT']
            max_equity_exposure = equity * max_position_size
            max_position_size_usd = max_equity_exposure / (leverage * fib_levels[200][1])
            balance = exchange.fetch_balance()['total']['USDT']
            position_size = min(max_position_size_usd, balance * risk / (leverage * fib_levels[200][1]))
            
            # Place limit buy order
            buy_price = fib_levels[200][1] * current_price / fib_levels[200][0]
            order = exchange.create_limit_buy_order(symbol, position_size, buy_price)
            
            # Set take-profit level and stop-loss level
            take_profit_price = fib_levels[200][2] * current_price / fib_levels[200][1]
            stop_loss_price = buy_price * (1 - stop_loss)
        
        time.sleep(60)
