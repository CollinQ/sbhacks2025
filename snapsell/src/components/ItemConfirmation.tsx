'use client'

import { useState } from 'react'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { ChevronLeft, ChevronRight, DollarSign } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface Item {
  id: number
  image: string
  description: string
  price: number
  confidence: number
}

interface ItemConfirmationProps {
  items: Item[]
}

export function ItemConfirmation({ items }: ItemConfirmationProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [editedItems, setEditedItems] = useState<Item[]>(items)
  const router = useRouter()

  const currentItem = editedItems[currentIndex]

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : prev))
  }

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < items.length - 1 ? prev + 1 : prev))
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setEditedItems((prev) =>
      prev.map((item, index) =>
        index === currentIndex ? { ...item, [name]: name === 'price' ? parseFloat(value) : value } : item
      )
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Send editedItems to backend
    console.log('Submitted items:', editedItems)
    router.push('/inventory')
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h2 className="text-3xl font-bold mb-8 text-center">Confirm Item Details</h2>
      <form onSubmit={handleSubmit}>
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="bg-white rounded-lg shadow-lg overflow-hidden"
          >
            <div className="md:flex">
              <div className="md:flex-shrink-0">
                <Image
                  src={currentItem.image}
                  alt={currentItem.description}
                  width={400}
                  height={400}
                  className="h-64 w-full object-cover md:w-64"
                />
              </div>
              <div className="p-8 w-full">
                <div className="space-y-6">
                  <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                      Description
                    </label>
                    <textarea
                      id="description"
                      name="description"
                      rows={3}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      value={currentItem.description}
                      onChange={handleChange}
                    />
                  </div>
                  <div>
                    <label htmlFor="price" className="block text-sm font-medium text-gray-700">
                      Price ($)
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <DollarSign className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="number"
                        id="price"
                        name="price"
                        step="0.01"
                        className="block w-full pl-10 pr-12 sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        value={currentItem.price}
                        onChange={handleChange}
                      />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">
                      Confidence: {(currentItem.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
        <div className="flex justify-between items-center mt-8">
          <button
            type="button"
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors duration-200"
          >
            <ChevronLeft className="h-5 w-5 mr-1" />
            Previous
          </button>
          <span className="text-sm text-gray-500">
            Item {currentIndex + 1} of {items.length}
          </span>
          {currentIndex === items.length - 1 ? (
            <button
              type="submit"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
            >
              Finish
            </button>
          ) : (
            <button
              type="button"
              onClick={handleNext}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
            >
              Next
              <ChevronRight className="h-5 w-5 ml-1" />
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

