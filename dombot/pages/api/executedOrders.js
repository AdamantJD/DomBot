const ccxt = require('ccxt');

const API_KEY = process.env.API_KEY;
const API_SECRET = process.env.API_SECRET;

const exchange = new ccxt.binance({
  apiKey: API_KEY,
  secret: API_SECRET,
  enableRateLimit: true,
});

exports.handler = async (event) => {
  try {
    const orders = await getExecutedOrders(exchange);
    return {
      statusCode: 200,
      body: JSON.stringify({ orders }),
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to fetch executed orders.' }),
    };
  }
};
