import React from 'react'
import { useAuth } from '../../hooks/useAuth'
import { UserIcon, Cog6ToothIcon } from '@heroicons/react/24/outline'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-40 h-16">
      <div className="h-full px-6">
        <div className="flex items-center justify-between h-full">
          {/* Logo and Title */}
          <div className="flex items-center">
            <div className="h-8 w-8 bg-aspen-blue rounded-lg flex items-center justify-center mr-3">
              <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.754 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Aspen Dental</h1>
              <p className="text-xs text-gray-500">AI Assistant</p>
            </div>
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <UserIcon className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-700">Welcome, {user?.full_name || 'User'}</span>
            </div>

            <div className="flex items-center space-x-2">
              <button className="p-1 text-gray-400 hover:text-gray-500">
                <Cog6ToothIcon className="h-5 w-5" />
              </button>

              <button
                onClick={logout}
                className="text-sm text-gray-600 hover:text-gray-900 px-3 py-1 rounded-md hover:bg-gray-100 transition-colors duration-200"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}