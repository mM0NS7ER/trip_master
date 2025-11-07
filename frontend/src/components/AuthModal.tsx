import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuthStore } from '@/store/authStore.tsx';
import { toast } from 'react-hot-toast';

const AuthModal: React.FC = () => {
  const {
    isAuthModalOpen,
    isLoginMode,
    user,
    isLoading,
    error,
    closeAuthModal,
    toggleAuthMode,
    login,
    register,
    clearError,
  } = useAuthStore();

  // 表单状态
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // 当模态框关闭或切换模式时重置表单
  useEffect(() => {
    if (!isAuthModalOpen) {
      resetForm();
    }
  }, [isAuthModalOpen]);

  useEffect(() => {
    resetForm();
    clearError();
  }, [isLoginMode, clearError]);

  const resetForm = () => {
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setName('');
    setUsername('');
    setFormErrors({});
  };

  const validateForm = () => {
    const errors: Record<string, string> = {};

    if (!email) {
      errors.email = '请输入邮箱';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = '请输入有效的邮箱地址';
    }

    if (!password) {
      errors.password = '请输入密码';
    } else if (password.length < 6) {
      errors.password = '密码至少需要6个字符';
    } 

    if (!isLoginMode) {
      if (!name) {
        errors.name = '请输入姓名';
      }
      
      if (!username) {
        errors.username = '请输入用户名';
      } else if (username.length < 3) {
        errors.username = '用户名至少需要3个字符';
      }

      if (!confirmPassword) {
        errors.confirmPassword = '请确认密码';
      } else if (password !== confirmPassword) {
        errors.confirmPassword = '两次输入的密码不一致';
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (!validateForm()) return;

    try {
      if (isLoginMode) {
        await login(email, password);
        // 登录成功后显示成功消息
        toast.success('登录成功！欢迎回来');
      } else {
        await register(email, password, name, username);
        // 注册成功后显示成功消息
        toast.success('注册成功！欢迎加入Trip Master');
      }
    } catch (err) {
      // 错误已在store中处理，并显示在错误区域
      // 使用toast通知显示错误
      const errorMessage = err instanceof Error ? err.message : "操作失败，请稍后再试";
      toast.error(errorMessage);
      console.error("认证错误:", err);
    }
  };

  return (
    <Dialog open={isAuthModalOpen} onOpenChange={closeAuthModal}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isLoginMode ? '登录' : '注册'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLoginMode && (
            <>
              <div className="space-y-2">
                <Label htmlFor="name">姓名</Label>
                <Input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="请输入姓名"
                />
                {formErrors.name && (
                  <p className="text-sm text-red-500">{formErrors.name}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="username">用户名</Label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="请输入用户名"
                />
                {formErrors.username && (
                  <p className="text-sm text-red-500">{formErrors.username}</p>
                )}
              </div>
            </>
          )}

          <div className="space-y-2">
            <Label htmlFor="email">邮箱</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="请输入邮箱"
            />
            {formErrors.email && (
              <p className="text-sm text-red-500">{formErrors.email}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">密码</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
            />
            {formErrors.password && (
              <p className="text-sm text-red-500">{formErrors.password}</p>
            )}
          </div>

          {!isLoginMode && (
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">确认密码</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="请再次输入密码"
              />
              {formErrors.confirmPassword && (
                <p className="text-sm text-red-500">{formErrors.confirmPassword}</p>
              )}
            </div>
          )}

          {error && (
            <div className="p-3 text-sm text-red-700 bg-red-50 rounded-md border border-red-200">
              <div className="flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            </div>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? '处理中...' : isLoginMode ? '登录' : '注册'}
          </Button>

          <div className="text-center">
            <button
              type="button"
              className="text-sm text-blue-500 hover:underline"
              onClick={toggleAuthMode}
            >
              {isLoginMode ? '没有账号？点击注册' : '已有账号？点击登录'}
            </button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AuthModal;
