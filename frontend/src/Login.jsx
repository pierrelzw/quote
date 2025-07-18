import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { API_ENDPOINTS } from './config/api'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState('')
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    try {
      const res = await axios.post(API_ENDPOINTS.AUTH.LOGIN, { username, password })
      localStorage.setItem('token', res.data.token)
      setMsg('登录成功！')
      setTimeout(() => navigate('/'), 1000)
    } catch (err) {
      setMsg(err.response?.data?.message || '登录失败')
    }
  }

  return (
    <div>
      <h2>登录</h2>
      <form onSubmit={handleLogin}>
        <input value={username} onChange={e => setUsername(e.target.value)} placeholder="用户名" />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="密码" />
        <button type="submit">登录</button>
      </form>
      <div>{msg}</div>
    </div>
  )
}
