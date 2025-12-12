#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
兑换码功能修复后的验证测试脚本

该脚本用于验证修复后的兑换码功能是否正常工作，包括：
1. 创建测试用户
2. 创建测试群组
3. 生成新的兑换码
4. 使用兑换码
5. 验证兑换结果和余额更新
"""

import requests
import time
import random

# API基础URL
API = "http://localhost:8001"

# 测试用户信息
TEST_USER_NAME = f"test_user_{random.randint(1000, 9999)}"
TEST_USER_PASSWORD = "testpassword123"
TEST_GROUP_NAME = f"test_group_{random.randint(1000, 9999)}"
TEST_CODE_AMOUNT = 100.0  # 测试兑换码金额

def print_divider(title=""):
    """打印分隔线，用于分隔不同的测试步骤"""
    print("=" * 60)
    if title:
        print(f"{title:^60}")
        print("=" * 60)

def test_create_user():
    """测试创建用户"""
    print_divider("测试创建用户")
    
    user_data = {
        "name": TEST_USER_NAME,
        "password": TEST_USER_PASSWORD,
        "public_info": "测试用户"
    }
    
    try:
        response = requests.post(f"{API}/users/register", json=user_data)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ 用户创建成功: {user_info['name']} (ID: {user_info['id']})")
            return user_info
        else:
            print(f"❌ 用户创建失败: {response.json().get('detail', '未知错误')}")
            return None
    except Exception as e:
        print(f"❌ 用户创建出错: {str(e)}")
        return None

def test_create_group(user_id):
    """测试创建群组并添加用户"""
    print_divider("测试创建群组")
    
    group_data = {
        "name": TEST_GROUP_NAME,
        "member_ids": [user_id]
    }
    
    try:
        response = requests.post(f"{API}/groups", json=group_data)
        if response.status_code == 200:
            group_info = response.json()
            print(f"✅ 群组创建成功: {group_info['name']} (ID: {group_info['id']})")
            # 检查成员信息
            if 'members' in group_info:
                print(f"   成员数量: {len(group_info['members'])}")
            elif 'added_members' in group_info:
                print(f"   添加成员: {group_info['added_members']} 人")
            else:
                print(f"   成员信息: 可用")
            return group_info
        else:
            print(f"❌ 群组创建失败: {response.json().get('detail', '未知错误')}")
            return None
    except Exception as e:
        print(f"❌ 群组创建出错: {str(e)}")
        return None

def test_create_code(admin_name="admin", admin_password="admin123"):
    """测试创建兑换码（需要管理员权限）"""
    print_divider("测试生成兑换码")
    
    # 管理员登录
    login_data = {
        "name": admin_name,
        "password": admin_password
    }
    
    try:
        # 登录获取管理员身份
        login_response = requests.post(f"{API}/users/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ 管理员登录失败: {login_response.json().get('detail', '未知错误')}")
            return None
        
        admin_info = login_response.json()
        print(f"✅ 管理员登录成功: {admin_info['name']} (ID: {admin_info['id']})")
        
        # 创建兑换码
        code_data = {
            "amount": TEST_CODE_AMOUNT
        }
        
        response = requests.post(f"{API}/codes", json=code_data)
        if response.status_code == 200:
            code_info = response.json()
            print(f"✅ 兑换码生成成功!")
            print(f"   兑换码: {code_info['code']}")
            print(f"   显示前缀: {code_info['code_prefix']}")
            print(f"   金额: ¥{code_info['amount']:.2f}")
            print(f"   生成时间: {code_info['created_at']}")
            print(f"   有效期至: {code_info['expires_at']}")
            return code_info
        else:
            print(f"❌ 兑换码生成失败: {response.json().get('detail', '未知错误')}")
            return None
    except Exception as e:
        print(f"❌ 兑换码生成出错: {str(e)}")
        return None

def test_get_user_groups(user_id):
    """获取用户所在的群组信息"""
    print_divider(f"测试获取用户 {user_id} 的群组")
    
    try:
        response = requests.get(f"{API}/users/{user_id}/groups")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 用户 {data['user_name']} 所在的群组:")
            for group in data['groups']:
                print(f"   - 群组ID: {group['group_id']}, 群组名称: {group['group_name']}, 余额: ¥{group['balance']:.2f}")
            return data['groups']
        else:
            print(f"❌ 获取用户群组失败: {response.json().get('detail', '未知错误')}")
            return []
    except Exception as e:
        print(f"❌ 获取用户群组出错: {str(e)}")
        return []

def test_use_code(user_id, group_id, code_str):
    """测试使用兑换码"""
    print_divider(f"测试用户 {user_id} 在群组 {group_id} 中使用兑换码")
    
    # 先获取当前余额
    user_groups = test_get_user_groups(user_id)
    initial_balance = 0.0
    group_name = "未知群组"
    
    for group in user_groups:
        if group['group_id'] == group_id:
            initial_balance = group['balance']
            group_name = group['group_name']
            break
    
    print(f"当前余额: ¥{initial_balance:.2f} (群组: {group_name})")
    
    use_data = {
        "code": code_str,
        "group_id": group_id,
        "user_id": user_id
    }
    
    try:
        response = requests.post(f"{API}/codes/use", json=use_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 兑换码使用成功!")
            print(f"   增加金额: ¥{result['amount']:.2f}")
            print(f"   群组: {result['group_name']}")
            print(f"   新余额: ¥{result['new_balance']:.2f}")
            
            # 验证余额是否正确增加
            expected_balance = initial_balance + TEST_CODE_AMOUNT
            if abs(result['new_balance'] - expected_balance) < 0.01:  # 允许小误差
                print(f"✅ 余额增加正确 (预期: ¥{expected_balance}, 实际: ¥{result['new_balance']})")
                return True
            else:
                print(f"❌ 余额增加不正确 (预期: ¥{expected_balance}, 实际: ¥{result['new_balance']})")
                return False
        else:
            print(f"❌ 兑换码使用失败: {response.json().get('detail', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 兑换码使用出错: {str(e)}")
        return False

def test_use_used_code(user_id, group_id, code_str):
    """测试使用已使用的兑换码"""
    print_divider("测试使用已使用的兑换码")
    
    use_data = {
        "code": code_str,
        "group_id": group_id,
        "user_id": user_id
    }
    
    try:
        response = requests.post(f"{API}/codes/use", json=use_data)
        
        if response.status_code == 400 and "已被使用" in response.json().get('detail', ''):
            print(f"✅ 正确阻止使用已使用的兑换码")
            return True
        else:
            print(f"❌ 没有正确阻止使用已使用的兑换码")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ 测试已使用兑换码出错: {str(e)}")
        return False

def test_view_all_codes():
    """测试查看所有兑换码（验证兑换码状态）"""
    print_divider("测试查看所有兑换码")
    
    try:
        response = requests.get(f"{API}/codes")
        if response.status_code == 200:
            codes = response.json()
            print(f"✅ 获取到 {len(codes)} 个兑换码")
            if codes:
                print("\n最近的兑换码:")
                # 按创建时间排序，显示最近的5个
                codes_sorted = sorted(codes, key=lambda x: x['created_at'], reverse=True)[:5]
                for code in codes_sorted:
                    status = "已使用" if code['is_used'] else "未使用"
                    print(f"   [ID: {code['id']}] 前缀: {code['code_prefix']}, 金额: ¥{code['amount']:.2f}, 状态: {status}")
            return codes
        else:
            print(f"❌ 获取兑换码列表失败: {response.json().get('detail', '未知错误')}")
            return []
    except Exception as e:
        print(f"❌ 获取兑换码列表出错: {str(e)}")
        return []

def main():
    """主测试函数"""
    print_divider("开始兑换码功能修复验证")
    print(f"测试用户: {TEST_USER_NAME}")
    print(f"测试群组: {TEST_GROUP_NAME}")
    print(f"测试金额: ¥{TEST_CODE_AMOUNT}")
    print("=" * 60)
    
    test_results = {
        "create_user": False,
        "create_group": False,
        "create_code": False,
        "use_code": False,
        "use_used_code": False,
        "view_codes": False
    }
    
    try:
        # 步骤1: 创建测试用户
        user_info = test_create_user()
        if user_info:
            test_results["create_user"] = True
        else:
            print("\n❌ 测试失败：无法创建测试用户")
            return
        
        # 步骤2: 创建测试群组
        group_info = test_create_group(user_info['id'])
        if group_info:
            test_results["create_group"] = True
        else:
            print("\n❌ 测试失败：无法创建测试群组")
            return
        
        # 步骤3: 生成兑换码
        code_info = test_create_code()
        if code_info:
            test_results["create_code"] = True
        else:
            print("\n❌ 测试失败：无法生成兑换码")
            return
        
        # 步骤4: 使用兑换码
        if test_use_code(user_info['id'], group_info['id'], code_info['code']):
            test_results["use_code"] = True
        else:
            print("\n❌ 测试失败：兑换码使用功能异常")
        
        # 步骤5: 测试重复使用同一兑换码
        if test_use_used_code(user_info['id'], group_info['id'], code_info['code']):
            test_results["use_used_code"] = True
        else:
            print("\n❌ 测试失败：未能正确处理已使用的兑换码")
        
        # 步骤6: 查看所有兑换码
        codes = test_view_all_codes()
        if codes:
            test_results["view_codes"] = True
        
        # 显示最终测试结果
        print_divider("最终测试结果")
        print("测试项			结果")
        print("-" * 40)
        
        all_passed = True
        for test_name, passed in test_results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{test_name:<20} {status}")
            if not passed:
                all_passed = False
        
        print("-" * 40)
        if all_passed:
            print("🎉 所有测试通过！兑换码功能修复成功！")
            print("\n✅ 修复总结：")
            print("1. 修复了hash_code函数中的bcrypt盐值处理问题")
            print("2. 确保了兑换码哈希生成与验证的一致性")
            print("3. 兑换码现在可以正常创建和使用")
            print("4. 用户余额正确更新")
            print("5. 安全机制（如防止重复使用）正常工作")
        else:
            print("❌ 部分测试失败，需要进一步排查问题")
            
    except KeyboardInterrupt:
        print("\n\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()