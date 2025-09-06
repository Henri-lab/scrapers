import json
import time
from typing import Dict, Optional, List


class BossAuth:
    """Boss直聘认证管理模块"""
    
    def __init__(self, page):
        """
        初始化认证模块
        
        Args:
            page: DrissionPage页面对象
        """
        self.page = page
        self.web_base_url = "https://www.zhipin.com"
        self._is_authenticated = False
        
    def load_cookies(self, cookies: List[Dict]) -> bool:
        """
        加载cookies到浏览器
        
        Args:
            cookies: cookies列表，格式: [{"name": "", "value": "", "domain": "", ...}, ...]
            
        Returns:
            bool: 是否成功加载
        """
        try:
            # 先访问主页建立基础会话
            self.page.get(self.web_base_url)
            time.sleep(1)
            
            # 添加cookies
            for cookie in cookies:
                try:
                    # 确保必要字段存在
                    if "name" not in cookie or "value" not in cookie:
                        continue
                        
                    # 设置默认domain
                    if "domain" not in cookie:
                        cookie["domain"] = ".zhipin.com"
                    
                    # 添加cookie
                    self.page.set.cookies(cookie)
                    
                except Exception as e:
                    print(f"加载cookie失败: {cookie.get('name', 'unknown')} - {e}")
                    continue
                    
            print("✅ Cookies加载完成")
            return True
            
        except Exception as e:
            print(f"❌ 加载cookies失败: {e}")
            return False
    
    def load_cookies_from_string(self, cookie_string: str) -> bool:
        """
        从cookie字符串加载cookies
        
        Args:
            cookie_string: cookie字符串，格式: "name1=value1; name2=value2; ..."
            
        Returns:
            bool: 是否成功加载
        """
        try:
            cookies = []
            for item in cookie_string.split(';'):
                item = item.strip()
                if '=' in item:
                    name, value = item.split('=', 1)
                    cookies.append({
                        "name": name.strip(),
                        "value": value.strip(),
                        "domain": ".zhipin.com"
                    })
            
            return self.load_cookies(cookies)
            
        except Exception as e:
            print(f"❌ 解析cookie字符串失败: {e}")
            return False
    
    def load_cookies_from_file(self, file_path: str) -> bool:
        """
        从文件加载cookies
        
        Args:
            file_path: cookies文件路径（JSON格式）
            
        Returns:
            bool: 是否成功加载
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            return self.load_cookies(cookies)
            
        except FileNotFoundError:
            print(f"❌ cookies文件不存在: {file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ cookies文件格式错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 加载cookies文件失败: {e}")
            return False
    
    def save_current_cookies(self, file_path: str) -> bool:
        """
        保存当前浏览器的cookies到文件
        
        Args:
            file_path: 保存路径
            
        Returns:
            bool: 是否成功保存
        """
        try:
            cookies = self.page.cookies(as_dict=False)
            
            # 转换为JSON格式
            cookies_list = []
            for cookie in cookies:
                cookie_dict = {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "secure": cookie.secure,
                    "httpOnly": cookie.httpOnly
                }
                if cookie.expiry:
                    cookie_dict["expiry"] = cookie.expiry
                cookies_list.append(cookie_dict)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cookies_list, f, ensure_ascii=False, indent=4)
            
            print(f"✅ cookies已保存到: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 保存cookies失败: {e}")
            return False
    
    def set_authorization_token(self, token: str, token_type: str = "Bearer") -> bool:
        """
        设置Authorization token
        
        Args:
            token: 认证token
            token_type: token类型，默认为Bearer
            
        Returns:
            bool: 是否成功设置
        """
        try:
            # 通过JavaScript设置请求头
            js_code = f"""
            // 拦截XMLHttpRequest
            (function() {{
                const open = XMLHttpRequest.prototype.open;
                XMLHttpRequest.prototype.open = function(method, url, ...rest) {{
                    this._method = method;
                    this._url = url;
                    return open.apply(this, arguments);
                }};
                
                const send = XMLHttpRequest.prototype.send;
                XMLHttpRequest.prototype.send = function(data) {{
                    if (this._url && this._url.includes('zhipin.com')) {{
                        this.setRequestHeader('Authorization', '{token_type} {token}');
                    }}
                    return send.apply(this, arguments);
                }};
            }})();
            
            // 拦截fetch请求
            (function() {{
                const originalFetch = window.fetch;
                window.fetch = function(url, options = {{}}) {{
                    if (typeof url === 'string' && url.includes('zhipin.com')) {{
                        options.headers = options.headers || {{}};
                        options.headers['Authorization'] = '{token_type} {token}';
                    }}
                    return originalFetch(url, options);
                }};
            }})();
            """
            
            self.page.run_js(js_code)
            print("✅ Authorization token设置完成")
            return True
            
        except Exception as e:
            print(f"❌ 设置token失败: {e}")
            return False
    
    def check_login_status(self) -> bool:
        """
        检查登录状态
        
        Returns:
            bool: 是否已登录
        """
        try:
            self.page.get(self.web_base_url)
            time.sleep(2)

            # 检查是否存在登录按钮
            login_btn = self.page.ele(".btn.btn-outline.header-login-btn", timeout=3)
            if login_btn:
                self._is_authenticated = False
                return False

            # 检查是否有用户信息
            user_info = self.page.ele(".user-nav", timeout=3)
            if user_info:
                self._is_authenticated = True
                print("✅ 已登录")
                return True

            self._is_authenticated = False
            return False
            
        except Exception as e:
            print(f"检查登录状态失败: {e}")
            self._is_authenticated = False
            return False
    
    def prompt_manual_login(self) -> bool:
        """
        提示用户手动登录
        
        Returns:
            bool: 是否登录成功
        """
        print("=== 需要登录 ===")
        print("请在打开的浏览器中手动完成登录:")
        print("1. 输入手机号")
        print("2. 获取并输入验证码")
        print("3. 完成机器人验证")
        print("4. 登录完成后按回车继续...")

        # 打开登录页面
        self.page.get("https://www.zhipin.com/web/user/")
        time.sleep(1)

        # 等待用户手动登录
        input("登录完成后按回车继续...")

        # 验证登录是否成功
        if self.check_login_status():
            print("✅ 登录成功")
            return True
        else:
            print("❌ 登录验证失败")
            return False
    
    def ensure_authenticated(self, 
                           cookies: Optional[List[Dict]] = None,
                           cookie_string: Optional[str] = None,
                           cookie_file: Optional[str] = None,
                           token: Optional[str] = None) -> bool:
        """
        确保已认证，优先级：cookies > cookie_string > cookie_file > token > 手动登录
        
        Args:
            cookies: cookies列表
            cookie_string: cookie字符串
            cookie_file: cookies文件路径
            token: 认证token
            
        Returns:
            bool: 是否认证成功
        """
        print("正在检查认证状态...")
        
        # 1. 尝试加载提供的cookies
        if cookies:
            print("尝试使用提供的cookies...")
            if self.load_cookies(cookies):
                if self.check_login_status():
                    return True
        
        # 2. 尝试解析cookie字符串
        if cookie_string:
            print("尝试使用cookie字符串...")
            if self.load_cookies_from_string(cookie_string):
                if self.check_login_status():
                    return True
        
        # 3. 尝试从文件加载cookies
        if cookie_file:
            print(f"尝试从文件加载cookies: {cookie_file}")
            if self.load_cookies_from_file(cookie_file):
                if self.check_login_status():
                    return True
        
        # 4. 尝试使用token
        if token:
            print("尝试使用认证token...")
            if self.set_authorization_token(token):
                # token无法直接验证登录状态，假设有效
                print("✅ Token设置完成，假设认证有效")
                self._is_authenticated = True
                return True
        
        # 5. 检查当前是否已登录
        if self.check_login_status():
            return True
        
        # 6. 最后尝试手动登录
        print("需要手动登录...")
        return self.prompt_manual_login()
    
    @property
    def is_authenticated(self) -> bool:
        """获取认证状态"""
        return self._is_authenticated
    
    def get_current_cookies(self) -> List[Dict]:
        """
        获取当前浏览器cookies
        
        Returns:
            List[Dict]: cookies列表
        """
        try:
            cookies = self.page.cookies(as_dict=False)
            cookies_list = []
            
            for cookie in cookies:
                cookie_dict = {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "secure": cookie.secure,
                    "httpOnly": cookie.httpOnly
                }
                if cookie.expiry:
                    cookie_dict["expiry"] = cookie.expiry
                cookies_list.append(cookie_dict)
            
            return cookies_list
            
        except Exception as e:
            print(f"获取cookies失败: {e}")
            return []