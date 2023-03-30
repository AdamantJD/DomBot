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
    const metrics = await getPerformanceMetrics(exchange);
    res.status(200).json(metrics);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to fetch performance metrics.' });
  }
}
