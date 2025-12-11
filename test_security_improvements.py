#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全改进测试脚本

测试密码哈希和兑换码的安全功能（不依赖数据库）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import bcrypt
from datetime import datetime, timedelta
from app import crud


def test_password_security():
    """测试密码安全功能"""
    print("\n=== 测试密码安全功能 ===")
    
    # 测试1: 密码哈希生成
    print("\n1. 测试密码哈希生成...")
    password = "SecurePassword123!"
    hashed_password = crud.hash_password(password)
    
    print(f"原始密码: {password}")
    print(f"哈希后的密码: {hashed_password}")
    print(f"哈希长度: {len(hashed_password)}")
    print(f"是否包含盐值 (bcrypt格式): {hashed_password.startswith('$2b$')}")
    
    # 测试2: 密码验证
    print("\n2. 测试密码验证...")
    is_valid = crud.verify_password(password, hashed_password)
    is_invalid = crud.verify_password("WrongPassword", hashed_password)
    
    print(f"正确密码验证结果: {is_valid} (预期: True)")
    print(f"错误密码验证结果: {is_invalid} (预期: False)")
    
    # 测试3: 相同密码生成不同哈希（验证盐值工作正常）
    print("\n3. 测试盐值功能...")
    hashed_password2 = crud.hash_password(password)
    print(f"相同密码的第二次哈希: {hashed_password2}")
    print(f"两次哈希是否不同: {hashed_password != hashed_password2} (预期: True)")
    print(f"两次哈希都能验证通过: {crud.verify_password(password, hashed_password) and crud.verify_password(password, hashed_password2)} (预期: True)")
    
    return is_valid and not is_invalid and (hashed_password != hashed_password2)


def test_code_generation():
    """测试兑换码生成功能（不依赖数据库）"""
    print("\n=== 测试兑换码生成功能 ===")
    
    # 测试1: 兑换码生成
    print("\n1. 测试兑换码生成...")
    code = crud.generate_code()
    print(f"生成的兑换码: {code}")
    print(f"兑换码长度: {len(code)} (预期: 12)")
    print(f"是否包含特殊字符: {any(c in '!@#$%^&*' for c in code)} (预期: 可能为True)")
    
    # 测试2: 生成多个不同的兑换码
    print("\n2. 测试兑换码唯一性...")
    codes = [crud.generate_code() for _ in range(10)]  # 生成更多以更好地测试唯一性
    print(f"生成的10个兑换码: {codes}")
    print(f"是否全部唯一: {len(set(codes)) == 10} (预期: True)")
    
    # 测试3: 检查兑换码字符集
    print("\n3. 测试兑换码字符集...")
    all_chars = ''.join(codes)
    has_uppercase = any(c.isupper() for c in all_chars)
    has_lowercase = any(c.islower() for c in all_chars)
    has_digit = any(c.isdigit() for c in all_chars)
    has_special = any(c in '!@#$%^&*' for c in all_chars)
    
    print(f"包含大写字母: {has_uppercase}")
    print(f"包含小写字母: {has_lowercase}")
    print(f"包含数字: {has_digit}")
    print(f"包含特殊字符: {has_special}")
    
    return len(code) == 12 and len(set(codes)) == 10


def main():
    """主测试函数"""
    print("开始安全改进测试...")
    
    tests = [
        ("密码安全测试", test_password_security),
        ("兑换码生成测试", test_code_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print(f"\n✓ {test_name}: {'通过' if result else '失败'}")
        except Exception as e:
            results.append(False)
            print(f"\n✗ {test_name}: 执行错误")
            print(f"错误信息: {e}")
            import traceback
            traceback.print_exc()
    
    # 汇总结果
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    passed = sum(results)
    total = len(results)
    
    print(f"通过测试: {passed}/{total}")
    print(f"通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有安全改进测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败，需要检查安全实现。")
        return 1


if __name__ == "__main__":
    sys.exit(main())