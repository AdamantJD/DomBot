import ccxt
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

# Set up exchange instance
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

# Fetch futures balance
balance = exchange.fapiPrivate_get_balance()
for entry in balance:
    if entry['asset'] == 'USDT':
        usdt_balance = float(entry['balance'])
        print(f"USDT balance: {usdt_balance}")
        break
# Print the balance
