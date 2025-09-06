from urllib.parse import quote
from typing import Dict, Optional
from .config import BossConfig


class BossUrlBuilder:
    """Boss直聘URL构建器"""
    
    def __init__(self, config: Optional[BossConfig] = None):
        """
        初始化URL构建器
        
        Args:
            config: 配置管理器实例
        """
        self.config = config or BossConfig()
        
        # 尝试导入查询创建器
        try:
            from queryCreator import QueryCreater
            self.query_creator = QueryCreater()
        except ImportError:
            print("❌ 无法导入QueryCreater，条件查询功能将受限")
            self.query_creator = None
    
    def build_web_url(self, search_params: Dict) -> str:
        """
        构建网页搜索URL
        
        Args:
            search_params: 搜索参数字典
            
        Returns:
            str: 构建的网页URL
        """
        base_url = self.config.base_url
        params = {}
        
        # 处理搜索参数
        self._add_basic_params(params, search_params)
        self._add_location_params(params, search_params)
        self._add_condition_params(params, search_params)
        
        return self._build_url(base_url, params)
    
    def build_api_url(self, search_params: Dict) -> str:
        """
        构建API请求URL
        
        Args:
            search_params: 搜索参数字典
            
        Returns:
            str: 构建的API URL
        """
        base_url = self.config.api_base_url
        params = {
            "scene": 1,
            "page": search_params.get("page", 1),
            "pageSize": search_params.get("page_size", self.config.get_limit("page_size"))
        }
        
        # 处理搜索参数
        self._add_basic_params(params, search_params)
        self._add_location_params(params, search_params)
        self._add_condition_params(params, search_params)
        
        return self._build_url(base_url, params)
    
    def _add_basic_params(self, params: Dict, search_params: Dict) -> None:
        """
        添加基础搜索参数
        
        Args:
            params: URL参数字典
            search_params: 搜索参数字典
        """
        # 搜索关键词
        if search_params.get("query"):
            params["query"] = search_params["query"]
    
    def _add_location_params(self, params: Dict, search_params: Dict) -> None:
        """
        添加地理位置参数
        
        Args:
            params: URL参数字典
            search_params: 搜索参数字典
        """
        # 城市代码
        city_name = search_params.get("city")
        if city_name:
            city_code = self.config.get_city_code(city_name)
            if city_code:
                params["city"] = city_code
            else:
                print(f"警告: 未找到城市 '{city_name}' 的代码")
        
        # 商圈代码
        district_name = search_params.get("district")
        if district_name and city_name:
            district_code = self.config.get_business_district_code(city_name, district_name)
            if district_code:
                params["multiBusinessDistrict"] = district_code
    
    def _add_condition_params(self, params: Dict, search_params: Dict) -> None:
        """
        添加条件查询参数
        
        Args:
            params: URL参数字典
            search_params: 搜索参数字典
        """
        if not self.query_creator:
            return
        
        # 条件映射关系
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
                try:
                    code = self.query_creator.get_code(query_key, value)
                    if code:
                        params[param_key] = code
                except Exception as e:
                    print(f"获取{param_key}代码失败: {e}")
    
    def _build_url(self, base_url: str, params: Dict) -> str:
        """
        构建完整URL
        
        Args:
            base_url: 基础URL
            params: 参数字典
            
        Returns:
            str: 完整URL
        """
        if not params:
            return base_url
        
        # 过滤空值并编码参数
        param_str = "&".join([
            f"{k}={quote(str(v))}" for k, v in params.items() 
            if v is not None and str(v).strip()
        ])
        
        return f"{base_url}?{param_str}" if param_str else base_url
    
    def parse_search_params(self, **kwargs) -> Dict:
        """
        解析和标准化搜索参数
        
        Args:
            **kwargs: 搜索参数
            
        Returns:
            Dict: 标准化的搜索参数
        """
        # 基础参数
        params = {
            "query": kwargs.get("query", ""),
            "city": kwargs.get("city", ""),
            "district": kwargs.get("district", ""),
            "experience": kwargs.get("experience", ""),
            "degree": kwargs.get("degree", ""),
            "salary": kwargs.get("salary", ""),
            "scale": kwargs.get("scale", ""),
            "stage": kwargs.get("stage", ""),
            "job_type": kwargs.get("job_type", ""),
            "page": kwargs.get("page", 1),
            "page_size": kwargs.get("page_size", self.config.get_limit("page_size"))
        }
        
        # 移除空值
        return {k: v for k, v in params.items() if v}
    
    def get_search_url(self, url_type: str = "web", **kwargs) -> str:
        """
        获取搜索URL（便捷方法）
        
        Args:
            url_type: URL类型，"web" 或 "api"
            **kwargs: 搜索参数
            
        Returns:
            str: 搜索URL
        """
        search_params = self.parse_search_params(**kwargs)
        
        if url_type == "api":
            return self.build_api_url(search_params)
        else:
            return self.build_web_url(search_params)
    
    def validate_search_params(self, search_params: Dict) -> tuple[bool, str]:
        """
        验证搜索参数
        
        Args:
            search_params: 搜索参数字典
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 检查必要参数
        if not search_params.get("query") and not search_params.get("city"):
            return False, "至少需要提供搜索关键词或城市"
        
        # 检查城市是否有效
        city_name = search_params.get("city")
        if city_name:
            city_code = self.config.get_city_code(city_name)
            if not city_code:
                return False, f"无效的城市名称: {city_name}"
        
        # 检查页面参数
        page = search_params.get("page", 1)
        if not isinstance(page, int) or page < 1:
            return False, "页码必须是大于0的整数"
        
        page_size = search_params.get("page_size", 15)
        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            return False, "页面大小必须是1-100之间的整数"
        
        return True, ""