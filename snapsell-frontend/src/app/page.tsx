'use client'
import { ItemStatusCard } from '../components/ItemStatusCard'
import VideoUpload from '../components/VideoUpload'
import { useItems } from '../context/ItemsContext'
import { useEffect } from 'react'

export default function Home() {
  const { items, loading, refreshItems } = useItems()

  useEffect(() => {
    refreshItems()
  }, [])

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Upload New Inventory</h2>
        <VideoUpload />
      </div>
      <h2 className="text-2xl font-semibold mb-4">Current Inventory Status</h2>
      {loading ? (
        <div className="text-center py-4">Loading items...</div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {items.map((item) => (
            <ItemStatusCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  )
}
