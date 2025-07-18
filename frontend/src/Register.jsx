import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { API_ENDPOINTS } from './config/api'

export default function Register() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState('')
  const navigate = useNavigate()

  const handleRegister = async (e) => {
    e.preventDefault()
    try {
      const res = await axios.post(API_ENDPOINTS.AUTH.REGISTER, { username, password })
      setMsg('注册成功，去登录吧！')
      setTimeout(() => navigate('/login'), 1000)
    } catch (err) {
      setMsg(err.response?.data?.message || '注册失败')
    }
  }

  return (
    <div>
      <h2>注册</h2>
      <form onSubmit={handleRegister}>
        <input value={username} onChange={e => setUsername(e.target.value)} placeholder="用户名" />
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="密码" />
        <button type="submit">注册</button>
      </form>
      <div>{msg}</div>
    </div>
  )
}
