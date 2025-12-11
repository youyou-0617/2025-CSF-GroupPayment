#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清空所有兑换码数据脚本

该脚本用于清空数据库中所有的兑换码记录，
只保留用户、群组和群组余额信息。
"""

from sqlmodel import Session, select
from app.db import engine, init_db
from app.models import Code, GroupMember, User, Group

def clear_codes():
    """清空所有兑换码数据"""
    print("开始清空兑换码数据...")
    
    try:
        # 初始化数据库（如果需要）
        init_db()
        
        # 创建数据库会话
        with Session(engine) as session:
            # 统计当前兑换码数量
            codes_count = len(session.exec(select(Code)).all())
            print(f"当前数据库中有 {codes_count} 个兑换码")
            
            if codes_count > 0:
                # 删除所有兑换码记录
                session.exec(Code.__table__.delete())
                session.commit()
                print(f"✅ 成功清空 {codes_count} 个兑换码")
            else:
                print("✅ 数据库中没有兑换码需要清空")
            
            # 验证是否清空成功
            remaining_codes = len(session.exec(select(Code)).all())
            print(f"清空后剩余兑换码数量: {remaining_codes}")
            
            # 显示其他数据的保留情况
            users_count = len(session.exec(select(User)).all())
            groups_count = len(session.exec(select(Group)).all())
            members_count = len(session.exec(select(GroupMember)).all())
            
            print("\n其他数据保留情况:")
            print(f"  用户数量: {users_count}")
            print(f"  群组数量: {groups_count}")
            print(f"  群组成员数量: {members_count}")
            
    except Exception as e:
        print(f"❌ 清空兑换码时发生错误: {str(e)}")
        raise

def main():
    """主函数"""
    try:
        clear_codes()
        print("\n🎉 兑换码数据清空完成！")
        print("\n提示:")
        print("- 所有兑换码记录已被删除")
        print("- 用户、群组和余额信息保持不变")
        print("- 可以重新生成新的兑换码进行测试")
    except KeyboardInterrupt:
        print("\n🛑 操作被用户中断")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {str(e)}")

if __name__ == "__main__":
    main()