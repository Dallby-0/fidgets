import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { taskApi } from '../services/api';
import { Task } from '../types/task';
import { useAuth } from '../hooks/useAuth';

export const Home = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'running': return 'blue';
      case 'failed': return 'red';
      default: return 'gray';
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h1>任务列表</h1>
        <div>
          <span>欢迎，{user?.username}</span>
          <button onClick={logout} style={{ marginLeft: '10px' }}>退出</button>
        </div>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/submit-task" style={{ marginRight: '10px' }}>提交任务</Link>
        <Link to="/datasets" style={{ marginRight: '10px' }}>数据集</Link>
        <Link to="/models" style={{ marginRight: '10px' }}>模型</Link>
        <Link to="/chat">对话</Link>
      </div>
      {loading ? (
        <div>加载中...</div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>任务名称</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>模型名称</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>状态</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>创建时间</th>
              <th style={{ border: '1px solid #ddd', padding: '8px' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.task_id}>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{task.name}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>{task.model_name}</td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  <span style={{ color: getStatusColor(task.status) }}>{task.status}</span>
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {new Date(task.created_at).toLocaleString()}
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  <Link to={`/tasks/${task.task_id}`}>详情</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {tasks.length === 0 && !loading && <div>暂无任务</div>}
    </div>
  );
};

