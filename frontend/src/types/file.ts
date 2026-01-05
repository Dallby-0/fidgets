export interface DatasetFile {
  file_id: string;
  user_id: string;
  filename: string;
  file_path: string;
  size: number;
  created_at: string;
}

export interface ModelFile {
  model_id: string;
  user_id: string;
  name: string;
  model_path: string;
  base_model_path?: string;
  task_id?: string;
  size?: number;
  created_at: string;
}

