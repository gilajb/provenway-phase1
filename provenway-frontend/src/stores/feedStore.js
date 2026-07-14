/**
 * src/stores/feedStore.js
 * ───────────────────────
 * Zustand store for the home feed.
 * Holds cursor state for infinite-scroll pagination.
 */
import { create } from "zustand";

const useFeedStore = create((set) => ({
  items: [],
  nextCursor: null,
  hasMore: true,

  appendItems: (newItems, nextCursor) =>
    set((state) => ({
      items: [...state.items, ...newItems],
      nextCursor,
      hasMore: !!nextCursor,
    })),

  prependItem: (item) =>
    set((state) => ({ items: [item, ...state.items] })),

  reset: () => set({ items: [], nextCursor: null, hasMore: true }),
}));

export default useFeedStore;
