import React, { createContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext({})

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Check for existing session on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token')
      const savedUser = localStorage.getItem('user')

      if (token && savedUser) {
        try {
          setUser(JSON.parse(savedUser))
          // Optionally verify token with server
          // const userData = await authAPI.getCurrentUser()
          // setUser(userData)
        } catch (error) {
          console.error('Error parsing saved user:', error)
          localStorage.removeItem('token')
          localStorage.removeItem('user')
        }
      }

      setLoading(false)
    }

    initializeAuth()
  }, [])

  const login = async (email, password) => {
    try {
      setError(null)
      setLoading(true)

      const response = await authAPI.login(email, password)
      const { access_token } = response

      // Store token
      localStorage.setItem('token', access_token)

      // Get user data
      const userData = await authAPI.getCurrentUser()
      setUser(userData)
      localStorage.setItem('user', JSON.stringify(userData))

      return userData
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Login failed'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const signup = async (userData) => {
    try {
      setError(null)
      setLoading(true)

      const response = await authAPI.signup(userData)
      const { access_token } = response

      // Store token
      localStorage.setItem('token', access_token)

      // Get user data
      const user = await authAPI.getCurrentUser()
      setUser(user)
      localStorage.setItem('user', JSON.stringify(user))

      return user
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Registration failed'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local storage and state regardless of API call success
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      setUser(null)
      setError(null)
    }
  }

  const clearError = () => {
    setError(null)
  }

  const value = {
    user,
    loading,
    error,
    login,
    signup,
    logout,
    clearError
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext