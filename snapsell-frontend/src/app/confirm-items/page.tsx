'use client'

import { ItemConfirmation } from '../../components/ItemConfirmation'
import { Item } from '../../types/item'
import { useItems } from '../../context/ItemsContext' 

// Mock data for demonstration

export default function ConfirmItems() {
  const { confirmItems } = useItems()

  console.log('confirmItems', confirmItems)

  return (
    <div className="min-h-screen bg-gray-100 py-12">
      <ItemConfirmation items={confirmItems} editMode={true} />
    </div>
  )
}
