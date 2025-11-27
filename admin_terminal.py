#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AA 群组记账系统 - 管理员终端

这个脚本提供命令行界面来管理用户、群组和交易。
"""

import requests
import json
import sys

# API地址 - 管理员终端只能使用本地地址访问，增强安全性（使用端口8001避免冲突）
BASE_URL = "http://localhost:8001"

class AdminTerminal:
    """管理员终端类"""
    
    def __init__(self):
        """初始化"""
        self.running = True
        
    def print_header(self):
        """打印头部信息"""
        print("=" * 60)
        print("📊 AA 群组记账系统 - 管理员终端")
        print("=" * 60)
        print("输入 'help' 查看可用命令")
        print("输入 'exit' 退出系统")
        print("=" * 60)
        print()
    
    def run(self):
        """运行终端"""
        self.print_header()
        
        while self.running:
            try:
                command = input("输入命令 > " ).strip()
                if not command:
                    continue
                
                if command == "exit":
                    print("👋 退出系统。")
                    self.running = False
                    continue
                
                self.parse_command(command)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 退出系统。")
                self.running = False
            except EOFError:
                print("\n👋 退出系统。")
                self.running = False
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                print()
    
    def parse_command(self, command):
        """解析命令"""
        parts = command.split()
        if not parts:
            return
        
        main_cmd = parts[0]
        sub_cmd = parts[1] if len(parts) > 1 else ""
        args = parts[2:]
        
        # 用户管理命令
        if main_cmd == "user":
            self.handle_user_command(sub_cmd, args)
        # 群组管理命令
        elif main_cmd == "group":
            self.handle_group_command(sub_cmd, args)
        # 交易管理命令
        elif main_cmd == "transaction":
            self.handle_transaction_command(sub_cmd, args)
        # 系统命令
        elif main_cmd == "system":
            self.handle_system_command(sub_cmd, args)
        # 帮助命令
        elif main_cmd == "help":
            self.show_help()
        else:
            print(f"❌ 未知命令: {main_cmd}")
            print("输入 'help' 查看可用命令")
    
    def handle_user_command(self, sub_cmd, args):
        """处理用户管理命令"""
        if sub_cmd == "create":
            self.create_user(args)
        elif sub_cmd == "list":
            self.list_users()
        elif sub_cmd == "delete":
            self.delete_user(args)
        else:
            print(f"❌ 用户管理未知子命令: {sub_cmd}")
            print("可用子命令: create, list, delete")
    
    def handle_group_command(self, sub_cmd, args):
        """处理群组管理命令"""
        if sub_cmd == "create":
            self.create_group(args)
        elif sub_cmd == "list":
            self.list_groups()
        elif sub_cmd == "delete":
            self.delete_group(args)
        elif sub_cmd == "detail":
            self.get_group_detail(args)
        elif sub_cmd == "add_member":
            self.add_group_member(args)
        elif sub_cmd == "update_balance":
            self.update_group_balance(args)
        else:
            print(f"❌ 群组管理未知子命令: {sub_cmd}")
            print("可用子命令: create, list, delete, detail, add_member, update_balance")
    
    def handle_transaction_command(self, sub_cmd, args):
        """处理交易管理命令"""
        if sub_cmd == "create_custom":
            self.create_custom_transaction(args)
        elif sub_cmd == "create_aa":
            self.create_aa_transaction(args)
        elif sub_cmd == "list":
            self.list_transactions(args)
        else:
            print(f"❌ 交易管理未知子命令: {sub_cmd}")
            print("可用子命令: create_custom, create_aa, list")
    
    def handle_system_command(self, sub_cmd, args):
        """处理系统命令"""
        if sub_cmd == "reset":
            self.reset_database()
        else:
            print(f"❌ 系统管理未知子命令: {sub_cmd}")
            print("可用子命令: reset")
    
    def show_help(self):
        """显示帮助信息"""
        print("📚 可用命令：")
        print()
        
        print("1. 用户管理")
        print("   user create <用户名> <公开信息>  - 创建新用户")
        print("   user list                      - 列出所有用户")
        print("   user delete <用户ID>           - 删除用户")
        print()
        
        print("2. 群组管理")
        print("   group create <群组名称>        - 创建新群组")
        print("   group list                     - 列出所有群组")
        print("   group delete <群组ID>          - 删除群组")
        print("   group detail <群组ID>          - 查看群组详情")
        print("   group add_member <群组ID> <用户ID> <初始余额> - 添加群组成员")
        print("   group update_balance <群组ID> <用户ID> <新余额> - 更新成员余额")
        print()
        
        print("3. 交易管理")
        print("   transaction create_custom <群组ID> <描述> <总金额> <付款人ID> <用户ID:份额>... - 创建自定义分摊交易")
        print("   transaction create_aa <群组ID> <描述> <总金额> <付款人ID> - 创建AA制交易")
        print("   transaction list <用户ID>      - 查看用户交易记录")
        print()
        
        print("4. 系统")
        print("   help                           - 显示帮助信息")
        print("   exit                           - 退出系统")
        print("   system reset                   - 重置数据库（删除所有用户和群组）")
    
    # 用户管理方法
    def create_user(self, args):
        """创建用户"""
        if len(args) < 2:
            print("❌ 参数错误：user create <用户名> <公开信息>")
            return
        
        name = args[0]
        public_info = " ".join(args[1:])
        
        try:
            response = requests.post(
                f"{BASE_URL}/users",
                json={"name": name, "public_info": public_info}
            )
            
            if response.status_code == 200:
                user = response.json()
                print(f"✅ 用户创建成功！")
                print(f"  用户ID: {user['id']}, 用户名: '{user['name']}', 公开信息: '{user['public_info']}'")
            else:
                print(f"❌ 创建用户失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def list_users(self):
        """列出所有用户"""
        try:
            response = requests.get(f"{BASE_URL}/users")
            
            if response.status_code == 200:
                users = response.json()
                print(f"✅ 共找到 {len(users)} 个用户：")
                print("-" * 50)
                print("{:<10} {:<20} {:<20}".format("用户ID", "用户名", "公开信息"))
                print("-" * 50)
                
                for user in users:
                    print(f"{user['id']:<10} '{user['name']:<18}' '{user['public_info']:<18}'")
                
            else:
                print(f"❌ 获取用户列表失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def delete_user(self, args):
        """删除用户"""
        if len(args) < 1:
            print("❌ 参数错误：user delete <用户ID>")
            return
        
        user_id = args[0]
        
        try:
            response = requests.delete(f"{BASE_URL}/users/{user_id}")
            
            if response.status_code == 200:
                print(f"✅ 用户 {user_id} 删除成功！")
            else:
                print(f"❌ 删除用户失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    # 群组管理方法
    def create_group(self, args):
        """创建群组"""
        if len(args) < 1:
            print("❌ 参数错误：group create <群组名称>")
            return
        
        name = " ".join(args)
        
        try:
            response = requests.post(
                f"{BASE_URL}/groups",
                json={"name": name}
            )
            
            if response.status_code == 200:
                group = response.json()
                print(f"✅ 群组创建成功！")
                print(f"  群组ID: {group['id']}, 名称: '{group['name']}'")
            else:
                print(f"❌ 创建群组失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def list_groups(self):
        """列出所有群组"""
        try:
            response = requests.get(f"{BASE_URL}/groups")
            
            if response.status_code == 200:
                groups = response.json()
                print(f"✅ 共找到 {len(groups)} 个群组：")
                print("-" * 60)
                print("{:<10} {:<30} {:<20}".format("群组ID", "群组名称", "成员数量"))
                print("-" * 60)
                
                for group in groups:
                    member_count = len(group.get("members", []))
                    print(f"{group['id']:<10} '{group['name']:<28}' {member_count:<20}")
                
            else:
                print(f"❌ 获取群组列表失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def delete_group(self, args):
        """删除群组"""
        if len(args) < 1:
            print("❌ 参数错误：group delete <群组ID>")
            return
        
        group_id = args[0]
        
        try:
            response = requests.delete(f"{BASE_URL}/groups/{group_id}")
            
            if response.status_code == 200:
                print(f"✅ 群组 {group_id} 删除成功！")
            else:
                print(f"❌ 删除群组失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def get_group_detail(self, args):
        """查看群组详情"""
        if len(args) < 1:
            print("❌ 参数错误：group detail <群组ID>")
            return
        
        group_id = args[0]
        
        try:
            response = requests.get(f"{BASE_URL}/groups/{group_id}")
            
            if response.status_code == 200:
                group = response.json()
                print(f"✅ 群组详情：")
                print("-" * 50)
                print(f"群组ID: {group['id']}")
                print(f"群组名称: '{group['name']}'")
                print(f"成员数量: {len(group.get('members', []))}")
                print()
                print("成员列表：")
                print("-" * 50)
                print("{:<10} {:<20} {:<20}".format("用户ID", "用户名", "余额"))
                print("-" * 50)
                
                for member in group.get('members', []):
                    user_name = member.get('user', {}).get('name', '')
                    print(f"{member['user_id']:<10} '{user_name:<18}' {member['balance']:<20}")
                
            else:
                print(f"❌ 获取群组详情失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def add_group_member(self, args):
        """添加群组成员"""
        if len(args) < 3:
            print("❌ 参数错误：group add_member <群组ID> <用户ID> <初始余额>")
            return
        
        group_id = args[0]
        user_id = args[1]
        balance = float(args[2])
        
        try:
            response = requests.post(
                f"{BASE_URL}/groups/{group_id}/members",
                json={"user_id": user_id, "balance": balance}
            )
            
            if response.status_code == 200:
                member = response.json()
                print(f"✅ 成员添加成功！")
                print(f"  群组ID: {member['group_id']}, 用户ID: {member['user_id']}, 余额: {member['balance']}")
            else:
                print(f"❌ 添加成员失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def update_group_balance(self, args):
        """更新群组成员余额"""
        if len(args) < 3:
            print("❌ 参数错误：group update_balance <群组ID> <用户ID> <新余额>")
            return
        
        group_id = args[0]
        user_id = args[1]
        new_balance = float(args[2])
        
        try:
            response = requests.put(
                f"{BASE_URL}/groups/{group_id}/members/{user_id}",
                json={"balance": new_balance}
            )
            
            if response.status_code == 200:
                member = response.json()
                print(f"✅ 余额更新成功！")
                print(f"  群组ID: {member['group_id']}, 用户ID: {member['user_id']}, 新余额: {member['balance']}")
            else:
                print(f"❌ 更新余额失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    # 交易管理方法
    def create_custom_transaction(self, args):
        """创建自定义分摊交易"""
        if len(args) < 5:
            print("❌ 参数错误：transaction create_custom <群组ID> <描述> <总金额> <付款人ID> <用户ID:份额>...")
            return
        
        group_id = args[0]
        # 查找总金额的索引（群组ID后的第一个浮点数）
        total_amount_index = None
        for i in range(1, len(args)):
            try:
                float(args[i])
                total_amount_index = i
                break
            except ValueError:
                continue
        
        if total_amount_index is None or total_amount_index + 2 > len(args):
            print("❌ 参数错误：transaction create_custom <群组ID> <描述> <总金额> <付款人ID> <用户ID:份额>...")
            return
        
        description = " ".join(args[1:total_amount_index])
        total_amount = float(args[total_amount_index])
        payer_id = args[total_amount_index + 1]
        
        # 解析用户份额
        shares = {}
        for arg in args[total_amount_index + 2:]:
            try:
                user_id, share = arg.split(":")
                shares[user_id] = float(share)
            except ValueError:
                print(f"❌ 份额格式错误: {arg} (应为 '用户ID:份额')")
                return
        
        try:
            response = requests.post(
                f"{BASE_URL}/transactions",
                json={
                    "group_id": group_id,
                    "description": description,
                    "total_amount": total_amount,
                    "payer_id": payer_id,
                    "is_aa": False,
                    "shares": shares
                }
            )
            
            if response.status_code == 200:
                transaction = response.json()
                print(f"✅ 自定义交易创建成功！")
                print(f"  交易ID: {transaction['id']}, 描述: '{transaction['description']}', 总金额: {transaction['total_amount']}")
            else:
                print(f"❌ 创建交易失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def create_aa_transaction(self, args):
        """创建AA制交易"""
        if len(args) < 4:
            print("❌ 参数错误：transaction create_aa <群组ID> <描述> <总金额> <付款人ID>")
            return
        
        group_id = args[0]
        # 查找总金额的索引（群组ID后的第一个浮点数）
        total_amount_index = None
        for i in range(1, len(args)):
            try:
                float(args[i])
                total_amount_index = i
                break
            except ValueError:
                continue
        
        if total_amount_index is None or total_amount_index + 1 >= len(args):
            print("❌ 参数错误：transaction create_aa <群组ID> <描述> <总金额> <付款人ID>")
            return
        
        description = " ".join(args[1:total_amount_index])
        total_amount = float(args[total_amount_index])
        payer_id = args[total_amount_index + 1]
        
        try:
            response = requests.post(
                f"{BASE_URL}/transactions",
                json={
                    "group_id": group_id,
                    "description": description,
                    "total_amount": total_amount,
                    "payer_id": payer_id,
                    "is_aa": True
                }
            )
            
            if response.status_code == 200:
                transaction = response.json()
                print(f"✅ AA制交易创建成功！")
                print(f"  交易ID: {transaction['id']}, 描述: '{transaction['description']}', 总金额: {transaction['total_amount']}")
            else:
                print(f"❌ 创建交易失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    def reset_database(self):
        """重置数据库，删除所有用户和群组"""
        print("⚠️  警告：此操作将删除所有用户和群组信息，不可恢复！")
        confirm = input("请输入 'confirm' 确认重置: ")
        if confirm != "confirm":
            print("✅ 重置操作已取消。")
            return
        
        try:
            # 删除所有用户
            print("🔄 正在删除所有用户...")
            users_response = requests.get(f"{BASE_URL}/users")
            if users_response.status_code == 200:
                users = users_response.json()
                for user in users:
                    delete_response = requests.delete(f"{BASE_URL}/users/{user['id']}")
                    if delete_response.status_code != 200:
                        print(f"❌ 删除用户 {user['id']} 失败: {delete_response.text}")
            
            # 删除所有群组
            print("🔄 正在删除所有群组...")
            groups_response = requests.get(f"{BASE_URL}/groups")
            if groups_response.status_code == 200:
                groups = groups_response.json()
                for group in groups:
                    delete_response = requests.delete(f"{BASE_URL}/groups/{group['id']}")
                    if delete_response.status_code != 200:
                        print(f"❌ 删除群组 {group['id']} 失败: {delete_response.text}")
            
            print("✅ 数据库重置成功！所有用户和群组信息已删除。")
            
        except Exception as e:
            print(f"❌ 重置数据库失败: {e}")
    
    def list_transactions(self, args):
        """查看用户交易记录"""
        if len(args) < 1:
            print("❌ 参数错误：transaction list <用户ID>")
            return
        
        user_id = args[0]
        
        try:
            response = requests.get(f"{BASE_URL}/users/{user_id}/transactions")
            
            if response.status_code == 200:
                transactions = response.json()
                print(f"✅ 用户 {user_id} 的交易记录：")
                print("-" * 60)
                print("{:<10} {:<20} {:<10} {:<10} {:<10}".format("交易ID", "描述", "总金额", "我的份额", "我的支付"))
                print("-" * 60)
                
                for transaction in transactions:
                    print(f"{transaction['id']:<10} '{transaction['description']:<18}' {transaction['total_amount']:<10} {transaction['my_share']:<10} {transaction['my_paid']:<10}")
                
            else:
                print(f"❌ 获取交易记录失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")

# 创建一个简单的测试脚本来验证群组列表功能
def test_group_list():
    """测试群组列表功能"""
    print("🔍 正在测试群组列表功能...")
    
    try:
        response = requests.get(f"{BASE_URL}/groups")
        
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ 共找到 {len(groups)} 个群组：")
            print("-" * 60)
            print("{:<10} {:<30} {:<20}".format("群组ID", "群组名称", "成员数量"))
            print("-" * 60)
            
            for group in groups:
                member_count = len(group.get("members", []))
                print(f"{group['id']:<10} '{group['name']:<28}' {member_count:<20}")
                
                # 如果有成员，打印成员信息
                if member_count > 0:
                    print("  成员:")
                    for member in group.get("members", []):
                        user_name = member.get('user', {}).get('name', '')
                        print(f"    - 用户ID: {member['user_id']}, 用户名: '{user_name}', 余额: {member['balance']}")
        else:
            print(f"❌ 获取群组列表失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    # 如果运行测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_group_list()
    else:
        # 运行正常的管理员终端
        terminal = AdminTerminal()
        terminal.run()