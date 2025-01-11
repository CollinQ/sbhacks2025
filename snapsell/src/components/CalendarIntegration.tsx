'use client'

import { useState } from 'react'

export default function CalendarIntegration() {
  const [connected, setConnected] = useState(false)
  const [availableSlots, setAvailableSlots] = useState<string[]>([])

  const handleConnect = () => {
    // TODO: Implement actual Google Calendar OAuth
    setConnected(true)
    // Mock available time slots
    setAvailableSlots([
      '2023-05-20 10:00 AM',
      '2023-05-20 2:00 PM',
      '2023-05-21 11:00 AM',
      '2023-05-21 3:00 PM',
    ])
  }

  const handleDisconnect = () => {
    // TODO: Implement actual disconnection logic
    setConnected(false)
    setAvailableSlots([])
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium">Google Calendar</h3>
        <p className="text-sm text-gray-500">Connect your Google Calendar to manage availability and schedule meetings.</p>
      </div>
      {connected ? (
        <div>
          <p className="text-green-600">Connected to Google Calendar</p>
          <button
            onClick={handleDisconnect}
            className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Disconnect
          </button>
          <div className="mt-4">
            <h4 className="text-md font-medium">Available Time Slots</h4>
            <ul className="mt-2 space-y-1">
              {availableSlots.map((slot, index) => (
                <li key={index} className="text-sm text-gray-600">{slot}</li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <button
          onClick={handleConnect}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Connect to Google Calendar
        </button>
      )}
    </div>
  )
}

