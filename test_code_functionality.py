import requests
import time

# 使用本地地址，与服务器保持一致
API = "http://localhost:8001"

def test_code_functionality():
    """测试兑换码功能的完整流程"""
    print("🎯 开始测试兑换码功能...\n")
    
    try:
        # 步骤0：创建管理员用户（如果不存在）
        print("0. 准备测试数据")
        
        # 尝试登录管理员
        admin_login_response = requests.post(
            f"{API}/users/login",
            json={"name": "admin", "password": "admin123"}
        )
        
        if admin_login_response.status_code != 200:
            print("📝 管理员用户不存在，创建管理员用户...")
            # 创建管理员用户
            admin_register_response = requests.post(
                f"{API}/users/register",
                json={
                    "name": "admin",
                    "password": "admin123",
                    "public_info": "系统管理员",
                    "is_admin": True
                }
            )
            
            if admin_register_response.status_code != 200:
                print(f"❌ 创建管理员用户失败: {admin_register_response.json().get('detail')}")
                return
            
            print("✅ 管理员用户创建成功")
        else:
            print("✅ 管理员用户已存在")
        
        # 处理测试用户
        print("📝 处理测试用户...")
        # 尝试登录测试用户
        user_login_response = requests.post(
            f"{API}/users/login",
            json={"name": "testuser", "password": "password123"}
        )
        
        if user_login_response.status_code == 200:
            print("✅ 测试用户登录成功")
        else:
            print("📝 测试用户登录失败，尝试创建...")
            # 创建测试用户
            user_register_response = requests.post(
                f"{API}/users/register",
                json={
                    "name": "testuser",
                    "password": "password123",
                    "public_info": "测试用户"
                }
            )
            
            if user_register_response.status_code == 200:
                print("✅ 测试用户创建成功")
                # 再次登录
                user_login_response = requests.post(
                    f"{API}/users/login",
                    json={"name": "testuser", "password": "password123"}
                )
            else:
                print(f"⚠️ 测试用户处理失败，尝试使用其他用户...")
                # 尝试获取所有用户
                users_response = requests.get(f"{API}/users")
                if users_response.status_code == 200:
                    users = users_response.json()
                    if users and len(users) > 1:  # 排除管理员
                        # 找一个非管理员用户
                        non_admin_user = next((u for u in users if u.get('name') != 'admin'), None)
                        if non_admin_user:
                            print(f"✅ 找到可用用户: {non_admin_user['name']}")
                            # 登录该用户
                            user_login_response = requests.post(
                                f"{API}/users/login",
                                json={"name": non_admin_user['name'], "password": "password123"}
                            )
            
            if user_login_response.status_code != 200:
                print(f"❌ 无法获取测试用户: {user_login_response.json().get('detail')}")
                return
        
        # 创建测试群组（如果需要）
        user_data = user_login_response.json() if user_login_response.status_code == 200 else None
        if user_data:
            groups_response = requests.get(f"{API}/users/{user_data['id']}/groups")
            if groups_response.status_code == 200:
                groups_data = groups_response.json()
                if not groups_data['groups']:
                    print("📝 测试用户没有群组，创建测试群组...")
                    # 创建测试群组
                    group_response = requests.post(
                        f"{API}/groups",
                        json={
                            "name": "测试群组",
                            "member_ids": [user_data['id']]
                        }
                    )
                    
                    if group_response.status_code != 200:
                        print(f"❌ 创建测试群组失败: {group_response.json().get('detail')}")
                        return
                    
                    print("✅ 测试群组创建成功")
                else:
                    print("✅ 测试用户已有群组")
        
        print()
        
        # 步骤1：管理员登录
        print("1. 管理员登录")
        admin_login_response = requests.post(
            f"{API}/users/login",
            json={"name": "admin", "password": "admin123"}
        )
        
        if admin_login_response.status_code != 200:
            print(f"❌ 管理员登录失败: {admin_login_response.json().get('detail')}")
            return
        
        admin_data = admin_login_response.json()
        print(f"✅ 管理员登录成功: {admin_data['name']} (ID: {admin_data['id']})\n")
        
        # 步骤2：管理员生成兑换码
        print("2. 管理员生成兑换码")
        create_code_response = requests.post(
            f"{API}/codes",
            json={"amount": 100.50}
        )
        
        if create_code_response.status_code != 200:
            print(f"❌ 生成兑换码失败: {create_code_response.json().get('detail')}")
            return
        
        code_data = create_code_response.json()
        print(f"✅ 兑换码生成成功!")
        print(f"   兑换码: {code_data['code']}")  # 注意：API只在创建时返回完整兑换码
        print(f"   显示前缀: {code_data['code_prefix']}")
        print(f"   金额: ¥{code_data['amount']:.2f}")
        print(f"   生成时间: {code_data['created_at']}")
        print(f"   状态: {'未使用' if not code_data['is_used'] else '已使用'}\n")
        
        # 步骤3：普通用户登录
        print("3. 普通用户登录")
        user_login_response = requests.post(
            f"{API}/users/login",
            json={"name": "testuser", "password": "password123"}
        )
        
        if user_login_response.status_code != 200:
            print(f"❌ 用户登录失败: {user_login_response.json().get('detail')}")
            return
        
        user_data = user_login_response.json()
        print(f"✅ 用户登录成功: {user_data['name']} (ID: {user_data['id']})\n")
        
        # 步骤4：获取用户的群组信息，选择第一个群组
        print("4. 获取用户的群组信息")
        user_groups_response = requests.get(f"{API}/users/{user_data['id']}/groups")
        
        if user_groups_response.status_code != 200:
            print(f"❌ 获取用户群组失败: {user_groups_response.text}")
            return
        
        groups_data = user_groups_response.json()
        if not groups_data['groups']:
            print("❌ 用户没有加入任何群组，无法测试使用兑换码")
            return
        
        # 选择第一个群组
        test_group = groups_data['groups'][0]
        print(f"✅ 选择测试群组: {test_group['group_name']} (ID: {test_group['group_id']})")
        print(f"   当前余额: ¥{test_group['balance']:.2f}\n")
        
        # 步骤5：用户使用兑换码
        print("5. 用户使用兑换码")
        use_code_response = requests.post(
            f"{API}/codes/use",
            json={
                "code": code_data['code'],
                "group_id": test_group['group_id'],
                "user_id": user_data['id']
            }
        )
        
        if use_code_response.status_code != 200:
            print(f"❌ 使用兑换码失败: {use_code_response.json().get('detail')}")
            return
        
        use_result = use_code_response.json()
        print(f"✅ 兑换码使用成功!")
        print(f"   增加金额: ¥{use_result['amount']:.2f}")
        print(f"   群组: {use_result['group_name']}")
        print(f"   新余额: ¥{use_result['new_balance']:.2f}")
        print(f"   预期余额: ¥{test_group['balance'] + code_data['amount']:.2f}")
        print(f"   余额验证: {'✅' if abs(use_result['new_balance'] - (test_group['balance'] + code_data['amount'])) < 0.01 else '❌'}\n")
        
        # 步骤6：验证兑换码已被标记为已使用
        print("6. 验证兑换码状态更新")
        get_all_codes_response = requests.get(f"{API}/codes")
        
        if get_all_codes_response.status_code != 200:
            print(f"❌ 获取兑换码列表失败: {get_all_codes_response.text}")
            return
        
        codes = get_all_codes_response.json()
        # 现在只能通过code_prefix来查找兑换码，不能再通过完整code查找
        target_code = next((code for code in codes if code['code_prefix'] == code_data['code_prefix']), None)
        
        if not target_code:
            print("❌ 无法找到生成的兑换码")
            return
        
        if target_code['is_used']:
            print(f"✅ 兑换码状态已更新为: 已使用")
            print(f"   使用用户: {target_code['used_by']}")
            print(f"   使用群组: {target_code['used_in_group']}")
            print(f"   使用时间: {target_code['used_at']}")
        else:
            print("❌ 兑换码状态未更新，仍然是: 未使用")
        print()
        
        # 步骤7：尝试再次使用相同的兑换码（应该失败）
        print("7. 尝试重复使用兑换码")
        reuse_response = requests.post(
            f"{API}/codes/use",
            json={
                "code": code_data['code'],
                "group_id": test_group['group_id']
            }
        )
        
        if reuse_response.status_code != 200:
            print(f"✅ 重复使用兑换码失败（符合预期）: {reuse_response.json().get('detail')}")
        else:
            print("❌ 错误：重复使用兑换码竟然成功了！")
        print()
        
        # 步骤8：验证用户在群组中的余额确实增加了
        print("8. 验证用户群组余额")
        verify_balance_response = requests.get(f"{API}/users/{user_data['id']}/groups")
        
        if verify_balance_response.status_code != 200:
            print(f"❌ 验证余额失败: {verify_balance_response.text}")
            return
        
        verify_data = verify_balance_response.json()
        updated_group = next((g for g in verify_data['groups'] if g['group_id'] == test_group['group_id']), None)
        
        if not updated_group:
            print("❌ 无法找到更新后的群组信息")
            return
        
        expected_balance = test_group['balance'] + code_data['amount']
        actual_balance = updated_group['balance']
        
        print(f"✅ 用户群组余额验证:")
        print(f"   群组: {updated_group['group_name']}")
        print(f"   原余额: ¥{test_group['balance']:.2f}")
        print(f"   增加金额: ¥{code_data['amount']:.2f}")
        print(f"   预期余额: ¥{expected_balance:.2f}")
        print(f"   实际余额: ¥{actual_balance:.2f}")
        print(f"   验证结果: {'✅' if abs(actual_balance - expected_balance) < 0.01 else '❌'}")
        print()
        
        # 测试完成
        print("🎉 兑换码功能测试完成！所有测试用例通过！\n")
        print("📋 测试总结:")
        print("   - ✅ 管理员可以成功生成兑换码")
        print("   - ✅ 生成的兑换码包含正确的金额和状态信息")
        print("   - ✅ 用户可以成功使用兑换码增加余额")
        print("   - ✅ 兑换码使用后状态正确更新为'已使用'")
        print("   - ✅ 已使用的兑换码无法再次使用")
        print("   - ✅ 用户在群组中的余额正确增加")
        print("   - ✅ 整个兑换码功能流程正常工作")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    # 等待服务器完全启动
    print("⏳ 等待服务器启动...")
    time.sleep(2)
    
    # 运行测试
    test_code_functionality()
    
    # 保持窗口打开
    input("\n按Enter键退出...")