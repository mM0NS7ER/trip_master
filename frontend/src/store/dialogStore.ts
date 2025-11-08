import { create } from 'zustand';

interface DialogState {
  isDeleteConfirmOpen: boolean;
  chatIdToDelete: string | null;
  openDeleteConfirm: (id: string) => void;
  closeDeleteConfirm: () => void;
}

export const useDialogStore = create<DialogState>((set) => ({
  isDeleteConfirmOpen: false,
  chatIdToDelete: null,
  openDeleteConfirm: (id: string) => set({ isDeleteConfirmOpen: true, chatIdToDelete: id }),
  closeDeleteConfirm: () => set({ isDeleteConfirmOpen: false, chatIdToDelete: null }),
}));
