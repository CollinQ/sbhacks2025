'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const tabs = [
  { name: 'Dashboard', href: '/' },
  { name: 'Inventory', href: '/inventory' },
  { name: 'Calendar', href: '/calendar' },
]

export function Tabs() {
  const pathname = usePathname()

  return (
    <div className="border-b border-gray-200 overflow-x-auto">
      <nav className="-mb-px flex space-x-8" aria-label="Tabs">
        {tabs.map((tab) => (
          <Link
            key={tab.name}
            href={tab.href}
            className={`
              whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
              ${pathname === tab.href
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }
            `}
          >
            {tab.name}
          </Link>
        ))}
      </nav>
    </div>
  )
}

