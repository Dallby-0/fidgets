import { useEffect, useState } from 'react';
import { fileApi } from '../services/api';
import { DatasetFile } from '../types/file';
import { Layout } from '../components/Layout';
import './Datasets.css';

export const Datasets = () => {
  const [datasets, setDatasets] = useState<DatasetFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [topic, setTopic] = useState('');
  const [filename, setFilename] = useState('');

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
    <Layout>
      <div className="datasets-page fade-in">
        <div className="page-header">
          <div>
            <h1 className="page-title">数据集管理</h1>
            <p className="text-muted">管理和上传您的训练数据集</p>
          </div>
        </div>

        <div className="action-bar">
          <label className="file-upload-label">
            <input
              type="file"
              onChange={handleFileUpload}
              disabled={uploading}
              accept=".json,.jsonl"
              className="file-input"
            />
            <span className="btn-secondary">
              {uploading ? (
                <>
                  <span className="loading-spinner"></span>
                  上传中...
                </>
              ) : (
                <>
                  📁 上传文件
                </>
              )}
            </span>
          </label>
          <button
            onClick={() => setShowGenerateForm(!showGenerateForm)}
            className={`btn-primary ${showGenerateForm ? 'active' : ''}`}
          >
            {showGenerateForm ? '✕ 取消生成' : '✨ AI生成数据集'}
          </button>
        </div>

        {showGenerateForm && (
          <div className="generate-form card slide-in">
            <h3>AI生成数据集</h3>
            <p className="text-muted form-description">
              AI将根据您提供的话题自动生成30条高质量的问答对
            </p>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="topic">
                  话题 <span className="required">*</span>
                </label>
                <input
                  id="topic"
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="例如：vibe coding、Python编程、机器学习"
                  disabled={generating}
                />
                <small className="form-hint">输入你想要生成数据集的话题</small>
              </div>
              <div className="form-group">
                <label htmlFor="filename">文件名（可选）</label>
                <input
                  id="filename"
                  type="text"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  placeholder="留空则使用话题前10个字符"
                  disabled={generating}
                />
                <small className="form-hint">如果不指定文件名，将自动使用话题的前10个字符</small>
              </div>
            </div>
            <div className="form-actions">
              <button
                onClick={handleGenerateDataset}
                disabled={generating || !topic.trim()}
                className="btn-primary"
              >
                {generating ? (
                  <>
                    <span className="loading-spinner"></span>
                    生成中...
                  </>
                ) : (
                  '🚀 开始生成'
                )}
              </button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p className="text-muted">加载中...</p>
          </div>
        ) : datasets.length === 0 ? (
          <div className="empty-state fade-in">
            <div className="empty-icon">📊</div>
            <h3>暂无数据集</h3>
            <p className="text-muted">上传文件或使用AI生成数据集</p>
          </div>
        ) : (
          <div className="table-container fade-in">
            <div className="card">
              <table className="datasets-table">
                <thead>
                  <tr>
                    <th>文件名</th>
                    <th>大小</th>
                    <th>上传时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {datasets.map((dataset, index) => (
                    <tr key={dataset.file_id} className="slide-in" style={{ animationDelay: `${index * 50}ms` }}>
                      <td>
                        <div className="file-name">
                          <span className="file-icon">📄</span>
                          {dataset.filename}
                        </div>
                      </td>
                      <td className="text-muted">{formatSize(dataset.size)}</td>
                      <td className="text-muted">
                        {new Date(dataset.created_at).toLocaleString('zh-CN')}
                      </td>
                      <td>
                        <button
                          onClick={() => handleDelete(dataset.file_id)}
                          className="btn-danger btn-sm"
                        >
                          删除
                        </button>
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
