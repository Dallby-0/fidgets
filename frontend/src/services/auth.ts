import axios from 'axios';
import { UserLogin, UserRegister, Token, User } from '../types/user';

const API_BASE_URL = '/api';

export const authService = {
  async register(userData: UserRegister): Promise<void> {
    await axios.post(`${API_BASE_URL}/auth/register`, userData);
  },

  async login(credentials: UserLogin): Promise<Token> {
    const response = await axios.post<Token>(`${API_BASE_URL}/auth/login`, credentials);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const token = localStorage.getItem('token');
    const response = await axios.get<User>(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getToken(): string | null {
    return localStorage.getItem('token');
  },

  setToken(token: string, user: User): void {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  },

  getUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};

