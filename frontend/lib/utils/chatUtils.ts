export interface ChatSession {
  id: string
  title: string // First message or "New Chat"
  createdAt: number
  updatedAt: number
  messages: Message[]
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: number
}

const CHAT_STORAGE_KEY = "rag_chat_sessions"

/**
 * Generate a unique chat ID using crypto.randomUUID() or fallback to timestamp
 */
export function generateChatId(): string {
  if (typeof window !== "undefined" && window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID()
  }
  // Fallback to timestamp-based ID
  return `chat-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
}

/**
 * Get all chat sessions from localStorage
 */
export function getChatSessions(): ChatSession[] {
  if (typeof window === "undefined") return []
  
  try {
    const stored = localStorage.getItem(CHAT_STORAGE_KEY)
    if (!stored) return []
    return JSON.parse(stored) as ChatSession[]
  } catch (error) {
    console.error("Error reading chat sessions from localStorage:", error)
    return []
  }
}

/**
 * Save chat sessions to localStorage
 */
export function saveChatSessions(sessions: ChatSession[]): void {
  if (typeof window === "undefined") return
  
  try {
    localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(sessions))
  } catch (error) {
    console.error("Error saving chat sessions to localStorage:", error)
  }
}

/**
 * Get a specific chat session by ID
 */
export function getChatSession(chatId: string): ChatSession | null {
  const sessions = getChatSessions()
  return sessions.find((session) => session.id === chatId) || null
}

/**
 * Create a new chat session
 */
export function createChatSession(): ChatSession {
  const newSession: ChatSession = {
    id: generateChatId(),
    title: "New Chat",
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messages: [],
  }
  
  const sessions = getChatSessions()
  sessions.unshift(newSession) // Add to beginning
  saveChatSessions(sessions)
  
  return newSession
}

/**
 * Update a chat session
 */
export function updateChatSession(chatId: string, updates: Partial<ChatSession>): void {
  const sessions = getChatSessions()
  const index = sessions.findIndex((session) => session.id === chatId)
  
  if (index !== -1) {
    sessions[index] = {
      ...sessions[index],
      ...updates,
      updatedAt: Date.now(),
    }
    saveChatSessions(sessions)
  }
}

/**
 * Add a message to a chat session
 */
export function addMessageToChat(chatId: string, message: Message): void {
  const sessions = getChatSessions()
  const index = sessions.findIndex((session) => session.id === chatId)
  
  if (index !== -1) {
    sessions[index].messages.push(message)
    
    // Update title if it's the first user message
    if (sessions[index].title === "New Chat" && message.role === "user") {
      sessions[index].title = message.content.substring(0, 50) || "New Chat"
    }
    
    sessions[index].updatedAt = Date.now()
    saveChatSessions(sessions)
  }
}

/**
 * Delete a chat session
 */
export function deleteChatSession(chatId: string): void {
  const sessions = getChatSessions()
  const filtered = sessions.filter((session) => session.id !== chatId)
  saveChatSessions(filtered)
}

