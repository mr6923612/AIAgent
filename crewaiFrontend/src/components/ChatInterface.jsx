import React, { useState, useRef, useEffect } from 'react'
import { Send, LogOut, User, Bot, Mic, MicOff, Image, X, Loader2, MessageSquare, Plus, Trash2 } from 'lucide-react'
import { sessionAPI, crewAPI, errorHandler } from '../utils/api'
import './ChatInterface.css'

const ChatInterface = ({ user, onLogout }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: '你好！我是智能客服机器人。请告诉我您需要什么帮助？',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [uploadedImage, setUploadedImage] = useState(null)
  const [recordedAudio, setRecordedAudio] = useState(null)
  const [currentJobId, setCurrentJobId] = useState(null)
  const [timeoutId, setTimeoutId] = useState(null)
  const [currentSessionId, setCurrentSessionId] = useState(null)
  const [sessions, setSessions] = useState([])
  const [showSessionList, setShowSessionList] = useState(false)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // 会话管理功能
  const createNewSession = async () => {
    try {
      const newSession = await sessionAPI.create(
        user?.id || 'anonymous',
        `新对话 ${new Date().toLocaleString()}`
      )
      
      setCurrentSessionId(newSession.session_id)
      
      // 重置消息为新对话
      setMessages([
        {
          id: 1,
          type: 'bot',
          content: '你好！我是智能客服机器人。请告诉我您需要什么帮助？',
          timestamp: new Date()
        }
      ])
      
      // 刷新会话列表，但不自动加载会话
      await refreshSessionsList()
      
      return newSession.session_id
    } catch (error) {
      const errorMsg = errorHandler.handleAPIError(error, '创建会话')
      errorHandler.showError(errorMsg)
      return null
    }
  }

  // 仅刷新会话列表，不自动加载
  const refreshSessionsList = async () => {
    try {
      const userId = user?.id || 'anonymous'
      const sessions = await sessionAPI.getUserSessions(userId)
      setSessions(sessions)
    } catch (error) {
      console.error('刷新会话列表失败:', error)
    }
  }

  const loadSessions = async (skipAutoLoad = false) => {
    try {
      const userId = user?.id || 'anonymous'
      const userSessions = await sessionAPI.getUserSessions(userId)
      setSessions(userSessions)
      
      // 如果没有现有会话且不是跳过自动加载，创建第一个会话
      if (userSessions.length === 0 && !skipAutoLoad) {
        await createNewSession()
      } else if (userSessions.length > 0 && !skipAutoLoad) {
        // 如果有现有会话，加载最新的会话
        const latestSession = userSessions[0] // 已经按更新时间排序
        await loadSession(latestSession.session_id)
      }
    } catch (error) {
      console.error('加载会话列表失败:', error)
      // 如果加载失败，尝试创建新会话
      if (!skipAutoLoad) {
        await createNewSession()
      }
    }
  }

  const loadSession = async (sessionId) => {
    try {
      const session = await sessionAPI.get(sessionId)
      
      // 转换消息格式
      const formattedMessages = session.messages.map(msg => ({
        id: msg.id,
        type: msg.role === 'user' ? 'user' : 'bot',
        content: msg.content,
        timestamp: new Date(msg.timestamp)
      }))
      
      setMessages(formattedMessages)
      setCurrentSessionId(sessionId)
      setShowSessionList(false)
      
      // 刷新会话列表以更新当前会话状态
      await refreshSessionsList()
    } catch (error) {
      const errorMsg = errorHandler.handleAPIError(error, '加载会话')
      errorHandler.showError(errorMsg)
    }
  }

  const saveMessageToSession = async (role, content) => {
    if (!currentSessionId) return
    
    try {
      await sessionAPI.addMessage(currentSessionId, role, content)
    } catch (error) {
      console.error('保存消息失败:', error)
    }
  }

  const deleteSession = async (sessionId, event) => {
    event.stopPropagation() // 阻止触发会话加载
    
    if (!window.confirm('确定要删除这个对话吗？删除后将无法恢复。')) {
      return
    }
    
    try {
      await sessionAPI.delete(sessionId)
      
      // 如果删除的是当前会话，重置为初始状态
      if (sessionId === currentSessionId) {
        setCurrentSessionId(null)
        setMessages([
          {
            id: 1,
            type: 'bot',
            content: '你好！我是智能客服机器人。请告诉我您需要什么帮助？',
            timestamp: new Date()
          }
        ])
      }
      
      // 刷新会话列表
      await refreshSessionsList()
      
      console.log('会话删除成功')
    } catch (error) {
      const errorMsg = errorHandler.handleAPIError(error, '删除会话')
      errorHandler.showError(errorMsg)
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 组件卸载时清理定时器
  useEffect(() => {
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }
  }, [timeoutId])

  // 组件初始化时加载会话列表
  useEffect(() => {
    loadSessions()
  }, [])

  // 检查任务状态
  useEffect(() => {
    if (currentJobId && isLoading) {
      // 设置1分钟超时
      const timeout = setTimeout(() => {
        setIsLoading(false)
        setCurrentJobId(null)
        
        const timeoutMessage = {
          id: Date.now(),
          type: 'bot',
          content: '抱歉，服务器响应超时。请稍后重试或联系人工客服。',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, timeoutMessage])
      }, 60000) // 60秒 = 60000毫秒
      
      setTimeoutId(timeout)

      const interval = setInterval(async () => {
        try {
          const response = await crewAPI.getStatus(currentJobId)
          const { status, result } = response
          
          if (status === 'COMPLETE') {
            setIsLoading(false)
            setCurrentJobId(null)
            clearTimeout(timeout) // 清除超时定时器
            
            const botMessage = {
              id: Date.now(),
              type: 'bot',
              content: result,
              timestamp: new Date()
            }
            setMessages(prev => [...prev, botMessage])
            clearInterval(interval)
            
            // 保存机器人回复到会话
            await saveMessageToSession('assistant', result)
            
            // 刷新会话列表以更新消息数量
            await refreshSessionsList()
          } else if (status === 'ERROR') {
            setIsLoading(false)
            setCurrentJobId(null)
            clearTimeout(timeout) // 清除超时定时器
            
            const errorMessage = {
              id: Date.now(),
              type: 'bot',
              content: '抱歉，处理您的请求时出现错误。请稍后重试。',
              timestamp: new Date()
            }
            setMessages(prev => [...prev, errorMessage])
            clearInterval(interval)
          }
        } catch (error) {
          console.error('Error checking job status:', error)
        }
      }, 2000)

      return () => {
        clearInterval(interval)
        clearTimeout(timeout)
      }
    }
  }, [currentJobId, isLoading])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if ((!inputValue.trim() && !uploadedImage && !recordedAudio) || isLoading) return

    // 如果有录音但没有文字输入，使用录音作为输入
    const finalInputValue = inputValue || (recordedAudio ? '语音消息' : '');

    // 添加用户消息
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: finalInputValue || (uploadedImage ? '上传了图片' : recordedAudio ? '发送了语音' : '发送了消息'),
      timestamp: new Date(),
      attachments: {
        image: uploadedImage,
        audio: recordedAudio
      }
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    
    // 保存用户消息到会话
    await saveMessageToSession('user', userMessage.content)

    try {
      let response;
      
      // 检查是否有文件上传
      if (uploadedImage || recordedAudio) {
        // 有文件时使用FormData
        const formData = new FormData()
        formData.append('customer_input', finalInputValue || '')
        
        const inputTypes = []
        if (finalInputValue.trim()) inputTypes.push('text')
        if (uploadedImage) inputTypes.push('image')
        if (recordedAudio) inputTypes.push('voice')
        formData.append('input_type', inputTypes.join('+') || 'text')
        
        formData.append('additional_context', '')
        formData.append('customer_domain', 'example.com')
        formData.append('project_description', finalInputValue || '多模态输入')
        formData.append('session_id', currentSessionId || '')

        // 添加图片文件
        if (uploadedImage) {
          formData.append('image', uploadedImage.file)
        }

        // 添加录音文件
        if (recordedAudio) {
          formData.append('audio', recordedAudio.blob, 'recording.wav')
        }

        response = await crewAPI.sendFileMessage(formData)
      } else {
        // 处理JSON请求
        response = await crewAPI.sendMessage({
          customer_input: finalInputValue,
          input_type: 'text',
          additional_context: '',
          customer_domain: 'example.com',
          project_description: finalInputValue,
          session_id: currentSessionId || ''
        })
      }

      setCurrentJobId(response.job_id)
      
      // 清除上传的文件
      setUploadedImage(null)
      setRecordedAudio(null)
      setInputValue('')
    } catch (error) {
      console.error('Error sending message:', error)
      setIsLoading(false)
      const errorMessage = {
        id: Date.now(),
        type: 'bot',
        content: '抱歉，发送消息时出现错误。请稍后重试。',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setRecordedAudio({
          blob: audioBlob,
          url: audioUrl
        })
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error starting recording:', error)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedImage({
          file: file,
          url: e.target.result
        })
      }
      reader.readAsDataURL(file)
    }
  }

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      backgroundColor: '#ffffff'
    }}>
      {/* 侧边栏 */}
      <div style={{
        width: '260px',
        backgroundColor: '#f7f7f8',
        display: 'flex',
        flexDirection: 'column',
        borderRight: '1px solid #e5e5e5'
      }}>
        {/* 新对话按钮 */}
        <div style={{ padding: '12px' }}>
          <button 
            className="new-chat-button"
            onClick={createNewSession} style={{
            width: '100%',
            padding: '12px',
            backgroundColor: 'transparent',
            color: '#374151',
            border: '1px solid #e5e5e5',
            borderRadius: '8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            fontWeight: '500',
            transition: 'background-color 0.2s'
          }}
          onMouseEnter={(e) => e.target.style.backgroundColor = '#f3f4f6'}
          onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
          >
            <Plus size={16} />
            New chat
          </button>
        </div>

        {/* 会话列表 */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '0 12px',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px'
        }}>
          
          {sessions.map(session => (
            <div
              key={session.session_id}
              onClick={() => loadSession(session.session_id)}
              style={{
                padding: '12px',
                borderRadius: '8px',
                backgroundColor: session.session_id === currentSessionId ? '#f3f4f6' : 'transparent',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
                border: 'none',
                color: '#374151',
                textAlign: 'left',
                fontSize: '14px',
                lineHeight: '1.4',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                position: 'relative',
                marginBottom: '2px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
              onMouseEnter={(e) => {
                if (session.session_id !== currentSessionId) {
                  e.target.style.backgroundColor = '#f3f4f6'
                }
              }}
              onMouseLeave={(e) => {
                if (session.session_id !== currentSessionId) {
                  e.target.style.backgroundColor = 'transparent'
                }
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ 
                  fontWeight: '500', 
                  marginBottom: '2px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {session.title}
                </div>
                <div style={{ 
                  fontSize: '12px', 
                  color: '#9ca3af',
                  marginTop: '2px'
                }}>
                  {session.message_count || 0} 条消息
                </div>
              </div>
              
              {/* 删除按钮 */}
              <button
                onClick={(e) => deleteSession(session.session_id, e)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#9ca3af',
                  cursor: 'pointer',
                  padding: '4px',
                  borderRadius: '4px',
                  transition: 'all 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: 0.7
                }}
                onMouseEnter={(e) => {
                  e.target.style.color = '#ef4444'
                  e.target.style.backgroundColor = '#fef2f2'
                  e.target.style.opacity = 1
                }}
                onMouseLeave={(e) => {
                  e.target.style.color = '#9ca3af'
                  e.target.style.backgroundColor = 'transparent'
                  e.target.style.opacity = 0.7
                }}
                title="删除对话"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>

        {/* 用户信息 */}
        <div style={{
          padding: '12px',
          borderTop: '1px solid #e5e5e5',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            backgroundColor: '#10a37f',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '14px',
            fontWeight: 'bold'
          }}>
            {user?.username?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div style={{ flex: 1, color: '#374151', fontSize: '14px', fontWeight: '500' }}>
            {user?.username || 'User'}
          </div>
          <button onClick={onLogout} style={{
            background: 'none',
            border: 'none',
            color: '#6b7280',
            cursor: 'pointer',
            padding: '4px',
            borderRadius: '4px',
            transition: 'color 0.2s'
          }}
          onMouseEnter={(e) => e.target.style.color = '#374151'}
          onMouseLeave={(e) => e.target.style.color = '#6b7280'}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>

      {/* 主聊天区域 */}
      <div style={{ 
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#ffffff'
      }}>
        {/* 消息区域 */}
        <div style={{ 
          flex: 1,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          padding: '0'
        }}>
          {messages.map((message) => (
            <div key={message.id} style={{
              display: 'flex',
              justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '0',
              padding: '20px 0'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                maxWidth: '70%',
                flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
                padding: '0 20px'
              }}>
                {/* 头像 */}
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: message.type === 'user' ? '#10a37f' : '#444654',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  flexShrink: 0
                }}>
                  {message.type === 'user' ? (user?.username?.charAt(0)?.toUpperCase() || 'U') : 'AI'}
                </div>
                
                {/* 消息内容 */}
                <div style={{
                  backgroundColor: message.type === 'user' ? '#10a37f' : '#f7f7f8',
                  color: message.type === 'user' ? 'white' : '#374151',
                  padding: '12px 16px',
                  borderRadius: '18px',
                  fontSize: '14px',
                  lineHeight: '1.5',
                  wordWrap: 'break-word',
                  maxWidth: '100%'
                }}>
                  {message.content}
                  {message.attachments?.image && (
                    <div style={{ marginTop: '8px' }}>
                      <img 
                        src={message.attachments.image.url} 
                        alt="上传的图片" 
                        style={{ 
                          maxWidth: '200px', 
                          maxHeight: '200px', 
                          borderRadius: '8px' 
                        }} 
                      />
                    </div>
                  )}
                  {message.attachments?.audio && (
                    <div style={{ marginTop: '8px' }}>
                      <audio 
                        controls 
                        src={message.attachments.audio.url}
                        style={{ maxWidth: '200px' }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div style={{
              display: 'flex',
              justifyContent: 'flex-start',
              marginBottom: '0',
              padding: '20px 0'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                padding: '0 20px'
              }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: '#444654',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}>
                  AI
                </div>
                <div style={{
                  backgroundColor: '#f7f7f8',
                  color: '#374151',
                  padding: '12px 16px',
                  borderRadius: '18px',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <Loader2 size={16} className="animate-spin" />
                  正在思考...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div style={{
          padding: '24px',
          backgroundColor: '#ffffff',
          display: 'flex',
          justifyContent: 'center'
        }}>
          <div style={{
            width: '100%',
            maxWidth: '768px',
            position: 'relative'
          }}>
            <form onSubmit={handleSubmit} style={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'white',
              borderRadius: '24px',
              padding: '12px 16px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
              border: '1px solid #e5e7eb',
              position: 'relative'
            }}>
              {/* 输入框 */}
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask anything..."
                style={{
                  flex: 1,
                  backgroundColor: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: '#1f2937',
                  fontSize: '16px',
                  lineHeight: '1.5',
                  resize: 'none',
                  minHeight: '24px',
                  maxHeight: '120px',
                  fontFamily: 'inherit',
                  padding: '0',
                  marginRight: '8px'
                }}
                disabled={isLoading}
                rows={1}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit(e)
                  }
                }}
              />
              
              {/* 右侧按钮组 */}
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px',
                marginLeft: '8px'
              }}>
                {/* 图片上传按钮 */}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    width: '32px',
                    height: '32px',
                    backgroundColor: '#f3f4f6',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    color: '#6b7280',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#e5e7eb'
                    e.target.style.color = '#374151'
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = '#f3f4f6'
                    e.target.style.color = '#6b7280'
                  }}
                  disabled={isLoading}
                >
                  <Image size={16} />
                </button>
                
                {/* 语音录制按钮 */}
                <button
                  type="button"
                  onClick={isRecording ? stopRecording : startRecording}
                  style={{
                    width: '32px',
                    height: '32px',
                    backgroundColor: isRecording ? '#ef4444' : '#f3f4f6',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    color: isRecording ? 'white' : '#6b7280',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  onMouseEnter={(e) => {
                    if (!isRecording) {
                      e.target.style.backgroundColor = '#e5e7eb'
                      e.target.style.color = '#374151'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isRecording) {
                      e.target.style.backgroundColor = '#f3f4f6'
                      e.target.style.color = '#6b7280'
                    }
                  }}
                  disabled={isLoading}
                >
                  {isRecording ? <MicOff size={16} /> : <Mic size={16} />}
                </button>
                
                {/* 发送按钮 */}
                <button
                  type="submit"
                  disabled={(!inputValue.trim() && !uploadedImage && !recordedAudio) || isLoading}
                  style={{
                    width: '32px',
                    height: '32px',
                    backgroundColor: isLoading ? '#9ca3af' : '#10a37f',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: isLoading ? 'not-allowed' : 'pointer',
                    color: 'white',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  onMouseEnter={(e) => {
                    if (!isLoading && (inputValue.trim() || uploadedImage || recordedAudio)) {
                      e.target.style.backgroundColor = '#059669'
                      e.target.style.transform = 'scale(1.05)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isLoading && (inputValue.trim() || uploadedImage || recordedAudio)) {
                      e.target.style.backgroundColor = '#10a37f'
                      e.target.style.transform = 'scale(1)'
                    }
                  }}
                >
                  {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                </button>
              </div>
            </form>
          
          {/* 文件预览 */}
          {(uploadedImage || recordedAudio) && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginTop: '12px',
              padding: '8px 12px',
              backgroundColor: 'white',
              borderRadius: '12px',
              border: '1px solid #e5e7eb',
              boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
              maxWidth: '768px',
              margin: '12px auto 0'
            }}>
              {uploadedImage && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Image size={16} color="#6b7280" />
                  <span style={{ color: '#374151', fontSize: '14px' }}>
                    {uploadedImage.file.name}
                  </span>
                  <button
                    onClick={() => setUploadedImage(null)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#ef4444',
                      cursor: 'pointer',
                      padding: '2px',
                      borderRadius: '4px',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#fef2f2'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                  >
                    <X size={16} />
                  </button>
                </div>
              )}
              {recordedAudio && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Mic size={16} color="#6b7280" />
                  <span style={{ color: '#374151', fontSize: '14px' }}>
                    录音文件
                  </span>
                  <button
                    onClick={() => setRecordedAudio(null)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#ef4444',
                      cursor: 'pointer',
                      padding: '2px',
                      borderRadius: '4px',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#fef2f2'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                  >
                    <X size={16} />
                  </button>
                </div>
              )}
            </div>
          )}
          </div>
        </div>
      </div>

      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        style={{ display: 'none' }}
      />
    </div>
  )
}

export default ChatInterface