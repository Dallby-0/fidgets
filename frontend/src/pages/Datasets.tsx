import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fileApi } from '../services/api';
import { DatasetFile } from '../types/file';
import { useAuth } from '../hooks/useAuth';

export const Datasets = () => {
  const [datasets, setDatasets] = useState<DatasetFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const { user, logout } = useAuth();

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      const data = await fileApi.getDatasets();
      setDatasets(data);
    } catch (error) {
      console.error('加载数据集失败', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await fileApi.uploadDataset(file);
      await loadDatasets();
      alert('上传成功');
    } catch (error: any) {
      alert('上传失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (fileId: string) => {
    if (!confirm('确定要删除这个文件吗？')) return;
    try {
      await fileApi.deleteDataset(fileId);
      await loadDatasets();
    } catch (error: any) {
      alert('删除失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h1>数据集管理</h1>
        <div>
          <span>欢迎，{user?.username}</span>
          <button onClick={logout} style={{ marginLeft: '10px' }}>退出</button>
        </div>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '10px' }}>任务列表</Link>
        <Link to="/submit-task" style={{ marginRight: '10px' }}>提交任务</Link>
        <Link to="/models" style={{ marginRight: '10px' }}>模型</Link>
        <Link to="/chat">对话</Link>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <input
          type="file"
          onChange={handleFileUpload}
          disabled={uploading}
          accept=".json,.jsonl"
        />
        {uploading && <span>上传中...</span>}
      </div>
      {loading ? (
        <div>加载中...</div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>文件名</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>大小</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>上传时间</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((dataset) => (
              <tr key={dataset.file_id}>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{dataset.filename}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{formatSize(dataset.size)}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {new Date(dataset.created_at).toLocaleString()}
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  <button onClick={() => handleDelete(dataset.file_id)}>删除</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {datasets.length === 0 && !loading && <div>暂无数据集</div>}
    </div>
  );
};

