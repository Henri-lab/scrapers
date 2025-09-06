import time
import random
from typing import Dict, List, Optional, Any
from .auth import BossAuth
from .browser import BossBrowser
from .config import BossConfig
from .url_builder import BossUrlBuilder
from .data_processor import BossDataProcessor


class BossScraper:
    """Boss直聘爬虫核心模块"""
    
    def __init__(self, config: Optional[BossConfig] = None):
        """
        初始化爬虫核心
        
        Args:
            config: 配置管理器实例
        """
        self.config = config or BossConfig()
        self.browser = BossBrowser(self.config)
        self.url_builder = BossUrlBuilder(self.config)
        self.data_processor = BossDataProcessor(self.config)
        
        self.auth: Optional[BossAuth] = None
        self.page = None
        self._initialized = False
    
    def initialize(self, **auth_params) -> bool:
        """
        初始化爬虫（启动浏览器、认证等）
        
        Args:
            **auth_params: 认证参数
                cookies: cookies列表
                cookie_string: cookie字符串
                cookie_file: cookies文件路径
                token: 认证token
        
        Returns:
            bool: 是否成功初始化
        """
        try:
            print("正在初始化Boss爬虫...")
            
            # 启动浏览器
            if not self.browser.setup_browser():
                return False
            
            self.page = self.browser.get_page()
            if not self.page:
                return False
            
            # 初始化认证模块
            self.auth = BossAuth(self.page)
            
            # 执行认证
            if not self.auth.ensure_authenticated(**auth_params):
                return False
            
            # 建立初始访问会话
            self._establish_session()
            
            self._initialized = True
            print("✅ Boss爬虫初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    def _establish_session(self) -> None:
        """建立访问会话"""
        print("正在建立访问会话...")
        
        try:
            # 访问主页
            self.page.get(self.config.web_base_url)
            time.sleep(random.uniform(*self.config.get_delay("initial_access")))
            
            # 访问搜索页面
            search_page = f"{self.config.web_base_url}/web/geek/job"
            self.page.get(search_page)
            time.sleep(random.uniform(*self.config.get_delay("search_access")))
            
            # 模拟用户交互
            try:
                search_input = self.page.ele('input[placeholder*="搜索"]', 
                timeout=self.config.get_timeout("element_wait"))
                if search_input:
                    search_input.click()
                    time.sleep(1)
            except:
                pass
            
            print("✅ 访问会话建立成功")
            
        except Exception as e:
            print(f"建立会话失败: {e}")
    
    def search_jobs(self, search_params: Dict) -> Dict:
        """
        搜索职位（单页）
        
        Args:
            search_params: 搜索参数
        
        Returns:
            Dict: 搜索结果
        """
        if not self._check_initialized():
            return {"success": False, "message": "爬虫未初始化"}
        
        try:
            # 验证搜索参数
            is_valid, error_msg = self.url_builder.validate_search_params(search_params)
            if not is_valid:
                return {"success": False, "message": f"参数验证失败: {error_msg}"}
            
            # 开启数据包监听
            self.page.listen.start("joblist.json")
            
            # 构建并访问搜索URL
            web_url = self.url_builder.build_web_url(search_params)
            print(f"访问搜索页面: {web_url}")
            
            self.page.get(web_url)
            time.sleep(random.uniform(*self.config.get_delay("page_load")))
            
            # 等待并获取数据包
            packets = self.page.listen.wait(timeout=self.config.get_timeout("packet_wait"))
            
            if not packets:
                self.page.listen.stop()
                return {
                    "success": False,
                    "message": "未监听到API响应数据"
                }
            
            # 处理响应数据
            result = self._process_search_response(packets)
            self.page.listen.stop()
            
            return result
            
        except Exception as e:
            try:
                self.page.listen.stop()
            except:
                pass
            
            return {"success": False, "message": f"搜索失败: {str(e)}"}
    
    def search_jobs_with_scrolling(self, search_params: Dict, 
                                 manual_scroll: bool = False, 
                                 max_scroll_times: Optional[int] = None) -> Dict:
        """
        通过滚动页面获取更多职位数据
        
        Args:
            search_params: 搜索参数
            manual_scroll: 是否手动滚动
            max_scroll_times: 最大滚动次数
        
        Returns:
            Dict: 搜索结果
        """
        if not self._check_initialized():
            return {"success": False, "message": "爬虫未初始化"}
        
        if max_scroll_times is None:
            max_scroll_times = self.config.get_limit("max_scroll_times")
        
        try:
            # 验证搜索参数
            is_valid, error_msg = self.url_builder.validate_search_params(search_params)
            if not is_valid:
                return {"success": False, "message": f"参数验证失败: {error_msg}"}
            
            # 开启持续监听
            self.page.listen.start("joblist.json")
            
            # 访问搜索页面
            web_url = self.url_builder.build_web_url(search_params)
            print(f"访问搜索页面: {web_url}")
            self.page.get(web_url)
            time.sleep(random.uniform(*self.config.get_delay("page_load")))
            
            all_jobs = []
            collected_packets = []
            
            # 获取初始数据
            packets = self.page.listen.wait(timeout=self.config.get_timeout("packet_wait"))
            if packets:
                new_count = self.data_processor.process_packets(packets, collected_packets, all_jobs)
                print(f"初始数据: 获得 {new_count} 个职位")
            
            if manual_scroll:
                result = self._handle_manual_scroll(all_jobs, collected_packets)
            else:
                result = self._handle_auto_scroll(all_jobs, collected_packets, max_scroll_times)
            
            # 停止监听
            self.page.listen.stop()
            
            # 保存数据
            if all_jobs:
                self.data_processor.save_jobs_data(all_jobs)
                print(f"✅ 滚动搜索完成！共获得 {len(all_jobs)} 个职位")
            
            return {
                "success": True,
                "jobs": all_jobs,
                "total_jobs": len(all_jobs),
                "packets_processed": len(collected_packets),
            }
            
        except Exception as e:
            try:
                self.page.listen.stop()
            except:
                pass
            
            return {"success": False, "message": f"滚动搜索失败: {str(e)}"}
    
    def batch_search(self, search_params: Dict, max_pages: Optional[int] = None) -> Dict:
        """
        批量搜索多页职位
        
        Args:
            search_params: 搜索参数
            max_pages: 最大页数
        
        Returns:
            Dict: 搜索结果
        """
        if not self._check_initialized():
            return {"success": False, "message": "爬虫未初始化"}
        
        if max_pages is None:
            max_pages = self.config.get_limit("max_pages")
        
        all_jobs = []
        total_count = 0
        
        for page in range(1, max_pages + 1):
            search_params_copy = search_params.copy()
            search_params_copy["page"] = page
            
            result = self.search_jobs(search_params_copy)
            
            if not result["success"]:
                print(f"第{page}页搜索失败: {result['message']}")
                break
            
            data = result["data"]
            job_list = data.get("jobList", [])
            
            if not job_list:
                print(f"第{page}页无更多职位")
                break
            
            page_jobs = self.data_processor.extract_job_list(job_list)
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
            time.sleep(random.uniform(*self.config.get_delay("request")))
        
        # 保存数据
        if all_jobs:
            self.data_processor.save_jobs_data(all_jobs)
        
        return {
            "success": True,
            "jobs": all_jobs,
            "total_jobs": len(all_jobs),
            "total_count": total_count,
            "pages_fetched": min(page, max_pages),
        }
    
    def _handle_manual_scroll(self, all_jobs: List, collected_packets: List) -> None:
        """处理手动滚动模式"""
        print("\n=== 手动滚动模式 ===")
        print("请在浏览器中手动滚动页面加载更多职位")
        print("每次滚动后会自动收集新数据")
        print("完成后输入 'done' 结束收集")
        
        while True:
            user_input = input("滚动后按回车继续，或输入 'done' 结束: ").strip().lower()
            if user_input == "done":
                break
            
            # 检查新的数据包
            packets = self.page.listen.wait(timeout=self.config.get_timeout("packet_wait_after_scroll"))
            if packets:
                old_count = len(all_jobs)
                new_count = self.data_processor.process_packets(packets, collected_packets, all_jobs)
                if new_count > 0:
                    print(f"收集到 {new_count} 个新职位，总计: {len(all_jobs)}")
                else:
                    print("未收集到新职位")
            else:
                print("未监听到新数据包")
    
    def _handle_auto_scroll(self, all_jobs: List, collected_packets: List, max_scroll_times: int) -> None:
        """处理自动滚动模式"""
        print(f"\n=== 自动滚动模式 (最多{max_scroll_times}次) ===")
        
        # 找到职位列表元素
        job_list = self.page.ele(".rec-job-list", 
                                timeout=self.config.get_timeout("element_wait"))
        if not job_list:
            print("未找到职位列表元素 .rec-job-list")
            return
        
        for i in range(max_scroll_times):
            print(f"第 {i+1} 次滚动...")
            
            # 滚动到页面底部
            self.page.scroll.to_bottom()
            time.sleep(random.uniform(*self.config.get_delay("scroll")))
            
            # 检查新的数据包
            packets = self.page.listen.wait(timeout=self.config.get_timeout("packet_wait_scroll"))
            if packets:
                old_count = len(all_jobs)
                new_count = self.data_processor.process_packets(packets, collected_packets, all_jobs)
                if new_count > 0:
                    print(f"收集到 {new_count} 个新职位，总计: {len(all_jobs)}")
                else:
                    print("未收集到新职位，可能已到底部")
                    break
            else:
                print("未监听到新数据包")
    
    def _process_search_response(self, packets) -> Dict:
        """处理搜索响应"""
        latest_packet = packets[-1] if isinstance(packets, list) else packets
        
        try:
            response_data = latest_packet.response.body
            
            # 如果是字节类型，转换为字符串
            if isinstance(response_data, bytes):
                response_data = response_data.decode("utf-8")
            
            # 解析JSON数据
            if isinstance(response_data, str):
                import json
                data = json.loads(response_data)
            else:
                data = response_data
            
            # 保存原始响应
            self.data_processor.save_raw_response(data)
            
            # 检查响应状态
            if data.get("code") == 0:
                return {
                    "success": True,
                    "data": data.get("zpData", {}),
                    "message": "搜索成功",
                }
            elif data.get("code") == 37:
                return {
                    "success": False,
                    "message": "访问被限制，需要等待或更换IP",
                }
            else:
                return {
                    "success": False,
                    "message": data.get("message", "搜索失败"),
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"响应处理失败: {str(e)}",
            }
    
    def _check_initialized(self) -> bool:
        """检查是否已初始化"""
        if not self._initialized:
            print("❌ 爬虫未初始化，请先调用 initialize() 方法")
            return False
        return True
    
    def save_current_cookies(self, file_path: str) -> bool:
        """
        保存当前cookies到文件
        
        Args:
            file_path: 保存路径
            
        Returns:
            bool: 是否保存成功
        """
        if not self.auth:
            print("❌ 认证模块未初始化")
            return False
        
        return self.auth.save_current_cookies(file_path)
    
    def close(self) -> None:
        """关闭爬虫（清理资源）"""
        try:
            if self.browser:
                self.browser.close()
            self._initialized = False
            print("✅ 爬虫已关闭")
        except Exception as e:
            print(f"关闭爬虫时出错: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    def __del__(self):
        """析构函数"""
        self.close()