import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { API_ENDPOINTS } from './config/api'

export default function AddQuote() {
  const [content, setContent] = useState('')
  const [author, setAuthor] = useState('')
  const [msg, setMsg] = useState('')
  const navigate = useNavigate()

  const handleAdd = async (e) => {
    e.preventDefault()
    const token = localStorage.getItem('token')
    if (!token) {
      setMsg('请先登录')
      return
    }
    try {
      await axios.post(API_ENDPOINTS.QUOTES.CREATE, { content, author }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setMsg('添加成功！')
      setTimeout(() => navigate('/'), 1000)
    } catch (err) {
      setMsg(err.response?.data?.message || '添加失败')
    }
  }

  return (
    <div>
      <h2>添加名言</h2>
      <form onSubmit={handleAdd}>
        <input value={content} onChange={e => setContent(e.target.value)} placeholder="名言内容" />
        <input value={author} onChange={e => setAuthor(e.target.value)} placeholder="作者" />
        <button type="submit">添加</button>
      </form>
      <div>{msg}</div>
    </div>
  )
}
