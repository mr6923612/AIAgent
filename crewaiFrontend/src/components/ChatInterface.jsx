import React, { useState, useRef, useEffect } from 'react'
import { Send, LogOut, User, Bot, Loader2 } from 'lucide-react'
import axios from 'axios'
import './ChatInterface.css'

const ChatInterface = ({ user, onLogout }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: '你好！我是CrewAI智能助手，可以帮助您进行项目分析和规划。请告诉我您的项目需求。',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentJobId, setCurrentJobId] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (currentJobId && isLoading) {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(`http://127.0.0.1:8012/api/crew/${currentJobId}`)
          const data = response.data
          
          if (data.status === 'COMPLETE') {
            setIsLoading(false)
            setCurrentJobId(null)
            
            // 处理AI回复消息，优化显示格式
            let displayContent = data.result || '任务已完成'
            
            // 如果是JSON格式，尝试解析并美化显示
            if (typeof displayContent === 'string') {
              try {
                const parsed = JSON.parse(displayContent)
                if (parsed.title && parsed.body) {
                  displayContent = `# ${parsed.title}\n\n${parsed.body}`
                }
              } catch (e) {
                // 如果不是JSON，保持原样
              }
            }
            
            const botMessage = {
              id: Date.now(),
              type: 'bot',
              content: displayContent,
              timestamp: new Date()
            }
            setMessages(prev => [...prev, botMessage])
            clearInterval(interval)
          } else if (data.status === 'ERROR') {
            setIsLoading(false)
            setCurrentJobId(null)
            
            const errorMessage = {
              id: Date.now(),
              type: 'bot',
              content: '抱歉，处理过程中出现了错误。请重试。',
              timestamp: new Date()
            }
            setMessages(prev => [...prev, errorMessage])
            clearInterval(interval)
          }
        } catch (error) {
          console.error('Error checking job status:', error)
        }
      }, 2000)

      return () => clearInterval(interval)
    }
  }, [currentJobId, isLoading])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      // 解析用户输入，提取项目信息
      const projectDescription = inputValue
      const customerDomain = extractDomain(inputValue) || 'example.com'

      const response = await axios.post('http://127.0.0.1:8012/api/crew', {
        customer_domain: customerDomain,
        project_description: projectDescription
      })

      setCurrentJobId(response.data.job_id)
    } catch (error) {
      console.error('Error sending message:', error)
      setIsLoading(false)
      
      const errorMessage = {
        id: Date.now(),
        type: 'bot',
        content: '抱歉，发送消息时出现错误。请检查后端服务是否正常运行。',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  const extractDomain = (text) => {
    const urlRegex = /(https?:\/\/)?([\w-]+\.)+[\w-]+(\/[\w- .\/?%&=]*)?/g
    const matches = text.match(urlRegex)
    if (matches) {
      return matches[0].replace(/^https?:\/\//, '')
    }
    return null
  }

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="chat-interface">
      {/* 头部 */}
      <div className="chat-header">
        <div className="header-left">
          <div className="chat-title">
            <Bot size={24} />
            <h1>CrewAI 智能助手</h1>
          </div>
        </div>
        <div className="header-right">
          <div className="user-info">
            <img src={user.avatar} alt={user.username} className="user-avatar" />
            <span className="user-name">{user.username}</span>
          </div>
          <button onClick={onLogout} className="logout-button">
            <LogOut size={20} />
            退出
          </button>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-avatar">
              {message.type === 'user' ? (
                <User size={20} />
              ) : (
                <Bot size={20} />
              )}
            </div>
            <div className="message-content">
              <div className="message-text">{message.content}</div>
              <div className="message-time">{formatTime(message.timestamp)}</div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot">
            <div className="message-avatar">
              <Bot size={20} />
            </div>
            <div className="message-content">
              <div className="message-text">
                <Loader2 className="loading-icon" size={16} />
                正在分析您的项目需求，请稍候...
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="input-container">
        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-wrapper">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="描述您的项目需求..."
              className="message-input"
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="send-button"
              disabled={!inputValue.trim() || isLoading}
            >
              <Send size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ChatInterface
