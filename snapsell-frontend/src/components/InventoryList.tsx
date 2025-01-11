'use client'

import { useState } from 'react'
import { ItemStatusCard } from './ItemStatusCard'

// Mock data for demonstration
const mockItems = [
  { 
    id: 1, 
    image: 'https://imgvrvsheaucvxnlqmqz.supabase.co/storage/v1/object/public/item-images/u2548699992_A_boy_in_Indonesia_stands_with_a_confident_look_p_c42b35ff-0382-45ea-9651-4063f1933a75_0.png?t=2025-01-11T19%3A49%3A09.127Z', 
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
