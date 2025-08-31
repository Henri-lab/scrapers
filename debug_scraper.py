#!/usr/bin/env python3
"""
Job Scraper Debug Script
用于详细调试爬虫功能的脚本
"""
import sys
import os
import logging
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_imports():
    """测试所有依赖包导入"""
    logger.info("=== 测试依赖包导入 ===")
    
    try:
        import requests
        logger.info(f"✓ requests: {requests.__version__}")
    except ImportError as e:
        logger.error(f"✗ requests导入失败: {e}")
        return False
    
    try:
        import bs4
        logger.info(f"✓ beautifulsoup4: {bs4.__version__}")
    except ImportError as e:
        logger.error(f"✗ beautifulsoup4导入失败: {e}")
        return False
    
    try:
        import selenium
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        logger.info(f"✓ selenium: {selenium.__version__}")
    except ImportError as e:
        logger.error(f"✗ selenium导入失败: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        logger.info("✓ python-dotenv: 已导入")
    except ImportError as e:
        logger.error(f"✗ python-dotenv导入失败: {e}")
        return False
    
    try:
        import schedule
        logger.info("✓ schedule: 已导入")
    except ImportError as e:
        logger.error(f"✗ schedule导入失败: {e}")
        return False
    
    return True

def test_api_connection():
    """测试API连接"""
    logger.info("=== 测试API连接 ===")
    
    import requests
    
    api_base = os.getenv('API_BASE_URL', 'http://localhost:3001/api')
    logger.info(f"API地址: {api_base}")
    
    # 测试基础连接
    try:
        response = requests.get('http://localhost:3001', timeout=5)
        logger.info(f"✓ 服务器连接成功: {response.status_code}")
        logger.debug(f"响应内容: {response.text[:200]}...")
    except Exception as e:
        logger.error(f"✗ 服务器连接失败: {e}")
        return False
    
    # 测试API端点
    try:
        response = requests.get(f'{api_base}/jobs', timeout=5)
        logger.info(f"✓ API端点连接: {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠ API端点测试: {e}")
    
    return True

def test_webdriver_setup():
    """测试WebDriver配置"""
    logger.info("=== 测试WebDriver配置 ===")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        logger.info("✓ Chrome选项配置完成")
        
        # 尝试创建WebDriver实例
        try:
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("✓ Chrome WebDriver创建成功")
            
            # 测试访问页面
            driver.get("https://www.baidu.com")
            title = driver.title
            logger.info(f"✓ 页面访问测试成功: {title}")
            
            driver.quit()
            return True
            
        except Exception as e:
            logger.error(f"✗ Chrome WebDriver创建失败: {e}")
            logger.info("提示: 请确保已安装Chrome浏览器和ChromeDriver")
            return False
            
    except ImportError as e:
        logger.error(f"✗ Selenium导入失败: {e}")
        return False

def test_scraper_init():
    """测试爬虫初始化"""
    logger.info("=== 测试爬虫初始化 ===")
    
    try:
        from job_scraper import JobScraper
        
        scraper = JobScraper()
        logger.info(f"✓ 爬虫初始化成功")
        logger.info(f"  - API地址: {scraper.api_base_url}")
        logger.info(f"  - API Token: {'已设置' if scraper.api_token else '未设置'}")
        
        scraper.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ 爬虫初始化失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_single_scrape():
    """测试单次爬取功能"""
    logger.info("=== 测试单次爬取功能 ===")
    
    try:
        from job_scraper import JobScraper
        
        scraper = JobScraper()
        
        # 测试爬取少量数据
        logger.info("开始测试Boss直聘爬取...")
        jobs = scraper.scrape_zhipin(keyword="Python", city="北京", pages=1)
        
        logger.info(f"✓ 爬取完成，获取到 {len(jobs)} 个职位")
        
        if jobs:
            # 打印第一个职位的详细信息
            job = jobs[0]
            logger.info("=== 第一个职位信息 ===")
            for key, value in job.items():
                logger.info(f"  {key}: {value}")
        
        scraper.close()
        return len(jobs) > 0
        
    except Exception as e:
        logger.error(f"✗ 单次爬取测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """主调试流程"""
    logger.info(f"=== 开始爬虫调试 - {datetime.now()} ===")
    
    # 1. 测试依赖包
    if not test_imports():
        logger.error("依赖包测试失败，请检查环境配置")
        return
    
    # 2. 测试API连接
    if not test_api_connection():
        logger.error("API连接测试失败，请启动后端服务")
        return
    
    # 3. 测试WebDriver
    if not test_webdriver_setup():
        logger.error("WebDriver测试失败，请检查Chrome配置")
        return
    
    # 4. 测试爬虫初始化
    if not test_scraper_init():
        logger.error("爬虫初始化失败")
        return
    
    # 5. 测试单次爬取
    if not test_single_scrape():
        logger.error("单次爬取测试失败")
        return
    
    logger.info("=== 所有测试通过！爬虫功能正常 ===")

if __name__ == "__main__":
    main()