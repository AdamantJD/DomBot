# DomBot

DomBot is an AI-powered cryptocurrency trading bot that trades based on Fibonacci levels, EMA strategies, and bullish/bearish divergence signals. The bot is built using Python and the Binance API, and the frontend is built using Next.js.

## Getting Started

To get started with DomBot, follow the steps below:

### Frontend Setup

1. Clone the project repository: `git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git`

2. Navigate to the project directory: `cd YOUR_REPO`

3. Install the necessary dependencies: `npm install`

4. Start the frontend server: `npm run dev`. This will start the frontend server on `http://localhost:3000`.

### Backend Setup

1. Create a new Python virtual environment by running the following command in your terminal: `python3 -m venv env`

2. Activate the virtual environment by running the following command: `source env/bin/activate`

3. Install the required Python packages by running the following command: `pip install -r requirements.txt`

4. Create a `.env` file in the root directory of your project, and add the following environment variables:

API_KEY=YOUR_BINANCE_API_KEY
API_SECRET=YOUR_BINANCE_API_SECRET


Replace `YOUR_BINANCE_API_KEY` and `YOUR_BINANCE_API_SECRET` with your Binance API key and secret.

5. Start the backend by running the following command in your terminal: `python main.py`. This will start the backend API server on `http://localhost:8000`.

Once you've completed these steps, you should be able to use the frontend to monitor the performance of your trading bot, and the bot should be making trades on your behalf based on the algorithm we've implemented in the Python code.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
