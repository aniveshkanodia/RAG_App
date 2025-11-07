"use client"

import { Sidebar } from "@/components/sidebar"
import { HomeScreen } from "@/components/home-screen"

export default function Home() {
  return (
    <div className="flex h-screen bg-white">
      <Sidebar />
      <HomeScreen />
    </div>
  )
}

