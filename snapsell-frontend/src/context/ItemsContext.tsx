'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { createClient } from '@supabase/supabase-js'
import { Item } from '../types/item'

interface ItemsContextType {
  items: Item[]
  loading: boolean
  error: Error | null
  refreshItems: () => Promise<void>
}

const ItemsContext = createContext<ItemsContextType | undefined>(undefined)

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export function ItemsProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<Item[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchItems = async () => {
    try {
      setLoading(true)
      const { data, error: supabaseError } = await supabase
        .from('items')
        .select('*')
        .eq('user_id', process.env.NEXT_PUBLIC_USER_ID)
        .order('created_at', { ascending: false })

      if (supabaseError) throw supabaseError

      setItems(data || [])
    } catch (e) {
      setError(e instanceof Error ? e : new Error('Failed to fetch items'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchItems()
  }, [])

  return (
    <ItemsContext.Provider value={{ items, loading, error, refreshItems: fetchItems }}>
      {children}
    </ItemsContext.Provider>
  )
}

export function useItems() {
  const context = useContext(ItemsContext)
  if (context === undefined) {
    throw new Error('useItems must be used within an ItemsProvider')
  }
  return context
}
