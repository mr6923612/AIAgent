#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent Prompt Update Script

Functions:
1. Read agent_config.yaml configuration file
2. Automatically update customer_service_agent configuration in crew.py
3. Backup original file
4. Verify if update was successful

Usage:
    python scripts/update_agent_prompt.py
    
Or from project root:
    python crewaiBackend/scripts/update_agent_prompt.py
"""

import os
import sys
import yaml
import re
from datetime import datetime
from pathlib import Path

# Add project root directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env file
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Import RAGFlow client
try:
    # Try two import methods to adapt to different runtime environments
    try:
        from crewaiBackend.utils.ragflow_client import create_ragflow_client
    except ImportError:
        from utils.ragflow_client import create_ragflow_client
except ImportError:
    print("[WARNING] Unable to import RAGFlow client, will skip chat_id update")
    create_ragflow_client = None


class AgentPromptUpdater:
    """Agent Prompt Updater"""
    
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
        """Load configuration file"""
        print(f"[INFO] Reading configuration file: {self.config_file}")
        
        if not self.config_file.exists():
            print(f"[ERROR] Configuration file does not exist: {self.config_file}")
            sys.exit(1)
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                print("[ERROR] Configuration file format is incorrect")
                sys.exit(1)
            
            if 'customer_service_agent' not in config:
                print("[ERROR] Configuration file missing customer_service_agent configuration")
                sys.exit(1)
            
            if 'customer_service_task' not in config:
                print("[ERROR] Configuration file missing customer_service_task configuration")
                sys.exit(1)
            
            print("[OK] Configuration file read successfully")
            return config
        
        except Exception as e:
            print(f"[ERROR] Failed to read configuration file: {e}")
            sys.exit(1)
    
    def backup_crew_file(self):
        """Backup crew.py file"""
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"crew_backup_{timestamp}.py"
        
        print(f"[BACKUP] Backing up original file to: {backup_file}")
        
        try:
            with open(self.crew_file, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            print("[OK] Backup successful")
            return True
        
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            return False
    
    def update_crew_file(self, config):
        """Update crew.py file"""
        print(f"[UPDATE] Updating {self.crew_file}")
        
        try:
            with open(self.crew_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ========== Update Agent definition ==========
            agent_config = config['customer_service_agent']
            role = agent_config.get('role', 'Customer Service Representative')
            goal = agent_config.get('goal', 'Provide friendly and professional service to customers')
            backstory = agent_config.get('backstory', 'You are an experienced customer service representative')
            
            # Format backstory, ensure correct indentation
            backstory_lines = backstory.strip().split('\n')
            formatted_backstory = '\n            '.join(line.strip() for line in backstory_lines)
            
            # Build new Agent code
            new_agent_code = f'''customer_service_agent = Agent(
            role="{role}",
            goal="{goal}",
            backstory="""{formatted_backstory}""",
            verbose=False,
            llm=self.llm,
        )'''
            
            # Use regex to replace customer_service_agent definition
            agent_pattern = r'customer_service_agent = Agent\([^)]+\)'
            
            # Check if match is found
            if not re.search(agent_pattern, content, re.DOTALL):
                print("[ERROR] Cannot find customer_service_agent definition in crew.py")
                return False
            
            # Replace Agent content
            content = re.sub(agent_pattern, new_agent_code, content, flags=re.DOTALL)
            print("[OK] Agent configuration updated")
            
            # ========== Update Task definition ==========
            task_config = config['customer_service_task']
            description_template = task_config.get('description_template', '')
            expected_output = task_config.get('expected_output', 'Professional customer service reply')
            
            # Format description_template, ensure correct indentation
            # Note: Preserve {customer_input}, {retrieved_summary}, {context_info} placeholders
            description_lines = description_template.strip().split('\n')
            formatted_description = '\n                '.join(line.strip() for line in description_lines)
            
            # Build new Task code
            new_task_code = f'''customer_service_task = Task(
            description=f"""
                {formatted_description}
            """,
            expected_output="{expected_output}",
            agent=agents["customer_service_agent"]
        )'''
            
            # Use regex to replace customer_service_task definition
            task_pattern = r'customer_service_task = Task\([^)]+\)'
            
            # Check if match is found
            if not re.search(task_pattern, content, re.DOTALL):
                print("[ERROR] Cannot find customer_service_task definition in crew.py")
                return False
            
            # Replace Task content
            content = re.sub(task_pattern, new_task_code, content, flags=re.DOTALL)
            print("[OK] Task configuration updated")
            
            # Write updated content
            with open(self.crew_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[OK] crew.py updated successfully")
            return True
        
        except Exception as e:
            print(f"[ERROR] Update failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_update(self):
        """Verify if update was successful"""
        print("[VERIFY] Verifying update...")
        
        try:
            with open(self.crew_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if contains customer_service_agent
            agent_found = 'customer_service_agent = Agent(' in content
            task_found = 'customer_service_task = Task(' in content
            
            if agent_found and task_found:
                print("[OK] Verification successful: Agent and Task configurations updated")
                return True
            else:
                if not agent_found:
                    print("[ERROR] Verification failed: customer_service_agent configuration not found")
                if not task_found:
                    print("[ERROR] Verification failed: customer_service_task configuration not found")
                return False
        
        except Exception as e:
            print(f"[ERROR] Verification failed: {e}")
            return False
    
    def fetch_ragflow_chat_id(self):
        """Get first chat_id from RAGFlow"""
        if create_ragflow_client is None:
            print("[SKIP] RAGFlow client unavailable, skipping chat_id retrieval")
            return None
        
        print("\n[RAGFLOW] Getting chat list from RAGFlow...")
        
        try:
            # Create RAGFlow client
            client = create_ragflow_client()
            
            # Get chat list
            chats = client.list_chats(page=1, page_size=10)
            
            if not chats:
                print("[WARNING] No available chats in RAGFlow")
                print("[HINT] Please create a chat (conversation assistant) in RAGFlow Web interface")
                return None
            
            # Get first chat ID
            first_chat = chats[0]
            chat_id = first_chat.get('id')
            chat_name = first_chat.get('name', 'Unknown')
            
            print(f"[OK] Found RAGFlow chat: {chat_name} (ID: {chat_id})")
            print(f"[INFO] Found {len(chats)} chats in total")
            
            return chat_id
        
        except Exception as e:
            print(f"[ERROR] Failed to get RAGFlow chat_id: {e}")
            return None
    
    def update_env_file(self, chat_id: str):
        """Update RAGFLOW_CHAT_ID in .env file"""
        print(f"\n[UPDATE] Updating RAGFLOW_CHAT_ID in .env file...")
        
        # If .env doesn't exist, copy from env.template
        if not self.env_file.exists():
            if self.env_template.exists():
                print(f"[INFO] .env file does not exist, creating from env.template")
                with open(self.env_template, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(self.env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                print(f"[ERROR] Both .env and env.template do not exist")
                return False
        
        try:
            # Read .env file
            with open(self.env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Update RAGFLOW_CHAT_ID
            updated = False
            new_lines = []
            
            for line in lines:
                if line.strip().startswith('RAGFLOW_CHAT_ID='):
                    new_lines.append(f'RAGFLOW_CHAT_ID={chat_id}\n')
                    updated = True
                    print(f"[OK] Updated RAGFLOW_CHAT_ID={chat_id}")
                else:
                    new_lines.append(line)
            
            # If RAGFLOW_CHAT_ID not found, add it
            if not updated:
                # Add to RAGFlow configuration section
                for i, line in enumerate(new_lines):
                    if 'RAGFlow' in line or 'RAGFLOW' in line:
                        # Find RAGFlow configuration section, add after it
                        insert_pos = i + 1
                        while insert_pos < len(new_lines) and new_lines[insert_pos].strip() and not new_lines[insert_pos].startswith('#'):
                            insert_pos += 1
                        new_lines.insert(insert_pos, f'RAGFLOW_CHAT_ID={chat_id}\n')
                        updated = True
                        print(f"[OK] Added RAGFLOW_CHAT_ID={chat_id}")
                        break
                
                # If still no suitable position found, add to end of file
                if not updated:
                    new_lines.append(f'\nRAGFLOW_CHAT_ID={chat_id}\n')
                    print(f"[OK] Added RAGFLOW_CHAT_ID={chat_id}")
            
            # Write back to file
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print("[OK] .env file updated successfully")
            return True
        
        except Exception as e:
            print(f"[ERROR] Failed to update .env file: {e}")
            return False
    
    def run(self, auto_yes=False):
        """Execute update process
        
        Args:
            auto_yes: Whether to auto-confirm (skip interactive prompts)
        """
        print("\n" + "="*60)
        print("AI Agent Prompt Update Tool")
        print("="*60 + "\n")
        
        # 1. Load configuration
        config = self.load_config()
        
        agent_config = config['customer_service_agent']
        task_config = config['customer_service_task']
        
        print("\n[CONFIG] Current configuration:")
        print("\n[Agent Configuration]")
        print(f"  Role: {agent_config.get('role')}")
        print(f"  Goal: {agent_config.get('goal')}")
        print(f"  Backstory: {agent_config.get('backstory', '')[:50]}...")
        print("\n[Task Configuration]")
        print(f"  Description template: {task_config.get('description_template', '')[:80]}...")
        print(f"  Expected output: {task_config.get('expected_output')}")
        
        # 2. Ask if continue (unless auto_yes is set)
        if not auto_yes:
            print("\n[WARNING] About to update crew.py file (Agent + Task)")
            response = input("Continue? (y/n): ").lower().strip()
            
            if response != 'y':
                print("[CANCEL] Operation cancelled")
                sys.exit(0)
        else:
            print("\n[AUTO] Auto-confirm mode, skipping interactive prompts")
        
        # 3. Backup original file
        if not self.backup_crew_file():
            print("[ERROR] Operation aborted due to backup failure")
            sys.exit(1)
        
        # 4. Update file
        if not self.update_crew_file(config):
            print("[ERROR] Update failed, please check error messages")
            sys.exit(1)
        
        # 5. Verify update
        if not self.verify_update():
            print("[ERROR] Verification failed")
            sys.exit(1)
        
        # 6. Get and update RAGFlow chat_id
        chat_id = self.fetch_ragflow_chat_id()
        if chat_id:
            self.update_env_file(chat_id)
        else:
            print("[SKIP] Skipping .env file update")
        
        print("\n" + "="*60)
        print("[SUCCESS] Update completed!")
        print("="*60)
        print("\n[NEXT] Next steps:")
        print("  1. Restart backend service to apply changes")
        print("  2. Test if the new prompt meets expectations")
        print(f"  3. If rollback needed, use backup file: {self.backup_dir}")
        if chat_id:
            print(f"  4. RAGFlow chat_id has been updated in .env file: {chat_id}")
        print("\n")


def main():
    """Main function"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI Agent Prompt Update Tool')
    parser.add_argument('--yes', '-y', action='store_true', 
                        help='Auto-confirm, skip interactive prompts')
    args = parser.parse_args()
    
    try:
        updater = AgentPromptUpdater()
        updater.run(auto_yes=args.yes)
    except KeyboardInterrupt:
        print("\n\n[CANCEL] Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

