import Image from 'next/image'

interface ItemStatusCardProps {
  item: {
    id: number
    image: string
    description: string
    price: number
    status: 'negotiating' | 'scheduled' | 'sold' | 'listed'
  }
}

export function ItemStatusCard({ item }: ItemStatusCardProps) {
  const statusColors = {
    negotiating: 'bg-yellow-100 text-yellow-800',
    scheduled: 'bg-blue-100 text-blue-800',
    sold: 'bg-green-100 text-green-800',
    listed: 'bg-gray-100 text-gray-800',
  }

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Image 
              className="h-16 w-16 rounded-lg object-cover" 
              src={item.image} 
              alt={item.description}
              width={64}
              height={64}
            />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{item.description}</dt>
              <dd>
                <div className="text-lg font-medium text-gray-900">${item.price.toFixed(2)}</div>
              </dd>
            </dl>
          </div>
        </div>
      </div>
      <div className="bg-gray-50 px-5 py-3">
        <div className="text-sm">
          <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold leading-5 ${statusColors[item.status]}`}>
            {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
          </span>
        </div>
      </div>
    </div>
  )
}

