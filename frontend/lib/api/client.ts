/**
 * API client for RAG application backend.
 * Provides functions to interact with the FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Response types from the API
 */
export interface ChatResponse {
  answer: string;
  sources?: SourceInfo[];
}

export interface SourceInfo {
  content: string;
  metadata?: Record<string, any>;
}

export interface ChatError {
  detail: string;
}

export interface UploadResponse {
  message: string;
  chunks?: number;
}

export interface UploadError {
  detail: string;
}

/**
 * Checks if the backend server is available.
 * 
 * @returns Promise resolving to true if server is available, false otherwise
 */
export async function checkServerHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Sends a chat question to the backend and returns the answer.
 * 
 * @param question - The user's question
 * @param conversationId - Required conversation ID to track multi-turn conversations
 * @param turnIndex - Optional turn index within the conversation (0, 1, 2, ...)
 * @returns Promise resolving to the chat response with answer and sources
 * @throws Error if the request fails
 */
export async function chat(
  question: string,
  conversationId?: string,
  turnIndex?: number
): Promise<ChatResponse> {
  if (!question || !question.trim()) {
    throw new Error("Question cannot be empty");
  }

  // Validate conversationId is provided
  if (!conversationId) {
    throw new Error("Conversation ID is required");
  }

  try {
    const body: any = { 
      question: question.trim(),
      conversation_id: conversationId  // Always include since we validated it exists
    };
    
    // Always include turn_index if provided
    if (turnIndex !== undefined && turnIndex !== null) {
      body.turn_index = turnIndex;
    }

    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      // Try to parse error message from response
      let errorMessage = `Request failed with status ${response.status}`;
      try {
        const errorData: ChatError = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // If parsing fails, use default message
      }
      throw new Error(errorMessage);
    }

    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    // Handle network errors or other exceptions
    if (error instanceof Error) {
      // Check if it's a network error (fetch API throws "Failed to fetch" for network errors)
      if (error.message === "Failed to fetch" || error.message.includes("fetch")) {
        throw new Error("We're having trouble reaching the server — please try again later.");
      }
      throw error;
    }
    throw new Error("We're having trouble reaching the server — please try again later.");
  }
}

/**
 * Uploads a file to the backend for processing and indexing.
 * 
 * @param file - The file to upload
 * @returns Promise resolving to the upload response with message and chunk count
 * @throws Error if the request fails
 */
export async function uploadFile(file: File): Promise<UploadResponse> {
  if (!file) {
    throw new Error("No file provided");
  }

  // Validate file type
  const fileExt = file.name.split('.').pop()?.toLowerCase();
  const supportedExtensions = ['pdf', 'txt', 'docx', 'doc'];
  
  if (!fileExt || !supportedExtensions.includes(fileExt)) {
    throw new Error(`Unsupported file type: .${fileExt}. Supported types: ${supportedExtensions.join(', ')}`);
  }

  try {
    // Create FormData with the file
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      // Try to parse error message from response
      let errorMessage = `Request failed with status ${response.status}`;
      try {
        const errorData: UploadError = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // If parsing fails, use default message
      }
      throw new Error(errorMessage);
    }

    const data: UploadResponse = await response.json();
    return data;
  } catch (error) {
    // Handle network errors or other exceptions
    if (error instanceof Error) {
      // Check if it's a network error (fetch API throws "Failed to fetch" for network errors)
      if (error.message === "Failed to fetch" || error.message.includes("fetch")) {
        throw new Error("We're having trouble reaching the server — please try again later.");
      }
      throw error;
    }
    throw new Error("We're having trouble reaching the server — please try again later.");
  }
}

