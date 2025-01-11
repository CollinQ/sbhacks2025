'use client'

import { useState } from 'react'

export default function MarketplaceIntegration() {
  const [connected, setConnected] = useState(false)

  const handleConnect = () => {
    // TODO: Implement actual Facebook OAuth
    setConnected(true)
  }

  const handleDisconnect = () => {
    // TODO: Implement actual disconnection logic
    setConnected(false)
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium">Facebook Marketplace</h3>
        <p className="text-sm text-gray-500">Connect your Facebook account to post listings automatically.</p>
      </div>
      {connected ? (
        <div>
          <p className="text-green-600">Connected to Facebook Marketplace</p>
          <button
            onClick={handleDisconnect}
            className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Disconnect
          </button>
        </div>
      ) : (
        <button
          onClick={handleConnect}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Connect to Facebook
        </button>
      )}
    </div>
  )
}

