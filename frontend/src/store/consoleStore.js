import { create } from 'zustand';

export const useConsoleStore = create((set) => ({
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  isPaletteOpen: false,
  togglePalette: () => set((state) => ({ isPaletteOpen: !state.isPaletteOpen })),
  activeTheme: 'dark',
  setTheme: (theme) => set({ activeTheme: theme }),
}));
