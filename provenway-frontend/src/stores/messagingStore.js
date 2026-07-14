/**
 * src/stores/messagingStore.js
 * ────────────────────────────
 * Zustand store for messaging. Holds active conversation and messages.
 */
import { create } from "zustand";

const useMessagingStore = create((set) => ({
  conversations: [],
  activeConversationId: null,
  messagesByConversation: {},

  setConversations: (conversations) => set({ conversations }),

  setActiveConversation: (id) => set({ activeConversationId: id }),

  setMessages: (conversationId, messages) =>
    set((state) => ({
      messagesByConversation: {
        ...state.messagesByConversation,
        [conversationId]: messages,
      },
    })),

  appendMessage: (conversationId, message) =>
    set((state) => {
      const existing = state.messagesByConversation[conversationId] ?? [];
      return {
        messagesByConversation: {
          ...state.messagesByConversation,
          [conversationId]: [...existing, message],
        },
      };
    }),
}));

export default useMessagingStore;
