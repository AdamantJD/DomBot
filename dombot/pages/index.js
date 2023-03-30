import { useState } from 'react'

export default function Home() {
  const [buying, setBuying] = useState(false)
  const handleBuy = async () => {
    setBuying(true)
    try {
      const res = await fetch('/api/buy', { method: 'POST' })
      if (res.ok) {
        console.log('Buy order placed successfully')
      } else {
        console.log('Error placing buy order')
      }
    } catch (error) {
      console.error(error)
    } finally {
      setBuying(false)
    }
  }

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

        <p className="description">
          Welcome to your trading bot dashboard!
        </p>

        <button disabled={buying} onClick={handleBuy}>Place Buy Order</button>
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
