export interface Item {
  id: string  // Changed to string since we're using UUID from Supabase
  user_id: string
  image_url?: string | null
  title: string
  description: string
  price: number
  condition: string
  status: string
  created_at?: string
  updated_at?: string
}

export type ItemStatus = 'active' | 'sold' | 'negotiating' | 'scheduled'

