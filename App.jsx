
import { useEffect, useState } from 'react'
import './App.css'

const API = 'http://127.0.0.1:5000'

function App() {
  const [product, setProduct] = useState(null)
  const [orders, setOrders] = useState([])
  const [error, setError] = useState('')
  const [buying, setBuying] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState('')

  async function loadProduct() {
    try {
      const response = await fetch(`${API}/api/products`)

      if (!response.ok) {
        throw new Error('Failed to load product')
      }

      const data = await response.json()
      setProduct(data.length > 0 ? data[0] : null)
      setError(data.length > 0 ? '' : 'No products found.')
    } catch {
      setError('Backend connection failed. Please check the Flask server.')
    }
  }

  async function loadOrders() {
    try {
      const response = await fetch(`${API}/api/orders`)

      if (!response.ok) {
        throw new Error('Failed to load orders')
      }

      const data = await response.json()
      setOrders(data)
    } catch {
      setMessage('Unable to load order history.')
      setMessageType('error')
    }
  }

  useEffect(() => {
    loadProduct()
    loadOrders()
  }, [])

  async function handleBuy() {
    if (buying || !product || product.stock <= 0) {
      return
    }

    setBuying(true)
    setMessage('')
    setMessageType('')

    try {
      const response = await fetch(`${API}/api/buy`, {
        method: 'POST',
        headers: {
          'Idempotency-Key': crypto.randomUUID(),
        },
      })

      const result = await response.json()

      setMessage(result.message || 'Purchase request completed.')
      setMessageType(response.ok ? 'success' : 'error')

      await Promise.all([
        loadProduct(),
        loadOrders(),
      ])
    } catch {
      setMessage(
        'Unable to connect to the backend. Please check your order before retrying.'
      )
      setMessageType('error')
    } finally {
      setBuying(false)
    }
  }

  return (
    <div className="app">
      <nav className="navbar">
        <a href="#home" className="logo">
          Flash<span>Sale</span>
        </a>

        <div className="nav-links">
          <a href="#home">Home</a>
          <a href="#product">Flash Deals</a>
          <a href="#orders">My Orders</a>
        </div>
      </nav>

      <main id="home">
        <section className="hero">
          <div>
            <p className="eyebrow">LIMITED TIME OFFER</p>

            <h1>
              Big deals.
              <br />
              <span>Small prices.</span>
            </h1>

            <p className="hero-text">
              Shop today's featured deal before it sells out.
            </p>

            <a className="hero-button" href="#product">
              Shop Now <span>→</span>
            </a>
          </div>

          <div className="hero-graphic" aria-hidden="true">
            <div className="sale-circle">
              FLASH
              <br />
              <strong>SALE</strong>
            </div>

            <div className="phone-art">
              <div className="camera camera-one" />
              <div className="camera camera-two" />
              <div className="camera camera-three" />
              <div className="phone-shine" />
            </div>

            <span className="spark spark-one">✦</span>
            <span className="spark spark-two">✧</span>
          </div>
        </section>

        <section className="benefits">
          <div>
            <span className="benefit-icon">✓</span>
            <span>
              <strong>Easy ordering</strong>
              <small>Quick purchase process</small>
            </span>
          </div>

          <div>
            <span className="benefit-icon">◉</span>
            <span>
              <strong>Live stock</strong>
              <small>Updated from the database</small>
            </span>
          </div>

          <div>
            <span className="benefit-icon">♡</span>
            <span>
              <strong>Limited deals</strong>
              <small>While stock lasts</small>
            </span>
          </div>
        </section>

        <section className="section" id="product">
          <div className="section-title">
            <div>
              <p className="eyebrow">TODAY'S PICK</p>
              <h2>Featured product</h2>
            </div>

            <span className="sale-label">🔥 Flash Sale</span>
          </div>

          {error && !product ? (
            <div className="message-box error" role="alert">
              {error}
            </div>
          ) : !product ? (
            <div className="message-box">
              Loading product...
            </div>
          ) : (
            <article className="product-card">
              <div className="product-picture">
                <div className="product-badge">SPECIAL DEAL</div>

                <div className="product-phone" aria-hidden="true">
                  <div className="product-camera camera-one" />
                  <div className="product-camera camera-two" />
                  <div className="product-camera camera-three" />
                  <div className="product-phone-shine" />
                </div>
              </div>

              <div className="product-info">
                <p className="category">ELECTRONICS</p>

                <h3>{product.name}</h3>

                <p className="description">
                  A great deal on today's featured product.
                  Order now while stock is available.
                </p>

                <div className="price">
                  ₹{Number(product.price).toLocaleString('en-IN')}
                </div>

                <div
                  className={`stock ${
                    product.stock <= 0 ? 'sold-out' : ''
                  }`}
                >
                  <span className="stock-dot" />

                  {product.stock > 0
                    ? `${product.stock} items available`
                    : 'Out of stock'}
                </div>

                <button
                  className="buy-button"
                  onClick={handleBuy}
                  disabled={buying || product.stock <= 0}
                >
                  {buying
                    ? 'Processing...'
                    : product.stock <= 0
                      ? 'Out of Stock'
                      : 'Buy Now'}

                  {!buying && product.stock > 0 && <span>→</span>}
                </button>

                {message && (
                  <p
                    className={`message ${messageType}`}
                    role="status"
                    aria-live="polite"
                  >
                    {message}
                  </p>
                )}

                <p className="secure-note">
                  ✓ Secure order processing
                </p>
              </div>
            </article>
          )}
        </section>

        <section className="section orders-section" id="orders">
          <div className="section-title">
            <div>
              <p className="eyebrow">YOUR PURCHASES</p>
              <h2>My order history</h2>
            </div>

            <span className="order-count">
              {orders.length} orders
            </span>
          </div>

          {orders.length === 0 ? (
            <div className="empty-orders">
              <div className="empty-symbol">▱</div>
              <h3>No orders yet</h3>

              <p>
                Your purchases will appear here after you place an order.
              </p>

              <a href="#product">View flash deal →</a>
            </div>
          ) : (
            <div className="orders-list">
              {orders.map((order) => (
                <div className="order-item" key={order.order_id}>
                  <div className="order-symbol">✓</div>

                  <div className="order-main">
                    <strong>{order.product_name}</strong>

                    <span>
                      Order #{order.order_id} · Quantity: {order.quantity}
                    </span>
                  </div>

                  <div className="order-right">
                    <strong>
                      ₹{Number(order.price).toLocaleString('en-IN')}
                    </strong>

                    <span>Confirmed</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <a href="#home" className="logo">
          Flash<span>Sale</span>
        </a>

        <p>Great deals, made simple.</p>

        <small>
          © {new Date().getFullYear()} Flash Sale Management System
        </small>
      </footer>
    </div>
  )
}

export default App
