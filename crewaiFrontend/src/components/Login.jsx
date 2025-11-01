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
      // Simulate login validation
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (formData.username && formData.password) {
        onLogin({
          id: 1,
          username: formData.username,
          email: `${formData.username}@example.com`,
          avatar: `https://ui-avatars.com/api/?name=${formData.username}&background=6366f1&color=fff`
        })
      } else {
        setError('Please enter username and password')
      }
    } catch (err) {
      setError('Login failed, please try again')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>CrewAI Chat</h1>
          <p>Welcome to Intelligent Conversation System</p>
        </div>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <div className="input-wrapper">
              <User className="input-icon" size={20} />
              <input
                type="text"
                name="username"
                placeholder="Username"
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
                placeholder="Password"
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
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="login-footer">
          <p>Demo account: Any username and password can login</p>
          <p>
            Don't have an account? 
            <Link to="/register" className="register-link">Register now</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
