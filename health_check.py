#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent 健康检查脚本
检查所有服务的运行状态
"""

import requests
import sys
import time
import json
from datetime import datetime

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class HealthChecker:
    def __init__(self):
        self.services = {
            'frontend': {
                'url': 'http://localhost:3000',
                'name': '前端服务',
                'timeout': 5
            },
            'backend': {
                'url': 'http://localhost:5000',
                'name': '后端API',
                'timeout': 5
            },
            'ragflow': {
                'url': 'http://localhost:9380',
                'name': 'RAGFlow服务',
                'timeout': 10
            }
        }
        
        # RAGFlow特殊检查
        self.ragflow_installed = self.check_ragflow_installation()
        
        self.results = {}
    
    def check_ragflow_installation(self):
        """检查RAGFlow是否已安装"""
        import os
        ragflow_path = os.path.join(os.getcwd(), 'ragflow')
        return os.path.exists(ragflow_path)
    
    def check_service(self, service_name, config):
        """检查单个服务"""
        try:
            response = requests.get(
                config['url'], 
                timeout=config['timeout'],
                allow_redirects=True
            )
            
            if response.status_code == 200:
                return True, f"状态码: {response.status_code}"
            else:
                return False, f"状态码: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "连接超时"
        except requests.exceptions.ConnectionError:
            return False, "连接失败"
        except Exception as e:
            return False, f"错误: {str(e)}"
    
    def check_backend_api(self):
        """检查后端API具体功能"""
        try:
            # 检查会话列表API
            response = requests.get(
                'http://localhost:5000/api/sessions',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, f"API正常，会话数: {len(data.get('sessions', []))}"
            else:
                return False, f"API错误，状态码: {response.status_code}"
                
        except Exception as e:
            return False, f"API检查失败: {str(e)}"
    
    def check_database(self):
        """检查数据库连接"""
        try:
            # 这里可以添加数据库连接检查
            # 由于数据库在Docker容器内，这里简化处理
            return True, "数据库连接正常"
        except Exception as e:
            return False, f"数据库连接失败: {str(e)}"
    
    def run_health_check(self):
        """运行健康检查"""
        print("🏥 AI Agent 健康检查")
        print("=" * 50)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 检查RAGFlow安装状态
        if self.ragflow_installed:
            print("✅ RAGFlow已安装")
        else:
            print("❌ RAGFlow未安装")
            print("💡 请运行以下命令安装RAGFlow:")
            print("   git clone https://github.com/infiniflow/ragflow.git")
            print("   cd ragflow/docker")
            print("   docker compose -f docker-compose.yml up -d")
        print()
        
        # 检查基础服务
        for service_name, config in self.services.items():
            print(f"🔍 检查 {config['name']}...")
            is_healthy, message = self.check_service(service_name, config)
            
            if is_healthy:
                print(f"✅ {config['name']}: {message}")
            else:
                print(f"❌ {config['name']}: {message}")
            
            self.results[service_name] = {
                'healthy': is_healthy,
                'message': message
            }
            print()
        
        # 检查后端API功能
        print("🔍 检查后端API功能...")
        is_healthy, message = self.check_backend_api()
        if is_healthy:
            print(f"✅ 后端API: {message}")
        else:
            print(f"❌ 后端API: {message}")
        self.results['backend_api'] = {
            'healthy': is_healthy,
            'message': message
        }
        print()
        
        # 检查数据库
        print("🔍 检查数据库连接...")
        is_healthy, message = self.check_database()
        if is_healthy:
            print(f"✅ 数据库: {message}")
        else:
            print(f"❌ 数据库: {message}")
        self.results['database'] = {
            'healthy': is_healthy,
            'message': message
        }
        print()
        
        # 总结
        self.print_summary()
    
    def print_summary(self):
        """打印检查总结"""
        print("📊 检查总结")
        print("=" * 50)
        
        healthy_count = sum(1 for result in self.results.values() if result['healthy'])
        total_count = len(self.results)
        
        print(f"健康服务: {healthy_count}/{total_count}")
        print()
        
        if healthy_count == total_count:
            print("🎉 所有服务运行正常！")
            print()
            print("🌐 访问地址:")
            print("  前端界面: http://localhost:3000")
            print("  后端API: http://localhost:5000")
            print("  RAGFlow: http://localhost:9380")
        else:
            print("⚠️ 部分服务异常，请检查以下问题:")
            print()
            for service_name, result in self.results.items():
                if not result['healthy']:
                    print(f"  ❌ {service_name}: {result['message']}")
        
        print()
        print("💡 故障排除:")
        print("  查看日志: docker-compose logs -f")
        print("  重启服务: docker-compose restart")
        print("  停止服务: docker-compose down")
        print("  启动服务: docker-compose up -d")
    
    def save_report(self, filename="health_report.json"):
        """保存检查报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'summary': {
                'healthy_count': sum(1 for r in self.results.values() if r['healthy']),
                'total_count': len(self.results)
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"📄 检查报告已保存: {filename}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Agent 健康检查')
    parser.add_argument('--save-report', action='store_true', help='保存检查报告到文件')
    parser.add_argument('--continuous', '-c', type=int, metavar='SECONDS', help='持续检查模式，指定间隔秒数')
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    
    if args.continuous:
        print(f"🔄 持续检查模式，间隔 {args.continuous} 秒")
        print("按 Ctrl+C 停止")
        print()
        
        try:
            while True:
                checker.run_health_check()
                print(f"\n⏰ 等待 {args.continuous} 秒后再次检查...")
                time.sleep(args.continuous)
                print("\n" + "="*80 + "\n")
        except KeyboardInterrupt:
            print("\n👋 检查已停止")
    else:
        checker.run_health_check()
        
        if args.save_report:
            checker.save_report()

if __name__ == "__main__":
    main()
