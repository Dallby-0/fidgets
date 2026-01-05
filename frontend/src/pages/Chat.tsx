import { useEffect, useState, useRef } from 'react';
import { fileApi, chatApi } from '../services/api';
import { ModelFile } from '../types/file';
import { ChatMessage } from '../types/chat';
import { Layout } from '../components/Layout';
import './Chat.css';

export const Chat = () => {
  const [models, setModels] = useState<ModelFile[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    loadModels();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const loadModels = async () => {
    try {
      const data = await fileApi.getAvailableModels();
      setModels(data);
      if (data.length > 0) {
        setSelectedModel(data[0].model_path);
      }
    } catch (error) {
      console.error('加载模型失败', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedModel || loading) return;

    const userMessage: ChatMessage = { role: 'user', content: inputMessage };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setLoading(true);

    // 自动调整文本框高度
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      const response = await chatApi.completion({
        model_path: selectedModel,
        messages: newMessages,
      });
      setMessages([...newMessages, response]);
    } catch (error: any) {
      alert('发送消息失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const adjustTextareaHeight = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
  };

  return (
    <Layout>
      <div className="chat-page fade-in">
        <div className="chat-header">
          <div>
            <h1 className="page-title">AI 对话</h1>
            <p className="text-muted">与 AI 模型进行对话交流</p>
          </div>
          <div className="chat-controls">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="model-select"
              disabled={loading}
            >
              {models.map((model) => (
                <option key={model.model_id} value={model.model_path}>
                  {model.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="chat-container card">
          <div className="messages-area" id="messages-area">
            {messages.length === 0 ? (
              <div className="empty-chat">
                <div className="empty-chat-icon">💬</div>
                <h3>开始对话</h3>
                <p className="text-muted">选择模型后，在下方输入消息开始对话</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  className={`message ${msg.role === 'user' ? 'message-user' : 'message-assistant'} slide-in`}
                  style={{ animationDelay: `${index * 30}ms` }}
                >
                  <div className="message-avatar">
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{msg.content}</div>
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="message message-assistant loading-message">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-area">
            <div className="input-wrapper">
              <textarea
                ref={textareaRef}
                value={inputMessage}
                onChange={(e) => {
                  setInputMessage(e.target.value);
                  adjustTextareaHeight(e);
                }}
                onKeyDown={handleKeyDown}
                placeholder="输入消息... (Shift + Enter 换行)"
                className="chat-input"
                rows={1}
                disabled={loading || !selectedModel}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !selectedModel || !inputMessage.trim()}
                className="btn-primary send-button"
                title="发送 (Enter)"
              >
                {loading ? (
                  <span className="loading-spinner"></span>
                ) : (
                  '📤'
                )}
              </button>
            </div>
            <div className="input-hint">
              {!selectedModel && (
                <span className="text-muted">请先选择一个模型</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};
