'use client'

import { useState } from 'react'
import Image from 'next/image'

interface ItemProps {
  item: {
    id: number
    image: string
    description: string
    price: number
    confidence: number
  }
  onEdit: (id: number, updatedItem: any) => void
  onDelete: (id: number) => void
}

export default function InventoryItem({ item, onEdit, onDelete }: ItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedItem, setEditedItem] = useState(item)

  const handleEdit = () => {
    onEdit(item.id, editedItem)
    setIsEditing(false)
  }

  return (
    <div className="border rounded-lg p-4 shadow-sm">
      <Image src={item.image} alt={item.description} width={200} height={200} className="w-full h-48 object-cover mb-2" />
      {isEditing ? (
        <div className="space-y-2">
          <input
            type="text"
            value={editedItem.description}
            onChange={(e) => setEditedItem({ ...editedItem, description: e.target.value })}
            className="w-full p-1 border rounded"
          />
          <input
            type="number"
            value={editedItem.price}
            onChange={(e) => setEditedItem({ ...editedItem, price: parseFloat(e.target.value) })}
            className="w-full p-1 border rounded"
          />
          <button onClick={handleEdit} className="bg-blue-500 text-white px-2 py-1 rounded">Save</button>
          <button onClick={() => setIsEditing(false)} className="bg-gray-300 px-2 py-1 rounded ml-2">Cancel</button>
        </div>
      ) : (
        <div>
          <p className="font-semibold">{item.description}</p>
          <p className="text-gray-600">${item.price.toFixed(2)}</p>
          <p className="text-sm text-gray-500">Confidence: {(item.confidence * 100).toFixed(0)}%</p>
          <div className="mt-2">
            <button onClick={() => setIsEditing(true)} className="text-blue-500 mr-2">Edit</button>
            <button onClick={() => onDelete(item.id)} className="text-red-500">Delete</button>
          </div>
        </div>
      )}
    </div>
  )
}

