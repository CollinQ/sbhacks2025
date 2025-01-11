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

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">Edit Item</h1>
      <ItemConfirmation items={[params.id]} editMode={true} />
    </div>
  )
}
