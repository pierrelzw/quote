import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'

function App() {
  const [quotes, setQuotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [index, setIndex] = useState(0)
  const [username, setUsername] = useState('')

  // 获取名言列表
  const fetchQuotes = async () => {
    setLoading(true)
    try {
      const res = await axios.get('http://localhost:3001/api/quotes')
      setQuotes(res.data)
      setIndex(0)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchQuotes()
    // 获取本地登录用户名
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        setUsername(payload.username)
      } catch {
        setUsername('')
      }
    } else {
      setUsername('')
    }
  }, [])

  // 刷新（切换下一条）
  const handleNext = () => {
    setIndex((prev) => (prev + 1) % quotes.length)
  }

  const quote = quotes[index]

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#fdf6ee',
        fontFamily: 'system-ui, sans-serif',
      }}
    >
      {/* 顶部导航 */}
      <div
        style={{
          width: '100%',
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0 40px',
          boxSizing: 'border-box',
          background: '#fff',
          borderBottom: '2px solid #e07a1f',
          position: 'fixed',
          top: 0,
          left: 0,
          zIndex: 10,
        }}
      >
        {/* 居中 logo */}
        <div style={{
          position: 'absolute',
          left: 0,
          right: 0,
          textAlign: 'center',
          fontWeight: 700,
          fontSize: 28,
          color: '#3a2c1a',
          letterSpacing: 1,
          pointerEvents: 'none', // 防止遮挡右侧按钮
          userSelect: 'none'
        }}>
          a moment of <span style={{ color: '#e07a1f' }}>insight</span>
        </div>
        {/* 右上角菜单 */}
        <div style={{
          marginLeft: 'auto',
          display: 'flex',
          alignItems: 'center',
          height: '100%',
          zIndex: 2
        }}>
          <Link to="/add" style={{
            color: '#3a2c1a',
            textDecoration: 'none',
            fontWeight: 500,
            marginRight: 24,
            fontSize: 18
          }}>我来贡献</Link>
          <div style={{ color: '#3a2c1a', fontWeight: 500, fontSize: 18 }}>
            {username ? username : <Link to="/login" style={{ color: '#e07a1f', textDecoration: 'none' }}>请登录</Link>}
          </div>
        </div>
      </div>

      {/* 居中内容 */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
        }}
      >
        {/* 间隔顶部导航 */}
        <div style={{ height: 100 }} />

        {/* 名言展示卡片 */}
        <div
          style={{
            background: '#fff',
            borderRadius: 16,
            boxShadow: '0 4px 24px 0 rgba(224,122,31,0.08)',
            border: '1.5px solid #f3e2c7',
            padding: '60px 48px 48px 48px',
            minWidth: 420,
            maxWidth: 700,
            margin: '0 auto',
            textAlign: 'center',
            marginBottom: 24,
            position: 'relative',
          }}
        >
          {loading ? (
            <div style={{ color: '#e07a1f', fontSize: 18 }}>正在加载...</div>
          ) : quote ? (
            <>
              <div style={{ fontSize: 28, color: '#3a2c1a', marginBottom: 40, lineHeight: 1.7 }}>
                “{quote.content}”
              </div>
              {/* 作者名靠右下 */}
              <div style={{
                position: 'absolute',
                right: 32,
                bottom: 32,
                color: '#e07a1f',
                fontWeight: 500,
                fontSize: 20,
                textAlign: 'right'
              }}>
                — {quote.author}
              </div>
            </>
          ) : (
            <div style={{ color: '#e07a1f', fontSize: 18 }}>暂无名言</div>
          )}
        </div>

        {/* 刷新符号，居中在卡片下方 */}
        <div
          onClick={handleNext}
          style={{
            cursor: 'pointer',
            fontSize: 48,
            color: '#e07a1f',
            marginTop: 8,
            marginBottom: 32,
            transition: 'color 0.2s',
            userSelect: 'none'
          }}
          title="换一句"
          onMouseOver={e => e.currentTarget.style.color = '#b85c00'}
          onMouseOut={e => e.currentTarget.style.color = '#e07a1f'}
        >⟳</div>
      </div>
    </div>
  )
}

export default App
