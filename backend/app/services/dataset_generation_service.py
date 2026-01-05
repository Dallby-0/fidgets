import logging
import json
import requests
import tempfile
import os
from typing import Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class DatasetGenerationService:
    """数据集生成服务，使用DeepSeek API生成数据集"""
    
    def __init__(self):
        self.api_url = settings.deepseek_api_url
        self.api_key = settings.deepseek_api_key
        self.model = settings.deepseek_model
        
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未配置，请在环境变量中设置DEEPSEEK_API_KEY")
        
        # 固定的系统提示词
        self.system_prompt = """你是一个高质量数据集生成器。请严格遵循以下规则：你只能输出一个纯粹的JSON数组，不要包含任何其他文字。数组中的每个对象必须且只能包含三个字段：instruction, input, output。instruction字段必须以你是一个专业的[用户指定话题]专家。开头，并描述一个具体任务。input字段提供任务所需的额外条件信息，如果不需要则为空字符串。output字段必须是符合专家身份的、详细且分步骤的专业回答。所有问答必须紧密围绕用户提供的话题，涵盖基础概念、进阶技巧、问题排查和方案设计等多个方面，总共生成30条不重复的高质量问答对。请直接开始生成JSON数组"""
    
    def generate_dataset(self, topic: str) -> list:
        """
        调用DeepSeek API生成数据集
        
        Args:
            topic: 用户输入的话题
            
        Returns:
            生成的数据集列表（JSON数组）
            
        Raises:
            Exception: API调用失败或返回格式错误
        """
        logger.info(f"[数据集生成] 开始生成数据集，话题: {topic}")
        
        # 构建请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        user_message = f"你好，生成{topic}相关的数据集"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": 0.8
        }
        
        try:
            # 发送请求
            logger.info(f"[数据集生成] 发送API请求到: {self.api_url}")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120  # 2分钟超时
            )
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            logger.info(f"[数据集生成] API响应状态: {response.status_code}")
            
            # 提取content
            if "choices" not in result or len(result["choices"]) == 0:
                raise Exception("API响应中没有choices字段")
            
            content = result["choices"][0]["message"]["content"]
            
            if not content:
                raise Exception("API返回的content为空")
            
            # 尝试解析JSON
            # 可能返回的content包含markdown代码块，需要清理
            content = content.strip()
            if content.startswith("```"):
                # 移除markdown代码块标记
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines)
            
            # 解析JSON数组
            dataset = json.loads(content)
            
            if not isinstance(dataset, list):
                raise Exception("API返回的不是JSON数组")
            
            logger.info(f"[数据集生成] 成功生成数据集，包含 {len(dataset)} 条记录")
            return dataset
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[数据集生成] API请求失败: {str(e)}", exc_info=True)
            raise Exception(f"API请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"[数据集生成] JSON解析失败: {str(e)}", exc_info=True)
            logger.error(f"[数据集生成] 原始content: {content[:500] if 'content' in locals() else 'N/A'}")
            raise Exception(f"JSON解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"[数据集生成] 生成数据集失败: {str(e)}", exc_info=True)
            raise
    
    def save_dataset_to_file(self, dataset: list, file_path: str) -> int:
        """
        将数据集保存到JSON文件
        
        Args:
            dataset: 数据集列表
            file_path: 文件保存路径
            
        Returns:
            文件大小（字节）
        """
        logger.info(f"[数据集生成] 保存数据集到文件: {file_path}")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存JSON文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        file_size = os.path.getsize(file_path)
        logger.info(f"[数据集生成] 文件保存成功，大小: {file_size} 字节")
        return file_size
    
    def generate_filename(self, topic: str, custom_filename: Optional[str] = None) -> str:
        """
        生成文件名
        
        Args:
            topic: 用户话题
            custom_filename: 用户指定的文件名（可选）
            
        Returns:
            文件名（带.json扩展名）
        """
        if custom_filename:
            # 如果用户指定了文件名，确保有.json扩展名
            if not custom_filename.endswith('.json'):
                return f"{custom_filename}.json"
            return custom_filename
        else:
            # 默认使用话题的前10个字符
            filename = topic[:10] if len(topic) > 10 else topic
            # 清理文件名中的非法字符
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
            if not filename:
                filename = "dataset"
            return f"{filename}.json"

