import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fileApi, chatApi } from '../services/api';
import { ModelFile } from '../types/file';
import { ChatMessage } from '../types/chat';
import { useAuth } from '../hooks/useAuth';

export const Chat = () => {
  const [models, setModels] = useState<ModelFile[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const { user, logout } = useAuth();

  useEffect(() => {
    loadModels();
  }, []);

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

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedModel || loading) return;

    const userMessage: ChatMessage = { role: 'user', content: inputMessage };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputMessage('');
    setLoading(true);

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

  const clearMessages = () => {
    setMessages([]);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h1>对话</h1>
        <div>
          <span>欢迎，{user?.username}</span>
          <button onClick={logout} style={{ marginLeft: '10px' }}>退出</button>
        </div>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '10px' }}>任务列表</Link>
        <Link to="/submit-task" style={{ marginRight: '10px' }}>提交任务</Link>
        <Link to="/datasets" style={{ marginRight: '10px' }}>数据集</Link>
        <Link to="/models">模型</Link>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <label>选择模型：</label>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          style={{ padding: '5px', minWidth: '300px' }}
        >
          {models.map((model) => (
            <option key={model.model_id} value={model.model_path}>
              {model.name}
            </option>
          ))}
        </select>
        <button onClick={clearMessages} style={{ marginLeft: '10px' }}>清空对话</button>
      </div>
      <div
        style={{
          border: '1px solid #ddd',
          height: '500px',
          overflowY: 'auto',
          padding: '10px',
          marginBottom: '20px',
          backgroundColor: '#f9f9f9',
        }}
      >
        {messages.length === 0 && <div>开始对话吧...</div>}
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              marginBottom: '10px',
              textAlign: msg.role === 'user' ? 'right' : 'left',
            }}
          >
            <div
              style={{
                display: 'inline-block',
                padding: '10px',
                borderRadius: '5px',
                backgroundColor: msg.role === 'user' ? '#007bff' : '#e9ecef',
                color: msg.role === 'user' ? 'white' : 'black',
                maxWidth: '70%',
              }}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && <div>AI正在思考...</div>}
      </div>
      <div style={{ display: 'flex' }}>
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="输入消息..."
          style={{ flex: 1, padding: '10px', minHeight: '80px' }}
          disabled={loading || !selectedModel}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !selectedModel || !inputMessage.trim()}
          style={{ marginLeft: '10px', padding: '10px 20px' }}
        >
          发送
        </button>
      </div>
    </div>
  );
};

