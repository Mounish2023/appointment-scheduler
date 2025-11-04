import React, { useState, useEffect } from 'react'
import { useAuth } from '../../hooks/useAuth'
import AppointmentCard from './AppointmentCard'
import { 
  CalendarDaysIcon, 
  PlusIcon, 
  FunnelIcon,
  MagnifyingGlassIcon 
} from '@heroicons/react/24/outline'
import { format, isAfter, isBefore, parseISO } from 'date-fns'

export default function AppointmentDashboard() {
  const [appointments, setAppointments] = useState([])
  const [filteredAppointments, setFilteredAppointments] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  // Mock appointment data
  useEffect(() => {
    const mockAppointments = [
      {
        id: '1',
        type: 'Routine Cleaning',
        date: '2025-10-20T14:00:00',
        specialist: 'Dr. Sarah Johnson',
        specialty: 'General Dentistry',
        status: 'scheduled',
        duration: '60 minutes',
        notes: 'Regular 6-month cleaning and checkup'
      },
      {
        id: '2',
        type: 'Orthodontic Consultation',
        date: '2025-11-05T10:30:00',
        specialist: 'Dr. Michael Chen',
        specialty: 'Orthodontics',
        status: 'scheduled',
        duration: '45 minutes',
        notes: 'Invisalign consultation'
      },
      {
        id: '3',
        type: 'Dental Filling',
        date: '2025-09-15T13:00:00',
        specialist: 'Dr. Sarah Johnson',
        specialty: 'General Dentistry',
        status: 'completed',
        duration: '90 minutes',
        notes: 'Composite filling for upper molar'
      },
      {
        id: '4',
        type: 'Teeth Whitening',
        date: '2025-08-22T11:00:00',
        specialist: 'Dr. Lisa Rodriguez',
        specialty: 'Cosmetic Dentistry',
        status: 'completed',
        duration: '120 minutes',
        notes: 'Professional whitening treatment'
      }
    ]

    setAppointments(mockAppointments)
    setFilteredAppointments(mockAppointments)
    setLoading(false)
  }, [])

  // Filter appointments based on search and status
  useEffect(() => {
    let filtered = appointments

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(apt => 
        apt.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        apt.specialist.toLowerCase().includes(searchTerm.toLowerCase()) ||
        apt.specialty.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Status filter
    if (statusFilter !== 'all') {
      if (statusFilter === 'upcoming') {
        filtered = filtered.filter(apt => 
          apt.status === 'scheduled' && isAfter(parseISO(apt.date), new Date())
        )
      } else if (statusFilter === 'past') {
        filtered = filtered.filter(apt => 
          apt.status === 'completed' || isBefore(parseISO(apt.date), new Date())
        )
      } else {
        filtered = filtered.filter(apt => apt.status === statusFilter)
      }
    }

    setFilteredAppointments(filtered)
  }, [appointments, searchTerm, statusFilter])

  const upcomingAppointments = appointments.filter(apt => 
    apt.status === 'scheduled' && isAfter(parseISO(apt.date), new Date())
  )

  const pastAppointments = appointments.filter(apt => 
    apt.status === 'completed' || isBefore(parseISO(apt.date), new Date())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-aspen-blue"></div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Appointments</h1>
          <p className="text-gray-600 mt-1">
            Manage your dental appointments and view your history
          </p>
        </div>
        <button className="btn-primary flex items-center space-x-2">
          <PlusIcon className="h-4 w-4" />
          <span>Book New Appointment</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CalendarDaysIcon className="h-8 w-8 text-aspen-blue" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Upcoming</p>
              <p className="text-2xl font-semibold text-gray-900">{upcomingAppointments.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="h-4 w-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Completed</p>
              <p className="text-2xl font-semibold text-gray-900">{pastAppointments.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <CalendarDaysIcon className="h-4 w-4 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total</p>
              <p className="text-2xl font-semibold text-gray-900">{appointments.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search appointments..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 input-field"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <FunnelIcon className="h-4 w-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field min-w-[140px]"
            >
              <option value="all">All Appointments</option>
              <option value="upcoming">Upcoming</option>
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>
      </div>

      {/* Appointments List */}
      <div className="space-y-4">
        {filteredAppointments.length === 0 ? (
          <div className="text-center py-12">
            <CalendarDaysIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No appointments found
            </h3>
            <p className="text-gray-500 mb-4">
              {searchTerm || statusFilter !== 'all' 
                ? "Try adjusting your search or filters." 
                : "You don't have any appointments yet."}
            </p>
            <button className="btn-primary">
              Book Your First Appointment
            </button>
          </div>
        ) : (
          filteredAppointments.map((appointment) => (
            <AppointmentCard 
              key={appointment.id} 
              appointment={appointment}
              onUpdate={(updatedAppointment) => {
                setAppointments(prev => 
                  prev.map(apt => 
                    apt.id === updatedAppointment.id ? updatedAppointment : apt
                  )
                )
              }}
            />
          ))
        )}
      </div>
    </div>
  )
}