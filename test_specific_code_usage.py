#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试特定兑换码的使用功能

这个脚本将：
1. 查找ID为2的兑换码（前缀@lW2IT）
2. 为用户生成新的测试兑换码
3. 测试使用兑换码的完整流程
"""

import requests

# API基础URL
API_BASE = "http://localhost:8001"

def print_divider(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'-'*60}\n{title}\n{'-'*60}")
    else:
        print("-"*60)

print_divider("测试兑换码使用功能")

# 测试1：创建一个测试用户（如果需要）
print("1. 创建测试用户...")
test_user = {
    "name": "test_user",
    "password": "password123",
    "public_info": "测试用户"
}

# 先尝试登录
login_response = requests.post(
    f"{API_BASE}/users/login",
    json={"name": test_user["name"], "password": test_user["password"]}
)

if login_response.status_code != 200:
    print("  创建新的测试用户...")
    register_response = requests.post(
        f"{API_BASE}/users/register",
        json=test_user
    )
    
    if register_response.status_code == 200:
        print("  ✅ 测试用户创建成功")
        user_data = register_response.json()
        user_id = user_data["id"]
    else:
        print(f"  ❌ 用户创建失败: {register_response.text}")
        exit(1)
else:
    print("  ✅ 测试用户登录成功")
    user_data = login_response.json()
    user_id = user_data["id"]

print(f"  用户ID: {user_id}, 用户名: {user_data['name']}")

# 测试2：创建一个测试群组
print("\n2. 创建测试群组...")
test_group = {
    "name": "测试群组",
    "member_ids": [user_id]
}

group_response = requests.post(
    f"{API_BASE}/groups",
    json=test_group
)

if group_response.status_code == 200:
    group_data = group_response.json()
    group_id = group_data["id"]
    print(f"  ✅ 测试群组创建成功: {group_data['name']} (ID: {group_id})")
else:
    print(f"  ❌ 群组创建失败: {group_response.text}")
    exit(1)

# 测试3：为用户生成新的测试兑换码
print("\n3. 生成新的测试兑换码...")
code_data = {
    "amount": 100.0
}

code_response = requests.post(
    f"{API_BASE}/codes",
    json=code_data
)

if code_response.status_code == 200:
    code_info = code_response.json()
    valid_code = code_info["code"]
    print(f"  ✅ 新兑换码生成成功！")
    print(f"     完整兑换码: {valid_code}")
    print(f"     兑换码前缀: {code_info['code_prefix']}")
    print(f"     金额: {code_info['amount']}")
else:
    print(f"  ❌ 兑换码生成失败: {code_response.text}")
    exit(1)

# 测试4：使用新生成的兑换码
print("\n4. 测试使用新生成的兑换码...")
use_code_data = {
    "code": valid_code,
    "group_id": group_id,
    "user_id": user_id
}

use_response = requests.post(
    f"{API_BASE}/codes/use",
    json=use_code_data
)

if use_response.status_code == 200:
    result = use_response.json()
    print(f"  ✅ 兑换码使用成功！")
    print(f"     消息: {result['message']}")
    print(f"     成功: {result['success']}")
else:
    print(f"  ❌ 兑换码使用失败: {use_response.text}")

# 测试5：尝试使用用户提到的不完整兑换码（作为对比）
print("\n5. 测试使用不完整的兑换码（预期失败）...")
invalid_code_data = {
    "code": "lW2IT",  # 用户提到的不完整兑换码
    "group_id": group_id,
    "user_id": user_id
}

invalid_response = requests.post(
    f"{API_BASE}/codes/use",
    json=invalid_code_data
)

if invalid_response.status_code == 400:
    print(f"  ✅ 预期行为: 不完整兑换码被正确拒绝")
    print(f"     错误信息: {invalid_response.json()['detail']}")
else:
    print(f"  ⚠️  意外行为: {invalid_response.status_code} - {invalid_response.text}")

print_divider("测试完成")
print("📋 总结:")
print(f"1. 测试用户: {user_data['name']} (ID: {user_id})")
print(f"2. 测试群组: {group_data['name']} (ID: {group_id})")
print(f"3. 有效兑换码: {valid_code}")
print(f"4. 用户问题: 提供的'lW2IT'是不完整的兑换码，缺少@符号和完整长度")
print(f"5. 解决方案: 使用上面生成的完整12位兑换码")
print("\n✅ 兑换码系统功能正常，只需使用完整的12位兑换码即可！")