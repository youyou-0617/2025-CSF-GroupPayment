#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查兑换码数据库并为用户生成新的有效兑换码
"""

from sqlmodel import Session, select
from app.db import engine, init_db
from app.models import Code
from app import crud

# 初始化数据库
init_db()

print("=== 检查数据库中的兑换码 ===")
with Session(engine) as session:
    # 获取所有兑换码（使用正确的SQLModel语法）
    codes = session.exec(select(Code)).all()
    
    print(f"数据库中共有 {len(codes)} 个兑换码")
    for i, code in enumerate(codes, 1):
        status = "已使用" if code.is_used else "未使用"
        print(f"{i}. ID: {code.id}, 前缀: {code.code_prefix}, 金额: {code.amount}, 状态: {status}")
    
    # 生成一个新的测试兑换码给用户
    print("\n=== 为用户生成新的测试兑换码 ===")
    try:
        # 生成一个金额为100的测试兑换码
        test_code = crud.create_code(session, 100.0, 1)  # 管理员ID为1
        print("✅ 新兑换码生成成功！")
        print(f"   完整兑换码: {test_code['code']}")
        print(f"   兑换码前缀: {test_code['code_prefix']}")
        print(f"   金额: {test_code['amount']}")
        print(f"   有效期: {test_code['expires_at']}")
        print("\n📌 使用说明:")
        print("- 请使用完整的12位兑换码")
        print("- 确保您在要使用的群组中")
        print("- 兑换码有效期30天")
    except Exception as e:
        print(f"❌ 生成兑换码失败: {e}")

# 为用户提供简单的使用指南
print("\n=== 兑换码使用指南 ===")
print("问题分析：")
print("- 您提供的'lW2IT'只有5个字符，而系统需要完整的12位兑换码")
print("- 兑换码系统工作正常，只需要使用完整的兑换码")
print("\n如何使用：")
print("1. 登录用户前端应用 (http://localhost:8501)")
print("2. 进入您的群组")
print("3. 使用上面生成的完整12位兑换码")
print("4. 系统会自动增加您在群组中的余额")