import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fileApi } from '../services/api';
import { DatasetFile } from '../types/file';
import { useAuth } from '../hooks/useAuth';

export const Datasets = () => {
  const [datasets, setDatasets] = useState<DatasetFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [topic, setTopic] = useState('');
  const [filename, setFilename] = useState('');
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

  const handleGenerateDataset = async () => {
    if (!topic.trim()) {
      alert('请输入话题');
      return;
    }

    setGenerating(true);
    try {
      await fileApi.generateDataset(topic.trim(), filename.trim() || undefined);
      await loadDatasets();
      alert('数据集生成成功！');
      setShowGenerateForm(false);
      setTopic('');
      setFilename('');
    } catch (error: any) {
      alert('生成失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setGenerating(false);
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
      <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
        <div>
          <input
            type="file"
            onChange={handleFileUpload}
            disabled={uploading}
            accept=".json,.jsonl"
            style={{ marginRight: '10px' }}
          />
          {uploading && <span>上传中...</span>}
        </div>
        <div>
          <button
            onClick={() => setShowGenerateForm(!showGenerateForm)}
            style={{
              padding: '8px 16px',
              backgroundColor: '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            {showGenerateForm ? '取消生成' : 'AI生成数据集'}
          </button>
        </div>
      </div>

      {showGenerateForm && (
        <div
          style={{
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '20px',
            backgroundColor: '#f9f9f9',
          }}
        >
          <h3 style={{ marginTop: 0 }}>AI生成数据集</h3>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              话题 <span style={{ color: 'red' }}>*</span>
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="例如：vibe coding、Python编程、机器学习"
              disabled={generating}
              style={{
                width: '100%',
                maxWidth: '500px',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px',
              }}
            />
            <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
              输入你想要生成数据集的话题，AI将自动生成30条高质量问答对
            </div>
          </div>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              文件名（可选）
            </label>
            <input
              type="text"
              value={filename}
              onChange={(e) => setFilename(e.target.value)}
              placeholder="留空则使用话题前10个字符"
              disabled={generating}
              style={{
                width: '100%',
                maxWidth: '500px',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px',
              }}
            />
            <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
              如果不指定文件名，将自动使用话题的前10个字符作为文件名
            </div>
          </div>
          <div>
            <button
              onClick={handleGenerateDataset}
              disabled={generating || !topic.trim()}
              style={{
                padding: '10px 20px',
                backgroundColor: generating ? '#ccc' : '#2196F3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: generating ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: 'bold',
              }}
            >
              {generating ? '生成中...' : '开始生成'}
            </button>
            {generating && (
              <span style={{ marginLeft: '10px', color: '#666' }}>
                正在调用AI生成数据集，请稍候...
              </span>
            )}
          </div>
        </div>
      )}
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

