'use client'

import { useState } from 'react'
import { createClient } from '@supabase/supabase-js'
import { Upload, X } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useItems } from '../context/ItemsContext'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
const supabase = createClient(supabaseUrl, supabaseKey)

interface VideoUploadProps {
  onUploadComplete?: (url: string) => void
}

export function VideoUpload({ onUploadComplete }: VideoUploadProps) {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const { confirmItems, updateConfirmItems } = useItems()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) {
      setFile(null)
      return
    }

    const selectedFile = e.target.files[0]
    
    // Validate file type
    if (!selectedFile.type.startsWith('video/')) {
      setError('Please select a valid video file')
      return
    }

    setFile(selectedFile)
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a video file')
      return
    }

    try {
      setUploading(true)
      setProgress(0)

      // Make API request to process video
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/process_video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_url: file.name, // You might want to pass more info about the video
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Video processing response:', data.data);

      if (onUploadComplete) {
        onUploadComplete(data.url || '');
      }

      await updateConfirmItems(data.data || [])

      console.log("Confirm items:", confirmItems)

      // Navigate after successful processing
      router.push('/confirm-items');

    } catch (error) {
      console.error('Error processing video:', error);
      setError('Failed to process video. Please try again.');
    } finally {
      setUploading(false);
    }
  }

  const clearFile = () => {
    setFile(null)
    setError(null)
    setProgress(0)
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-6 hover:border-gray-400 transition-colors">
          <input
            type="file"
            onChange={handleFileChange}
            accept="video/*"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={uploading}
          />
          <div className="text-center">
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-2">
              {file ? (
                <div className="flex items-center justify-center space-x-2">
                  <span className="text-sm text-gray-600">{file.name}</span>
                  <button
                    type="button"
                    onClick={clearFile}
                    className="text-red-500 hover:text-red-700"
                    disabled={uploading}
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <p className="text-gray-500">
                  Drag and drop a video or click to select
                </p>
              )}
            </div>
          </div>
        </div>

        {error && (
          <div className="text-red-500 text-sm text-center">{error}</div>
        )}

        {uploading && (
          <div className="space-y-2">
            <div className="h-2 bg-gray-200 rounded-full">
              <div
                className="h-2 bg-blue-600 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-sm text-gray-600 text-center">
              Uploading... {progress}%
            </p>
          </div>
        )}

        <button
          type="submit"
          disabled={!file || uploading}
          className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {uploading ? 'Uploading...' : 'Upload Video'}
        </button>
      </form>
    </div>
  )
}

export default VideoUpload