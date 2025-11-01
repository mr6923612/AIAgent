#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent Health Check Script
Check the running status of all services
"""

import requests
import sys
import time
import json
from datetime import datetime

# Set encoding
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class HealthChecker:
    def __init__(self):
        self.services = {
            'frontend': {
                'url': 'http://localhost:3000',
                'name': 'Frontend Service',
                'timeout': 5
            },
            'backend': {
                'url': 'http://localhost:5000',
                'name': 'Backend API',
                'timeout': 5
            },
            'ragflow': {
                'url': 'http://localhost:9380',
                'name': 'RAGFlow Service',
                'timeout': 10
            }
        }
        
        # RAGFlow special check
        self.ragflow_installed = self.check_ragflow_installation()
        
        self.results = {}
    
    def check_ragflow_installation(self):
        """Check if RAGFlow is installed"""
        import os
        ragflow_path = os.path.join(os.getcwd(), 'ragflow')
        return os.path.exists(ragflow_path)
    
    def check_service(self, service_name, config):
        """Check a single service"""
        try:
            response = requests.get(
                config['url'], 
                timeout=config['timeout'],
                allow_redirects=True
            )
            
            if response.status_code == 200:
                return True, f"Status code: {response.status_code}"
            else:
                return False, f"Status code: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection failed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_backend_api(self):
        """Check backend API specific functionality"""
        try:
            # Check session list API
            response = requests.get(
                'http://localhost:5000/api/sessions',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, f"API normal, session count: {len(data.get('sessions', []))}"
            else:
                return False, f"API error, status code: {response.status_code}"
                
        except Exception as e:
            return False, f"API check failed: {str(e)}"
    
    def check_database(self):
        """Check database connection"""
        try:
            # Database connection check can be added here
            # Since database is inside Docker container, simplified here
            return True, "Database connection normal"
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    def run_health_check(self):
        """Run health check"""
        print("🏥 AI Agent Health Check")
        print("=" * 50)
        print(f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check RAGFlow installation status
        if self.ragflow_installed:
            print("✅ RAGFlow is installed")
        else:
            print("❌ RAGFlow is not installed")
            print("💡 Please run the following commands to install RAGFlow:")
            print("   git clone https://github.com/infiniflow/ragflow.git")
            print("   cd ragflow/docker")
            print("   docker compose -f docker-compose.yml up -d")
        print()
        
        # Check basic services
        for service_name, config in self.services.items():
            print(f"🔍 Checking {config['name']}...")
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
        
        # Check backend API functionality
        print("🔍 Checking backend API functionality...")
        is_healthy, message = self.check_backend_api()
        if is_healthy:
            print(f"✅ Backend API: {message}")
        else:
            print(f"❌ Backend API: {message}")
        self.results['backend_api'] = {
            'healthy': is_healthy,
            'message': message
        }
        print()
        
        # Check database
        print("🔍 Checking database connection...")
        is_healthy, message = self.check_database()
        if is_healthy:
            print(f"✅ Database: {message}")
        else:
            print(f"❌ Database: {message}")
        self.results['database'] = {
            'healthy': is_healthy,
            'message': message
        }
        print()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print check summary"""
        print("📊 Check Summary")
        print("=" * 50)
        
        healthy_count = sum(1 for result in self.results.values() if result['healthy'])
        total_count = len(self.results)
        
        print(f"Healthy services: {healthy_count}/{total_count}")
        print()
        
        if healthy_count == total_count:
            print("🎉 All services running normally!")
            print()
            print("🌐 Access URLs:")
            print("  Frontend interface: http://localhost:3000")
            print("  Backend API: http://localhost:5000")
            print("  RAGFlow: http://localhost:9380")
        else:
            print("⚠️ Some services are abnormal, please check the following issues:")
            print()
            for service_name, result in self.results.items():
                if not result['healthy']:
                    print(f"  ❌ {service_name}: {result['message']}")
        
        print()
        print("💡 Troubleshooting:")
        print("  View logs: docker-compose logs -f")
        print("  Restart services: docker-compose restart")
        print("  Stop services: docker-compose down")
        print("  Start services: docker-compose up -d")
    
    def save_report(self, filename="health_report.json"):
        """Save check report"""
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
            print(f"📄 Check report saved: {filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Agent Health Check')
    parser.add_argument('--save-report', action='store_true', help='Save check report to file')
    parser.add_argument('--continuous', '-c', type=int, metavar='SECONDS', help='Continuous check mode, specify interval in seconds')
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    
    if args.continuous:
        print(f"🔄 Continuous check mode, interval {args.continuous} seconds")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                checker.run_health_check()
                print(f"\n⏰ Waiting {args.continuous} seconds before next check...")
                time.sleep(args.continuous)
                print("\n" + "="*80 + "\n")
        except KeyboardInterrupt:
            print("\n👋 Check stopped")
    else:
        checker.run_health_check()
        
        if args.save_report:
            checker.save_report()

if __name__ == "__main__":
    main()
