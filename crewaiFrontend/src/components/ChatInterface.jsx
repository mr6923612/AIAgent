import React, { useState, useRef, useEffect } from 'react'
import { Send, LogOut, User, Bot, Mic, MicOff, Image, X, Loader2, MessageSquare, Plus, Trash2 } from 'lucide-react'
import { sessionAPI, crewAPI, errorHandler } from '../utils/api'
import './ChatInterface.css'

const ChatInterface = ({ user, onLogout }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I am an intelligent customer service bot. How can I help you?',
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

  // Session management functions
  const createNewSession = async () => {
    try {
      const newSession = await sessionAPI.create(
        user?.id || 'anonymous',
        `New Chat ${new Date().toLocaleString()}`
      )
      
      setCurrentSessionId(newSession.session_id)
      
      // Reset messages for new chat
      setMessages([
        {
          id: 1,
          type: 'bot',
          content: 'Hello! I am an intelligent customer service bot. How can I help you?',
          timestamp: new Date()
        }
      ])
      
      // Refresh session list but don't auto-load session
      await refreshSessionsList()
      
      return newSession.session_id
    } catch (error) {
      const errorMsg = errorHandler.handleAPIError(error, 'Create session')
      errorHandler.showError(errorMsg)
      return null
    }
  }

  // Only refresh session list, don't auto-load
  const refreshSessionsList = async () => {
    try {
      const userId = user?.id || 'anonymous'
      const sessions = await sessionAPI.getUserSessions(userId)
      setSessions(sessions)
    } catch (error) {
      console.error('Failed to refresh session list:', error)
    }
  }

  const loadSessions = async (skipAutoLoad = false) => {
    try {
      const userId = user?.id || 'anonymous'
      const userSessions = await sessionAPI.getUserSessions(userId)
      setSessions(userSessions)
      
      // If no existing sessions and not skipping auto-load, create first session
      if (userSessions.length === 0 && !skipAutoLoad) {
        await createNewSession()
      } else if (userSessions.length > 0 && !skipAutoLoad) {
        // If existing sessions, load the latest session
        const latestSession = userSessions[0] // Already sorted by update time
        await loadSession(latestSession.session_id)
      }
    } catch (error) {
      console.error('Failed to load session list:', error)
      // If loading fails, try to create new session
      if (!skipAutoLoad) {
        await createNewSession()
      }
    }
  }

  const loadSession = async (sessionId) => {
    try {
      const session = await sessionAPI.get(sessionId)
      
      // Convert message format
      const formattedMessages = session.messages.map(msg => ({
        id: msg.id,
        type: msg.role === 'user' ? 'user' : 'bot',
        content: msg.content,
        timestamp: new Date(msg.timestamp)
      }))
      
      setMessages(formattedMessages)
      setCurrentSessionId(sessionId)
      setShowSessionList(false)
      
      // Refresh session list to update current session status
      await refreshSessionsList()
    } catch (error) {
      const errorMsg = errorHandler.handleAPIError(error, 'Load session')
      errorHandler.showError(errorMsg)
    }
  }

  const saveMessageToSession = async (role, content) => {
    if (!currentSessionId) return
    
    try {
      await sessionAPI.addMessage(currentSessionId, role, content)
    } catch (error) {
      console.error('Failed to save message:', error)
    }
  }

  const deleteSession = async (sessionId, event) => {
    event.stopPropagation() // Prevent triggering session load
    
    if (!window.confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
      return
    }
    
    try {
      await sessionAPI.delete(sessionId)
      
      // If deleting current session, reset to initial state
      if (sessionId === currentSessionId) {
        setCurrentSessionId(null)
        setMessages([
          {
            id: 1,
            type: 'bot',
            content: 'Hello! I am an intelligent customer service bot. How can I help you?',
            timestamp: new Date()
          }
        ])
      }
      
      // Refresh session list
      await refreshSessionsList()
      
      console.log('Session deleted successfully')
    } catch (error) {
      const errorMsg = errorHandler.handleAPIError(error, 'Delete session')
      errorHandler.showError(errorMsg)
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Clean up timer when component unmounts
  useEffect(() => {
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }
  }, [timeoutId])

  // Load session list when component initializes
  useEffect(() => {
    loadSessions()
  }, [])

  // Check task status
  useEffect(() => {
    if (currentJobId && isLoading) {
      // Set 1 minute timeout
      const timeout = setTimeout(() => {
        setIsLoading(false)
        setCurrentJobId(null)
        
        const timeoutMessage = {
          id: Date.now(),
          type: 'bot',
          content: 'Sorry, server response timed out. Please try again later or contact customer service.',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, timeoutMessage])
      }, 60000) // 60 seconds = 60000 milliseconds
      
      setTimeoutId(timeout)

      const interval = setInterval(async () => {
        try {
          const response = await crewAPI.getStatus(currentJobId)
          const { status, result } = response
          
          if (status === 'COMPLETE') {
            setIsLoading(false)
            setCurrentJobId(null)
            clearTimeout(timeout) // Clear timeout timer
            
            const botMessage = {
              id: Date.now(),
              type: 'bot',
              content: result,
              timestamp: new Date()
            }
            setMessages(prev => [...prev, botMessage])
            clearInterval(interval)
            
            // Save bot reply to session
            await saveMessageToSession('assistant', result)
            
            // Refresh session list to update message count
            await refreshSessionsList()
          } else if (status === 'ERROR') {
            setIsLoading(false)
            setCurrentJobId(null)
            clearTimeout(timeout) // Clear timeout timer
            
            const errorMessage = {
              id: Date.now(),
              type: 'bot',
              content: 'Sorry, an error occurred while processing your request. Please try again later.',
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

    // If there's audio recording but no text input, use audio as input
    const finalInputValue = inputValue || (recordedAudio ? 'Voice message' : '');

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: finalInputValue || (uploadedImage ? 'Uploaded image' : recordedAudio ? 'Sent voice' : 'Sent message'),
      timestamp: new Date(),
      attachments: {
        image: uploadedImage,
        audio: recordedAudio
      }
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    
    // Save user message to session
    await saveMessageToSession('user', userMessage.content)

    try {
      let response;
      
      // Check if there are file uploads
      if (uploadedImage || recordedAudio) {
        // Use FormData when there are files
        const formData = new FormData()
        formData.append('customer_input', finalInputValue || '')
        
        const inputTypes = []
        if (finalInputValue.trim()) inputTypes.push('text')
        if (uploadedImage) inputTypes.push('image')
        if (recordedAudio) inputTypes.push('voice')
        formData.append('input_type', inputTypes.join('+') || 'text')
        
        formData.append('additional_context', '')
        formData.append('customer_domain', 'example.com')
        formData.append('project_description', finalInputValue || 'Multimodal input')
        formData.append('session_id', currentSessionId || '')

        // Add image file
        if (uploadedImage) {
          formData.append('image', uploadedImage.file)
        }

        // Add audio file
        if (recordedAudio) {
          formData.append('audio', recordedAudio.blob, 'recording.wav')
        }

        response = await crewAPI.sendFileMessage(formData)
      } else {
        // Handle JSON request
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
      
      // Clear uploaded files
      setUploadedImage(null)
      setRecordedAudio(null)
      setInputValue('')
    } catch (error) {
      console.error('Error sending message:', error)
      setIsLoading(false)
      const errorMessage = {
        id: Date.now(),
        type: 'bot',
        content: 'Sorry, an error occurred while sending the message. Please try again later.',
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
      {/* Sidebar */}
      <div style={{
        width: '260px',
        backgroundColor: '#f7f7f8',
        display: 'flex',
        flexDirection: 'column',
        borderRight: '1px solid #e5e5e5'
      }}>
        {/* New chat button */}
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

        {/* Session list */}
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
                  {session.message_count || 0} messages
                </div>
              </div>
              
              {/* Delete button */}
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
                title="Delete conversation"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>

        {/* User info */}
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

      {/* Main chat area */}
      <div style={{ 
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#ffffff'
      }}>
        {/* Message area */}
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
                {/* Avatar */}
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
                
                {/* Message content */}
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
                        alt="Uploaded image" 
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
                  Thinking...
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
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
              {/* Input field */}
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
              
              {/* Right button group */}
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px',
                marginLeft: '8px'
              }}>
                {/* Image upload button */}
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
                
                {/* Voice recording button */}
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
                
                {/* Send button */}
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
          
          {/* File preview */}
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
                    Audio file
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

      {/* Hidden file input */}
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