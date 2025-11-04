import React, { useState, useEffect, useRef } from 'react'
import { useWebSocket } from '../../hooks/useWebSocket'
import { useAuth } from '../../hooks/useAuth'
import MessageBubble from './MessageBubble'
import ConfirmationModal from './ConfirmationModal'
import { PaperAirplaneIcon } from '@heroicons/react/24/solid'
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'

export default function ChatInterface() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [isTyping, setIsTyping] = useState(false)
  const [confirmationRequest, setConfirmationRequest] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const { user } = useAuth()
  const { 
    sendMessage, 
    isConnected, 
    connect, 
    disconnect,
    lastMessage 
  } = useWebSocket()

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Connect to WebSocket on component mount
  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      const messageData = JSON.parse(lastMessage.data)

      switch (messageData.type) {
        case 'agent_message':
          setMessages(prev => [...prev, {
            id: Date.now(),
            sender: 'agent',
            content: messageData.content,
            timestamp: new Date().toISOString()
          }])
          setIsTyping(false)
          break

        case 'typing_indicator':
          setIsTyping(messageData.is_typing)
          break

        case 'request_approval':
          setConfirmationRequest(messageData.details)
          break

        case 'connection_status':
          console.log('Connection status:', messageData.status)
          break

        default:
          console.log('Unknown message type:', messageData.type)
      }
    }
  }, [lastMessage])

  const handleSendMessage = () => {
    if (!message.trim() || !isConnected) return

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])

    // Send message via WebSocket
    sendMessage({
      type: 'user_message',
      content: message.trim()
    })

    setMessage('')
    setIsTyping(true)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleConfirmationResponse = (approved) => {
    if (!confirmationRequest) return

    sendMessage({
      type: 'approval_response',
      action_id: confirmationRequest.action_id,
      approved: approved
    })

    setConfirmationRequest(null)
  }

  const startNewChat = () => {
    setMessages([])
    setIsTyping(false)
    setConfirmationRequest(null)
    // Send a greeting request
    setTimeout(() => {
      sendMessage({
        type: 'user_message',
        content: 'Hello'
      })
    }, 500)
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center">
          <ChatBubbleLeftRightIcon className="h-6 w-6 text-aspen-blue mr-3" />
          <div>
            <h1 className="text-xl font-semibold text-gray-900">AI Assistant</h1>
            <p className="text-sm text-gray-500">
              {isConnected ? (
                <span className="flex items-center">
                  <span className="h-2 w-2 bg-green-400 rounded-full mr-2"></span>
                  Connected
                </span>
              ) : (
                <span className="flex items-center">
                  <span className="h-2 w-2 bg-red-400 rounded-full mr-2"></span>
                  Disconnected
                </span>
              )}
            </p>
          </div>
        </div>
        <button
          onClick={startNewChat}
          className="btn-secondary text-sm"
        >
          New Chat
        </button>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto bg-gray-50 px-6 py-4 space-y-4 scrollbar-thin">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <ChatBubbleLeftRightIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to Aspen Dental AI Assistant
            </h3>
            <p className="text-gray-500 max-w-md mx-auto">
              I'm here to help you book, modify, or cancel dental appointments. 
              Start by saying hello or asking about available appointments.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {isTyping && (
          <div className="flex items-start space-x-3 animate-fade-in">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-aspen-blue rounded-full flex items-center justify-center">
                <svg className="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
            <div className="message-bubble message-agent">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1">
            <textarea
              ref={inputRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              rows={1}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-aspen-blue focus:border-transparent resize-none"
              style={{ minHeight: '44px', maxHeight: '120px' }}
              disabled={!isConnected}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!message.trim() || !isConnected}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed p-3"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
        {!isConnected && (
          <p className="text-sm text-red-500 mt-2">
            Connection lost. Please refresh the page to reconnect.
          </p>
        )}
      </div>

      {/* Confirmation Modal */}
      {confirmationRequest && (
        <ConfirmationModal
          request={confirmationRequest}
          onConfirm={() => handleConfirmationResponse(true)}
          onCancel={() => handleConfirmationResponse(false)}
        />
      )}
    </div>
  )
}