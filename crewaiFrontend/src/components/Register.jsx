import React, { useState } from 'react'
import { User, Lock, Eye, EyeOff, Mail, ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'
import './Register.css'

const Register = ({ onRegister }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
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
      // 验证密码是否匹配
      if (formData.password !== formData.confirmPassword) {
        setError('两次输入的密码不一致')
        setIsLoading(false)
        return
      }

      // 验证必填字段
      if (!formData.username || !formData.email || !formData.password) {
        setError('请填写所有必填字段')
        setIsLoading(false)
        return
      }

      // 模拟注册过程
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 注册成功，直接登录
      onRegister({
        id: Date.now(),
        username: formData.username,
        email: formData.email,
        avatar: `https://ui-avatars.com/api/?name=${formData.username}&background=6366f1&color=fff`
      })
    } catch (err) {
      setError('注册失败，请重试')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <div className="register-header">
          <Link to="/login" className="back-button">
            <ArrowLeft size={20} />
          </Link>
          <h1>创建账户</h1>
          <p>加入CrewAI智能对话系统</p>
        </div>
        
        <form onSubmit={handleSubmit} className="register-form">
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
              <Mail className="input-icon" size={20} />
              <input
                type="email"
                name="email"
                placeholder="邮箱地址"
                value={formData.email}
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

          <div className="input-group">
            <div className="input-wrapper">
              <Lock className="input-icon" size={20} />
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                name="confirmPassword"
                placeholder="确认密码"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="register-button"
            disabled={isLoading}
          >
            {isLoading ? '注册中...' : '创建账户'}
          </button>
        </form>

        <div className="register-footer">
          <p>
            已有账户？ 
            <Link to="/login" className="login-link">立即登录</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Register

