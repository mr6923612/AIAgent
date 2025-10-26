#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent Prompt 更新脚本

功能：
1. 读取 agent_config.yaml 配置文件
2. 自动更新 crew.py 中的 customer_service_agent 配置
3. 备份原始文件
4. 验证更新是否成功

使用方法：
    python scripts/update_agent_prompt.py
    
或者从项目根目录：
    python crewaiBackend/scripts/update_agent_prompt.py
"""

import os
import sys
import yaml
import re
from datetime import datetime
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载 .env 文件
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# 导入RAGFlow客户端
try:
    # 尝试两种导入方式，适配不同的运行环境
    try:
        from crewaiBackend.utils.ragflow_client import create_ragflow_client
    except ImportError:
        from utils.ragflow_client import create_ragflow_client
except ImportError:
    print("[WARNING] 无法导入RAGFlow客户端，将跳过chat_id更新")
    create_ragflow_client = None


class AgentPromptUpdater:
    """Agent Prompt 更新器"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.backend_dir = self.script_dir.parent
        self.project_root = self.backend_dir.parent
        self.config_file = self.backend_dir / "agent_config.yaml"
        self.crew_file = self.backend_dir / "crew.py"
        self.backup_dir = self.backend_dir / "backups"
        self.env_file = self.backend_dir / ".env"
        self.env_template = self.backend_dir / "env.template"
        
    def load_config(self):
        """加载配置文件"""
        print(f"[INFO] 正在读取配置文件: {self.config_file}")
        
        if not self.config_file.exists():
            print(f"[ERROR] 错误: 配置文件不存在: {self.config_file}")
            sys.exit(1)
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                print("[ERROR] 错误: 配置文件格式不正确")
                sys.exit(1)
            
            if 'customer_service_agent' not in config:
                print("[ERROR] 错误: 配置文件缺少 customer_service_agent 配置")
                sys.exit(1)
            
            if 'customer_service_task' not in config:
                print("[ERROR] 错误: 配置文件缺少 customer_service_task 配置")
                sys.exit(1)
            
            print("[OK] 配置文件读取成功")
            return config
        
        except Exception as e:
            print(f"[ERROR] 读取配置文件失败: {e}")
            sys.exit(1)
    
    def backup_crew_file(self):
        """备份 crew.py 文件"""
        # 创建备份目录
        self.backup_dir.mkdir(exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"crew_backup_{timestamp}.py"
        
        print(f"[BACKUP] 正在备份原始文件到: {backup_file}")
        
        try:
            with open(self.crew_file, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            print("[OK] 备份成功")
            return True
        
        except Exception as e:
            print(f"[ERROR] 备份失败: {e}")
            return False
    
    def update_crew_file(self, config):
        """更新 crew.py 文件"""
        print(f"[UPDATE] 正在更新 {self.crew_file}")
        
        try:
            with open(self.crew_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ========== 更新 Agent 定义 ==========
            agent_config = config['customer_service_agent']
            role = agent_config.get('role', '智能客服代表')
            goal = agent_config.get('goal', '为客户提供友好、专业的服务')
            backstory = agent_config.get('backstory', '你是一位经验丰富的客服代表')
            
            # 格式化 backstory，确保正确的缩进
            backstory_lines = backstory.strip().split('\n')
            formatted_backstory = '\n            '.join(line.strip() for line in backstory_lines)
            
            # 构建新的 Agent 代码
            new_agent_code = f'''customer_service_agent = Agent(
            role="{role}",
            goal="{goal}",
            backstory="""{formatted_backstory}""",
            verbose=False,
            llm=self.llm,
        )'''
            
            # 使用正则表达式替换 customer_service_agent 的定义
            agent_pattern = r'customer_service_agent = Agent\([^)]+\)'
            
            # 检查是否找到匹配
            if not re.search(agent_pattern, content, re.DOTALL):
                print("[ERROR] 错误: 在 crew.py 中找不到 customer_service_agent 定义")
                return False
            
            # 替换 Agent 内容
            content = re.sub(agent_pattern, new_agent_code, content, flags=re.DOTALL)
            print("[OK] Agent 配置已更新")
            
            # ========== 更新 Task 定义 ==========
            task_config = config['customer_service_task']
            description_template = task_config.get('description_template', '')
            expected_output = task_config.get('expected_output', '专业的客服回复')
            
            # 格式化 description_template，确保正确的缩进
            # 注意：保留 {customer_input}, {retrieved_summary}, {context_info} 占位符
            description_lines = description_template.strip().split('\n')
            formatted_description = '\n                '.join(line.strip() for line in description_lines)
            
            # 构建新的 Task 代码
            new_task_code = f'''customer_service_task = Task(
            description=f"""
                {formatted_description}
            """,
            expected_output="{expected_output}",
            agent=agents["customer_service_agent"]
        )'''
            
            # 使用正则表达式替换 customer_service_task 的定义
            task_pattern = r'customer_service_task = Task\([^)]+\)'
            
            # 检查是否找到匹配
            if not re.search(task_pattern, content, re.DOTALL):
                print("[ERROR] 错误: 在 crew.py 中找不到 customer_service_task 定义")
                return False
            
            # 替换 Task 内容
            content = re.sub(task_pattern, new_task_code, content, flags=re.DOTALL)
            print("[OK] Task 配置已更新")
            
            # 写入更新后的内容
            with open(self.crew_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[OK] crew.py 更新成功")
            return True
        
        except Exception as e:
            print(f"[ERROR] 更新失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_update(self):
        """验证更新是否成功"""
        print("[VERIFY] 正在验证更新...")
        
        try:
            with open(self.crew_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含 customer_service_agent
            agent_found = 'customer_service_agent = Agent(' in content
            task_found = 'customer_service_task = Task(' in content
            
            if agent_found and task_found:
                print("[OK] 验证成功: Agent 和 Task 配置已更新")
                return True
            else:
                if not agent_found:
                    print("[ERROR] 验证失败: 未找到 customer_service_agent 配置")
                if not task_found:
                    print("[ERROR] 验证失败: 未找到 customer_service_task 配置")
                return False
        
        except Exception as e:
            print(f"[ERROR] 验证失败: {e}")
            return False
    
    def fetch_ragflow_chat_id(self):
        """从RAGFlow获取第一个chat_id"""
        if create_ragflow_client is None:
            print("[SKIP] RAGFlow客户端不可用，跳过chat_id获取")
            return None
        
        print("\n[RAGFLOW] 正在从RAGFlow获取chat列表...")
        
        try:
            # 创建RAGFlow客户端
            client = create_ragflow_client()
            
            # 获取chat列表
            chats = client.list_chats(page=1, page_size=10)
            
            if not chats:
                print("[WARNING] RAGFlow中没有可用的chat")
                print("[HINT] 请在RAGFlow Web界面创建一个chat（对话助手）")
                return None
            
            # 获取第一个chat的ID
            first_chat = chats[0]
            chat_id = first_chat.get('id')
            chat_name = first_chat.get('name', 'Unknown')
            
            print(f"[OK] 找到RAGFlow chat: {chat_name} (ID: {chat_id})")
            print(f"[INFO] 共找到 {len(chats)} 个chat")
            
            return chat_id
        
        except Exception as e:
            print(f"[ERROR] 获取RAGFlow chat_id失败: {e}")
            return None
    
    def update_env_file(self, chat_id: str):
        """更新.env文件中的RAGFLOW_CHAT_ID"""
        print(f"\n[UPDATE] 正在更新.env文件中的RAGFLOW_CHAT_ID...")
        
        # 如果.env不存在，从env.template复制
        if not self.env_file.exists():
            if self.env_template.exists():
                print(f"[INFO] .env文件不存在，从env.template创建")
                with open(self.env_template, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(self.env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print(f"[ERROR] .env和env.template都不存在")
                return False
        
        try:
            # 读取.env文件
            with open(self.env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 更新RAGFLOW_CHAT_ID
            updated = False
            new_lines = []
            
            for line in lines:
                if line.strip().startswith('RAGFLOW_CHAT_ID='):
                    new_lines.append(f'RAGFLOW_CHAT_ID={chat_id}\n')
                    updated = True
                    print(f"[OK] 已更新RAGFLOW_CHAT_ID={chat_id}")
                else:
                    new_lines.append(line)
            
            # 如果没有找到RAGFLOW_CHAT_ID，添加它
            if not updated:
                # 在RAGFlow配置部分添加
                for i, line in enumerate(new_lines):
                    if 'RAGFlow配置' in line or 'RAGFLOW' in line:
                        # 找到RAGFlow配置部分，在后面添加
                        insert_pos = i + 1
                        while insert_pos < len(new_lines) and new_lines[insert_pos].strip() and not new_lines[insert_pos].startswith('#'):
                            insert_pos += 1
                        new_lines.insert(insert_pos, f'RAGFLOW_CHAT_ID={chat_id}\n')
                        updated = True
                        print(f"[OK] 已添加RAGFLOW_CHAT_ID={chat_id}")
                        break
                
                # 如果还是没找到合适位置，添加到文件末尾
                if not updated:
                    new_lines.append(f'\nRAGFLOW_CHAT_ID={chat_id}\n')
                    print(f"[OK] 已添加RAGFLOW_CHAT_ID={chat_id}")
            
            # 写回文件
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print("[OK] .env文件更新成功")
            return True
        
        except Exception as e:
            print(f"[ERROR] 更新.env文件失败: {e}")
            return False
    
    def run(self, auto_yes=False):
        """执行更新流程
        
        Args:
            auto_yes: 是否自动确认（跳过交互式询问）
        """
        print("\n" + "="*60)
        print("AI Agent Prompt 更新工具")
        print("="*60 + "\n")
        
        # 1. 加载配置
        config = self.load_config()
        
        agent_config = config['customer_service_agent']
        task_config = config['customer_service_task']
        
        print("\n[CONFIG] 当前配置:")
        print("\n[Agent 配置]")
        print(f"  角色: {agent_config.get('role')}")
        print(f"  目标: {agent_config.get('goal')}")
        print(f"  背景: {agent_config.get('backstory', '')[:50]}...")
        print("\n[Task 配置]")
        print(f"  描述模板: {task_config.get('description_template', '')[:80]}...")
        print(f"  期望输出: {task_config.get('expected_output')}")
        
        # 2. 询问是否继续（除非设置了auto_yes）
        if not auto_yes:
            print("\n[WARNING] 即将更新 crew.py 文件 (Agent + Task)")
            response = input("是否继续? (y/n): ").lower().strip()
            
            if response != 'y':
                print("[CANCEL] 操作已取消")
                sys.exit(0)
        else:
            print("\n[AUTO] 自动确认模式，跳过交互式询问")
        
        # 3. 备份原文件
        if not self.backup_crew_file():
            print("[ERROR] 由于备份失败，操作已中止")
            sys.exit(1)
        
        # 4. 更新文件
        if not self.update_crew_file(config):
            print("[ERROR] 更新失败，请检查错误信息")
            sys.exit(1)
        
        # 5. 验证更新
        if not self.verify_update():
            print("[ERROR] 验证失败")
            sys.exit(1)
        
        # 6. 获取并更新RAGFlow chat_id
        chat_id = self.fetch_ragflow_chat_id()
        if chat_id:
            self.update_env_file(chat_id)
        else:
            print("[SKIP] 跳过.env文件更新")
        
        print("\n" + "="*60)
        print("[SUCCESS] 更新完成！")
        print("="*60)
        print("\n[NEXT] 后续步骤:")
        print("  1. 重启后端服务以应用更改")
        print("  2. 测试新的 prompt 是否符合预期")
        print(f"  3. 如需回滚，可使用备份文件: {self.backup_dir}")
        if chat_id:
            print(f"  4. RAGFlow chat_id 已更新到 .env 文件: {chat_id}")
        print("\n")


def main():
    """主函数"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AI Agent Prompt 更新工具')
    parser.add_argument('--yes', '-y', action='store_true', 
                        help='自动确认，跳过交互式询问')
    args = parser.parse_args()
    
    try:
        updater = AgentPromptUpdater()
        updater.run(auto_yes=args.yes)
    except KeyboardInterrupt:
        print("\n\n[CANCEL] 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

