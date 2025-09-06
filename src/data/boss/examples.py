"""
Boss直聘爬虫使用示例

这个文件展示了如何使用重构后的Boss爬虫模块。
"""

from boss_scraper import BossJobScraper


def example_1_manual_login():
    """示例1：手动登录"""
    print("=== 示例1：手动登录 ===")
    
    scraper = BossJobScraper()
    try:
        # 手动登录方式
        if scraper.initialize():
            search_params = {
                "query": "Python开发",
                "city": "上海",
                "experience": "1-3年",
                "salary": "10-20K"
            }
            
            result = scraper.search_jobs(search_params)
            if result["success"]:
                print(f"搜索成功，获得 {len(result['data'].get('jobList', []))} 个职位")
            else:
                print(f"搜索失败: {result['message']}")
        else:
            print("初始化失败")
    
    finally:
        scraper.close()


def example_2_cookie_string():
    """示例2：使用cookie字符串"""
    print("=== 示例2：使用cookie字符串 ===")
    
    # 请替换为你的实际cookie字符串
    cookie_string = """
    wt2=D_OkbIInVxXsGKxMpJjhJqvLvs_aKL0ldZVHTRQJ7IebkzxINJLqDqHf_kjNJQYNK37wuKVBK3qmgDmNHnAtyJA~~;
    __zp_stoken__=your_token_here;
    _uab_collina=your_collina_here
    """
    
    scraper = BossJobScraper()
    try:
        if scraper.initialize(cookie_string=cookie_string.strip()):
            search_params = {
                "query": "数据分析",
                "city": "北京",
                "degree": "本科",
                "salary": "15-25K"
            }
            
            # 批量搜索多页
            result = scraper.batch_search(search_params, max_pages=3)
            if result["success"]:
                print(f"批量搜索成功，获得 {result['total_jobs']} 个职位")
                
                # 保存数据
                if result["jobs"]:
                    scraper.scraper.data_processor.save_jobs_data(
                        result["jobs"], 
                        "example_data_analysis_jobs.json"
                    )
            else:
                print(f"搜索失败: {result.get('message', '未知错误')}")
        else:
            print("Cookie认证失败")
    
    finally:
        scraper.close()


def example_3_cookie_file():
    """示例3：使用cookie文件"""
    print("=== 示例3：使用cookie文件 ===")
    
    # cookies文件应该是JSON格式，包含cookie列表
    cookie_file = "cookies.json"
    
    scraper = BossJobScraper()
    try:
        if scraper.initialize(cookie_file=cookie_file):
            search_params = {
                "query": "前端开发",
                "city": "深圳",
                "experience": "3-5年",
                "salary": "20-30K"
            }
            
            # 滚动搜索获取更多数据
            result = scraper.search_jobs_with_scrolling(
                search_params, 
                manual_scroll=False,  # 自动滚动
                max_scroll_times=5
            )
            
            if result["success"]:
                print(f"滚动搜索成功，获得 {result['total_jobs']} 个职位")
                print(f"处理了 {result['packets_processed']} 个数据包")
            else:
                print(f"搜索失败: {result['message']}")
        else:
            print("Cookie文件加载失败")
    
    finally:
        scraper.close()


def example_4_save_cookies():
    """示例4：保存当前cookies"""
    print("=== 示例4：保存当前cookies ===")
    
    scraper = BossJobScraper()
    try:
        # 手动登录后保存cookies
        if scraper.initialize():
            # 搜索一次确保session有效
            search_params = {"query": "测试", "city": "上海"}
            scraper.search_jobs(search_params)
            
            # 保存cookies供下次使用
            if scraper.save_current_cookies("my_cookies.json"):
                print("Cookies已保存到 my_cookies.json")
            else:
                print("保存cookies失败")
        else:
            print("初始化失败")
    
    finally:
        scraper.close()


def example_5_custom_config():
    """示例5：自定义配置"""
    print("=== 示例5：自定义配置 ===")
    
    from config import BossConfig
    
    # 创建自定义配置
    config = BossConfig()
    
    # 修改配置
    config.update_scraper_config(
        delays={
            "page_load": (5, 10),  # 增加页面加载等待时间
            "scroll": (3, 6),
            "request": (3, 8)
        },
        limits={
            "max_scroll_times": 20,  # 增加最大滚动次数
            "max_pages": 10
        }
    )
    
    # 使用自定义配置创建爬虫
    scraper = BossJobScraper(config)
    try:
        if scraper.initialize():
            search_params = {
                "query": "机器学习",
                "city": "杭州",
                "salary": "25-40K"
            }
            
            result = scraper.search_jobs_with_scrolling(
                search_params,
                max_scroll_times=config.get_limit("max_scroll_times")
            )
            
            if result["success"]:
                print(f"使用自定义配置搜索成功，获得 {result['total_jobs']} 个职位")
            else:
                print(f"搜索失败: {result['message']}")
        else:
            print("初始化失败")
    
    finally:
        scraper.close()


if __name__ == "__main__":
    print("Boss直聘爬虫使用示例")
    print("请选择要运行的示例：")
    print("1. 手动登录")
    print("2. 使用cookie字符串")
    print("3. 使用cookie文件")
    print("4. 保存当前cookies")
    print("5. 自定义配置")
    
    choice = input("请输入选项 (1-5): ").strip()
    
    examples = {
        "1": example_1_manual_login,
        "2": example_2_cookie_string,
        "3": example_3_cookie_file,
        "4": example_4_save_cookies,
        "5": example_5_custom_config
    }
    
    if choice in examples:
        examples[choice]()
    else:
        print("无效选项")