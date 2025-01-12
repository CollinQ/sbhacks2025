'use client'
import { ItemStatusCard } from '../components/ItemStatusCard'
import VideoUpload from '../components/VideoUpload'
import { useItems } from '../context/ItemsContext'
import { useEffect, useState } from 'react'
import { Facebook, Loader2 } from 'lucide-react'
import { postItemsToFacebookMarketplace } from '../utils/facebook'
import { toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'

export default function Home() {
  const { items, loading, refreshItems } = useItems()
  const [isPosting, setIsPosting] = useState(false)

  useEffect(() => {
    refreshItems()
  }, [])

  const handlePostToFacebook = async () => {
    try {
      setIsPosting(true)
      await postItemsToFacebookMarketplace(items);
      // Refresh items after posting
      refreshItems();
      // Show success toast
      toast.success('All listings have been posted to Facebook Marketplace');
    } catch (error) {
      console.error('Failed to post to Facebook Marketplace:', error);
      toast.error('Failed to post listings to Facebook Marketplace');
    } finally {
      setIsPosting(false)
    }
  };

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Upload New Inventory</h2>
        <VideoUpload />
      </div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-semibold">Current Inventory Status</h2>
        <button
          onClick={handlePostToFacebook}
          disabled={isPosting}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-[#1877F2] hover:bg-[#166fe0] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1877F2] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isPosting ? (
            <Loader2 className="w-5 h-5 mr-2 animate-spin" />
          ) : (
            <Facebook className="w-5 h-5 mr-2" />
          )}
          {isPosting ? 'Posting...' : 'Post to Facebook Marketplace'}
        </button>
      </div>
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
