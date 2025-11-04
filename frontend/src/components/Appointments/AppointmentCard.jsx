import React, { useState } from 'react'
import { format, parseISO, isAfter, isBefore } from 'date-fns'
import { 
  CalendarIcon,
  ClockIcon,
  UserIcon,
  MapPinIcon,
  PencilSquareIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'

export default function AppointmentCard({ appointment, onUpdate }) {
  const [showActions, setShowActions] = useState(false)
  const appointmentDate = parseISO(appointment.date)
  const isUpcoming = isAfter(appointmentDate, new Date())
  const isPast = isBefore(appointmentDate, new Date())

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      case 'modified':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-4 w-4" />
      case 'cancelled':
        return <XCircleIcon className="h-4 w-4" />
      default:
        return <CalendarIcon className="h-4 w-4" />
    }
  }

  const handleReschedule = () => {
    // This would typically open a modal or navigate to a reschedule page
    console.log('Reschedule appointment:', appointment.id)
    // For demo, just update the status
    const updatedAppointment = {
      ...appointment,
      status: 'modified'
    }
    onUpdate(updatedAppointment)
  }

  const handleCancel = () => {
    if (window.confirm('Are you sure you want to cancel this appointment?')) {
      const updatedAppointment = {
        ...appointment,
        status: 'cancelled'
      }
      onUpdate(updatedAppointment)
    }
  }

  return (
    <div 
      className="card hover:shadow-md transition-shadow duration-200 cursor-pointer"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {appointment.type}
              </h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(appointment.status)}`}>
                  {getStatusIcon(appointment.status)}
                  <span className="ml-1 capitalize">{appointment.status}</span>
                </span>
                {isUpcoming && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Upcoming
                  </span>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            {showActions && isUpcoming && appointment.status === 'scheduled' && (
              <div className="flex items-center space-x-2 fade-in">
                <button
                  onClick={handleReschedule}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors duration-200"
                  title="Reschedule"
                >
                  <PencilSquareIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={handleCancel}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors duration-200"
                  title="Cancel"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <CalendarIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {format(appointmentDate, 'EEEE, MMMM do, yyyy')}
                  </p>
                  <p className="text-sm text-gray-500">
                    {format(appointmentDate, 'h:mm a')}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <UserIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {appointment.specialist}
                  </p>
                  <p className="text-sm text-gray-500">
                    {appointment.specialty}
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <ClockIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    Duration
                  </p>
                  <p className="text-sm text-gray-500">
                    {appointment.duration}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <MapPinIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    Aspen Dental - Main Office
                  </p>
                  <p className="text-sm text-gray-500">
                    123 Dental Way, Suite 100
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Notes */}
          {appointment.notes && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700">
                <span className="font-medium">Notes:</span> {appointment.notes}
              </p>
            </div>
          )}

          {/* Quick Actions for Upcoming Appointments */}
          {isUpcoming && appointment.status === 'scheduled' && (
            <div className="mt-4 flex items-center space-x-3 pt-3 border-t border-gray-100">
              <button className="text-sm text-aspen-blue hover:text-blue-700 font-medium">
                View Details
              </button>
              <span className="text-gray-300">•</span>
              <button className="text-sm text-aspen-blue hover:text-blue-700 font-medium">
                Get Directions
              </button>
              <span className="text-gray-300">•</span>
              <button className="text-sm text-aspen-blue hover:text-blue-700 font-medium">
                Add to Calendar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}