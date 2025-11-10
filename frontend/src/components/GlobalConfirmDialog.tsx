import React from 'react';
import { Button } from '@/components/ui/button';
import { useDialogStore } from '@/store/dialogStore';
import { toast } from 'react-hot-toast';
import { useChatStore } from '@/store/chatStore';
import { apiDelete } from '@/utils/api';

const GlobalConfirmDialog = () => {
  const { isDeleteConfirmOpen, chatIdToDelete, closeDeleteConfirm } = useDialogStore();
  const { removeChat } = useChatStore();

  const confirmDeleteChat = async () => {
    if (!chatIdToDelete) return;

    try {
      const token = localStorage.getItem('token');

      if (!token) {
        toast.error('用户未登录，无法删除聊天记录');
        closeDeleteConfirm();
        return;
      }

      // 显示加载提示
      toast.loading('正在删除会话...', { id: 'delete-chat' });

      const response = await apiDelete(`/chats/${chatIdToDelete}`);

      if (!response.ok) {
        throw new Error('删除聊天记录失败');
      }

      // 显示成功提示
      toast.success('会话已永久删除', { id: 'delete-chat' });

      // 更新聊天列表状态
      removeChat(chatIdToDelete);
    } catch (error) {
      console.error('删除聊天记录失败:', error);
      // 显示错误提示
      toast.error('删除失败，请稍后再试', { id: 'delete-chat' });
    } finally {
      // 无论成功或失败，都关闭确认对话框
      closeDeleteConfirm();
    }
  };

  if (!isDeleteConfirmOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center">
      {/* 背景遮罩 */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={closeDeleteConfirm}
      />

      {/* 对话框内容 */}
      <div className="relative z-[10000] bg-white rounded-lg shadow-xl p-6 max-w-md mx-4 transform transition-all">
        <h3 className="text-lg font-semibold mb-2">删除会话</h3>
        <p className="text-gray-600 mb-6">确定要删除此会话吗？删除后将无法恢复。</p>

        <div className="flex justify-end space-x-3">
          <Button 
            variant="outline" 
            onClick={closeDeleteConfirm}
            className="px-4"
          >
            取消
          </Button>
          <Button 
            variant="destructive" 
            onClick={confirmDeleteChat}
            className="px-4"
          >
            删除
          </Button>
        </div>
      </div>
    </div>
  );
};

export default GlobalConfirmDialog;
