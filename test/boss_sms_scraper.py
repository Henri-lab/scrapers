from DrissionPage import Chromium, ChromiumOptions
import pandas as pd
import time
import random
import json
import os
from urllib.parse import quote

class BossZhipinSmsScraper:
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
            "cookies_file": "boss_cookies.json",
            "login_method": "sms",  # sms: 短信验证码, manual: 手动登录
            "auto_send_sms": True,  # 是否自动发送短信验证码
            "user_agents": [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        }
        return default_config
        
        #if os.path.exists(self.config_file):
        #    with open(self.config_file, 'r', encoding='utf-8') as f:
        #        config = json.load(f)
        #    # 合并默认配置
        #    for key, value in default_config.items():
        #        if key not in config:
        #            config[key] = value
        #    return config
        #else:
        #    # 创建默认配置文件
        #    with open(self.config_file, 'w', encoding='utf-8') as f:
        #        json.dump(default_config, f, ensure_ascii=False, indent=2)
        #    print(f"已创建配置文件 {self.config_file}，请填入手机号")
        #    return default_config
    
    def setup_browser(self):
        """配置浏览器"""
        co = ChromiumOptions().set_browser_path(self.path).auto_port()
        
        # 反检测设置
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_argument('--disable-dev-shm-usage')
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-gpu')
        co.set_argument('--disable-extensions')
        co.set_argument('--disable-notifications')
        
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
            window.chrome = {
                runtime: {}
            };
        ''')
    
    def save_cookies(self):
        """保存cookies"""
        try:
            cookies = self.page.cookies()
            with open(self.config['cookies_file'], 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print("✅ Cookies已保存")
        except Exception as e:
            print(f"❌ 保存cookies失败: {e}")
    
    def load_cookies(self):
        """加载cookies"""
        if not os.path.exists(self.config['cookies_file']):
            return False
        
        try:
            with open(self.config['cookies_file'], 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            # 访问首页并设置cookies
            print("🔄 正在加载保存的登录状态...")
            self.page.get(self.base_url)
            time.sleep(2)
            
            for cookie in cookies:
                try:
                    self.page.set_cookie(**cookie)
                except Exception as e:
                    continue
            
            # 刷新页面验证cookies
            self.page.refresh()
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"❌ 加载cookies失败: {e}")
            return False
    
    def sms_login(self):
        """短信验证码登录"""
        if not self.config['phone']:
            print("❌ 请在配置文件中设置手机号")
            return False
        
        try:
            print("📱 开始短信验证码登录...")
            
            # 访问登录页面
            login_url = f"{self.base_url}/web/user/login"
            self.page.get(login_url)
            time.sleep(3)
            
            # 等待页面完全加载
            self.page.wait.load_complete()
            
            # 查找手机号输入框（多种选择器）
            phone_selectors = [
                'input[placeholder*="手机号"]',
                'input[name="phone"]',
                'input[type="tel"]',
                '.form-input input[placeholder*="手机"]'
            ]
            
            phone_input = None
            for selector in phone_selectors:
                phone_input = self.page.ele(selector, timeout=3)
                if phone_input:
                    break
            
            if not phone_input:
                print("❌ 找不到手机号输入框，页面结构可能已变更")
                return False
            
            # 输入手机号
            print(f"📞 输入手机号: {self.config['phone']}")
            phone_input.clear()
            time.sleep(0.5)
            phone_input.input(self.config['phone'])
            time.sleep(1)
            
            # 发送验证码
            if self.config.get('auto_send_sms', True):
                send_code_selectors = [
                    'button:has-text("获取验证码")',
                    'button:has-text("发送验证码")',
                    '.send-code-btn',
                    'button[class*="code"]',
                    'text:获取验证码',
                    'text:发送验证码'
                ]
                
                send_btn = None
                for selector in send_code_selectors:
                    send_btn = self.page.ele(selector, timeout=2)
                    if send_btn:
                        break
                
                if send_btn:
                    print("📨 正在发送验证码...")
                    send_btn.click()
                    time.sleep(2)
                    
                    # 检查是否有错误提示
                    error_msg = self.page.ele('.error-msg', timeout=2)
                    if error_msg:
                        print(f"❌ 发送验证码失败: {error_msg.text}")
                        return False
                    
                    print("✅ 验证码已发送，请查收短信")
                else:
                    print("⚠️  找不到发送验证码按钮，请手动点击发送")
            
            # 等待用户输入验证码
            print("🔢 请输入收到的短信验证码:")
            sms_code = input("验证码: ").strip()
            
            if not sms_code:
                print("❌ 验证码不能为空")
                return False
            
            # 查找验证码输入框
            code_selectors = [
                'input[placeholder*="验证码"]',
                'input[name="code"]',
                'input[maxlength="6"]',
                '.form-input input[placeholder*="码"]'
            ]
            
            code_input = None
            for selector in code_selectors:
                code_input = self.page.ele(selector, timeout=3)
                if code_input:
                    break
            
            if not code_input:
                print("❌ 找不到验证码输入框")
                return False
            
            # 输入验证码
            code_input.clear()
            time.sleep(0.5)
            code_input.input(sms_code)
            time.sleep(1)
            
            # 点击登录按钮
            login_selectors = [
                'button:has-text("登录")',
                '.login-btn',
                'button[type="submit"]',
                '.btn-login'
            ]
            
            login_btn = None
            for selector in login_selectors:
                login_btn = self.page.ele(selector, timeout=3)
                if login_btn:
                    break
            
            if not login_btn:
                print("❌ 找不到登录按钮")
                return False
            
            print("🔐 正在登录...")
            login_btn.click()
            time.sleep(5)
            
            # 检查登录结果
            if self.check_login_status():
                print("🎉 登录成功！")
                self.save_cookies()
                return True
            else:
                # 检查是否有错误信息
                error_selectors = ['.error-msg', '.toast-error', '.tips-error']
                for selector in error_selectors:
                    error_elem = self.page.ele(selector, timeout=1)
                    if error_elem:
                        print(f"❌ 登录失败: {error_elem.text}")
                        return False
                
                print("❌ 登录失败，请检查验证码是否正确")
                return False
                
        except Exception as e:
            print(f"❌ 短信登录过程出错: {e}")
            return False
    
    def check_login_status(self):
        """检查登录状态"""
        # 检查多种登录成功的标识
        success_indicators = [
            '.user-nav',           # 用户导航菜单
            '.nav-figure',         # 用户头像
            '.header-username',    # 用户名
            'text:我的简历',        # 我的简历文本
            'text:个人中心',        # 个人中心文本
            '.geek-nav'           # 求职者导航
        ]
        
        for indicator in success_indicators:
            if self.page.ele(indicator, timeout=2):
                return True
        
        # 检查URL变化
        current_url = self.page.url
        if any(path in current_url for path in ['/web/geek/', '/web/boss/', '/index.html']):
            return True
        
        # 检查页面标题
        title = self.page.title
        if '登录' not in title and 'BOSS直聘' in title:
            return True
            
        return False
    
    def ensure_login(self):
        """确保已登录"""
        print("🔍 检查登录状态...")
        
        # 方法1: 尝试加载保存的cookies
        if self.load_cookies():
            if self.check_login_status():
                print("✅ 使用保存的登录状态成功")
                return True
            else:
                print("⚠️  保存的登录状态已失效")
        
        # 方法2: 短信验证码登录
        if self.config.get('login_method') == 'sms':
            if self.sms_login():
                return True
        
        # 方法3: 手动登录备用方案
        print("\n🔄 自动登录失败，启用手动登录模式")
        print("请在浏览器中手动完成登录...")
        self.page.get(f"{self.base_url}/web/user/login")
        
        print("⏳ 等待登录完成，登录后请按回车键继续...")
        input()
        
        # 验证手动登录状态
        if self.check_login_status():
            print("✅ 手动登录验证成功")
            self.save_cookies()
            return True
        
        print("❌ 登录验证失败")
        return False
    
    def search_jobs(self, keyword, city="上海", pages=3):
        """搜索职位"""
        if not self.ensure_login():
            print("❌ 登录失败，无法继续爬取")
            return []
        
        # 构建搜索URL
        search_url = f"https://www.zhipin.com/web/geek/job?query={quote(keyword)}&city={quote(city)}"
        print(f"\n🔍 搜索参数:")
        print(f"   关键词: {keyword}")
        print(f"   城市: {city}")
        print(f"   页数: {pages}")
        
        self.page.get(search_url)
        time.sleep(random.uniform(3, 5))
        
        jobs = []
        
        for page_num in range(1, pages + 1):
            print(f"\n📄 正在爬取第 {page_num} 页...")
            
            # 等待页面加载并查找职位卡片
            job_cards = self.wait_for_job_cards()
            
            if not job_cards:
                print("⚠️  未找到职位信息，可能遇到反爬虫限制")
                break
            
            # 提取当前页面的职位信息
            page_jobs = self.extract_page_jobs(job_cards)
            jobs.extend(page_jobs)
            
            print(f"✅ 第 {page_num} 页完成，获取 {len(page_jobs)} 个职位")
            print(f"📊 累计获取 {len(jobs)} 个职位")
            
            # 翻页
            if page_num < pages:
                if not self.go_to_next_page():
                    print("📄 已到最后一页")
                    break
                time.sleep(random.uniform(3, 6))
        
        return jobs
    
    def wait_for_job_cards(self, max_attempts=3):
        """等待并查找职位卡片"""
        job_cards_selectors = [
            '.job-card-wrapper',
            '.job-list-item', 
            '[ka="search_list_item"]',
            '.job-card',
            '.search-job-result li'
        ]
        
        for attempt in range(max_attempts):
            for selector in job_cards_selectors:
                job_cards = self.page.eles(selector, timeout=5)
                if job_cards:
                    return job_cards
            
            if attempt < max_attempts - 1:
                print(f"⏳ 第 {attempt + 1} 次尝试未找到职位，刷新页面重试...")
                self.page.refresh()
                time.sleep(3)
        
        return []
    
    def extract_page_jobs(self, job_cards):
        """提取当前页面的所有职位信息"""
        jobs = []
        
        for i, card in enumerate(job_cards):
            try:
                job_info = self.extract_job_info(card)
                if job_info and job_info.get('职位名称'):
                    jobs.append(job_info)
                
                # 随机延时
                if i % 3 == 0 and i > 0:
                    time.sleep(random.uniform(0.5, 1.5))
                    
            except Exception as e:
                print(f"⚠️  提取第 {i+1} 个职位信息时出错: {e}")
                continue
        
        return jobs
    
    def extract_job_info(self, card):
        """提取单个职位信息"""
        job_info = {}
        
        try:
            # 职位名称 - 多种选择器
            name_selectors = ['.job-name a', '.job-name', '.job-title', 'h3 a', '.position-name']
            for selector in name_selectors:
                name_elem = card.ele(selector, timeout=1)
                if name_elem and name_elem.text.strip():
                    job_info['职位名称'] = name_elem.text.strip()
                    break
            else:
                job_info['职位名称'] = ''
            
            # 薪资
            salary_selectors = ['.salary', '.red', '.job-limit .red']
            for selector in salary_selectors:
                salary_elem = card.ele(selector, timeout=1)
                if salary_elem and salary_elem.text.strip():
                    job_info['薪资'] = salary_elem.text.strip()
                    break
            else:
                job_info['薪资'] = ''
            
            # 公司名称
            company_selectors = ['.company-name a', '.company-name', '.company-text h3']
            for selector in company_selectors:
                company_elem = card.ele(selector, timeout=1)
                if company_elem and company_elem.text.strip():
                    job_info['公司名称'] = company_elem.text.strip()
                    break
            else:
                job_info['公司名称'] = ''
            
            # 工作地点
            location_selectors = ['.job-area', '.job-area-wrapper', '.work-addr']
            for selector in location_selectors:
                location_elem = card.ele(selector, timeout=1)
                if location_elem and location_elem.text.strip():
                    job_info['工作地点'] = location_elem.text.strip()
                    break
            else:
                job_info['工作地点'] = ''
            
            # 工作经验和学历要求
            limit_elem = card.ele('.job-limit', timeout=1)
            if limit_elem:
                limit_text = limit_elem.text.strip()
                parts = limit_text.split('·')
                job_info['工作经验'] = parts[0].strip() if parts else ''
                job_info['学历要求'] = parts[1].strip() if len(parts) > 1 else ''
            else:
                job_info['工作经验'] = ''
                job_info['学历要求'] = ''
            
            # 公司信息
            company_tags = card.eles('.company-tag-list li')
            if company_tags:
                job_info['公司规模'] = company_tags[0].text.strip() if len(company_tags) > 0 else ''
                job_info['公司行业'] = company_tags[1].text.strip() if len(company_tags) > 1 else ''
            else:
                job_info['公司规模'] = ''
                job_info['公司行业'] = ''
            
            # 职位标签
            tag_elems = card.eles('.tag-list li')
            tags = [tag.text.strip() for tag in tag_elems if tag.text.strip()]
            job_info['职位标签'] = ' | '.join(tags) if tags else ''
            
            # HR信息
            boss_elem = card.ele('.boss-info', timeout=1)
            job_info['HR信息'] = boss_elem.text.strip() if boss_elem else ''
            
            # 职位链接
            link_elem = card.ele('a', timeout=1)
            if link_elem and link_elem.attr('href'):
                href = link_elem.attr('href')
                job_info['职位链接'] = f"https://www.zhipin.com{href}" if href.startswith('/') else href
            else:
                job_info['职位链接'] = ''
            
            return job_info
            
        except Exception as e:
            print(f"⚠️  解析职位信息出错: {e}")
            return {}
    
    def go_to_next_page(self):
        """翻到下一页"""
        try:
            next_selectors = [
                '.ui-icon-arrow-right',
                'text:下一页',
                '.page-next:not(.disabled)',
                'a[ka="page-next"]:not(.disabled)'
            ]
            
            for selector in next_selectors:
                next_btn = self.page.ele(selector, timeout=3)
                if next_btn:
                    # 检查按钮是否可用
                    classes = next_btn.attr('class') or ''
                    if 'disabled' not in classes:
                        next_btn.click()
                        return True
            
            return False
            
        except Exception as e:
            print(f"⚠️  翻页失败: {e}")
            return False
    
    def save_to_excel(self, jobs, filename):
        """保存数据到Excel文件"""
        if not jobs:
            print("❌ 没有数据可保存")
            return
        
        try:
            df = pd.DataFrame(jobs)
            
            # 数据清理
            for col in df.columns:
                df[col] = df[col].astype(str).str.strip()
            
            # 列顺序
            columns_order = [
                '职位名称', '薪资', '公司名称', '公司规模', '公司行业', 
                '工作地点', '工作经验', '学历要求', '职位标签', 'HR信息', '职位链接'
            ]
            
            # 确保所有列都存在
            for col in columns_order:
                if col not in df.columns:
                    df[col] = ''
            
            df = df[columns_order]
            
            # 保存到Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            
            print(f"\n📊 数据保存成功!")
            print(f"   文件名: {filename}")
            print(f"   职位数: {len(jobs)} 个")
            
            # 显示数据预览
            if len(jobs) > 0:
                print(f"\n📋 数据预览 (前5条):")
                preview_cols = ['职位名称', '薪资', '公司名称', '工作地点']
                preview_df = df[preview_cols].head()
                for i, row in preview_df.iterrows():
                    print(f"   {i+1}. {row['职位名称']} | {row['薪资']} | {row['公司名称']} | {row['工作地点']}")
                    
        except Exception as e:
            print(f"❌ 保存Excel文件失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        try:
            if hasattr(self, 'browser'):
                self.browser.quit()
        except:
            pass

def main():
    scraper = None
    try:
        scraper = BossZhipinSmsScraper()
        
        # 检查配置
        if not scraper.config['phone']:
            print("❌ 请先在 boss_config.json 中配置手机号")
            print("   设置格式: \"phone\": \"您的手机号\"")
            return
        
        print("🚀 Boss直聘职位爬虫启动")
        print("=" * 50)
        
        # 输入搜索参数
        keyword = input("💼 请输入职位关键词 (默认: Python开发): ").strip() or "Python开发"
        city = input("🏙️  请输入城市 (默认: 上海): ").strip() or "上海"
        
        try:
            pages = int(input("📄 请输入爬取页数 (默认: 3): ").strip() or "3")
            pages = max(1, min(pages, 10))  # 限制在1-10页之间
        except:
            pages = 3
        
        print("\n" + "=" * 50)
        
        # 搜索职位
        jobs = scraper.search_jobs(keyword, city, pages)
        
        if jobs:
            # 生成文件名
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"boss直聘_{keyword}_{city}_{timestamp}.xlsx"
            
            # 保存到Excel文件
            scraper.save_to_excel(jobs, filename)
        else:
            print("❌ 未获取到任何职位数据")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
    finally:
        if scraper:
            scraper.close()
        print("\n👋 程序结束")

if __name__ == "__main__":
    main()