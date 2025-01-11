'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ItemConfirmation } from '../../../components/ItemConfirmation'

interface Item {
  id: number
  image: string
  title: string
  description: string
  price: number
  condition: string
  status: string
  confidence: number
}

export default function EditItem() {
  const params = useParams()
  const router = useRouter()
  const [item, setItem] = useState<Item | null>(null)

  useEffect(() => {
    // TODO: Fetch item data from Supabase using params.id
    // For now using mock data
    setItem({
      id: Number(params.id),
      image: '/placeholder.svg',
      title: 'Sample Item',
      description: 'Sample description',
      price: 99.99,
      condition: 'good',
      status: 'available',
      confidence: 1
    })
  }, [params.id])

  if (!item) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">Edit Item</h1>
      <ItemConfirmation items={[item]} editMode={true} />
    </div>
  )
}
