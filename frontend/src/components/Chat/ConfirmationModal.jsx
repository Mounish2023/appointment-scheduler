import React from 'react'
import { Dialog } from '@headlessui/react'
import { CheckCircleIcon, XCircleIcon, CalendarIcon, ClockIcon, UserIcon } from '@heroicons/react/24/outline'

export default function ConfirmationModal({ request, onConfirm, onCancel }) {
  const getActionTitle = () => {
    switch (request.action_type) {
      case 'book_appointment':
        return 'Confirm New Appointment'
      case 'modify_appointment':
        return 'Confirm Appointment Change'
      case 'cancel_appointment':
        return 'Confirm Cancellation'
      default:
        return 'Confirm Action'
    }
  }

  const getActionDescription = () => {
    switch (request.action_type) {
      case 'book_appointment':
        return 'Please confirm the details for your new appointment:'
      case 'modify_appointment':
        return 'Please confirm the changes to your appointment:'
      case 'cancel_appointment':
        return 'Are you sure you want to cancel this appointment?'
      default:
        return 'Please confirm this action:'
    }
  }

  const getActionIcon = () => {
    switch (request.action_type) {
      case 'book_appointment':
        return <CalendarIcon className="h-8 w-8 text-green-500" />
      case 'modify_appointment':
        return <ClockIcon className="h-8 w-8 text-blue-500" />
      case 'cancel_appointment':
        return <XCircleIcon className="h-8 w-8 text-red-500" />
      default:
        return <CheckCircleIcon className="h-8 w-8 text-gray-500" />
    }
  }

  const renderAppointmentDetails = () => {
    if (request.action_type === 'book_appointment') {
      return (
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <CalendarIcon className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-700">
              <strong>Date:</strong> {request.date} at {request.time}
            </span>
          </div>
          <div className="flex items-center space-x-3">
            <UserIcon className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-700">
              <strong>Specialist:</strong> {request.specialist}
            </span>
          </div>
          <div className="flex items-center space-x-3">
            <ClockIcon className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-700">
              <strong>Duration:</strong> {request.duration}
            </span>
          </div>
          {request.appointment_type && (
            <div className="flex items-center space-x-3">
              <CheckCircleIcon className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-700">
                <strong>Type:</strong> {request.appointment_type}
              </span>
            </div>
          )}
        </div>
      )
    } else if (request.action_type === 'modify_appointment') {
      return (
        <div className="space-y-4">
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Current Appointment:</h4>
            <p className="text-sm text-gray-600">{request.current_date}</p>
          </div>
          <div className="bg-blue-50 p-3 rounded-lg">
            <h4 className="text-sm font-medium text-blue-700 mb-2">New Appointment:</h4>
            <p className="text-sm text-blue-600">{request.new_date}</p>
            <p className="text-sm text-blue-600">with {request.specialist}</p>
          </div>
        </div>
      )
    } else if (request.action_type === 'cancel_appointment') {
      return (
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="space-y-2">
            <p className="text-sm text-red-700">
              <strong>Date:</strong> {request.appointment_date}
            </p>
            <p className="text-sm text-red-700">
              <strong>Specialist:</strong> {request.specialist}
            </p>
            <p className="text-sm text-red-700">
              <strong>Type:</strong> {request.appointment_type}
            </p>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <Dialog open={true} onClose={onCancel} className="relative z-50">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

      {/* Full-screen container */}
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="mx-auto max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          {/* Icon and Title */}
          <div className="flex items-center space-x-3 mb-4">
            {getActionIcon()}
            <div>
              <Dialog.Title className="text-lg font-semibold text-gray-900">
                {getActionTitle()}
              </Dialog.Title>
            </div>
          </div>

          {/* Description */}
          <p className="text-sm text-gray-600 mb-4">
            {getActionDescription()}
          </p>

          {/* Appointment Details */}
          <div className="mb-6">
            {renderAppointmentDetails()}
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              onClick={onConfirm}
              className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
                request.action_type === 'cancel_appointment'
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-aspen-blue hover:bg-blue-700 text-white'
              }`}
            >
              {request.action_type === 'cancel_appointment' ? 'Yes, Cancel' : 'Confirm'}
            </button>
            <button
              onClick={onCancel}
              className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium transition-colors duration-200"
            >
              {request.action_type === 'cancel_appointment' ? 'Keep Appointment' : 'Cancel'}
            </button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}