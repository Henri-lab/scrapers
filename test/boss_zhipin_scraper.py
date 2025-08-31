from DrissionPage import Chromium, ChromiumOptions
import pandas as pd
import time
import random
from urllib.parse import quote

class BossZhipinScraper:
    def __init__(self):
        self.path = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.base_url = "https://www.zhipin.com"
        self.setup_browser()
    
    def setup_browser(self):
        """配置浏览器"""
        co = ChromiumOptions().set_browser_path(self.path).auto_port()
        # 添加一些常用的反检测选项
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_argument('--disable-dev-shm-usage')
        co.set_argument('--no-sandbox')
        
        self.browser = Chromium(co)
        self.page = self.browser.latest_tab
        
        # 设置用户代理
        self.page.run_js('''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        ''')
    
    def login_check_and_wait(self):
        """检查登录状态，如果需要登录则等待用户手动登录"""
        print("正在访问boss直聘...")
        self.page.get(self.base_url)
        time.sleep(3)
        
        # 检查是否需要登录
        if self.page.ele('.sign-form', timeout=2) or '登录' in self.page.html:
            print("\n=== 需要登录 ===")
            print("请在浏览器中手动登录boss直聘")
            print("登录完成后，按回车键继续...")
            input()
            
            # 验证登录状态
            self.page.refresh()
            time.sleep(2)
            if self.page.ele('.user-nav', timeout=3):
                print("登录成功！")
                return True
            else:
                print("登录验证失败，请重试")
                return False
        else:
            print("无需登录，可直接使用")
            return True
    
    def search_jobs(self, keyword, city="上海"):
        """搜索职位"""
        if not self.login_check_and_wait():
            return []
        
        # 构建搜索URL
        search_url = f"https://www.zhipin.com/web/geek/job?query={quote(keyword)}&city={quote(city)}"
        print(f"搜索关键词: {keyword}")
        print(f"搜索城市: {city}")
        print(f"访问URL: {search_url}")
        
        self.page.get(search_url)
        time.sleep(random.uniform(2, 4))
        
        jobs = []
        page_num = 1
        max_pages = 5  # 限制爬取页数
        
        while page_num <= max_pages:
            print(f"正在爬取第{page_num}页...")
            
            # 等待页面加载
            job_cards = self.page.eles('.job-card-wrapper', timeout=10)
            
            if not job_cards:
                print("未找到职位信息，可能页面结构发生变化或被反爬虫拦截")
                break
            
            for card in job_cards:
                try:
                    job_info = self.extract_job_info(card)
                    if job_info:
                        jobs.append(job_info)
                except Exception as e:
                    print(f"提取职位信息时出错: {e}")
                    continue
            
            print(f"第{page_num}页完成，已获取{len(jobs)}个职位")
            
            # 尝试翻页
            next_btn = self.page.ele('.ui-icon-arrow-right', timeout=2)
            if next_btn and not next_btn.parent().attr('class').__contains__('disabled'):
                next_btn.click()
                time.sleep(random.uniform(3, 5))
                page_num += 1
            else:
                print("已到最后一页或找不到翻页按钮")
                break
        
        return jobs
    
    def extract_job_info(self, card):
        """提取单个职位信息"""
        job_info = {}
        
        try:
            # 职位名称
            job_name = card.ele('.job-name', timeout=1)
            job_info['职位名称'] = job_name.text if job_name else ''
            
            # 薪资
            salary = card.ele('.salary', timeout=1)
            job_info['薪资'] = salary.text if salary else ''
            
            # 公司名称
            company = card.ele('.company-name', timeout=1)
            job_info['公司名称'] = company.text if company else ''
            
            # 公司信息（规模、行业等）
            company_info = card.eles('.company-tag-list li')
            job_info['公司规模'] = company_info[0].text if len(company_info) > 0 else ''
            job_info['公司行业'] = company_info[1].text if len(company_info) > 1 else ''
            
            # 工作地点
            location = card.ele('.job-area', timeout=1)
            job_info['工作地点'] = location.text if location else ''
            
            # 工作经验和学历要求
            job_limit = card.ele('.job-limit', timeout=1)
            if job_limit:
                limit_parts = job_limit.text.split('·')
                job_info['工作经验'] = limit_parts[0] if len(limit_parts) > 0 else ''
                job_info['学历要求'] = limit_parts[1] if len(limit_parts) > 1 else ''
            
            # 职位描述/标签
            tags = card.eles('.tag-list li')
            job_info['职位标签'] = '|'.join([tag.text for tag in tags]) if tags else ''
            
            # HR信息
            boss_info = card.ele('.boss-info', timeout=1)
            job_info['HR信息'] = boss_info.text if boss_info else ''
            
            # 职位链接
            job_link = card.ele('a', timeout=1)
            job_info['职位链接'] = f"https://www.zhipin.com{job_link.attr('href')}" if job_link else ''
            
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
        
        # 调整列顺序
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
    
    def close(self):
        """关闭浏览器"""
        if hasattr(self, 'browser'):
            self.browser.quit()

def main():
    scraper = BossZhipinScraper()
    
    try:
        # 输入搜索关键词
        keyword = input("请输入职位关键词 (默认: Python开发): ").strip()
        if not keyword:
            keyword = "Python开发"
        
        city = input("请输入城市 (默认: 上海): ").strip()
        if not city:
            city = "上海"
        
        # 搜索职位
        jobs = scraper.search_jobs(keyword, city)
        
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