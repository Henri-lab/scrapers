import os
import sys
import json
import time
import random
from urllib.parse import quote
from DrissionPage import Chromium, ChromiumOptions

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入本地模块
import codeCreator
from queryCreator import QueryCreater


class BossJobScraper:
    def __init__(self):
        """初始化Boss直聘职位爬虫"""
        self.path = r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        self.base_url = "https://www.zhipin.com/web/geek/jobs"
        self.web_base_url = "https://www.zhipin.com"
        self.query_creator = QueryCreater()
        self.city_codes = self.load_city_codes()
        self.setup_browser()
        self.cookies_loaded = False

    def setup_browser(self):
        """设置浏览器"""
        co = ChromiumOptions().set_browser_path(self.path).auto_port()

        # 反检测设置
        co.set_argument("--disable-blink-features=AutomationControlled")
        co.set_argument("--disable-dev-shm-usage")
        co.set_argument("--no-sandbox")
        co.set_argument("--disable-gpu")
        co.set_argument("--disable-extensions")
        co.set_argument("--disable-notifications")

        # 随机用户代理
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        user_agent = random.choice(user_agents)
        co.set_argument(f"--user-agent={user_agent}")

        self.browser = Chromium(co)
        self.page = self.browser.latest_tab

        # 执行反检测脚本
        self.page.run_js(
            """
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
        """
        )

    def ensure_proper_access(self):
        """确保正确的访问流程"""
        if not self.cookies_loaded:
            print("正在初始化访问...")
            # 首先访问主页
            self.page.get(self.web_base_url)
            time.sleep(random.uniform(2, 4))

            # 访问搜索页面建立会话
            search_page = f"{self.web_base_url}/web/geek/job"
            self.page.get(search_page)
            time.sleep(random.uniform(3, 5))

            # 模拟用户交互
            try:
                # 尝试点击搜索框或其他元素
                search_input = self.page.ele('input[placeholder*="搜索"]', timeout=3)
                if search_input:
                    search_input.click()
                    time.sleep(1)
            except:
                pass

            self.cookies_loaded = True
            print("初始化访问完成")

    def build_url(self, search_params, url_type="web"):
        """
        构建搜索URL

        Args:
            search_params (dict): 搜索参数
            url_type (str): URL类型 - "web": 网页版, "api": API接口

        Returns:
            str: 构建的URL
        """
        # 选择基础URL
        if url_type == "api":
            base_url = "https://www.zhipin.com/wapi/zpgeek/search/joblist.json"
            # API参数
            params = {
                "page": search_params.get("page", 1),
                "pageSize": search_params.get("page_size", 15),
                "scene": 1,
            }
        else:
            base_url = "https://www.zhipin.com/web/geek/job"
            params = {}

        # 搜索关键词
        if search_params.get("query"):
            params["query"] = search_params["query"]

        # 城市代码
        city_name = search_params.get("city")
        if city_name:
            city_code = self.city_codes.get(city_name)
            if city_code:
                params["city"] = city_code
            else:
                print(f"警告: 未找到城市 '{city_name}' 的代码")

        # 商圈代码
        district_name = search_params.get("district")
        if district_name and city_name:
            try:
                business_codes = codeCreator.getBusinessDistrictCodes(city_name)
                district_code = business_codes.get(district_name)
                if district_code:
                    params["multiBusinessDistrict"] = district_code
            except Exception as e:
                print(f"获取商圈代码失败: {e}")

        # 其他查询条件
        condition_mappings = [
            ("experience", "experience"),
            ("degree", "degree"),
            ("salary", "salary"),
            ("scale", "scale"),
            ("stage", "stage"),
            ("job_type", "jobType"),
        ]

        for param_key, query_key in condition_mappings:
            value = search_params.get(param_key)
            if value:
                code = self.query_creator.get_code(query_key, value)
                if code:
                    params[param_key] = code

        # 构建URL
        if params:
            param_str = "&".join(
                [f"{k}={quote(str(v))}" for k, v in params.items() if v]
            )
            return f"{base_url}?{param_str}"
        return base_url

    def search_jobs(self, search_params):
        """
        搜索职位

        Args:
            search_params (dict): 搜索参数

        Returns:
            dict: 搜索结果
        """
        try:
            # 确保正确的访问流程
            self.ensure_proper_access()

            # 先访问网页搜索页面
            web_url = self.build_url(search_params, "web")
            print(f"访问网页搜索: {web_url}")
            self.page.get(web_url)
            time.sleep(random.uniform(3, 6))

            # 等待页面加载完成
            self.page.wait.load_complete()
            time.sleep(2)

            # 现在尝试获取API数据
            api_url = self.build_url(search_params, "api")
            print(f"请求API: {api_url}")

            # 使用浏览器访问API
            self.page.get(api_url)
            time.sleep(random.uniform(2, 4))

            # 获取页面JSON数据
            page_text = self.page.html

            # 尝试解析JSON
            try:
                data = json.loads(page_text)
            except json.JSONDecodeError:
                # 如果页面不是纯JSON，尝试从<pre>标签中提取
                pre_elem = self.page.ele("pre")
                if pre_elem:
                    data = json.loads(pre_elem.text)
                else:
                    # 检查是否被重定向或需要验证
                    current_url = self.page.url
                    if "login" in current_url or "verify" in current_url:
                        return {
                            "success": False,
                            "data": None,
                            "message": "需要登录或验证",
                        }
                    raise Exception(f"无法解析响应数据，当前页面: {current_url}")

            # 检查响应状态
            if data.get("code") == 0:
                return {
                    "success": True,
                    "data": data.get("zpData", {}),
                    "message": "搜索成功",
                }
            elif data.get("code") == 37:  # 访问异常
                return {
                    "success": False,
                    "data": None,
                    "message": "访问被限制，需要等待或更换IP",
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": data.get("message", "搜索失败"),
                }

        except Exception as e:
            return {"success": False, "data": None, "message": f"搜索失败: {str(e)}"}

    def extract_job_data(self, job_list):
        """
        提取职位数据

        Args:
            job_list (list): 原始职位列表

        Returns:
            list: 格式化的职位数据
        """
        jobs = []

        for job in job_list:
            try:
                job_info = {
                    "job_name": job.get("jobName", ""),
                    "salary_desc": job.get("salaryDesc", ""),
                    "job_degree": job.get("jobDegree", ""),
                    "job_experience": job.get("jobExperience", ""),
                    "city_name": job.get("cityName", ""),
                    "area_district": job.get("areaDistrict", ""),
                    "business_district": job.get("businessDistrict", ""),
                    "job_type": job.get("jobType", ""),
                    "prolong": job.get("prolong", ""),
                    "job_labels": job.get("jobLabels", []),
                    "job_valid_status": job.get("jobValidStatus", ""),
                    "icon_word": job.get("iconWord", ""),
                    "skills": job.get("skills", []),
                    "job_id": job.get("encryptJobId", ""),
                    "lid": job.get("lid", ""),
                    "security_id": job.get("securityId", ""),
                    # 公司信息
                    "brand_name": job.get("brandName", ""),
                    "brand_logo": job.get("brandLogo", ""),
                    "brand_stage_name": job.get("brandStageName", ""),
                    "brand_industry": job.get("brandIndustry", ""),
                    "brand_scale_name": job.get("brandScaleName", ""),
                    "welfare_list": job.get("welfareList", []),
                    "company_id": job.get("encryptBrandId", ""),
                    # HR信息
                    "boss_name": job.get("bossName", ""),
                    "boss_title": job.get("bossTitle", ""),
                    "boss_avatar": job.get("bossAvatar", ""),
                    "boss_id": job.get("encryptBossId", ""),
                    # 其他信息
                    "expect_id": job.get("expectId", ""),
                    "job_status_desc": job.get("jobStatusDesc", ""),
                    "contact_chat_im": job.get("contactChatIm", ""),
                    "last_modify_time": job.get("lastModifyTime", ""),
                }

                jobs.append(job_info)

            except Exception as e:
                print(f"提取职位信息失败: {e}")
                continue

        return jobs

    def batch_search(self, search_params, max_pages=5):
        """
        批量搜索多页职位

        Args:
            search_params (dict): 搜索参数
            max_pages (int): 最大页数

        Returns:
            dict: 搜索结果
        """
        all_jobs = []
        total_count = 0

        for page in range(1, max_pages + 1):
            search_params["page"] = page
            result = self.search_jobs(search_params)

            if not result["success"]:
                print(f"第{page}页搜索失败: {result['message']}")
                break

            data = result["data"]
            job_list = data.get("jobList", [])

            if not job_list:
                print(f"第{page}页无更多职位")
                break

            page_jobs = self.extract_job_data(job_list)
            all_jobs.extend(page_jobs)

            # 获取总数信息（第一页）
            if page == 1:
                total_count = data.get("totalCount", 0)
                print(f"搜索到总计 {total_count} 个职位")

            print(f"第{page}页获取 {len(page_jobs)} 个职位")

            # 检查是否还有下一页
            if not data.get("hasMore", False):
                print("已到最后一页")
                break

            # 随机延时防止被封
            time.sleep(random.uniform(2, 5))

        return {
            "success": True,
            "jobs": all_jobs,
            "total_jobs": len(all_jobs),
            "total_count": total_count,
            "pages_fetched": min(page, max_pages),
        }

    def close(self):
        """关闭浏览器"""
        try:
            if hasattr(self, "browser"):
                self.browser.quit()
        except:
            pass


# API 接口函数，供 Node.js 后台调用
def search_boss_jobs(params):
    """
    Boss直聘职位搜索API接口

    Args:
        params (dict): 搜索参数
            {
                "query": "Python开发",
                "city": "上海",
                "district": "黄浦区",
                "experience": "1-3年",
                "degree": "本科",
                "salary": "10-20K",
                "scale": "100-499人",
                "stage": "A轮",
                "job_type": "全职",
                "max_pages": 3
            }

    Returns:
        dict: 搜索结果
    """
    scraper = None
    try:
        scraper = BossJobScraper()

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
def test_scraper():
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
    result = search_boss_jobs(test_params)

    if result["success"]:
        print(f"✅ 测试成功!")
        print(f"   获取职位数: {result['total_jobs']}")
        print(f"   爬取页数: {result['pages_fetched']}")

        # 显示前3个职位
        if result["jobs"]:
            print("\\n前3个职位预览:")
            for i, job in enumerate(result["jobs"][:3]):
                print(
                    f"   {i+1}. {job['job_name']} | {job['salary_desc']} | {job['brand_name']} | {job['city_name']}"
                )
    else:
        print(f"❌ 测试失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    test_scraper()
