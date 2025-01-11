'use client'
import Image from 'next/image'
import { Pencil } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface ItemStatusCardProps {
  item: {
    id: number
    image: string
    title: string
    description: string
    price: number
    condition: string
    status: 'negotiating' | 'scheduled' | 'sold' | 'listed' | 'available'
  }
}

export function ItemStatusCard({ item }: ItemStatusCardProps) {
  const router = useRouter()
  
  const statusColors = {
    negotiating: 'bg-yellow-100 text-yellow-800',
    scheduled: 'bg-blue-100 text-blue-800',
    sold: 'bg-green-100 text-green-800',
    listed: 'bg-gray-100 text-gray-800',
    available: 'bg-purple-100 text-purple-800',
  }

  const handleEdit = () => {
    router.push(`/edit-item/${item.id}`)
  }

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Image 
              className="h-16 w-16 rounded-lg object-cover" 
              src={item.image} 
              alt={item.title || item.description}
              width={64}
              height={64}
            />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-900 truncate">{item.title}</dt>
              <dd className="text-sm text-gray-500 truncate">{item.description}</dd>
              <dd>
                <div className="text-lg font-medium text-gray-900">${item.price.toFixed(2)}</div>
              </dd>
            </dl>
          </div>
          <div className="ml-4">
            <button
              onClick={handleEdit}
              className="inline-flex items-center p-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Pencil className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
      <div className="bg-gray-50 px-5 py-3 flex justify-between items-center">
        <div className="text-sm">
          <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold leading-5 ${statusColors[item.status]}`}>
            {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
          </span>
        </div>
        <div className="text-sm text-gray-500">
          {item.condition ? 
            item.condition.charAt(0).toUpperCase() + item.condition.slice(1).replace('_', ' ') 
            : 'Not specified'
          }
        </div>
      </div>
    </div>
  )
}
