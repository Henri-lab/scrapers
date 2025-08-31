from DrissionPage import Chromium
from DrissionPage import ChromiumOptions
import time

path = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # macOS的Chrome可执行文件路径
url = r"https://www.zhipin.com"

# 配置Chrome选项，启用调试端口
co = ChromiumOptions().set_browser_path(path).auto_port()
browser = Chromium(co)
page = browser.latest_tab
page.get(url)

# 等待页面加载
time.sleep(3)
print("页面标题:", page.title)

# 检查是否需要登录
login_elements = page.eles('.sign-form')
if login_elements:
    print("检测到登录页面")
else:
    print("无需登录，可直接访问")
    
# 尝试搜索功能
search_input = page.ele('.search-input', timeout=2)
if search_input:
    print("找到搜索框")
else:
    print("未找到搜索框，可能需要进一步分析页面结构")
