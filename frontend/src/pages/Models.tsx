import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fileApi } from '../services/api';
import { ModelFile } from '../types/file';
import { useAuth } from '../hooks/useAuth';

export const Models = () => {
  const [models, setModels] = useState<ModelFile[]>([]);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const data = await fileApi.getModels();
      setModels(data);
    } catch (error) {
      console.error('加载模型失败', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h1>模型管理</h1>
        <div>
          <span>欢迎，{user?.username}</span>
          <button onClick={logout} style={{ marginLeft: '10px' }}>退出</button>
        </div>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '10px' }}>任务列表</Link>
        <Link to="/submit-task" style={{ marginRight: '10px' }}>提交任务</Link>
        <Link to="/datasets" style={{ marginRight: '10px' }}>数据集</Link>
        <Link to="/chat">对话</Link>
      </div>
      {loading ? (
        <div>加载中...</div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>模型名称</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>模型路径</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>基础模型</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>创建时间</th>
            </tr>
          </thead>
          <tbody>
            {models.map((model) => (
              <tr key={model.model_id}>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{model.name}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{model.model_path}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{model.base_model_path || '-'}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {new Date(model.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {models.length === 0 && !loading && <div>暂无模型</div>}
    </div>
  );
};

