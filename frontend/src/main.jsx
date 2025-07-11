import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App'
import Register from './Register'
import Login from './Login'
import AddQuote from './AddQuote'
import QuoteList from './QuoteList'
import './reset.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/add" element={<AddQuote />} />
        <Route path="/list" element={<QuoteList />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)
