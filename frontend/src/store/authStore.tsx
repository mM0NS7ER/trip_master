import React, { createContext, useContext, useState, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  age?: number;
  bio?: string;
  isGuest?: boolean;
}

interface AuthContextType {
  isAuthModalOpen: boolean;
  isLoginMode: boolean;
  user: User | null;
  isLoading: boolean;
  error: string | null;
  openAuthModal: () => void;
  closeAuthModal: () => void;
  toggleAuthMode: () => void;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string,username: string) => Promise<void>;
  logout: () => void;
  guestLogin: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const openAuthModal = () => setIsAuthModalOpen(true);
  const closeAuthModal = () => setIsAuthModalOpen(false);
  const toggleAuthMode = () => setIsLoginMode(!isLoginMode);
  const clearError = () => setError(null);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/auth/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        let errorMessage = '登录失败';

        try {
          const errorData = await response.json();
          console.log("登录错误响应:", errorData);

          // 处理新的错误码格式
          if (errorData.detail && errorData.detail.code && errorData.detail.message) {
            errorMessage = errorData.detail.message;
          }
          // 兼容旧的错误格式
          else if (response.status === 401) {
            errorMessage = '用户名或密码错误，请检查您的输入';
          } else if (response.status === 400) {
            errorMessage = errorData.detail || '请求参数错误';
          } else if (response.status >= 500) {
            errorMessage = '服务器错误，请稍后再试';
          }
        } catch (e) {
          // 如果解析错误响应失败，使用默认错误消息
          console.error("解析错误响应失败:", e);
          errorMessage = `登录失败 (${response.status})`;
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();
      const userData: User = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        avatar: data.user.avatar_url,
        age: data.user.age,
        bio: data.user.bio,
        isGuest: data.user.is_guest
      };

      // 存储令牌到本地存储
      localStorage.setItem('token', data.token);

      setUser(userData);
      setIsAuthModalOpen(false);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '登录失败，请检查用户名和密码';
      setError(errorMessage);
      console.error("登录错误:", errorMessage);
      // 确保错误被传播到调用方
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string, username: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name, username })
      });

      if (!response.ok) {
        let errorMessage = '注册失败';

        try {
          const errorData = await response.json();
          console.log("注册错误响应:", errorData);

          // 处理新的错误码格式
          if (errorData.detail && errorData.detail.code && errorData.detail.message) {
            // 根据错误码添加更具体的提示
            if (errorData.detail.code === 'EMAIL_ALREADY_EXISTS') {
              errorMessage = errorData.detail.message;
            } else if (errorData.detail.code === 'USERNAME_ALREADY_EXISTS') {
              errorMessage = errorData.detail.message;
            } else if (errorData.detail.code === 'WEAK_PASSWORD') {
              errorMessage = errorData.detail.message;
            } else {
              errorMessage = errorData.detail.message;
            }
          }
          // 兼容旧的错误格式
          else if (response.status === 400) {
            if (errorData.detail === '邮箱已被使用') {
              errorMessage = '该邮箱已被注册，请使用其他邮箱或尝试登录';
            } else if (errorData.detail === '用户名已被使用') {
              errorMessage = '该用户名已被使用，请选择其他用户名';
            } else {
              errorMessage = errorData.detail || '请求参数错误';
            }
          } else if (response.status >= 500) {
            errorMessage = '服务器错误，请稍后再试';
          }
        } catch (e) {
          // 如果解析错误响应失败，使用默认错误消息
          console.error("解析错误响应失败:", e);
          errorMessage = `注册失败 (${response.status})`;
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();
      const userData: User = {
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        avatar: data.user.avatar_url,
        age: data.user.age,
        bio: data.user.bio,
        isGuest: data.user.is_guest
      };

      // 存储令牌到本地存储
      localStorage.setItem('token', data.token);

      setUser(userData);
      setIsAuthModalOpen(false);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '注册失败，邮箱可能已被使用';
      setError(errorMessage);
      console.error("注册错误:", errorMessage);
      // 确保错误被传播到调用方
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => setUser(null);

  const guestLogin = () => {
    const guestUser: User = {
      id: `guest-${Date.now()}`,
      email: 'guest@example.com',
      name: '访客用户',
      age: 18,
      bio: '这是一个访客账户，部分功能受限',
      isGuest: true
    };

    setUser(guestUser);
    setIsAuthModalOpen(false);
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthModalOpen,
        isLoginMode,
        user,
        isLoading,
        error,
        openAuthModal,
        closeAuthModal,
        toggleAuthMode,
        login,
        register,
        logout,
        guestLogin,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthStore = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthStore must be used within an AuthProvider');
  }
  return context;
};
