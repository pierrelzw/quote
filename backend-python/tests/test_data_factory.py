"""
测试数据工厂
用于创建测试数据
"""
import random
import string
from datetime import datetime, timedelta

class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def random_string(length=10):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_username():
        """生成随机用户名"""
        return f"user_{TestDataFactory.random_string(8)}"
    
    @staticmethod
    def random_password():
        """生成随机密码"""
        return TestDataFactory.random_string(12)
    
    @staticmethod
    def random_quote():
        """生成随机名言"""
        quotes = [
            "生活不是等待暴风雨过去，而是学会在雨中跳舞。",
            "成功不是终点，失败不是致命的，勇气才是最重要的。",
            "你今天的努力，是幸运的伏笔。",
            "不要让昨天的失败，毁掉今天的成功。",
            "每一次跌倒，都是为了更好地站起来。",
            "相信自己，你比你想象的更强大。",
            "梦想不会发光，发光的是追梦的你。",
            "困难是弱者的借口，更是强者的垫脚石。",
            "没有人能够回到过去，但任何人都可以从现在开始。",
            "你的努力，时光会给你答案。"
        ]
        return random.choice(quotes)
    
    @staticmethod
    def random_author():
        """生成随机作者"""
        authors = [
            "李白", "杜甫", "苏轼", "白居易", "王维",
            "陆游", "辛弃疾", "李清照", "王勃", "孟浩然",
            "测试作者", "匿名", "智者", "哲人", "思想家"
        ]
        return random.choice(authors)
    
    @staticmethod
    def create_user_data(username=None, password=None):
        """创建用户数据"""
        return {
            'username': username or TestDataFactory.random_username(),
            'password': password or TestDataFactory.random_password()
        }
    
    @staticmethod
    def create_quote_data(content=None, author=None):
        """创建名言数据"""
        return {
            'content': content or TestDataFactory.random_quote(),
            'author': author or TestDataFactory.random_author()
        }
    
    @staticmethod
    def create_multiple_users(count=5):
        """创建多个用户数据"""
        return [TestDataFactory.create_user_data() for _ in range(count)]
    
    @staticmethod
    def create_multiple_quotes(count=10):
        """创建多个名言数据"""
        return [TestDataFactory.create_quote_data() for _ in range(count)]
    
    @staticmethod
    def create_test_scenario_data():
        """创建测试场景数据"""
        return {
            'users': TestDataFactory.create_multiple_users(3),
            'quotes': TestDataFactory.create_multiple_quotes(5),
            'admin_user': {
                'username': 'admin_test',
                'password': 'admin_password_123'
            }
        }

class TestHelpers:
    """测试辅助函数"""
    
    @staticmethod
    def register_and_login_user(client, username=None, password=None):
        """注册并登录用户，返回token"""
        user_data = TestDataFactory.create_user_data(username, password)
        
        # 注册用户
        register_response = client.post('/api/auth/register', json=user_data)
        if register_response.status_code != 201:
            return None, None
        
        # 登录用户
        login_response = client.post('/api/auth/login', json=user_data)
        if login_response.status_code != 200:
            return None, None
        
        import json
        login_data = json.loads(login_response.data)
        return login_data['token'], user_data
    
    @staticmethod
    def add_test_quote(client, token, content=None, author=None):
        """添加测试名言"""
        quote_data = TestDataFactory.create_quote_data(content, author)
        
        response = client.post('/api/quotes',
                             json=quote_data,
                             headers={'Authorization': f'Bearer {token}'})
        
        if response.status_code == 201:
            import json
            return json.loads(response.data)
        return None
    
    @staticmethod
    def setup_test_data(client):
        """设置测试数据"""
        # 创建测试用户
        tokens = []
        users = []
        
        for i in range(3):
            token, user_data = TestHelpers.register_and_login_user(client)
            if token:
                tokens.append(token)
                users.append(user_data)
        
        # 每个用户添加一些名言
        quotes = []
        for token in tokens:
            for _ in range(2):
                quote = TestHelpers.add_test_quote(client, token)
                if quote:
                    quotes.append(quote)
        
        return {
            'tokens': tokens,
            'users': users,
            'quotes': quotes
        }

# 测试数据常量
TEST_USERS = [
    {'username': 'testuser1', 'password': 'password123'},
    {'username': 'testuser2', 'password': 'password456'},
    {'username': 'testuser3', 'password': 'password789'}
]

TEST_QUOTES = [
    {'content': '测试名言1', 'author': '测试作者1'},
    {'content': '测试名言2', 'author': '测试作者2'},
    {'content': '测试名言3', 'author': '测试作者3'}
]

# 边界测试数据
EDGE_CASE_DATA = {
    'long_username': 'a' * 100,
    'long_password': 'b' * 200,
    'long_quote_content': 'c' * 1000,
    'long_author_name': 'd' * 100,
    'empty_string': '',
    'whitespace_string': '   ',
    'special_chars': '!@#$%^&*()_+{}[]|:";\'<>?,./',
    'unicode_content': '这是一个包含unicode字符的测试内容 🌟',
    'sql_injection_attempt': "'; DROP TABLE users; --",
    'xss_attempt': '<script>alert("XSS")</script>'
}
