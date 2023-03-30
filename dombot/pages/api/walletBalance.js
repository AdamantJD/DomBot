import ccxt from 'ccxt';

const API_KEY = process.env.API_KEY;
const SECRET_KEY = process.env.API_SECRET;

const exchange = new ccxt.binance({
  apiKey: API_KEY,
  secret: SECRET_KEY,
  enableRateLimit: true,
});

export default async function handler(req, res) {
  try {
    const balance = await exchange.fapiPrivateGetBalance();
    res.status(200).json({ balance });
  } catch (error) {
    console.error(`Error fetching futures balance: ${error.message}`);
    res.status(500).json({ error: 'Failed to fetch wallet balance.' });
  }
}
