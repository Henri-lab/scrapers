import time
import random

class AntiDetection:
    """反检测工具类"""
    
    @staticmethod
    def random_delay(min_sec=1, max_sec=3):
        """随机延时"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    @staticmethod
    def simulate_human_behavior(page):
        """模拟人类行为"""
        # 随机滚动页面
        scroll_height = random.randint(200, 800)
        page.scroll(0, scroll_height)
        AntiDetection.random_delay(0.5, 1.5)
        
        # 随机移动鼠标
        try:
            page.actions.move(random.randint(100, 500), random.randint(100, 400))
            AntiDetection.random_delay(0.2, 0.8)
        except:
            pass
    
    @staticmethod
    def get_random_headers():
        """获取随机请求头"""
        headers = [
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
        ]
        return random.choice(headers)
    
    @staticmethod
    def setup_stealth_browser(co):
        """配置隐身浏览器选项"""
        # 禁用图像加载以提高速度
        co.set_argument('--blink-settings=imagesEnabled=false')
        
        # 禁用通知
        co.set_argument('--disable-notifications')
        
        # 禁用密码保存提示
        co.set_argument('--disable-save-password-bubble')
        
        # 设置窗口大小
        co.set_argument('--window-size=1366,768')
        
        # 禁用扩展
        co.set_argument('--disable-extensions-file-access-check')
        
        return co