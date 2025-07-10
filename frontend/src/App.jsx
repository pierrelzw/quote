import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'

function App() {
  const [quotes, setQuotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [index, setIndex] = useState(0)

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
  }, [])

  // 刷新（切换下一条）
  const handleNext = () => {
    setIndex((prev) => (prev + 1) % quotes.length)
  }

  const quote = quotes[index]

  return (
    <div style={{
      minHeight: '100vh',
      background: '#cfd8c2',
      color: '#e07a5f',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'sans-serif',
      position: 'relative'
    }}>
      {/* 顶部小字 */}
      <div style={{
        position: 'absolute',
        top: 40,
        left: 0,
        right: 0,
        textAlign: 'center',
        color: '#e07a5f',
        fontSize: 18,
        letterSpacing: 1
      }}>
        a moment of insight 
      </div>

      {/* 名言内容 */}
      {loading ? (
        <div>加载中...</div>
      ) : quote ? (
        <>
          <div style={{
            fontSize: 36,
            textAlign: 'center',
            margin: '40px 0 20px 0',
            fontWeight: 400,
            lineHeight: 1.3
          }}>
            "{quote.content}"
          </div>
          <div style={{
            textAlign: 'right',
            width: '100%',
            maxWidth: 600,
            marginBottom: 30,
            fontSize: 22,
            color: '#e07a5f'
          }}>
            - {quote.author}
          </div>
          {/* 刷新按钮 */}
          <div
            style={{
              cursor: 'pointer',
              fontSize: 40,
              margin: '20px 0'
            }}
            onClick={handleNext}
            title="下一条"
          >⟳</div>
        </>
      ) : (
        <div>暂无名言</div>
      )}

      {/* 底部信息 */}
      <div style={{
        position: 'absolute',
        bottom: 20,
        left: 0,
        right: 0,
        textAlign: 'center',
        color: '#e07a5f',
        fontSize: 14
      }}>
        made by zhiwei &nbsp; | &nbsp;
        <a href="#" style={{ color: '#e07a5f', textDecoration: 'underline' }}>buy me a coffee</a>
      </div>

      {/* 右上角导航 */}
      <div style={{
        position: 'absolute',
        top: 40,
        right: 40,
        fontSize: 16
      }}>
        <Link to="/register" style={{ color: '#e07a5f', marginRight: 10 }}>注册</Link>
        <Link to="/login" style={{ color: '#e07a5f', marginRight: 10 }}>登录</Link>
        <Link to="/add" style={{ color: '#e07a5f' }}>添加名言</Link>
      </div>
    </div>
  )
}

export default App
