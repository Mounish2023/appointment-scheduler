import React from 'react'
import { format } from 'date-fns'
import { UserIcon } from '@heroicons/react/24/solid'

export default function MessageBubble({ message }) {
  const isUser = message.sender === 'user'
  const timestamp = new Date(message.timestamp)

  const formatMessageContent = (content) => {
    // Convert markdown-like formatting to HTML
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br />')
  }

  return (
    <div className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''} fade-in`}>
      {/* Avatar */}
      <div className="flex-shrink-0">
        {isUser ? (
          <div className="h-8 w-8 bg-aspen-blue rounded-full flex items-center justify-center">
            <UserIcon className="h-4 w-4 text-white" />
          </div>
        ) : (
          <div className="h-8 w-8 bg-aspen-green rounded-full flex items-center justify-center">
            <svg className="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
        )}
      </div>

      {/* Message Content */}
      <div className={`max-w-xs lg:max-w-md ${isUser ? 'ml-auto' : 'mr-auto'}`}>
        <div className={`message-bubble ${isUser ? 'message-user' : 'message-agent'}`}>
          <div 
            className="text-sm leading-relaxed"
            dangerouslySetInnerHTML={{ 
              __html: formatMessageContent(message.content) 
            }}
          />
        </div>

        {/* Timestamp */}
        <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {format(timestamp, 'HH:mm')}
        </div>
      </div>
    </div>
  )
}