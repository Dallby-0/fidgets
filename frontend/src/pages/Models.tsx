import { useEffect, useState } from 'react';
import { fileApi } from '../services/api';
import { ModelFile } from '../types/file';
import { Layout } from '../components/Layout';
import './Models.css';

export const Models = () => {
  const [models, setModels] = useState<ModelFile[]>([]);
  const [loading, setLoading] = useState(true);

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
    <Layout>
      <div className="models-page fade-in">
        <div className="page-header">
          <div>
            <h1 className="page-title">模型管理</h1>
            <p className="text-muted">查看和管理您的AI模型</p>
          </div>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p className="text-muted">加载中...</p>
          </div>
        ) : models.length === 0 ? (
          <div className="empty-state fade-in">
            <div className="empty-icon">🤖</div>
            <h3>暂无模型</h3>
            <p className="text-muted">当前没有可用的模型</p>
          </div>
        ) : (
          <div className="table-container fade-in">
            <div className="card">
              <table className="models-table">
                <thead>
                  <tr>
                    <th>模型名称</th>
                    <th>模型路径</th>
                    <th>基础模型</th>
                    <th>创建时间</th>
                  </tr>
                </thead>
                <tbody>
                  {models.map((model, index) => (
                    <tr key={model.model_id} className="slide-in" style={{ animationDelay: `${index * 50}ms` }}>
                      <td>
                        <div className="model-name">
                          <span className="model-icon">🤖</span>
                          {model.name}
                        </div>
                      </td>
                      <td className="text-muted model-path">{model.model_path}</td>
                      <td className="text-muted">
                        {model.base_model_path || <span className="text-tertiary">-</span>}
                      </td>
                      <td className="text-muted">
                        {new Date(model.created_at).toLocaleString('zh-CN')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
