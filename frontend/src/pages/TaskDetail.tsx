import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { taskApi } from '../services/api';
import { Task } from '../types/task';
import { Layout } from '../components/Layout';
import './TaskDetail.css';

export const TaskDetail = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const [task, setTask] = useState<Task | null>(null);
  const [logs, setLogs] = useState('');
  const [showLogs, setShowLogs] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (taskId) {
      loadTask();
    }
  }, [taskId]);

  const loadTask = async () => {
    try {
      const data = await taskApi.getTask(taskId!);
      setTask(data);
    } catch (error) {
      console.error('加载任务失败', error);
    } finally {
      setLoading(false);
    }
  };

  const loadLogs = async () => {
    if (!taskId) return;
    setLoadingLogs(true);
    try {
      const data = await taskApi.getTaskLogs(taskId);
      setLogs(data.logs);
      setShowLogs(true);
    } catch (error) {
      console.error('加载日志失败', error);
    } finally {
      setLoadingLogs(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; className: string }> = {
      completed: { label: '已完成', className: 'badge-success' },
      running: { label: '运行中', className: 'badge-info' },
      failed: { label: '失败', className: 'badge-error' },
      pending: { label: '等待中', className: 'badge-warning' },
    };
    
    const statusInfo = statusMap[status] || { label: status, className: 'badge-gray' };
    return <span className={`badge ${statusInfo.className}`}>{statusInfo.label}</span>;
  };

  if (loading) {
    return (
      <Layout>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="text-muted">加载中...</p>
        </div>
      </Layout>
    );
  }

  if (!task) {
    return (
      <Layout>
        <div className="error-state fade-in">
          <div className="error-icon">⚠️</div>
          <h3>任务不存在</h3>
          <p className="text-muted">无法找到指定的任务</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            返回任务列表
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="task-detail-page fade-in">
        <div className="page-header">
          <div>
            <h1 className="page-title">{task.name}</h1>
            <p className="text-muted">任务详情和日志</p>
          </div>
          <div className="header-actions">
            <button onClick={() => navigate(-1)} className="btn-secondary">
              ← 返回
            </button>
            <button onClick={loadLogs} className="btn-primary" disabled={loadingLogs}>
              {loadingLogs ? (
                <>
                  <span className="loading-spinner"></span>
                  加载中...
                </>
              ) : (
                '📋 查看日志'
              )}
            </button>
          </div>
        </div>

        <div className="detail-grid">
          <div className="detail-card card">
            <h2 className="card-title">基本信息</h2>
            <div className="detail-list">
              <div className="detail-item">
                <span className="detail-label">状态</span>
                <span className="detail-value">{getStatusBadge(task.status)}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">模型名称</span>
                <span className="detail-value">{task.model_name}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">数据集路径</span>
                <span className="detail-value text-muted">{task.dataset_path}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">创建时间</span>
                <span className="detail-value text-muted">
                  {new Date(task.created_at).toLocaleString('zh-CN')}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">更新时间</span>
                <span className="detail-value text-muted">
                  {new Date(task.updated_at).toLocaleString('zh-CN')}
                </span>
              </div>
            </div>
          </div>

          <div className="detail-card card">
            <h2 className="card-title">训练参数</h2>
            <div className="detail-list">
              <div className="detail-item">
                <span className="detail-label">训练阶段</span>
                <span className="detail-value">{task.stage}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">训练轮数</span>
                <span className="detail-value">{task.epochs}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">学习率</span>
                <span className="detail-value">{task.learning_rate}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">批次大小</span>
                <span className="detail-value">{task.batch_size}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">梯度累积步数</span>
                <span className="detail-value">{task.gradient_accumulation_steps}</span>
              </div>
              {task.output_dir && (
                <div className="detail-item">
                  <span className="detail-label">输出目录</span>
                  <span className="detail-value text-muted font-mono">{task.output_dir}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {showLogs && (
          <div className="logs-card card slide-in">
            <div className="logs-header">
              <h2 className="card-title">任务日志</h2>
              <button
                onClick={() => setShowLogs(false)}
                className="btn-text btn-sm"
              >
                ✕ 关闭
              </button>
            </div>
            <div className="logs-content">
              <pre className="logs-text">{logs || '暂无日志'}</pre>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
