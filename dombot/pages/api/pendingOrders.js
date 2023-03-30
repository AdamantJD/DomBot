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
    const orders = await exchange.fapiPrivateGetOpenOrders();
    res.status(200).json({ orders });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to fetch pending orders.' });
  }
}
