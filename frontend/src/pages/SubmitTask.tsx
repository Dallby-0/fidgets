import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { taskApi, fileApi } from '../services/api';
import { TaskCreate } from '../types/task';
import { DatasetFile } from '../types/file';
import { useAuth } from '../hooks/useAuth';

export const SubmitTask = () => {
  const [datasets, setDatasets] = useState<DatasetFile[]>([]);
  const [taskData, setTaskData] = useState<TaskCreate>({
    name: '',
    // 默认基础模型名称，建议替换为你实际使用的模型路径
    model_name: '/root/autodl-tmp/Qwen2-0.5B-Instruct',
    dataset_path: '',
    // 以下默认值与在云端测试成功的命令保持一致
    stage: 'sft',
    template: 'qwen2',
    epochs: 3.0,
    learning_rate: 5e-5,
    batch_size: 4,
    gradient_accumulation_steps: 4,
    // output_dir 留空时后端会自动生成用户专属目录，也可以在下面的表单中自定义
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
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
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await taskApi.createTask(taskData);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || '提交任务失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h1>提交任务</h1>
        <div>
          <span>欢迎，{user?.username}</span>
          <button onClick={logout} style={{ marginLeft: '10px' }}>退出</button>
        </div>
      </div>
      <div style={{ marginBottom: '20px' }}>
        <Link to="/" style={{ marginRight: '10px' }}>任务列表</Link>
        <Link to="/datasets" style={{ marginRight: '10px' }}>数据集</Link>
        <Link to="/models" style={{ marginRight: '10px' }}>模型</Link>
        <Link to="/chat">对话</Link>
      </div>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label>任务名称：</label>
          <input
            type="text"
            value={taskData.name}
            onChange={(e) => setTaskData({ ...taskData, name: e.target.value })}
            required
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>模型名称：</label>
          <input
            type="text"
            value={taskData.model_name}
            onChange={(e) => setTaskData({ ...taskData, model_name: e.target.value })}
            required
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>数据集：</label>
          <select
            value={taskData.dataset_path}
            onChange={(e) => setTaskData({ ...taskData, dataset_path: e.target.value })}
            required
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          >
            <option value="">请选择数据集</option>
            {datasets.map((dataset) => (
              <option key={dataset.file_id} value={dataset.file_path}>
                {dataset.filename}
              </option>
            ))}
          </select>
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>训练阶段（stage）：</label>
          <input
            type="text"
            value={taskData.stage}
            onChange={(e) => setTaskData({ ...taskData, stage: e.target.value })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>模板（template）：</label>
          <input
            type="text"
            value={taskData.template}
            onChange={(e) => setTaskData({ ...taskData, template: e.target.value })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>训练轮数：</label>
          <input
            type="number"
            value={taskData.epochs}
            onChange={(e) => setTaskData({ ...taskData, epochs: parseFloat(e.target.value) })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>学习率：</label>
          <input
            type="number"
            step="0.00001"
            value={taskData.learning_rate}
            onChange={(e) => setTaskData({ ...taskData, learning_rate: parseFloat(e.target.value) })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>批次大小：</label>
          <input
            type="number"
            value={taskData.batch_size}
            onChange={(e) => setTaskData({ ...taskData, batch_size: parseInt(e.target.value) })}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>梯度累积步数（gradient_accumulation_steps）：</label>
          <input
            type="number"
            value={taskData.gradient_accumulation_steps}
            onChange={(e) =>
              setTaskData({
                ...taskData,
                gradient_accumulation_steps: parseInt(e.target.value),
              })
            }
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label>输出目录（可选）：</label>
          <input
            type="text"
            value={taskData.output_dir || ''}
            onChange={(e) => setTaskData({ ...taskData, output_dir: e.target.value || undefined })}
            placeholder="留空则使用默认用户专属目录"
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          />
        </div>
        {error && <div style={{ color: 'red', marginBottom: '15px' }}>{error}</div>}
        <button type="submit" disabled={loading} style={{ width: '100%', padding: '10px' }}>
          {loading ? '提交中...' : '提交任务'}
        </button>
      </form>
    </div>
  );
};

