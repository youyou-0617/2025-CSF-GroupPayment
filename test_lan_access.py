#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
局域网访问测试脚本
用于验证 Group Payment System 的局域网访问功能
"""

import requests
import sys

# 服务器局域网IP地址
SERVER_IP = "10.31.1.192"

# 测试的端口和服务
TESTS = [
    {
        "name": "后端API服务器",
        "url": f"http://{SERVER_IP}:8001/users",
        "method": "get",
        "expected_status": 200
    },
    {
        "name": "用户前端应用",
        "url": f"http://{SERVER_IP}:8501",
        "method": "get",
        "expected_status": 200
    },
    {
        "name": "管理员前端应用",
        "url": f"http://{SERVER_IP}:8502",
        "method": "get",
        "expected_status": 200
    },
    {
        "name": "API文档",
        "url": f"http://{SERVER_IP}:8001/docs",
        "method": "get",
        "expected_status": 200
    }
]

def test_service(test):
    """测试单个服务的访问情况"""
    print(f"\n=== 测试 {test['name']} ===")
    print(f"URL: {test['url']}")
    
    try:
        if test['method'].lower() == 'post':
            response = requests.post(test['url'], json=test.get('data', {}), timeout=10)
        else:
            response = requests.get(test['url'], timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == test['expected_status']:
            print("✅ 测试通过!")
            return True
        else:
            print(f"❌ 测试失败: 期望状态码 {test['expected_status']}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到服务器")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 服务器响应时间过长")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")
        return False

def main():
    """主函数：运行所有测试"""
    print("🚀 开始测试 Group Payment System 局域网访问功能...")
    print(f"🌐 测试服务器IP: {SERVER_IP}")
    print("-" * 60)
    
    results = []
    for test in TESTS:
        result = test_service(test)
        results.append(result)
    
    print("\n" + "-" * 60)
    print("📊 测试结果汇总")
    print(f"总测试数: {len(TESTS)}")
    print(f"通过数: {sum(results)}")
    print(f"失败数: {len(TESTS) - sum(results)}")
    
    if all(results):
        print("\n🎉 所有测试通过！局域网访问功能正常。")
        print("\n📋 访问地址汇总：")
        print(f"  - 后端API服务器: http://{SERVER_IP}:8001")
        print(f"  - 用户前端应用: http://{SERVER_IP}:8501")
        print(f"  - 管理员前端应用: http://{SERVER_IP}:8502")
        print(f"  - API文档: http://{SERVER_IP}:8001/docs")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查网络配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())