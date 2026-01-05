import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { taskApi } from '../services/api';
import { Task } from '../types/task';
import { Layout } from '../components/Layout';
import './Home.css';

export const Home = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await taskApi.getTasks();
      setTasks(data);
    } catch (error) {
      console.error('加载任务失败', error);
    } finally {
      setLoading(false);
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

  return (
    <Layout>
      <div className="page-header fade-in">
        <div>
          <h1 className="page-title">任务列表</h1>
          <p className="text-muted">管理和查看您的训练任务</p>
        </div>
        <Link to="/submit-task" className="btn-primary">
          <span>+</span>
          提交新任务
        </Link>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p className="text-muted">加载中...</p>
        </div>
      ) : tasks.length === 0 ? (
        <div className="empty-state fade-in">
          <div className="empty-icon">📋</div>
          <h3>暂无任务</h3>
          <p className="text-muted">开始创建您的第一个训练任务吧</p>
          <Link to="/submit-task" className="btn-primary">
            提交新任务
          </Link>
        </div>
      ) : (
        <div className="table-container fade-in">
          <div className="card">
            <table className="tasks-table">
              <thead>
                <tr>
                  <th>任务名称</th>
                  <th>模型名称</th>
                  <th>状态</th>
                  <th>创建时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task, index) => (
                  <tr key={task.task_id} className="slide-in" style={{ animationDelay: `${index * 50}ms` }}>
                    <td>
                      <div className="task-name">{task.name}</div>
                    </td>
                    <td>
                      <span className="model-name">{task.model_name}</span>
                    </td>
                    <td>{getStatusBadge(task.status)}</td>
                    <td className="text-muted">
                      {new Date(task.created_at).toLocaleString('zh-CN')}
                    </td>
                    <td>
                      <Link
                        to={`/tasks/${task.task_id}`}
                        className="btn-text"
                      >
                        查看详情 →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </Layout>
  );
};
