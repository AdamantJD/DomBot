export default async function handler(req, res) {
    try {
      // Make POST request to your trading bot API here
      const response = await fetch('http://your-api-endpoint.com/buy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      })
      if (response.ok) {
        res.status(200).json({ message: 'Buy order placed successfully' })
      } else {
        res.status(response.status).json({ message: 'Error placing buy order' })
      }
    } catch (error) {
      console.error(error)
      res.status(500).json({ message: 'Internal server error' })
    }
  }
  