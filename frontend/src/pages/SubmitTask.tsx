import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { taskApi, fileApi, AvailableModel } from '../services/api';
import { TaskCreate } from '../types/task';
import { DatasetFile } from '../types/file';
import { Layout } from '../components/Layout';
import './SubmitTask.css';

export const SubmitTask = () => {
  const [datasets, setDatasets] = useState<DatasetFile[]>([]);
  const [availableModels, setAvailableModels] = useState<AvailableModel[]>([]);
  const [taskData, setTaskData] = useState<TaskCreate>({
    name: '',
    model_name: '',
    dataset_path: '',
    stage: 'sft',
    epochs: 3.0,
    learning_rate: 5e-5,
    batch_size: 4,
    gradient_accumulation_steps: 4,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadDatasets();
    loadAvailableModels();
  }, []);

  const loadDatasets = async () => {
    try {
      const data = await fileApi.getDatasets();
      setDatasets(data);
    } catch (error) {
      console.error('加载数据集失败', error);
    }
  };

  const loadAvailableModels = async () => {
    try {
      const data = await taskApi.getAvailableModels();
      setAvailableModels(data);
      if (data.length > 0) {
        setTaskData({ ...taskData, model_name: data[0].name });
      }
    } catch (error) {
      console.error('加载模型列表失败', error);
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
    <Layout>
      <div className="submit-task-page fade-in">
        <div className="page-header">
          <div>
            <h1 className="page-title">提交任务</h1>
            <p className="text-muted">创建新的模型训练任务</p>
          </div>
        </div>

        <div className="form-container card">
          <form onSubmit={handleSubmit} className="task-form">
            <div className="form-section">
              <h3 className="section-title">基本信息</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="name">任务名称 <span className="required">*</span></label>
                  <input
                    id="name"
                    type="text"
                    value={taskData.name}
                    onChange={(e) => setTaskData({ ...taskData, name: e.target.value })}
                    required
                    placeholder="请输入任务名称"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="model_name">模型 <span className="required">*</span></label>
                  <select
                    id="model_name"
                    value={taskData.model_name}
                    onChange={(e) => setTaskData({ ...taskData, model_name: e.target.value })}
                    required
                  >
                    <option value="">请选择模型</option>
                    {availableModels.map((model) => (
                      <option key={model.name} value={model.name}>
                        {model.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="dataset_path">数据集 <span className="required">*</span></label>
                  <select
                    id="dataset_path"
                    value={taskData.dataset_path}
                    onChange={(e) => setTaskData({ ...taskData, dataset_path: e.target.value })}
                    required
                  >
                    <option value="">请选择数据集</option>
                    {datasets.map((dataset) => (
                      <option key={dataset.file_id} value={dataset.file_path}>
                        {dataset.filename}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label htmlFor="stage">训练阶段（stage）</label>
                  <input
                    id="stage"
                    type="text"
                    value={taskData.stage}
                    onChange={(e) => setTaskData({ ...taskData, stage: e.target.value })}
                    placeholder="sft"
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3 className="section-title">训练参数</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="epochs">训练轮数</label>
                  <input
                    id="epochs"
                    type="number"
                    value={taskData.epochs}
                    onChange={(e) => setTaskData({ ...taskData, epochs: parseFloat(e.target.value) })}
                    step="0.1"
                    min="0.1"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="learning_rate">学习率</label>
                  <input
                    id="learning_rate"
                    type="number"
                    step="0.00001"
                    value={taskData.learning_rate}
                    onChange={(e) => setTaskData({ ...taskData, learning_rate: parseFloat(e.target.value) })}
                    min="0"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="batch_size">批次大小</label>
                  <input
                    id="batch_size"
                    type="number"
                    value={taskData.batch_size}
                    onChange={(e) => setTaskData({ ...taskData, batch_size: parseInt(e.target.value) })}
                    min="1"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="gradient_accumulation_steps">梯度累积步数</label>
                  <input
                    id="gradient_accumulation_steps"
                    type="number"
                    value={taskData.gradient_accumulation_steps}
                    onChange={(e) =>
                      setTaskData({
                        ...taskData,
                        gradient_accumulation_steps: parseInt(e.target.value),
                      })
                    }
                    min="1"
                  />
                </div>
              </div>
            </div>

            {error && (
              <div className="error-message slide-in">
                {error}
              </div>
            )}

            <div className="form-actions">
              <button
                type="button"
                onClick={() => navigate('/')}
                className="btn-secondary"
              >
                取消
              </button>
              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? (
                  <>
                    <span className="loading-spinner"></span>
                    提交中...
                  </>
                ) : (
                  '🚀 提交任务'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
};
