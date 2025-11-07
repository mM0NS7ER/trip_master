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
  register: (email: string, password: string, name: string) => Promise<void>;
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
      // TODO: 实现登录API调用
      // const response = await fetch('/api/auth/signin', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, password })
      // });
      // const data = await response.json();

      // 模拟登录成功
      const userData: User = {
        id: '1',
        email,
        name: email.split('@')[0],
      };

      setUser(userData);
      setIsAuthModalOpen(false);
    } catch (error) {
      setError('登录失败，请检查用户名和密码');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // TODO: 实现注册API调用
      // const response = await fetch('/api/auth/signup', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email, password, name })
      // });
      // const data = await response.json();

      // 模拟注册成功
      const userData: User = {
        id: '1',
        email,
        name,
      };

      setUser(userData);
      setIsAuthModalOpen(false);
    } catch (error) {
      setError('注册失败，邮箱可能已被使用');
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