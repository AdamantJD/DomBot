import ccxt from 'ccxt';

const API_KEY = process.env.API_KEY;
const API_SECRET = process.env.API_SECRET;

const exchange = new ccxt.binance({
  apiKey: API_KEY,
  secret: API_SECRET,
  enableRateLimit: true,
});

exports.handler = async (event, context) => {
  try {
    const metrics = await getPerformanceMetrics(exchange);
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(metrics),
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ error: 'Failed to fetch performance metrics.' }),
    };
  }
};
