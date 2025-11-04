import React, { createContext, useState, useEffect, useRef } from 'react'
import websocketService from '../services/websocket'
import { useAuth } from '../hooks/useAuth'

const WebSocketContext = createContext({})

export const WebSocketProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState(null)
  const [connectionError, setConnectionError] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const { user } = useAuth()
  const reconnectTimeoutRef = useRef(null)

  useEffect(() => {
    if (!user) {
      disconnect()
      return
    }

    // Generate or retrieve session ID
    let currentSessionId = localStorage.getItem('chatSessionId')
    if (!currentSessionId) {
      currentSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      localStorage.setItem('chatSessionId', currentSessionId)
    }
    setSessionId(currentSessionId)

    // Setup WebSocket event listeners
    const handleOpen = () => {
      setIsConnected(true)
      setConnectionError(null)
      clearTimeout(reconnectTimeoutRef.current)
    }

    // const handleClose = (event) => {
    //   setIsConnected(false)
    //   if (event.code !== 1000) {
    //     setConnectionError('Connection lost')
    //     // Attempt to reconnect after a delay
    //     reconnectTimeoutRef.current = setTimeout(() => {
    //       if (user) {
    //         connect(currentSessionId)
    //       }
    //     }, 3000)
    //   }
    // }

    const handleMessage = (data) => {
      setLastMessage({ data: JSON.stringify(data), timestamp: Date.now() })
    }

    const handleError = (error) => {
      setConnectionError('Connection error')
      console.error('WebSocket error:', error)
    }
    websocketService.addEventListener('open', () => console.log('🔄 Reconnected'));

    websocketService.addEventListener('open', handleOpen)
    websocketService.addEventListener('close', handleClose)
    websocketService.addEventListener('message', handleMessage)
    websocketService.addEventListener('error', handleError)

    return () => {
      websocketService.removeEventListener('open', handleOpen)
      websocketService.removeEventListener('close', handleClose)
      websocketService.removeEventListener('message', handleMessage)
      websocketService.removeEventListener('error', handleError)
      clearTimeout(reconnectTimeoutRef.current)
    }
  }, [user])

  const connect = (customSessionId = null) => {
    if (!user) {
      console.error('Cannot connect WebSocket: User not authenticated')
      return
    }

    const token = localStorage.getItem('token')
    if (!token) {
      console.error('Cannot connect WebSocket: No auth token')
      return
    }

    const targetSessionId = customSessionId || sessionId
    if (!targetSessionId) {
      console.error('Cannot connect WebSocket: No session ID')
      return
    }

    try {
      websocketService.connect(targetSessionId, token)
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      setConnectionError('Failed to connect')
    }
  }

  const disconnect = () => {
    websocketService.disconnect()
    setIsConnected(false)
    setLastMessage(null)
    setConnectionError(null)
    clearTimeout(reconnectTimeoutRef.current)
  }

  const sendMessage = (message) => {
    if (!isConnected) {
      console.error('Cannot send message: WebSocket not connected')
      return false
    }

    try {
      return websocketService.send(message)
    } catch (error) {
      console.error('Failed to send WebSocket message:', error)
      return false
    }
  }

  const reconnect = () => {
    disconnect()
    setTimeout(() => {
      if (user && sessionId) {
        connect()
      }
    }, 1000)
  }

  const value = {
    isConnected,
    lastMessage,
    connectionError,
    sessionId,
    connect,
    disconnect,
    sendMessage,
    reconnect
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}

export default WebSocketContext