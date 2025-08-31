from DrissionPage import Chromium, ChromiumOptions
import pandas as pd
import time
import random
import json
import os
from urllib.parse import quote

class BossZhipinAutoScraper:
    def __init__(self, config_file="boss_config.json"):
        self.path = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.base_url = "https://www.zhipin.com"
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_browser()
    
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "phone": "",  # 手机号
            "password": "",  # 密码
            "cookies_file": "boss_cookies.json",
            "user_agents": [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            ]
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # 合并默认配置
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            return config
        else:
            # 创建默认配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"已创建配置文件 {self.config_file}，请填入登录信息")
            return default_config
    
    def setup_browser(self):
        """配置浏览器"""
        co = ChromiumOptions().set_browser_path(self.path).auto_port()
        
        # 反检测设置
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_argument('--disable-dev-shm-usage')
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-gpu')
        co.set_argument('--disable-extensions')
        
        # 随机用户代理
        user_agent = random.choice(self.config['user_agents'])
        co.set_argument(f'--user-agent={user_agent}')
        
        self.browser = Chromium(co)
        self.page = self.browser.latest_tab
        
        # 执行反检测脚本
        self.page.run_js('''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en'],
            });
        ''')
    
    def save_cookies(self):
        """保存cookies"""
        cookies = self.page.cookies()
        with open(self.config['cookies_file'], 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print("Cookies已保存")
    
    def load_cookies(self):
        """加载cookies"""
        if os.path.exists(self.config['cookies_file']):
            with open(self.config['cookies_file'], 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # 设置cookies
            self.page.get(self.base_url)
            time.sleep(2)
            
            for cookie in cookies:
                try:
                    self.page.set_cookie(**cookie)
                except:
                    continue
            
            # 刷新页面验证cookies
            self.page.refresh()
            time.sleep(3)
            return True
        return False
    
    def auto_login(self):
        """自动登录"""
        if not self.config['phone'] or not self.config['password']:
            print("请在配置文件中设置手机号和密码")
            return False
        
        try:
            print("开始自动登录...")
            self.page.get(f"{self.base_url}/web/user/login")
            time.sleep(3)
            
            # 点击手机号登录
            phone_tab = self.page.ele('text:手机号登录', timeout=5)
            if phone_tab:
                phone_tab.click()
                time.sleep(1)
            
            # 输入手机号
            phone_input = self.page.ele('input[placeholder*="手机号"]', timeout=5)
            if phone_input:
                phone_input.clear()
                phone_input.input(self.config['phone'])
                time.sleep(1)
            else:
                print("找不到手机号输入框")
                return False
            
            # 输入密码
            password_input = self.page.ele('input[type="password"]', timeout=5)
            if password_input:
                password_input.clear()
                password_input.input(self.config['password'])
                time.sleep(1)
            else:
                print("找不到密码输入框")
                return False
            
            # 点击登录按钮
            login_btn = self.page.ele('button:has-text("登录")', timeout=5)
            if not login_btn:
                login_btn = self.page.ele('.btn-sign', timeout=5)
            
            if login_btn:
                login_btn.click()
                time.sleep(3)
            else:
                print("找不到登录按钮")
                return False
            
            # 检查是否有验证码
            if self.page.ele('.geetest', timeout=3):
                print("需要完成滑动验证码，请手动完成...")
                time.sleep(10)  # 等待用户完成验证码
            
            # 验证登录状态
            time.sleep(3)
            if self.check_login_status():
                print("登录成功！")
                self.save_cookies()
                return True
            else:
                print("登录失败，请检查账号密码")
                return False
                
        except Exception as e:
            print(f"自动登录出错: {e}")
            return False
    
    def check_login_status(self):
        """检查登录状态"""
        # 检查是否有用户头像或用户菜单
        user_elements = [
            '.user-nav',
            '.nav-figure', 
            'text:我的',
            '.header-username'
        ]
        
        for selector in user_elements:
            if self.page.ele(selector, timeout=2):
                return True
        
        # 检查URL是否跳转到首页
        current_url = self.page.url
        if '/web/geek/job' in current_url or current_url == self.base_url + '/':
            return True
            
        return False
    
    def ensure_login(self):
        """确保已登录"""
        # 先尝试加载cookies
        if self.load_cookies() and self.check_login_status():
            print("使用保存的cookies登录成功")
            return True
        
        # cookies失效，尝试自动登录
        if self.auto_login():
            return True
        
        # 自动登录失败，提示手动登录
        print("\n自动登录失败，请手动登录...")
        self.page.get(self.base_url)
        print("请在浏览器中完成登录，然后按回车键继续...")
        input()
        
        if self.check_login_status():
            self.save_cookies()
            return True
        
        print("登录验证失败")
        return False
    
    def search_jobs(self, keyword, city="上海", pages=5):
        """搜索职位"""
        if not self.ensure_login():
            print("登录失败，无法继续")
            return []
        
        # 构建搜索URL
        search_url = f"https://www.zhipin.com/web/geek/job?query={quote(keyword)}&city={quote(city)}"
        print(f"搜索关键词: {keyword}")
        print(f"搜索城市: {city}")
        
        self.page.get(search_url)
        time.sleep(random.uniform(3, 5))
        
        jobs = []
        page_num = 1
        
        while page_num <= pages:
            print(f"正在爬取第{page_num}页...")
            
            # 等待页面加载
            job_cards = self.page.eles('.job-card-wrapper', timeout=10)
            
            if not job_cards:
                print("未找到职位信息，尝试其他选择器...")
                # 尝试其他可能的选择器
                job_cards = self.page.eles('.job-list-item', timeout=5)
                if not job_cards:
                    job_cards = self.page.eles('[ka="search_list_item"]', timeout=5)
            
            if not job_cards:
                print("页面可能被反爬虫拦截，等待后重试...")
                time.sleep(random.uniform(10, 15))
                self.page.refresh()
                time.sleep(5)
                continue
            
            for i, card in enumerate(job_cards):
                try:
                    job_info = self.extract_job_info(card)
                    if job_info:
                        jobs.append(job_info)
                    
                    # 随机延时
                    if i % 3 == 0:
                        time.sleep(random.uniform(1, 2))
                        
                except Exception as e:
                    print(f"提取第{i+1}个职位信息时出错: {e}")
                    continue
            
            print(f"第{page_num}页完成，已获取{len(jobs)}个职位")
            
            # 翻页
            if page_num < pages:
                if self.go_to_next_page():
                    page_num += 1
                    time.sleep(random.uniform(3, 6))
                else:
                    break
            else:
                break
        
        return jobs
    
    def go_to_next_page(self):
        """翻到下一页"""
        try:
            # 多种翻页按钮选择器
            next_selectors = [
                '.ui-icon-arrow-right',
                'text:下一页',
                '.page-next',
                'a[ka="page-next"]'
            ]
            
            for selector in next_selectors:
                next_btn = self.page.ele(selector, timeout=2)
                if next_btn and 'disabled' not in (next_btn.attr('class') or ''):
                    next_btn.click()
                    return True
            
            print("找不到下一页按钮或已到最后一页")
            return False
            
        except Exception as e:
            print(f"翻页失败: {e}")
            return False
    
    def extract_job_info(self, card):
        """提取单个职位信息"""
        job_info = {}
        
        try:
            # 使用多种选择器提取信息
            selectors = {
                '职位名称': ['.job-name', '.job-title', 'h3 a'],
                '薪资': ['.salary', '.red'],
                '公司名称': ['.company-name', '.company-text h3'],
                '工作地点': ['.job-area', '.job-area-wrapper'],
                '工作经验': ['.job-limit', '.job-detail .job-limit'],
                'HR信息': ['.boss-info', '.boss-name']
            }
            
            for key, selectors_list in selectors.items():
                for selector in selectors_list:
                    element = card.ele(selector, timeout=1)
                    if element and element.text.strip():
                        job_info[key] = element.text.strip()
                        break
                else:
                    job_info[key] = ''
            
            # 提取公司信息
            company_tags = card.eles('.company-tag-list li')
            if company_tags:
                job_info['公司规模'] = company_tags[0].text if len(company_tags) > 0 else ''
                job_info['公司行业'] = company_tags[1].text if len(company_tags) > 1 else ''
            else:
                job_info['公司规模'] = ''
                job_info['公司行业'] = ''
            
            # 处理工作经验和学历
            if job_info['工作经验']:
                parts = job_info['工作经验'].split('·')
                if len(parts) >= 2:
                    job_info['工作经验'] = parts[0]
                    job_info['学历要求'] = parts[1]
                else:
                    job_info['学历要求'] = ''
            else:
                job_info['学历要求'] = ''
            
            # 职位标签
            tags = card.eles('.tag-list li')
            job_info['职位标签'] = '|'.join([tag.text for tag in tags if tag.text]) if tags else ''
            
            # 职位链接
            job_link = card.ele('a', timeout=1)
            if job_link and job_link.attr('href'):
                href = job_link.attr('href')
                job_info['职位链接'] = f"https://www.zhipin.com{href}" if href.startswith('/') else href
            else:
                job_info['职位链接'] = ''
            
            return job_info
            
        except Exception as e:
            print(f"解析职位信息出错: {e}")
            return None
    
    def save_to_excel(self, jobs, filename):
        """保存数据到Excel文件"""
        if not jobs:
            print("没有数据可保存")
            return
        
        df = pd.DataFrame(jobs)
        
        # 列顺序
        columns_order = ['职位名称', '薪资', '公司名称', '公司规模', '公司行业', 
                        '工作地点', '工作经验', '学历要求', '职位标签', 'HR信息', '职位链接']
        
        # 确保所有列都存在
        for col in columns_order:
            if col not in df.columns:
                df[col] = ''
        
        df = df[columns_order]
        
        # 保存到Excel
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"数据已保存到: {filename}")
        print(f"共保存{len(jobs)}条职位信息")
        
        # 显示数据预览
        print("\n数据预览:")
        print(df[['职位名称', '薪资', '公司名称', '工作地点']].head())
    
    def close(self):
        """关闭浏览器"""
        if hasattr(self, 'browser'):
            self.browser.quit()

def main():
    scraper = BossZhipinAutoScraper()
    
    try:
        # 检查配置
        if not scraper.config['phone']:
            print("请先在boss_config.json中配置登录信息:")
            print("- phone: 手机号")
            print("- password: 密码")
            return
        
        # 输入搜索参数
        keyword = input("请输入职位关键词 (默认: Python开发): ").strip() or "Python开发"
        city = input("请输入城市 (默认: 上海): ").strip() or "上海"
        pages = int(input("请输入爬取页数 (默认: 3): ").strip() or "3")
        
        # 搜索职位
        jobs = scraper.search_jobs(keyword, city, pages)
        
        if jobs:
            # 保存到Excel文件
            filename = f"boss直聘_{keyword}_{city}_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
            scraper.save_to_excel(jobs, filename)
        else:
            print("未获取到职位数据")
    
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()