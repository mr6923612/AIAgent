import React, { useState } from 'react'
import { User, Lock, Eye, EyeOff } from 'lucide-react'
import { Link } from 'react-router-dom'
import './Login.css'

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      // 模拟登录验证
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (formData.username && formData.password) {
        onLogin({
          id: 1,
          username: formData.username,
          email: `${formData.username}@example.com`,
          avatar: `https://ui-avatars.com/api/?name=${formData.username}&background=6366f1&color=fff`
        })
      } else {
        setError('请输入用户名和密码')
      }
    } catch (err) {
      setError('登录失败，请重试')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>CrewAI Chat</h1>
          <p>欢迎使用智能对话系统</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <div className="input-wrapper">
              <User className="input-icon" size={20} />
              <input
                type="text"
                name="username"
                placeholder="用户名"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="input-group">
            <div className="input-wrapper">
              <Lock className="input-icon" size={20} />
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                placeholder="密码"
                value={formData.password}
                onChange={handleChange}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? '登录中...' : '登录'}
          </button>
        </form>

        <div className="login-footer">
          <p>演示账号：任意用户名和密码即可登录</p>
          <p>
            还没有账户？ 
            <Link to="/register" className="register-link">立即注册</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
