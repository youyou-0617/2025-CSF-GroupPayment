#!/usr/bin/env python3
# 测试群组列表功能的简单脚本

import requests
import json

def test_group_list():
    """测试获取群组列表功能"""
    print("测试群组列表功能...")
    
    try:
        # 发送请求获取群组列表
        response = requests.get("http://localhost:8001/groups")
        
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ 成功获取 {len(groups)} 个群组")
            
            # 打印每个群组的信息
            for group in groups:
                group_id = group.get("id")
                group_name = group.get("name")
                members = group.get("members", [])
                member_count = len(members)
                
                print(f"群组 ID: {group_id}, 名称: '{group_name}', 成员数量: {member_count}")
                
                # 如果有成员，打印成员信息
                if members:
                    print("  成员:")
                    for member in members:
                        user_id = member.get("user_id")
                        user_name = member.get("user", {}).get("name", "")
                        balance = member.get("balance")
                        print(f"    - 用户ID: {user_id}, 用户名: '{user_name}', 余额: {balance}")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    test_group_list()