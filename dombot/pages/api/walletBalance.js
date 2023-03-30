import ccxt from 'ccxt';

const API_KEY = process.env.API_KEY;
const API_SECRET = process.env.API_SECRET;

const exchange = new ccxt.binance({
  apiKey: API_KEY,
  secret: API_SECRET,
  enableRateLimit: true,
});

export default async function handler(req, res) {
  try {
    const balances = await exchange.fapiPrivateGetBalance();

    // Filter for only the USDT balance
    const usdtBalance = balances.find(b => b.asset === 'USDT').balance;

    console.log(usdtBalance); // log the balance to the console

    res.status(200).json({ balance: usdtBalance });

  } catch (error) {
    console.error(`Error fetching futures balance: ${error.message}`);
    res.status(500).json({ error: 'Failed to fetch wallet balance.' });
  }
}
