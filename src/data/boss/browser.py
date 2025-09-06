import random
from DrissionPage import Chromium, ChromiumOptions
from typing import Optional
from .config import BossConfig


class BossBrowser:
    """Boss直聘浏览器管理模块"""
    
    def __init__(self, config: Optional[BossConfig] = None):
        """
        初始化浏览器管理器
        
        Args:
            config: 配置管理器实例
        """
        self.config = config or BossConfig()
        self.browser: Optional[Chromium] = None
        self.page = None
        
    def setup_browser(self) -> bool:
        """
        设置并启动浏览器
        
        Returns:
            bool: 是否成功启动
        """
        try:
            # 创建浏览器选项
            co = ChromiumOptions().set_browser_path(self.config.chrome_path).auto_port()
            
            # 添加启动参数
            for arg in self.config.browser_arguments:
                co.set_argument(arg)
            
            # 设置随机用户代理
            user_agent = random.choice(self.config.user_agents)
            co.set_argument(f"--user-agent={user_agent}")
            
            # 创建浏览器实例
            self.browser = Chromium(co)
            self.page = self.browser.latest_tab
            
            # 执行反检测脚本
            self.page.run_js(self.config.anti_detect_script)
            
            print("✅ 浏览器启动成功")
            return True
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            return False
    
    def get_page(self):
        """
        获取页面对象
        
        Returns:
            页面对象或None
        """
        if not self.page:
            if not self.setup_browser():
                return None
        return self.page
    
    def is_browser_running(self) -> bool:
        """
        检查浏览器是否正在运行
        
        Returns:
            bool: 浏览器是否运行中
        """
        try:
            return self.browser is not None and self.page is not None
        except:
            return False
    
    def restart_browser(self) -> bool:
        """
        重启浏览器
        
        Returns:
            bool: 是否成功重启
        """
        print("正在重启浏览器...")
        self.close()
        return self.setup_browser()
    
    def close(self) -> None:
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.quit()
                self.browser = None
                self.page = None
                print("✅ 浏览器已关闭")
        except Exception as e:
            print(f"关闭浏览器时出错: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        self.setup_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def __del__(self):
        """析构函数"""
        self.close()