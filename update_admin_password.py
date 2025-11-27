#!/usr/bin/env python
# 更新管理员用户密码的脚本

from app.db import get_session
from app.models import User
from app.crud import hash_password

def update_admin_password():
    """更新管理员用户的密码为admin123"""
    session = next(get_session())
    try:
        # 查找管理员用户
        admin = session.query(User).filter(User.name == 'admin').first()
        
        if admin:
            print(f'管理员用户存在，ID: {admin.id}, 密码状态: {bool(admin.password)}')
            
            # 更新密码为admin123
            admin.password = hash_password('admin123')
            session.commit()
            print('密码已成功更新为admin123')
            
            # 验证更新是否成功
            admin = session.query(User).filter(User.name == 'admin').first()
            if admin and admin.password:
                print('密码更新验证成功')
            else:
                print('密码更新验证失败')
        else:
            print('管理员用户不存在，正在创建...')
            # 创建管理员用户
            admin = User(
                name='admin',
                public_info='系统管理员',
                password=hash_password('admin123')
            )
            session.add(admin)
            session.commit()
            print('管理员用户已创建，用户名: admin, 密码: admin123')
            
    except Exception as e:
        print(f'发生错误: {e}')
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    update_admin_password()