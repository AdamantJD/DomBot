import Head from 'next/head'
import { useState, useEffect } from 'react'

export default function Home() {
  const [walletBalance, setWalletBalance] = useState(null)
  const [pendingOrders, setPendingOrders] = useState([])
  const [executedOrders, setExecutedOrders] = useState([])
  const [pnl, setPnL] = useState(null)
  const [pnlPercent, setPnLPercent] = useState(null)
  const [winRate, setWinRate] = useState(null)

  useEffect(() => {
    // Fetch wallet balance from backend API
    fetch('/api/walletBalance')
      .then(res => res.json())
      .then(data => setWalletBalance(data.balance))
      .catch(error => console.error(error))

    // Fetch pending orders from backend API
    fetch('/api/pendingOrders')
      .then(res => res.json())
      .then(data => setPendingOrders(data.orders))
      .catch(error => console.error(error))

    // Fetch executed orders from backend API
    fetch('/api/executedOrders')
      .then(res => res.json())
      .then(data => setExecutedOrders(data.orders))
      .catch(error => console.error(error))

    // Fetch PnL, PnL%, and win rate from backend API
    fetch('/api/performanceMetrics')
      .then(res => res.json())
      .then(data => {
        setPnL(data.pnl)
        setPnLPercent(data.pnlPercent)
        setWinRate(data.winRate)
      })
      .catch(error => console.error(error))
  }, [])

  return (
    <div className="container">
      <Head>
        <title>Trading Bot Dashboard</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1 className="title">
          Trading Bot Dashboard
        </h1>

        <div className="dashboard">
          <div className="section">
            <h2>Wallet Balance</h2>
            <p>{walletBalance != null ? walletBalance.toFixed(2) : '-'}</p>
          </div>

          <div className="section">
            <h2>Pending Orders</h2>
            <ul>
              {pendingOrders.map(order => (
                <li key={order.id}>
                  {order.type === 'buy' ? 'Buy' : 'Sell'} {order.amount} {order.symbol} at {order.price.toFixed(2)}
                </li>
              ))}
            </ul>
          </div>

          <div className="section">
            <h2>Executed Orders</h2>
            <ul>
              {executedOrders.map(order => (
                <li key={order.id}>
                  {order.type === 'buy' ? 'Bought' : 'Sold'} {order.amount} {order.symbol} at {order.price.toFixed(2)}
                </li>
              ))}
            </ul>
          </div>

          <div className="section">
            <h2>PnL</h2>
            <p>{pnl != null ? pnl.toFixed(2) : '-'} ({pnlPercent != null ? pnlPercent.toFixed(2) : '-'}%)</p>
          </div>

          <div className="section">
            <h2>Win Rate</h2>
            <p>{winRate != null ? winRate.toFixed(2) : '-'}%</p>
          </div>
        </div>
      </main>
      <footer>
        <p>Powered by your trading bot</p>
      </footer>

      <style jsx>{`
        .container {
          min-height: 100vh;
          padding: 0 0.5rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
        }

        main {
          padding: 5rem 0;
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
        }

        .dashboard {
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          align-items: center;
        }

        .section {
          margin: 2rem;
          padding: 2rem;
          border: 1px solid #eaeaea;
          border-radius: 10px;
          text-align: center;
        }

        ul {
          list-style: none;
          padding-left: 0;
        }

        li {
          margin-bottom: 0.5rem;
        }

        footer {
          width: 100%;
          height: 100px;
          border-top: 1px solid #eaeaea;
          display: flex;
          justify-content: center;
          align-items: center;
        }

        footer img {
          margin-left: 0.5rem;
        }

        footer a {
          display: flex;
          justify-content: center;
          align-items: center;
        }

        a {
          color: inherit;
          text-decoration: none;
        }

        .title a {
          color: #0070f3;
          text-decoration: none;
        }

        .title a:hover,
        .title a:focus,
        .title a:active {
          text-decoration: underline;
        }

        .description {
          line-height: 1.5;
          font-size: 1.5rem;
        }

        @media (max-width: 600px) {
          .grid {
            width: 100%;
            flex-direction: column;
          }
        }
      `}</style>

      <style jsx global>{`
        html,
        body {
          padding: 0;
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu,
            Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
        }

        * {
          box-sizing: border-box;
        }
      `}</style>
    </div>
  )
}

