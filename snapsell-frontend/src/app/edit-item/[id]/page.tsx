'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ItemConfirmation } from '../../../components/ItemConfirmation'
import { useItems } from '../../../context/ItemsContext'
import { Item } from '../../../types/item'

export default function EditItem() {
  const params = useParams()
  const router = useRouter()
  const { items, loading } = useItems()
  const [editItem, setEditItem] = useState<Item | null>(null)

  useEffect(() => {
    if (items.length > 0) {
      const item = items.find((item) => item.id === params.id)
      if (item) {
        setEditItem(item)
      } else {
        router.push('/inventory')
      }
    }
  }, [items, params.id, router])  

  if (!editItem) {
    return (
      <div className="text-center py-8">
        <h2 className="text-2xl font-semibold mb-4">Item not found</h2>
        <button 
          onClick={() => router.push('/inventory')} 
          className="text-blue-600 hover:text-blue-800"
        >
          Return to Inventory
        </button>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">Edit Item</h1>
      <ItemConfirmation 
        items={[editItem]} 
        editMode={true} 
        onConfirm={() => router.push('/inventory')}
      />
    </div>
  )
}