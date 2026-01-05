import { useState, useEffect } from 'react';
import { User } from '../types/user';
import { authService } from '../services/auth';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = authService.getToken();
      if (token) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
        } catch (error) {
          authService.logout();
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = (token: string, userData: User) => {
    authService.setToken(token, userData);
    setUser(userData);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return { user, loading, login, logout };
};

