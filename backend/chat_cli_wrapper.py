#!/usr/bin/env python3
"""
LlamaFactory CLI 对话包装脚本
此脚本用于通过pexpect与交互式的llamafactory-cli chat命令交互

使用方法:
    python3 chat_cli_wrapper.py '{"base_model_path": "...", "adapter_path": "...", "template": "qwen2", "message": "你好"}'

输出: JSON格式 {"role": "assistant", "content": "..."}
"""

import sys
import json
import pexpect
import logging
import re
import base64
from typing import Dict

# 配置日志（输出到stderr，避免干扰JSON输出）
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

def extract_assistant_response(output: str) -> str:
    """从输出中提取Assistant回复，过滤掉系统日志和警告信息"""
    
    # 简单方法：直接找到 "FP32)" 后面的内容（截掉FP32)及之前的所有内容）
    fp32_pattern = r'FP32\)\s*(.+?)(?=\nUser:|$)'
    match = re.search(fp32_pattern, output, re.DOTALL | re.IGNORECASE)
    if match:
        response = match.group(1).strip()
        # 清理多余的空白行
        cleaned_lines = [line.strip() for line in response.split('\n') if line.strip()]
        if cleaned_lines:
            return '\n'.join(cleaned_lines)
    
    def is_log_line(line: str) -> bool:
        """判断是否是日志/警告行"""
        line = line.strip()
        if not line:
            return False  # 空行不是日志行，会在后面单独处理
        
        # 匹配各种日志格式
        log_patterns = [
            r'^\[(WARNING|INFO|ERROR|DEBUG|logging\.py)',  # [WARNING|...] 或 [INFO|...] 开头
            r'^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # 时间戳开头: 2026-01-05 20:17:34
            r'starting from v\d+\.\d+',  # 版本警告: Starting from v4.46
            r'>>\s+',  # 日志消息分隔符: >> 
            r'\[WARNING\|.*?\]',  # [WARNING|logging.py:328] 格式
            r'\[INFO\|.*?\]',  # [INFO|...] 格式
            r'FP32\)',  # FP32) 标记
        ]
        for pattern in log_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    # 尝试匹配 "Assistant: <回复内容>"
    patterns = [
        r'Assistant:\s*(.+?)(?=\nUser:|$)',
        r'Assistant\s*:\s*(.+?)(?=\nUser:|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output, re.DOTALL | re.IGNORECASE)
        if match:
            response = match.group(1).strip()
            # 清理响应：过滤日志行并移除多余的空白行
            cleaned_lines = []
            for line in response.split('\n'):
                line = line.strip()
                if line and not is_log_line(line):
                    cleaned_lines.append(line)
            if cleaned_lines:
                return '\n'.join(cleaned_lines)
            # 如果清理后没有内容，继续尝试其他方法
    
    # 如果没有匹配到，尝试查找最后的大段文本输出
    lines = output.split('\n')
    assistant_lines = []
    in_assistant = False
    
    for line in lines:
        # 跳过所有日志行
        if is_log_line(line):
            continue
            
        if 'Assistant' in line and ':' in line:
            in_assistant = True
            # 提取冒号后的内容
            parts = line.split(':', 1)
            if len(parts) > 1:
                content = parts[1].strip()
                if content and not is_log_line(content):
                    assistant_lines.append(content)
        elif in_assistant:
            # 如果遇到新的User提示，停止
            if 'User:' in line:
                break
            # 跳过空行和日志行，但保留有内容的行
            if line.strip() and not is_log_line(line):
                assistant_lines.append(line.strip())
    
    if assistant_lines:
        return '\n'.join(assistant_lines).strip()
    
    return ""


def chat_with_cli(config: Dict) -> Dict:
    """使用pexpect与llamafactory-cli chat交互"""
    base_model_path = config.get("base_model_path")
    adapter_path = config.get("adapter_path")
    template = config.get("template", "qwen2")
    message = config.get("message", "")
    
    if not base_model_path or not adapter_path or not message:
        raise ValueError("缺少必要参数: base_model_path, adapter_path, message")
    
    # 构建命令
    # 注意：这里假设llamafactory-cli在PATH中，如果不在，需要指定完整路径
    cmd = f"llamafactory-cli chat --model_name_or_path {base_model_path} --adapter_name_or_path {adapter_path} --template {template}"
    
    logger.info(f"执行命令: {cmd}")
    logger.info(f"发送消息: {message}")
    
    try:
        # 启动子进程
        child = pexpect.spawn(cmd, encoding='utf-8', timeout=300)
        child.logfile_read = sys.stderr  # 将日志输出到stderr
        
        # 等待欢迎消息和提示符
        # 根据实际输出，可能需要调整这些匹配模式
        welcome_patterns = [
            "Welcome to the CLI application",
            "User:",
            "user:",
            pexpect.EOF,
            pexpect.TIMEOUT
        ]
        
        index = child.expect(welcome_patterns, timeout=120)
        logger.info(f"等待欢迎消息完成，匹配到索引: {index}")
        
        # 如果超时或EOF，说明命令可能已经失败
        if index >= len(welcome_patterns) - 2:  # EOF 或 TIMEOUT
            output_before = child.before if hasattr(child, 'before') else ""
            raise Exception(f"命令启动失败或超时，输出: {output_before}")
        
        # 发送用户消息
        child.sendline(message)
        
        # 等待回复
        # 寻找 "Assistant:" 或类似的提示
        response_patterns = [
            r'Assistant\s*:',
            r'Assistant\s*：',  # 中文冒号
            pexpect.EOF,
            pexpect.TIMEOUT
        ]
        
        index = child.expect(response_patterns, timeout=300)
        logger.info(f"等待回复完成，匹配到索引: {index}")
        
        if index >= len(response_patterns) - 2:  # EOF 或 TIMEOUT
            output_before = child.before if hasattr(child, 'before') else ""
            raise Exception(f"等待回复超时或进程结束，输出: {output_before}")
        
        # 读取所有输出
        # 继续读取直到遇到下一个 "User:" 提示或EOF
        try:
            child.expect([r'User\s*:', pexpect.EOF, pexpect.TIMEOUT], timeout=5)
        except:
            pass  # 忽略超时，我们已经得到了回复
        
        # 获取所有输出
        output = child.before if hasattr(child, 'before') else ""
        
        # 关闭进程
        try:
            child.send('exit\n')  # 尝试优雅退出
            child.expect(pexpect.EOF, timeout=2)
        except:
            pass
        finally:
            child.close()
        
        # 提取Assistant回复
        assistant_content = extract_assistant_response(output)
        
        if not assistant_content:
            # 如果无法提取，返回原始输出的一部分
            logger.warning("无法提取Assistant回复，使用原始输出")
            assistant_content = output[-500:] if len(output) > 500 else output
        
        return {
            "role": "assistant",
            "content": assistant_content
        }
        
    except pexpect.TIMEOUT:
        raise Exception("对话超时")
    except pexpect.EOF:
        output_before = child.before if hasattr(child, 'before') else ""
        raise Exception(f"进程意外结束，输出: {output_before}")
    except Exception as e:
        raise Exception(f"执行失败: {str(e)}")


def main():
    """主函数"""
    try:
        # 从命令行参数读取配置
        if len(sys.argv) < 2:
            print(json.dumps({"error": "缺少配置参数"}), file=sys.stderr)
            sys.exit(1)
        
        config_arg = sys.argv[1]
        
        # 尝试解析：可能是base64编码的JSON，也可能是直接JSON
        try:
            # 先尝试base64解码
            config_str = base64.b64decode(config_arg.encode('ascii')).decode('utf-8')
            config = json.loads(config_str)
            logger.info("使用base64编码的配置参数")
        except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
            # 如果不是base64，尝试直接解析JSON（向后兼容）
            try:
                config = json.loads(config_arg)
                logger.info("使用直接JSON配置参数")
            except json.JSONDecodeError as e:
                raise ValueError(f"无法解析配置参数（既不是有效的base64编码JSON，也不是直接JSON）: {str(e)}")
        
        # 执行对话
        result = chat_with_cli(config)
        
        # 输出JSON结果到stdout
        print(json.dumps(result, ensure_ascii=False))
        
    except json.JSONDecodeError as e:
        error_result = {"error": f"JSON解析失败: {str(e)}"}
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

