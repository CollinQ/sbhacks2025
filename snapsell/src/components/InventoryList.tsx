'use client'

import { useState } from 'react'
import { ItemStatusCard } from './ItemStatusCard'

// Mock data for demonstration
const mockItems = [
  { id: 1, image: '/placeholder.svg', description: 'Vintage chair', price: 50, status: 'negotiating' },
  { id: 2, image: '/placeholder.svg', description: 'Antique lamp', price: 75, status: 'scheduled' },
  { id: 3, image: '/placeholder.svg', description: 'Modern coffee table', price: 120, status: 'sold' },
  { id: 4, image: '/placeholder.svg', description: 'Bookshelf', price: 80, status: 'listed' },
]

export default function InventoryList() {
  const [items, setItems] = useState(mockItems)

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {items.map((item) => (
        <ItemStatusCard key={item.id} item={item} />
      ))}
    </div>
  )
}

