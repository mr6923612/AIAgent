import React, { useState, useRef, useEffect } from 'react'
import { Send, LogOut, User, Bot, Mic, MicOff, Image, X, Loader2 } from 'lucide-react'
import axios from 'axios'
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
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const fileInputRef = useRef(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 检查任务状态
  useEffect(() => {
    if (currentJobId && isLoading) {
      const interval = setInterval(async () => {
        try {
          const response = await axios.get(`http://127.0.0.1:8012/api/crew/${currentJobId}`)
          const { status, result } = response.data
          
          if (status === 'COMPLETE') {
            setIsLoading(false)
            setCurrentJobId(null)
            
            const botMessage = {
              id: Date.now(),
              type: 'bot',
              content: result,
              timestamp: new Date()
            }
            setMessages(prev => [...prev, botMessage])
            clearInterval(interval)
          } else if (status === 'ERROR') {
            setIsLoading(false)
            setCurrentJobId(null)
            
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

      return () => clearInterval(interval)
    }
  }, [currentJobId, isLoading])

  // 录音功能
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setRecordedAudio({ blob: audioBlob, url: audioUrl });
        
        // 停止所有音频轨道
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('无法访问麦克风:', error);
      alert('无法访问麦克风，请检查权限设置');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const removeRecordedAudio = () => {
    if (recordedAudio) {
      URL.revokeObjectURL(recordedAudio.url);
      setRecordedAudio(null);
    }
  };

  // 图片上传功能
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setUploadedImage({ file, url: imageUrl });
    }
  };

  const removeImage = () => {
    if (uploadedImage) {
      URL.revokeObjectURL(uploadedImage.url);
      setUploadedImage(null);
    }
  };


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

        // 添加图片文件
        if (uploadedImage) {
          formData.append('image', uploadedImage.file)
        }

        // 添加录音文件
        if (recordedAudio) {
          formData.append('audio', recordedAudio.blob, 'recording.wav')
        }

        response = await axios.post('http://127.0.0.1:8012/api/crew', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
      } else {
        // 处理JSON请求
        response = await axios.post('http://127.0.0.1:8012/api/crew', {
          customer_input: finalInputValue,
          input_type: 'text',
          additional_context: '',
          customer_domain: 'example.com',
          project_description: finalInputValue
        })
      }

      setCurrentJobId(response.data.job_id)
      
      // 清除上传的文件
      removeImage()
      removeRecordedAudio()
      setInputValue('')
      
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

  return (
    <div style={{ 
      height: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#f7f7f8'
    }}>
      {/* 头部 */}
      <div style={{ 
        background: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Bot size={24} />
          <h1 style={{ margin: 0, color: '#1f2937' }}>智能客服机器人</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <User size={20} />
            <span>{user?.username || '用户'}</span>
          </div>
          <button onClick={onLogout} style={{ 
            padding: '8px 16px',
            backgroundColor: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <LogOut size={16} />
            退出
          </button>
        </div>
      </div>

      {/* 消息区域 */}
      <div style={{ 
        flex: 1,
        padding: '20px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {messages.map((message) => (
          <div key={message.id} style={{
            display: 'flex',
            justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start'
          }}>
            <div style={{
              maxWidth: '70%',
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: message.type === 'user' ? '#3b82f6' : 'white',
              color: message.type === 'user' ? 'white' : '#1f2937',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
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
        ))}
        {isLoading && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start'
          }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: 'white',
              color: '#1f2937',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
              正在思考中...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 文件预览 */}
      {(uploadedImage || recordedAudio) && (
        <div style={{ 
          padding: '0 20px',
          display: 'flex',
          gap: '12px',
          alignItems: 'center'
        }}>
          {uploadedImage && (
            <>
              <img 
                src={uploadedImage.url} 
                alt="图片预览" 
                style={{ 
                  width: '60px', 
                  height: '60px', 
                  objectFit: 'cover',
                  borderRadius: '8px' 
                }} 
              />
              <button 
                onClick={removeImage}
                style={{
                  padding: '4px',
                  backgroundColor: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="移除图片"
              >
                <X size={16} />
              </button>
            </>
          )}
          {recordedAudio && (
            <>
              <div style={{
                width: '60px',
                height: '60px',
                backgroundColor: '#3b82f6',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white'
              }}>
                <Mic size={24} />
              </div>
              <button 
                onClick={removeRecordedAudio}
                style={{
                  padding: '4px',
                  backgroundColor: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="移除录音"
              >
                <X size={16} />
              </button>
            </>
          )}
        </div>
      )}

      {/* 输入区域 */}
      <form onSubmit={handleSubmit} style={{ 
        padding: '20px',
        background: 'white',
        borderTop: '1px solid #e5e7eb'
      }}>
        <div style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="请输入您的问题..."
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '16px'
            }}
            disabled={isLoading}
          />
          {/* 图片上传按钮 */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            style={{
              padding: '12px',
              backgroundColor: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title="上传图片"
            disabled={isLoading}
          >
            <Image size={20} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            style={{ display: 'none' }}
          />
          {/* 录音按钮 */}
          <button
            type="button"
            onClick={isRecording ? stopRecording : startRecording}
            style={{
              padding: '12px',
              backgroundColor: isRecording ? '#ef4444' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
            title={isRecording ? "停止录音" : "开始录音"}
            disabled={isLoading}
          >
            {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          <button
            type="submit"
            style={{
              padding: '12px 24px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
            disabled={isLoading || (!inputValue.trim() && !uploadedImage && !recordedAudio)}
          >
            <Send size={16} />
            发送
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatInterface