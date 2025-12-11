#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查特定兑换码的状态和验证过程

该脚本用于检查用户报告的兑换码'lW2IT'的情况，包括：
1. 检查数据库中是否存在相关兑换码
2. 验证兑换码的格式和哈希值
3. 测试兑换过程
4. 提供详细的诊断信息
"""

import requests
import bcrypt
import hashlib
import re
import sys

# API基础URL
API = "http://localhost:8001"

# 用户报告的兑换码
REPORTED_CODE = "lW2IT"

def print_divider(title=""):
    """打印分隔线，用于分隔不同的测试步骤"""
    print("=" * 60)
    if title:
        print(f"{title:^60}")
        print("=" * 60)

def check_code_format(code):
    """检查兑换码格式"""
    print_divider("检查兑换码格式")
    
    print(f"用户报告的兑换码: '{code}'")
    print(f"长度: {len(code)} 个字符")
    print(f"字符集: {set(code)}")
    
    # 检查是否符合预期格式
    # 根据代码，兑换码应该是32位的字母数字组合
    expected_length = 32
    
    if len(code) != expected_length:
        print(f"❌ 格式警告：兑换码长度应该是 {expected_length} 位，当前是 {len(code)} 位")
        print("   注意：'lW2IT'可能只是兑换码的前缀（前6位）")
        return False
    
    # 检查是否只包含字母和数字
    if not re.match(r'^[A-Za-z0-9]+$', code):
        print("❌ 格式警告：兑换码应该只包含字母和数字")
        return False
    
    print("✅ 兑换码格式符合要求")
    return True

def test_generate_new_code():
    """测试生成新的完整兑换码，用于对比"""
    print_divider("测试生成新兑换码")
    
    try:
        # 使用管理员身份生成新兑换码
        admin_login = requests.post(f"{API}/users/login", json={
            "name": "admin",
            "password": "admin123"
        })
        
        if admin_login.status_code != 200:
            print(f"❌ 管理员登录失败: {admin_login.json().get('detail', '未知错误')}")
            return None
        
        response = requests.post(f"{API}/codes", json={"amount": 100.0})
        
        if response.status_code == 200:
            code_info = response.json()
            print(f"✅ 成功生成新兑换码:")
            print(f"   完整兑换码: {code_info['code']}")
            print(f"   长度: {len(code_info['code'])} 位")
            print(f"   前缀 (前6位): {code_info['code_prefix']}")
            print(f"   金额: ¥{code_info['amount']:.2f}")
            return code_info
        else:
            print(f"❌ 生成兑换码失败: {response.json().get('detail', '未知错误')}")
            return None
    except Exception as e:
        print(f"❌ 生成兑换码出错: {str(e)}")
        return None

def check_code_in_database():
    """检查数据库中是否存在相关兑换码"""
    print_divider("检查数据库中的兑换码")
    
    try:
        # 获取所有兑换码
        response = requests.get(f"{API}/codes")
        
        if response.status_code == 200:
            codes = response.json()
            print(f"✅ 获取到 {len(codes)} 个兑换码记录")
            
            if codes:
                print("\n所有兑换码记录:")
                for i, code in enumerate(codes, 1):
                    status = "已使用" if code['is_used'] else "未使用"
                    print(f"   {i}. ID: {code['id']}, 前缀: {code['code_prefix']}, "
                          f"状态: {status}, 金额: ¥{code['amount']:.2f}")
                    
                    # 检查是否与用户报告的前缀匹配
                    if code['code_prefix'] == REPORTED_CODE:
                        print(f"   🔍 发现匹配前缀的兑换码!")
                        return code
            else:
                print("   数据库中没有兑换码记录")
                return None
        else:
            print(f"❌ 获取兑换码列表失败: {response.json().get('detail', '未知错误')}")
            return None
    except Exception as e:
        print(f"❌ 检查数据库出错: {str(e)}")
        return None

def test_bcrypt_hash(code):
    """测试bcrypt哈希生成（用于调试）"""
    print_divider("测试bcrypt哈希生成")
    
    try:
        # 模拟系统中的哈希生成过程
        code_bytes = code.encode('utf-8')
        
        # 生成盐值
        salt = bcrypt.gensalt()
        print(f"生成的盐值 (bytes): {salt}")
        print(f"盐值长度: {len(salt)} 字节")
        
        # 生成哈希值
        hashed = bcrypt.hashpw(code_bytes, salt)
        print(f"生成的哈希值 (bytes): {hashed}")
        print(f"哈希值长度: {len(hashed)} 字节")
        
        # 测试验证
        is_valid = bcrypt.checkpw(code_bytes, hashed)
        print(f"验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        
        return {
            'salt': salt,
            'hash': hashed,
            'is_valid': is_valid
        }
    except Exception as e:
        print(f"❌ bcrypt测试出错: {str(e)}")
        return None

def test_existing_user_and_group():
    """测试是否存在可用的用户和群组用于兑换测试"""
    print_divider("测试可用的用户和群组")
    
    try:
        # 获取所有用户
        users_response = requests.get(f"{API}/users")
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"✅ 发现 {len(users)} 个用户")
            
            if users:
                print("\n用户列表:")
                for user in users:
                    print(f"   ID: {user['id']}, 用户名: {user['name']}")
            else:
                print("   没有可用用户")
                return None, None
        else:
            print(f"❌ 获取用户列表失败")
            return None, None
        
        # 获取所有群组
        groups_response = requests.get(f"{API}/groups")
        if groups_response.status_code == 200:
            groups = groups_response.json()
            print(f"\n✅ 发现 {len(groups)} 个群组")
            
            if groups:
                print("\n群组列表:")
                for group in groups:
                    print(f"   ID: {group['id']}, 名称: {group['name']}, 成员数: {len(group.get('members', []))}")
                    
                # 返回第一个用户和第一个群组用于测试
                return users[0], groups[0]
            else:
                print("   没有可用群组")
                return None, None
        else:
            print(f"❌ 获取群组列表失败")
            return None, None
            
    except Exception as e:
        print(f"❌ 测试用户和群组出错: {str(e)}")
        return None, None

def test_code_redeem(code, user, group):
    """测试兑换码的使用过程"""
    if not code or not user or not group:
        print("❌ 缺少必要的测试数据，无法进行兑换测试")
        return False
    
    print_divider("测试兑换码使用过程")
    
    print(f"使用兑换码: '{code}'")
    print(f"用户: {user['name']} (ID: {user['id']})")
    print(f"群组: {group['name']} (ID: {group['id']})")
    
    try:
        # 先获取用户当前余额
        balance_response = requests.get(f"{API}/users/{user['id']}/groups")
        if balance_response.status_code == 200:
            user_groups = balance_response.json()
            current_balance = 0.0
            
            for g in user_groups['groups']:
                if g['group_id'] == group['id']:
                    current_balance = g['balance']
                    break
            
            print(f"当前余额: ¥{current_balance:.2f}")
        else:
            print(f"❌ 获取当前余额失败")
        
        # 尝试使用兑换码
        redeem_data = {
            "code": code,
            "group_id": group['id'],
            "user_id": user['id']
        }
        
        redeem_response = requests.post(f"{API}/codes/use", json=redeem_data)
        
        print(f"\n兑换请求结果:")
        print(f"状态码: {redeem_response.status_code}")
        
        if redeem_response.status_code == 200:
            result = redeem_response.json()
            print("✅ 兑换成功!")
            print(f"   增加金额: ¥{result['amount']:.2f}")
            print(f"   新余额: ¥{result['new_balance']:.2f}")
            return True
        else:
            error = redeem_response.json().get('detail', '未知错误')
            print(f"❌ 兑换失败: {error}")
            return False
            
    except Exception as e:
        print(f"❌ 兑换测试出错: {str(e)}")
        return False

def check_code_prefix_match():
    """检查用户报告的前缀是否与数据库中的兑换码匹配"""
    print_divider("检查前缀匹配")
    
    try:
        # 获取所有兑换码并检查前缀
        response = requests.get(f"{API}/codes")
        
        if response.status_code == 200:
            codes = response.json()
            matching_codes = []
            
            print(f"用户报告的前缀: '{REPORTED_CODE}'")
            print(f"数据库中共有 {len(codes)} 个兑换码")
            
            for code in codes:
                print(f"   数据库记录 - ID: {code['id']}, 前缀: {code['code_prefix']}, "
                      f"状态: {'已使用' if code['is_used'] else '未使用'}")
                
                if code['code_prefix'] == REPORTED_CODE:
                    matching_codes.append(code)
                    print(f"   🔍 发现匹配前缀的兑换码!")
            
            if matching_codes:
                print(f"\n✅ 找到 {len(matching_codes)} 个匹配前缀的兑换码")
                return matching_codes
            else:
                print(f"\n❌ 没有找到与前缀 '{REPORTED_CODE}' 匹配的兑换码")
                return []
        else:
            print(f"❌ 获取兑换码列表失败")
            return []
            
    except Exception as e:
        print(f"❌ 前缀匹配检查出错: {str(e)}")
        return []

def main():
    """主函数"""
    print_divider("开始兑换码问题诊断")
    print(f"用户报告的兑换码: '{REPORTED_CODE}'")
    print("=" * 60)
    
    try:
        # 步骤1: 检查用户报告的兑换码格式
        check_code_format(REPORTED_CODE)
        
        # 步骤2: 检查数据库中是否存在相关兑换码
        found_code = check_code_in_database()
        
        # 步骤3: 生成新的完整兑换码用于对比
        new_code = test_generate_new_code()
        
        # 步骤4: 检查前缀匹配情况
        matching_codes = check_code_prefix_match()
        
        # 步骤5: 测试bcrypt哈希生成（使用完整的新兑换码）
        if new_code:
            test_bcrypt_hash(new_code['code'])
        
        # 步骤6: 测试可用的用户和群组
        test_user, test_group = test_existing_user_and_group()
        
        # 步骤7: 测试兑换过程（如果有匹配的兑换码和测试账户）
        if matching_codes and test_user and test_group:
            print("\n📝 注意：由于您报告的'lW2IT'看起来是一个前缀而不是完整兑换码，")
            print("我们将使用新生成的完整兑换码进行测试：")
            
            if new_code:
                test_code_redeem(new_code['code'], test_user, test_group)
        
        # 最终诊断结果
        print_divider("最终诊断结果")
        
        print("📋 问题分析：")
        print(f"1. 用户报告的字符串: '{REPORTED_CODE}' (6个字符)")
        print(f"2. 完整兑换码应为: 32个字符的字母数字组合")
        print(f"3. 数据库中{'' if matching_codes else '未'}找到匹配前缀的兑换码")
        
        print("\n🔍 可能的原因：")
        if len(REPORTED_CODE) != 32:
            print("1. ❌ 兑换码不完整：您提供的'lW2IT'可能只是兑换码的前6位前缀")
            print("   完整的兑换码应该是32位长，例如：XXXXXX...（6位前缀 + 26位剩余部分）")
        
        if not matching_codes:
            print("2. ❌ 数据库中没有匹配此前缀的兑换码")
            print("   可能原因：兑换码已被使用、过期或从未生成")
        else:
            for code in matching_codes:
                if code['is_used']:
                    print("3. ❌ 兑换码已被使用")
                else:
                    print("4. ℹ️  找到了匹配前缀的未使用兑换码，但需要完整的32位兑换码")
        
        print("\n💡 建议解决方案：")
        print("1. 获取完整的32位兑换码（管理员生成时提供的完整字符串）")
        print("2. 确保输入的兑换码没有空格、大小写错误或其他字符")
        print("3. 请管理员重新生成一个新的完整兑换码")
        
        if new_code:
            print("\n✅ 示例：")
            print(f"   完整兑换码: {new_code['code']}")
            print(f"   前缀: {new_code['code_prefix']} (前6位)")
            print(f"   金额: ¥{new_code['amount']:.2f}")
            print("   请使用完整的32位兑换码进行兑换")
            
    except KeyboardInterrupt:
        print("\n\n🛑 诊断被用户中断")
    except Exception as e:
        print(f"\n❌ 诊断过程中发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()