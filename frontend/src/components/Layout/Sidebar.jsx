import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  ChatBubbleLeftRightIcon, 
  CalendarDaysIcon, 
  UserIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { 
  ChatBubbleLeftRightIcon as ChatBubbleLeftRightIconSolid, 
  CalendarDaysIcon as CalendarDaysIconSolid 
} from '@heroicons/react/24/solid'

export default function Sidebar() {
  const location = useLocation()

  const navigation = [
    {
      name: 'Chat Assistant',
      href: '/chat',
      icon: ChatBubbleLeftRightIcon,
      iconSolid: ChatBubbleLeftRightIconSolid,
      description: 'Talk to your AI assistant'
    },
    {
      name: 'Appointments',
      href: '/appointments',
      icon: CalendarDaysIcon,
      iconSolid: CalendarDaysIconSolid,
      description: 'View and manage appointments'
    }
  ]

  const isActive = (href) => location.pathname === href

  return (
    <div className="fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-gray-200 z-30">
      <div className="flex flex-col h-full">
        <div className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => {
            const Icon = isActive(item.href) ? item.iconSolid : item.icon
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-colors duration-200 ${
                  isActive(item.href)
                    ? 'bg-aspen-blue text-white'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                }`}
              >
                <Icon className="h-5 w-5 mr-3 flex-shrink-0" />
                <div>
                  <div>{item.name}</div>
                  <div className={`text-xs mt-0.5 ${
                    isActive(item.href) ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {item.description}
                  </div>
                </div>
              </Link>
            )
          })}
        </div>

        {/* Quick Stats */}
        <div className="px-4 py-4 border-t border-gray-200">
          <div className="bg-gray-50 rounded-lg p-3">
            <h3 className="text-sm font-medium text-gray-900 mb-2">Quick Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Upcoming</span>
                <span className="font-medium text-aspen-blue">2</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">This Month</span>
                <span className="font-medium text-gray-900">3</span>
              </div>
            </div>
          </div>
        </div>

        {/* Support Section */}
        <div className="px-4 py-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            <p>Need help? Contact support:</p>
            <p className="font-medium text-aspen-blue">(555) 123-4567</p>
          </div>
        </div>
      </div>
    </div>
  )
}