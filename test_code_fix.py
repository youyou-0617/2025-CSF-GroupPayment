#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试兑换码功能修复

此脚本用于验证兑换码使用功能的修复，特别是检查用户不在群组中时使用兑换码的情况。
"""

import requests
import json

# API 地址
API = "http://localhost:8001"

# 测试用户信息
TEST_USER_ID = 2  # 假设ID为2的用户是测试用户
TEST_GROUP_ID = 1  # 假设ID为1的群组是测试群组
NON_MEMBER_USER_ID = 3  # 假设ID为3的用户不在测试群组中

def test_code_creation():
    """测试创建兑换码"""
    print("\n1. 测试创建兑换码...")
    try:
        response = requests.post(
            f"{API}/codes",
            json={"amount": 100.0}
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            code_data = response.json()
            print(f"创建兑换码成功: {code_data['code']} (金额: {code_data['amount']})")  # API只在创建时返回完整兑换码
            print(f"兑换码前缀: {code_data['code_prefix']}")
            return code_data['code']
        else:
            print(f"创建兑换码失败: {response.text}")
            return None
    except Exception as e:
        print(f"创建兑换码出错: {str(e)}")
        return None

def test_code_use_by_member(code, user_id, group_id):
    """测试群组成员使用兑换码"""
    print(f"\n2. 测试用户 {user_id} 在群组 {group_id} 中使用兑换码...")
    try:
        response = requests.post(
            f"{API}/codes/use",
            json={
                "code": code,
                "group_id": group_id,
                "user_id": user_id
            }
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"使用兑换码成功: {result['message']}")
            print(f"金额: {result['amount']}")
            print(f"新余额: {result['new_balance']}")
            return True
        else:
            print(f"使用兑换码失败: {response.json().get('detail', response.text)}")
            return False
    except Exception as e:
        print(f"使用兑换码出错: {str(e)}")
        return False

def test_code_use_by_non_member(code, user_id, group_id):
    """测试非群组成员使用兑换码"""
    print(f"\n3. 测试非群组成员 {user_id} 在群组 {group_id} 中使用兑换码...")
    try:
        response = requests.post(
            f"{API}/codes/use",
            json={
                "code": code,
                "group_id": group_id,
                "user_id": user_id
            }
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 400 and "用户不在该群组中" in response.json().get('detail', ''):
            print(f"使用兑换码失败（预期行为）: {response.json().get('detail')}")
            print("✅ 修复验证成功: 非群组成员无法使用兑换码")
            return True
        elif response.status_code == 200:
            print("❌ 修复验证失败: 非群组成员能够使用兑换码")
            return False
        else:
            print(f"使用兑换码失败: {response.json().get('detail', response.text)}")
            print("⚠️  修复验证结果不确定: 出现了意外的错误信息")
            return None
    except Exception as e:
        print(f"使用兑换码出错: {str(e)}")
        return None

def test_get_user_groups(user_id):
    """测试获取用户的群组信息"""
    print(f"\n4. 获取用户 {user_id} 的群组信息...")
    try:
        response = requests.get(f"{API}/users/{user_id}/groups")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"用户 {data['user_name']} 加入了 {len(data['groups'])} 个群组:")
            for group in data['groups']:
                print(f"  - 群组ID: {group['group_id']}, 群组名称: {group['group_name']}, 余额: {group['balance']}")
            return data['groups']
        else:
            print(f"获取群组信息失败: {response.text}")
            return []
    except Exception as e:
        print(f"获取群组信息出错: {str(e)}")
        return []

def main():
    """主测试函数"""
    print("开始测试兑换码功能修复...")
    
    # 1. 创建测试用的兑换码
    code = test_code_creation()
    if not code:
        print("\n❌ 测试失败: 无法创建兑换码")
        return
    
    # 2. 获取测试用户的群组信息（用于验证用户确实在某个群组中）
    user_groups = test_get_user_groups(TEST_USER_ID)
    if not user_groups:
        print("\n⚠️  警告: 测试用户没有加入任何群组，请先添加用户到群组")
    
    # 3. 测试群组成员使用兑换码
    member_success = test_code_use_by_member(code, TEST_USER_ID, TEST_GROUP_ID)
    
    # 4. 创建新的兑换码用于测试非成员使用
    code2 = test_code_creation()
    if code2:
        # 5. 测试非群组成员使用兑换码
        non_member_result = test_code_use_by_non_member(code2, NON_MEMBER_USER_ID, TEST_GROUP_ID)
        
        # 6. 总结测试结果
        print("\n" + "-" * 50)
        print("测试总结:")
        if member_success:
            print("✅ 群组成员可以正常使用兑换码")
        else:
            print("❌ 群组成员无法使用兑换码（这可能是正常的，取决于测试用户是否在测试群组中）")
        
        if non_member_result is True:
            print("✅ 非群组成员无法使用兑换码（修复成功）")
        elif non_member_result is False:
            print("❌ 非群组成员仍然可以使用兑换码（修复失败）")
        else:
            print("⚠️  非群组成员使用兑换码的测试结果不确定")
        
        if member_success and non_member_result is True:
            print("\n🎉 兑换码功能修复验证通过！")
        else:
            print("\n⚠️  兑换码功能修复验证不完全通过，请检查测试结果")
    else:
        print("\n❌ 测试失败: 无法创建第二个兑换码用于非成员测试")

if __name__ == "__main__":
    main()