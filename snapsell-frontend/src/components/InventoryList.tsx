'use client'

import { useState } from 'react'
import { ItemStatusCard } from './ItemStatusCard'

// Mock data for demonstration
const mockItems = [
  { 
    id: 1, 
    image: '/placeholder.svg', 
    title: 'Vintage Chair',
    description: 'Beautiful vintage chair in great condition', 
    price: 50, 
    status: 'negotiating',
    condition: 'good'
  },
  { 
    id: 2, 
    image: '/placeholder.svg', 
    title: 'Antique Lamp',
    description: 'Antique brass lamp from the 1920s', 
    price: 75, 
    status: 'scheduled',
    condition: 'fair'
  },
  { 
    id: 3, 
    image: '/placeholder.svg', 
    title: 'Modern Coffee Table',
    description: 'Modern glass and steel coffee table', 
    price: 120, 
    status: 'sold',
    condition: 'like_new'
  },
  { 
    id: 4, 
    image: '/placeholder.svg', 
    title: 'Wooden Bookshelf',
    description: 'Solid wood bookshelf with 5 shelves', 
    price: 80, 
    status: 'listed',
    condition: 'good'
  },
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
