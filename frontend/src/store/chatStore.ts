import { create } from 'zustand';

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
  userId: string;
}

interface ChatState {
  chats: Chat[];
  setChats: (chats: Chat[]) => void;
  addChat: (chat: Chat) => void;
  removeChat: (id: string) => void;
  updateChat: (id: string, updatedChat: Partial<Chat>) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  chats: [],
  setChats: (chats) => set({ chats }),
  addChat: (chat) => set((state) => ({ chats: [...state.chats, chat] })),
  removeChat: (id) => set((state) => ({ chats: state.chats.filter((chat) => chat.id !== id) })),
  updateChat: (id, updatedChat) =>
    set((state) => ({
      chats: state.chats.map((chat) => (chat.id === id ? { ...chat, ...updatedChat } : chat)),
    })),
}));
