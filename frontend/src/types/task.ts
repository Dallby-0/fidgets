export interface Task {
  task_id: string;
  user_id: string;
  name: string;
  model_name: string;
  dataset_path: string;
  epochs: number;
  learning_rate: number;
  batch_size: number;
  output_dir: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  name: string;
  model_name: string;
  dataset_path: string;
  // 训练相关参数（带默认值，可在前端调整）
  stage?: string;                     // 默认 sft
  template?: string;                  // 默认 qwen2
  epochs?: number;                    // 默认 3.0
  learning_rate?: number;             // 默认 5e-5
  batch_size?: number;                // 默认 4
  gradient_accumulation_steps?: number; // 默认 4
  output_dir?: string;                // 默认由后端生成，可覆盖
}

