"""
Boss直聘爬虫 - 兼容层

这是一个轻量级的兼容层，用于保持向后兼容。
实际功能由新的模块化架构提供。
"""

import os
import sys
from typing import Dict, List, Optional

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

# 导入新的模块化组件
from .config import BossConfig
from .scraper import BossScraper


class BossJobScraper:
    """Boss直聘职位爬虫 - 兼容旧接口的入口类"""
    
    def __init__(self, config: Optional[BossConfig] = None):
        """初始化Boss直聘职位爬虫"""
        self.config = config or BossConfig()
        self.scraper = BossScraper(self.config)
        self._initialized = False
    
    def initialize(self, **auth_params) -> bool:
        """
        初始化爬虫（包括浏览器、认证等）
        
        Args:
            **auth_params: 认证参数
                cookies: cookies列表
                cookie_string: cookie字符串  
                cookie_file: cookies文件路径
                token: 认证token
        
        Returns:
            bool: 是否成功初始化
        """
        result = self.scraper.initialize(**auth_params)
        self._initialized = result
        return result
    
    def search_jobs(self, search_params: Dict) -> Dict:
        """
        搜索职位 - 使用数据包监听获取API响应

        Args:
            search_params: 搜索参数

        Returns:
            dict: 搜索结果
        """
        if not self._initialized:
            if not self.initialize():
                return {"success": False, "message": "爬虫初始化失败"}
        
        return self.scraper.search_jobs(search_params)
    
    def search_jobs_with_scrolling(
        self, search_params: Dict, manual_scroll: bool = False, max_scroll_times: int = 10
    ) -> Dict:
        """
        通过滚动页面持续监听获取更多职位数据

        Args:
            search_params: 搜索参数
            manual_scroll: 是否手动滚动
            max_scroll_times: 最大滚动次数

        Returns:
            dict: 所有搜索结果
        """
        if not self._initialized:
            if not self.initialize():
                return {"success": False, "message": "爬虫初始化失败"}
        
        return self.scraper.search_jobs_with_scrolling(
            search_params, manual_scroll, max_scroll_times
        )
    
    def batch_search(self, search_params: Dict, max_pages: int = 5) -> Dict:
        """
        批量搜索多页职位

        Args:
            search_params: 搜索参数
            max_pages: 最大页数

        Returns:
            dict: 搜索结果
        """
        if not self._initialized:
            if not self.initialize():
                return {"success": False, "message": "爬虫初始化失败"}
        
        return self.scraper.batch_search(search_params, max_pages)
    
    def extract_job_data(self, job_list: List[Dict]) -> List[Dict]:
        """
        提取职位数据（兼容旧接口）

        Args:
            job_list: 原始职位列表

        Returns:
            list: 格式化的职位数据
        """
        return self.scraper.data_processor.extract_job_list(job_list)
    
    def save_current_cookies(self, file_path: str) -> bool:
        """
        保存当前cookies到文件
        
        Args:
            file_path: 保存路径
            
        Returns:
            bool: 是否保存成功
        """
        if not self._initialized:
            print("❌ 爬虫未初始化")
            return False
        
        return self.scraper.save_current_cookies(file_path)
    
    def close(self):
        """关闭浏览器"""
        if self.scraper:
            self.scraper.close()
        self._initialized = False


# API 接口函数，供 Node.js 后台调用
def search_boss_jobs(params: Dict, **auth_params) -> Dict:
    """
    Boss直聘职位搜索API接口

    Args:
        params: 搜索参数
        **auth_params: 认证参数（cookies、cookie_string、cookie_file、token）

    Returns:
        dict: 搜索结果
    """
    scraper = None
    try:
        scraper = BossJobScraper()
        
        # 初始化爬虫（包括认证）
        if not scraper.initialize(**auth_params):
            return {"success": False, "jobs": [], "total_jobs": 0, "error": "初始化失败"}

        # 提取参数
        search_params = {
            "query": params.get("query", ""),
            "city": params.get("city", ""),
            "district": params.get("district", ""),
            "experience": params.get("experience", ""),
            "degree": params.get("degree", ""),
            "salary": params.get("salary", ""),
            "scale": params.get("scale", ""),
            "stage": params.get("stage", ""),
            "job_type": params.get("job_type", ""),
            "page_size": params.get("page_size", 15),
        }

        max_pages = params.get("max_pages", 3)

        # 批量搜索
        result = scraper.batch_search(search_params, max_pages)

        return result

    except Exception as e:
        return {"success": False, "jobs": [], "total_jobs": 0, "error": str(e)}
    finally:
        if scraper:
            scraper.close()


# 测试函数
def test_scraper(**auth_params):
    """测试爬虫功能"""
    test_params = {
        "query": "Python开发",
        "city": "上海",
        "experience": "1-3年",
        "degree": "本科",
        "salary": "10-20K",
        "max_pages": 2,
    }

    print("开始测试Boss直聘职位爬虫...")
    
    try:
        result = search_boss_jobs(test_params, **auth_params)

        if result["success"]:
            print(f"✅ 测试成功!")
            print(f"   获取职位数: {result['total_jobs']}")
            print(f"   爬取页数: {result.get('pages_fetched', 'N/A')}")

            # 显示前3个职位
            if result["jobs"]:
                print("\n前3个职位预览:")
                for i, job in enumerate(result["jobs"][:3]):
                    print(
                        f"   {i+1}. {job['job_name']} | {job['salary_desc']} | {job['brand_name']} | {job['city_name']}"
                    )
        else:
            print(f"❌ 测试失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")


if __name__ == "__main__":
    # 示例：使用cookie字符串测试
    # test_scraper(cookie_string="your_cookie_string_here")
    
    # 示例：使用cookie文件测试
    # test_scraper(cookie_file="/path/to/cookies.json")
    
    # 示例：手动登录测试
    test_scraper()