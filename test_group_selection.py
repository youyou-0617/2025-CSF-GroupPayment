import requests
import json

# API基础URL
API = "http://localhost:8001"

# 测试用户凭证
users = [
    {"id": 1, "name": "张三", "username": "zhangsan", "password": "password123"},
    {"id": 2, "name": "李四", "username": "lisi", "password": "password123"},
    {"id": 3, "name": "王五", "username": "wangwu", "password": "password123"},
    {"id": 4, "name": "赵六", "username": "zhaoliu", "password": "password123"},
    {"id": 5, "name": "管理员", "username": "admin", "password": "admin123"}
]

# 测试函数：获取用户所在的群组
def test_get_user_groups(user_id):
    print(f"\n=== 测试获取用户 {user_id} 的群组 ===")
    try:
        response = requests.get(f"{API}/users/{user_id}/groups")
        if response.status_code == 200:
            data = response.json()
            print(f"用户 {data['user_name']} 所在的群组:")
            for group in data['groups']:
                print(f"  - 群组ID: {group['group_id']}, 群组名称: {group['group_name']}, 余额: {group['balance']}")
            return data['groups']
        else:
            print(f"获取用户群组失败: {response.text}")
            return []
    except Exception as e:
        print(f"获取用户群组出错: {str(e)}")
        return []

# 测试函数：尝试查看用户所在的群组
def test_view_user_groups(user_id, group_id):
    print(f"\n=== 测试用户 {user_id} 查看群组 {group_id} ===")
    try:
        response = requests.get(f"{API}/groups/{group_id}")
        if response.status_code == 200:
            group = response.json()
            print(f"成功获取群组详情:")
            print(f"  - 群组名称: {group['name']}")
            print(f"  - 总成员数: {group.get('total_members', 0)}")
            print("  - 成员列表:")
            if 'members' in group and group['members']:
                for member in group['members']:
                    user_name = member.get('user', {}).get('name', '未知用户') if 'user' in member else '未知用户'
                    print(f"    * 用户ID: {member['user_id']}, 用户名: {user_name}, 余额: {member['balance']}")
            return True
        else:
            print(f"获取群组详情失败: {response.text}")
            return False
    except Exception as e:
        print(f"获取群组详情出错: {str(e)}")
        return False

# 测试函数：创建测试兑换码
def create_test_code(admin_username, admin_password, amount=100):
    print(f"\n=== 创建测试兑换码 ===")
    try:
        # 管理员登录
        login_response = requests.post(
            f"{API}/admin/login",
            json={"username": admin_username, "password": admin_password}
        )
        if login_response.status_code != 200:
            print(f"管理员登录失败: {login_response.text}")
            return None
        
        # 创建兑换码
        create_code_response = requests.post(
            f"{API}/admin/codes/create",
            json={"amount": amount, "expires_in": 3600}
        )
        
        if create_code_response.status_code == 200:
            code = create_code_response.json()
            print(f"成功创建兑换码: {code['code']}, 金额: {code['amount']}")  # API只在创建时返回完整兑换码
            print(f"兑换码前缀: {code['code_prefix']}")
            return code['code']
        else:
            print(f"创建兑换码失败: {create_code_response.text}")
            return None
    except Exception as e:
        print(f"创建测试兑换码出错: {str(e)}")
        return None

# 测试函数：使用兑换码
def test_use_code(user_id, code, group_id):
    print(f"\n=== 测试用户 {user_id} 使用兑换码 {code} 到群组 {group_id} ===")
    try:
        response = requests.post(
            f"{API}/codes/use",
            json={
                "code": code,
                "group_id": group_id,
                "user_id": user_id
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"兑换成功!")
            print(f"  - 增加金额: {result['amount']}")
            print(f"  - 群组: {result['group_name']}")
            print(f"  - 当前余额: {result['new_balance']}")
            return True
        else:
            print(f"兑换失败: {response.json().get('detail', '兑换码无效或已使用')}")
            return False
    except Exception as e:
        print(f"兑换出错: {str(e)}")
        return False

# 主测试函数
def run_tests():
    print("开始测试用户群组和兑换码功能...")
    
    # 测试1: 获取用户1的群组
    user1_groups = test_get_user_groups(1)
    
    # 测试2: 获取用户2的群组
    user2_groups = test_get_user_groups(2)
    
    # 测试3: 用户1查看自己所在的群组
    if user1_groups:
        for group in user1_groups:
            test_view_user_groups(1, group['group_id'])
    
    # 测试4: 创建测试兑换码
    test_code = create_test_code("admin", "admin123", 100)
    
    # 测试5: 使用兑换码到用户所在的群组
    if test_code and user1_groups:
        # 使用第一个群组测试兑换码
        test_use_code(1, test_code, user1_groups[0]['group_id'])
        
        # 再次获取用户群组信息，验证余额已更新
        updated_groups = test_get_user_groups(1)
        
        # 测试6: 尝试使用已使用的兑换码
        print("\n=== 测试使用已使用的兑换码 ===")
        test_use_code(1, test_code, user1_groups[0]['group_id'])
    
    # 测试7: 获取用户4的群组（可能没有加入任何群组）
    user4_groups = test_get_user_groups(4)
    
    print("\n所有测试完成!")

# 运行测试
if __name__ == "__main__":
    run_tests()