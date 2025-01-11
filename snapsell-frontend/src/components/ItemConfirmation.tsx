'use client'

import { useState } from 'react'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { ChevronLeft, ChevronRight, DollarSign } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

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

interface ItemConfirmationProps {
  items: Item[]
  editMode?: boolean
}

export function ItemConfirmation({ items, editMode = false }: ItemConfirmationProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [editedItems, setEditedItems] = useState<Item[]>(items.map(item => ({
    ...item,
    condition: item.condition || 'good',
    status: item.status || 'available',
    title: item.title || ''
  })))
  const router = useRouter()

  const currentItem = editedItems[currentIndex]

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : prev))
  }

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < items.length - 1 ? prev + 1 : prev))
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setEditedItems((prev) =>
      prev.map((item, index) =>
        index === currentIndex ? { ...item, [name]: name === 'price' ? parseFloat(value) : value } : item
      )
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (editMode) {
        // TODO: Update item in Supabase
        console.log('Updating item:', editedItems[0])
        router.push('/inventory')
      } else {
        // TODO: Create new items in Supabase
        console.log('Creating items:', editedItems)
        router.push('/inventory')
      }
    } catch (error) {
      console.error('Error saving items:', error)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      {!editMode && (
        <div className="mb-8 text-center">
          <h2 className="text-3xl font-bold">Confirm Item Details</h2>
          <p className="text-gray-600 mt-2">Item {currentIndex + 1} of {items.length}</p>
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
          >
            <div className="md:grid md:grid-cols-2 md:gap-6">
              {/* Image Section */}
              <div className="md:col-span-1">
                <div className="relative h-96 w-full">
                  <Image
                    src={currentItem.image}
                    alt={currentItem.title || currentItem.description}
                    fill
                    className="object-cover"
                  />
                </div>
              </div>

              {/* Form Section */}
              <div className="p-8 bg-white">
                <div className="space-y-6">
                  {/* Title Field */}
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                      Title <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      id="title"
                      name="title"
                      className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 ease-in-out sm:text-sm"
                      value={currentItem.title}
                      onChange={handleChange}
                      required
                      placeholder="Enter item title"
                    />
                  </div>

                  {/* Description Field */}
                  <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      id="description"
                      name="description"
                      rows={3}
                      className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 ease-in-out sm:text-sm"
                      value={currentItem.description}
                      onChange={handleChange}
                      placeholder="Describe your item"
                    />
                  </div>

                  {/* Price and Condition Row */}
                  <div className="grid grid-cols-2 gap-4">
                    {/* Price Field */}
                    <div>
                      <label htmlFor="price" className="block text-sm font-medium text-gray-700 mb-1">
                        Price ($) <span className="text-red-400">*</span>
                      </label>
                      <div className="mt-1 relative rounded-md shadow-sm">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <DollarSign className="h-4 w-4 text-gray-400" />
                        </div>
                        <input
                          type="number"
                          id="price"
                          name="price"
                          min="0"
                          step="0.01"
                          className="block w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 ease-in-out sm:text-sm"
                          value={currentItem.price}
                          onChange={handleChange}
                          required
                        />
                      </div>
                    </div>

                    {/* Condition Field */}
                    <div>
                      <label htmlFor="condition" className="block text-sm font-medium text-gray-700 mb-1">
                        Condition <span className="text-red-400">*</span>
                      </label>
                      <select
                        id="condition"
                        name="condition"
                        className="mt-1 block w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 ease-in-out sm:text-sm"
                        value={currentItem.condition}
                        onChange={handleChange}
                        required
                      >
                        <option value="new">New</option>
                        <option value="like_new">Like New</option>
                        <option value="good">Good</option>
                        <option value="fair">Fair</option>
                        <option value="poor">Poor</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="px-8 py-4 bg-gray-50/50 flex items-center justify-between border-t border-gray-100">
              {!editMode && (
                <button
                  type="button"
                  onClick={handlePrevious}
                  disabled={currentIndex === 0}
                  className="inline-flex items-center px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 ease-in-out"
                >
                  <ChevronLeft className="h-5 w-5 mr-2" />
                  Previous
                </button>
              )}
              
              <div className="flex-1 flex justify-center">
                <button
                  type="submit"
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 ease-in-out transform hover:scale-105"
                >
                  {editMode ? 'Save Changes' : 'Submit Item'}
                </button>
              </div>

              {!editMode && currentIndex !== items.length - 1 && (
                <button
                  type="button"
                  onClick={handleNext}
                  className="inline-flex items-center px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 ease-in-out"
                >
                  Next
                  <ChevronRight className="h-5 w-5 ml-2" />
                </button>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </form>
    </div>
  )
}
