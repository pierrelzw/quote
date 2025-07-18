import React, { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import html2canvas from 'html2canvas'
import { FaShareAlt } from 'react-icons/fa'
import { useNavigate } from 'react-router-dom'
import { API_ENDPOINTS } from './config/api'

export default function QuoteList() {
  const navigate = useNavigate()
  const [quotes, setQuotes] = useState([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const pageSize = 10
  // 用于存储每个卡片的ref
  const cardRefs = useRef([])
  const [previewImg, setPreviewImg] = useState(null)
  const [hideShareIdx, setHideShareIdx] = useState(null)

  useEffect(() => {
    axios.get(API_ENDPOINTS.QUOTES.LIST, {
      params: { page, pageSize }
    }).then(res => {
      setQuotes(res.data.quotes)
      setTotal(res.data.total)
    })
  }, [page])

  // 分享图片
  const handleShare = async (idx) => {
    setHideShareIdx(idx) // 先隐藏按钮
    await new Promise(r => setTimeout(r, 30)) // 等待渲染
    const card = cardRefs.current[idx]
    if (!card) return
    // 创建竖屏容器，内容居中
    const container = document.createElement('div')
    container.style.width = '380px'
    container.style.height = '600px'
    container.style.background = '#fff'
    container.style.display = 'flex'
    container.style.flexDirection = 'column'
    container.style.justifyContent = 'center'
    container.style.alignItems = 'center'
    container.style.borderRadius = '18px'
    container.style.boxSizing = 'border-box'
    container.style.position = 'relative'
    // 克隆卡片内容
    const clone = card.cloneNode(true)
    clone.style.margin = '0'
    clone.style.position = 'static'
    clone.style.boxShadow = 'none'
    clone.style.border = 'none'
    clone.style.background = 'none'
    clone.style.width = '320px'
    clone.style.minHeight = 'unset'
    clone.style.padding = '0'
    // 移除所有绝对定位的按钮
    Array.from(clone.querySelectorAll('button')).forEach(btn => btn.remove())
    // 调整名人名位置
    const authorDiv = clone.querySelector('div[style*="color: #e07a1f"]')
    if (authorDiv) {
      authorDiv.style.position = 'static'
      authorDiv.style.textAlign = 'right'
      authorDiv.style.marginTop = '32px'
      authorDiv.style.marginBottom = '0'
      authorDiv.style.fontSize = '18px'
    }
    container.appendChild(clone)
    document.body.appendChild(container)
    // 用高scale生成高分辨率图片
    const canvas = await html2canvas(container, { backgroundColor: '#fff', scale: 4, width: 380, height: 600 })
    const imgData = canvas.toDataURL('image/png')
    setPreviewImg(imgData)
    setHideShareIdx(null) // 恢复按钮
    document.body.removeChild(container)
  }

  return (
    <div style={{ maxWidth: 500, margin: '0 auto', padding: 20 }}>
      <button
        onClick={() => navigate('/')}
        style={{
          marginBottom: 16,
          padding: '6px 18px',
          borderRadius: 8,
          border: '1.5px solid #e07a1f',
          background: '#fffbe6',
          color: '#e07a1f',
          fontWeight: 500,
          fontSize: 15,
          cursor: 'pointer',
          boxShadow: '0 1px 4px #f5e2c0',
        }}
      >返回首页</button>
      <h2>名言列表</h2>
      {quotes.map((q, idx) => (
        <div
          key={q.id}
          ref={el => cardRefs.current[idx] = el}
          style={{
            background: '#fff',
            borderRadius: 10,
            boxShadow: '0 2px 8px #eee',
            marginBottom: 16, // 增加卡片间隔
            padding: 20,
            position: 'relative',
            border: '1.5px solid #e0e0e0',
            borderBottom: 'none',
            minHeight: 180,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            paddingTop: 48,
            paddingBottom: 24,
          }}
        >
          <div style={{ fontSize: 18, color: '#333', wordBreak: 'break-all', textAlign: 'center' }}>“{q.content}”</div>
          {/* 名人名字右下角，分享按钮左下角 */}
          <div style={{ position: 'relative', marginTop: 24, minHeight: 32 }}>
            {hideShareIdx !== idx && (
              <button
                style={{
                  position: 'absolute',
                  left: 0,
                  bottom: -50,
                  background: 'none',
                  color: '#f5b96a',
                  border: 'none',
                  borderRadius: 0,
                  padding: 0,
                  cursor: 'pointer',
                  width: 22,
                  height: 22,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 16,
                  boxShadow: 'none',
                  marginLeft: 2
                }}
                onClick={() => handleShare(idx)}
                title="分享"
              >
                <FaShareAlt />
              </button>
            )}
            <div style={{
              position: 'absolute',
              right: 0,
              bottom: 4,
              textAlign: 'right',
              color: '#e07a1f',
              fontWeight: 500,
              fontSize: 16
            }}>
              — {q.author}
            </div>
          </div>
        </div>
      ))}
      {/* 分界线 */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
        <button disabled={page === 1} onClick={() => setPage(page - 1)}>上一页</button>
        <span>第 {page} 页 / 共 {Math.ceil(total / pageSize)} 页</span>
        <button disabled={page * pageSize >= total} onClick={() => setPage(page + 1)}>下一页</button>
      </div>
      {/* 预览弹窗 */}
      {previewImg && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          background: 'rgba(0,0,0,0.5)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
          onClick={() => setPreviewImg(null)}
        >
          <img
            src={previewImg}
            alt="名言分享预览"
            style={{
              width: 'min(380px, 90vw)',
              height: 'auto',
              maxHeight: '80vh',
              background: '#fff',
              borderRadius: 18,
              boxShadow: '0 4px 24px #0002',
              cursor: 'pointer',
              border: '4px solid #fff',
              display: 'block',
            }}
            title="右键图片可复制或下载"
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  )
}
