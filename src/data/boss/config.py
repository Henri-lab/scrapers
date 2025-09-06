import os
import json
from typing import Dict, Optional


class BossConfig:
    """Boss直聘配置管理模块"""
    
    def __init__(self):
        """初始化配置管理器"""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.city_codes = {}
        self.browser_config = self._get_default_browser_config()
        self.scraper_config = self._get_default_scraper_config()
        
        # 加载城市代码
        self.load_city_codes()
    
    def _get_default_browser_config(self) -> Dict:
        """获取默认浏览器配置"""
        return {
            "path": r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "user_agents": [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ],
            "arguments": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-notifications"
            ],
            "anti_detect_script": """
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
        }
    
    def _get_default_scraper_config(self) -> Dict:
        """获取默认爬虫配置"""
        return {
            "base_url": "https://www.zhipin.com/web/geek/jobs",
            "web_base_url": "https://www.zhipin.com",
            "api_base_url": "https://www.zhipin.com/wapi/zpgeek/search/joblist.json",
            "delays": {
                "page_load": (3, 8),
                "scroll": (2, 4),
                "request": (2, 5),
                "initial_access": (2, 4),
                "search_access": (3, 5)
            },
            "timeouts": {
                "element_wait": 3,
                "packet_wait": 10,
                "packet_wait_scroll": 5,
                "packet_wait_after_scroll": 3
            },
            "limits": {
                "max_scroll_times": 10,
                "max_pages": 5,
                "page_size": 15
            }
        }
    
    def load_city_codes(self) -> Dict:
        """
        加载城市代码映射
        
        Returns:
            Dict: 城市代码映射
        """
        try:
            city_file = os.path.join(self.script_dir, "city_code_map.json")
            
            if os.path.exists(city_file):
                with open(city_file, "r", encoding="utf-8") as f:
                    self.city_codes = json.load(f)
                print(f"✅ 加载城市代码: {len(self.city_codes)} 个城市")
            else:
                print("城市代码文件不存在，正在生成...")
                try:
                    import codeCreator
                    self.city_codes = codeCreator.getCityCodes()
                    self.save_city_codes()
                except ImportError:
                    print("❌ 无法导入codeCreator模块")
                    self.city_codes = {}
                
        except Exception as e:
            print(f"❌ 加载城市代码失败: {e}")
            self.city_codes = {}
            
        return self.city_codes
    
    def save_city_codes(self, city_codes: Optional[Dict] = None) -> bool:
        """
        保存城市代码到文件
        
        Args:
            city_codes: 城市代码字典，为空则保存当前加载的
            
        Returns:
            bool: 是否保存成功
        """
        try:
            codes_to_save = city_codes or self.city_codes
            city_file = os.path.join(self.script_dir, "city_code_map.json")
            
            with open(city_file, "w", encoding="utf-8") as f:
                json.dump(codes_to_save, f, ensure_ascii=False, indent=4)
            
            print(f"✅ 城市代码已保存: {city_file}")
            return True
            
        except Exception as e:
            print(f"❌ 保存城市代码失败: {e}")
            return False
    
    def get_city_code(self, city_name: str) -> Optional[str]:
        """
        根据城市名称获取城市代码
        
        Args:
            city_name: 城市名称
            
        Returns:
            str or None: 城市代码
        """
        return self.city_codes.get(city_name)
    
    def get_business_district_code(self, city_name: str, district_name: str) -> Optional[str]:
        """
        获取商圈代码
        
        Args:
            city_name: 城市名称
            district_name: 商圈名称
            
        Returns:
            str or None: 商圈代码
        """
        try:
            import codeCreator
            business_codes = codeCreator.getBusinessDistrictCodes(city_name)
            return business_codes.get(district_name)
        except Exception as e:
            print(f"获取商圈代码失败: {e}")
            return None
    
    def update_browser_config(self, **kwargs) -> None:
        """
        更新浏览器配置
        
        Args:
            **kwargs: 配置参数
        """
        self.browser_config.update(kwargs)
    
    def update_scraper_config(self, **kwargs) -> None:
        """
        更新爬虫配置
        
        Args:
            **kwargs: 配置参数
        """
        # 支持嵌套更新
        for key, value in kwargs.items():
            if key in self.scraper_config and isinstance(self.scraper_config[key], dict) and isinstance(value, dict):
                self.scraper_config[key].update(value)
            else:
                self.scraper_config[key] = value
    
    def get_result_dir(self) -> str:
        """
        获取结果保存目录
        
        Returns:
            str: 结果目录路径
        """
        result_dir = os.path.join(self.script_dir, "result")
        os.makedirs(result_dir, exist_ok=True)
        return result_dir
    
    def load_config_from_file(self, config_file: str) -> bool:
        """
        从文件加载配置
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            bool: 是否加载成功
        """
        try:
            if not os.path.exists(config_file):
                print(f"配置文件不存在: {config_file}")
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新配置
            if 'browser' in config:
                self.update_browser_config(**config['browser'])
            
            if 'scraper' in config:
                self.update_scraper_config(**config['scraper'])
            
            if 'city_codes' in config:
                self.city_codes.update(config['city_codes'])
            
            print(f"✅ 配置已从文件加载: {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return False
    
    def save_config_to_file(self, config_file: str) -> bool:
        """
        保存当前配置到文件
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            config = {
                "browser": self.browser_config,
                "scraper": self.scraper_config,
                "city_codes": self.city_codes
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            print(f"✅ 配置已保存到文件: {config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            return False
    
    @property
    def chrome_path(self) -> str:
        """获取Chrome浏览器路径"""
        return self.browser_config["path"]
    
    @property
    def user_agents(self) -> list:
        """获取用户代理列表"""
        return self.browser_config["user_agents"]
    
    @property
    def browser_arguments(self) -> list:
        """获取浏览器启动参数"""
        return self.browser_config["arguments"]
    
    @property
    def anti_detect_script(self) -> str:
        """获取反检测脚本"""
        return self.browser_config["anti_detect_script"]
    
    @property
    def base_url(self) -> str:
        """获取基础URL"""
        return self.scraper_config["base_url"]
    
    @property
    def web_base_url(self) -> str:
        """获取网页基础URL"""
        return self.scraper_config["web_base_url"]
    
    @property
    def api_base_url(self) -> str:
        """获取API基础URL"""
        return self.scraper_config["api_base_url"]
    
    def get_delay(self, delay_type: str) -> tuple:
        """
        获取延时配置
        
        Args:
            delay_type: 延时类型
            
        Returns:
            tuple: (最小延时, 最大延时)
        """
        return self.scraper_config["delays"].get(delay_type, (1, 3))
    
    def get_timeout(self, timeout_type: str) -> int:
        """
        获取超时配置
        
        Args:
            timeout_type: 超时类型
            
        Returns:
            int: 超时时间（秒）
        """
        return self.scraper_config["timeouts"].get(timeout_type, 10)
    
    def get_limit(self, limit_type: str) -> int:
        """
        获取限制配置
        
        Args:
            limit_type: 限制类型
            
        Returns:
            int: 限制值
        """
        return self.scraper_config["limits"].get(limit_type, 10)