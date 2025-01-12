'use client'

import { useState, useEffect } from 'react'

const GOOGLE_CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || '';
const SCOPES = 'https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events';

export default function CalendarIntegration() {
  const [connected, setConnected] = useState(false)
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [availableSlots, setAvailableSlots] = useState<string[]>([])

  useEffect(() => {
    console.log(accessToken)
    // Load the Google API Client Library
    const loadGoogleApi = () => {
      const script = document.createElement('script')
      script.src = 'https://apis.google.com/js/api.js'
      script.onload = () => {
        window.gapi.load('client:auth2', initClient)
      }
      document.body.appendChild(script)
    }

    const initClient = () => {
      window.gapi.client.init({
        clientId: GOOGLE_CLIENT_ID,
        scope: SCOPES,
        plugin_name: 'SnapSell'
      }).then(() => {
        // Check if user is already signed in
        if (window.gapi.auth2.getAuthInstance().isSignedIn.get()) {
          handleAuthSuccess()
        }
      })
    }

    loadGoogleApi()
  }, [])

  const handleAuthSuccess = () => {
    const authInstance = window.gapi.auth2.getAuthInstance()
    const currentUser = authInstance.currentUser.get()
    const token = currentUser.getAuthResponse().access_token
    setAccessToken(token)
    console.log(token)
    setConnected(true)
  }

  const handleConnect = async () => {
    try {
      const authInstance = window.gapi.auth2.getAuthInstance()
      await authInstance.signIn()
      handleAuthSuccess()
    } catch (error) {
      console.error('Error signing in:', error)
    }
    console.log(accessToken)
  }

  const handleDisconnect = async () => {
    try {
      const authInstance = window.gapi.auth2.getAuthInstance()
      await authInstance.signOut()
      setAccessToken(null)
      setConnected(false)
      setAvailableSlots([])
    } catch (error) {
      console.error('Error signing out:', error)
    }
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
          <div className="flex gap-2">
            <button
              onClick={handleDisconnect}
              className="mt-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              Disconnect
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={handleConnect}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Connect to Google Calendar
        </button>
      )}
    </div>
  )
}
