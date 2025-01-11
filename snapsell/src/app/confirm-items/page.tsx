import { ItemConfirmation } from '../../components/ItemConfirmation'

// Mock data for demonstration
const mockItems = [
  { id: 1, image: '/placeholder.svg', description: 'Vintage chair', price: 50, confidence: 0.9 },
  { id: 2, image: '/placeholder.svg', description: 'Antique lamp', price: 75, confidence: 0.85 },
  { id: 3, image: '/placeholder.svg', description: 'Modern coffee table', price: 120, confidence: 0.95 },
]

export default function ConfirmItems() {
  return (
    <div className="min-h-screen bg-gray-100 py-12">
      <ItemConfirmation items={mockItems} />
    </div>
  )
}
