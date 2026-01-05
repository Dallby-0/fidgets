import axios from 'axios';
import { Task, TaskCreate } from '../types/task';
import { DatasetFile, ModelFile } from '../types/file';
import { ChatRequest, ChatResponse } from '../types/chat';

const API_BASE_URL = '/api';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
});

// 请求拦截器：添加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const taskApi = {
  async createTask(taskData: TaskCreate): Promise<Task> {
    const response = await api.post<Task>('/tasks', taskData);
    return response.data;
  },

  async getTasks(): Promise<Task[]> {
    const response = await api.get<Task[]>('/tasks');
    return response.data;
  },

  async getTask(taskId: string): Promise<Task> {
    const response = await api.get<Task>(`/tasks/${taskId}`);
    return response.data;
  },

  async getTaskLogs(taskId: string): Promise<{ logs: string }> {
    const response = await api.get<{ logs: string }>(`/tasks/${taskId}/logs`);
    return response.data;
  },
};

export const fileApi = {
  async uploadDataset(file: File): Promise<DatasetFile> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<DatasetFile>('/files/datasets', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async getDatasets(): Promise<DatasetFile[]> {
    const response = await api.get<DatasetFile[]>('/files/datasets');
    return response.data;
  },

  async deleteDataset(fileId: string): Promise<void> {
    await api.delete(`/files/datasets/${fileId}`);
  },

  async generateDataset(topic: string, filename?: string): Promise<DatasetFile> {
    const response = await api.post<DatasetFile>('/files/datasets/generate', {
      topic,
      filename,
    });
    return response.data;
  },

  async getModels(): Promise<ModelFile[]> {
    const response = await api.get<ModelFile[]>('/files/models');
    return response.data;
  },

  async getAvailableModels(): Promise<ModelFile[]> {
    const response = await api.get<ModelFile[]>('/files/models/available');
    return response.data;
  },
};

export const chatApi = {
  async completion(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat/completion', request);
    return response.data;
  },
};

