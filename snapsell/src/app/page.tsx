import { ItemStatusCard } from '../components/ItemStatusCard'
import VideoUpload from '../components/VideoUpload'

// Mock data for demonstration
const mockItems = [
  { id: 1, image: '/placeholder.svg', description: 'Vintage chair', price: 50, status: 'negotiating' },
  { id: 2, image: '/placeholder.svg', description: 'Antique lamp', price: 75, status: 'scheduled' },
  { id: 3, image: '/placeholder.svg', description: 'Modern coffee table', price: 120, status: 'sold' },
  { id: 4, image: '/placeholder.svg', description: 'Bookshelf', price: 80, status: 'listed' },
]

export default function Home() {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Upload New Inventory</h2>
        <VideoUpload />
      </div>
      <h2 className="text-2xl font-semibold mb-4">Current Inventory Status</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {mockItems.map((item) => (
          <ItemStatusCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  )
}
