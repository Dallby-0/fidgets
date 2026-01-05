import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { taskApi } from '../services/api';
import { Task } from '../types/task';
import { useAuth } from '../hooks/useAuth';

export const TaskDetail = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const [task, setTask] = useState<Task | null>(null);
  const [logs, setLogs] = useState('');
  const [showLogs, setShowLogs] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { user, logout } = useAuth();

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
    try {
      const data = await taskApi.getTaskLogs(taskId);
      setLogs(data.logs);
      setShowLogs(true);
    } catch (error) {
      console.error('加载日志失败', error);
    }
  };

  if (loading) return <div>加载中...</div>;
  if (!task) return <div>任务不存在</div>;

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h1>任务详情</h1>
        <div>
          <span>欢迎，{user?.username}</span>
          <button onClick={logout} style={{ marginLeft: '10px' }}>退出</button>
        </div>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '10px' }}>任务列表</Link>
        <Link to="/submit-task" style={{ marginRight: '10px' }}>提交任务</Link>
        <Link to="/datasets" style={{ marginRight: '10px' }}>数据集</Link>
        <Link to="/models" style={{ marginRight: '10px' }}>模型</Link>
        <Link to="/chat">对话</Link>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={loadLogs}>查看日志</button>
        <button onClick={() => navigate(-1)} style={{ marginLeft: '10px' }}>返回</button>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <h2>{task.name}</h2>
        <p><strong>状态：</strong>{task.status}</p>
        <p><strong>模型名称：</strong>{task.model_name}</p>
        <p><strong>数据集路径：</strong>{task.dataset_path}</p>
        <p><strong>训练轮数：</strong>{task.epochs}</p>
        <p><strong>学习率：</strong>{task.learning_rate}</p>
        <p><strong>批次大小：</strong>{task.batch_size}</p>
        <p><strong>输出目录：</strong>{task.output_dir}</p>
        <p><strong>创建时间：</strong>{new Date(task.created_at).toLocaleString()}</p>
        <p><strong>更新时间：</strong>{new Date(task.updated_at).toLocaleString()}</p>
      </div>
      {showLogs && (
        <div style={{ marginTop: '20px' }}>
          <h3>日志</h3>
          <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', overflow: 'auto', maxHeight: '500px' }}>
            {logs || '暂无日志'}
          </pre>
        </div>
      )}
    </div>
  );
};

