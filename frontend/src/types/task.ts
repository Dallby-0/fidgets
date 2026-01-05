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
  epochs?: number;
  learning_rate?: number;
  batch_size?: number;
  output_dir?: string;
}

