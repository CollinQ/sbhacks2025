import Link from 'next/link'
import InventoryList from '../../components/InventoryList'

export default function Inventory() {
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold">Inventory Management</h2>
        <Link
          href="/"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Add New Item
        </Link>
      </div>
      <InventoryList />
    </div>
  )
}

