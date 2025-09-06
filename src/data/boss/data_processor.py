import json
import time
import os
from typing import Dict, List, Optional, Any
from .config import BossConfig


class BossDataProcessor:
    """Boss直聘数据处理模块"""
    
    def __init__(self, config: Optional[BossConfig] = None):
        """
        初始化数据处理器
        
        Args:
            config: 配置管理器实例
        """
        self.config = config or BossConfig()
    
    def process_packets(self, packets, collected_packets: List, all_jobs: List) -> int:
        """
        处理监听到的数据包
        
        Args:
            packets: 数据包或数据包列表
            collected_packets: 已处理数据包列表
            all_jobs: 所有职位列表
            
        Returns:
            int: 新增职位数量
        """
        if not packets:
            return 0
        
        packet_list = packets if isinstance(packets, list) else [packets]
        new_jobs_count = 0
        
        for packet in packet_list:
            if packet in collected_packets:
                continue
            
            try:
                response_data = packet.response.body
                data = response_data
                
                if data.get("code") == 0:
                    zp_data = data.get("zpData", {})
                    job_list = zp_data.get("jobList", [])
                    
                    # 提取并去重职位数据
                    existing_ids = {job.get("job_id") for job in all_jobs}
                    new_jobs = []
                    
                    for job in job_list:
                        job_id = job.get("encryptJobId", "")
                        if job_id and job_id not in existing_ids:
                            job_info = self.extract_single_job(job)
                            new_jobs.append(job_info)
                            existing_ids.add(job_id)
                    
                    all_jobs.extend(new_jobs)
                    new_jobs_count += len(new_jobs)
                    collected_packets.append(packet)
                    
            except Exception as e:
                print(f"处理数据包失败: {e}")
                continue
        
        return new_jobs_count
    
    def extract_single_job(self, job: Dict) -> Dict:
        """
        提取单个职位信息
        
        Args:
            job: 原始职位数据
            
        Returns:
            Dict: 标准化的职位信息
        """
        return {
            # 基础信息
            "job_name": job.get("jobName", ""),
            "salary_desc": job.get("salaryDesc", ""),
            "job_degree": job.get("jobDegree", ""),
            "job_experience": job.get("jobExperience", ""),
            
            # 地理信息
            "city_name": job.get("cityName", ""),
            "area_district": job.get("areaDistrict", ""),
            "business_district": job.get("businessDistrict", ""),
            
            # 职位详情
            "job_type": job.get("jobType", ""),
            "job_labels": job.get("jobLabels", []),
            "skills": job.get("skills", []),
            "welfare_list": job.get("welfareList", []),
            
            # ID信息
            "job_id": job.get("encryptJobId", ""),
            "lid": job.get("lid", ""),
            "security_id": job.get("securityId", ""),
            "expect_id": job.get("expectId", ""),
            
            # 公司信息
            "brand_name": job.get("brandName", ""),
            "brand_logo": job.get("brandLogo", ""),
            "brand_stage_name": job.get("brandStageName", ""),
            "brand_industry": job.get("brandIndustry", ""),
            "brand_scale_name": job.get("brandScaleName", ""),
            "company_id": job.get("encryptBrandId", ""),
            
            # HR信息
            "boss_name": job.get("bossName", ""),
            "boss_title": job.get("bossTitle", ""),
            "boss_avatar": job.get("bossAvatar", ""),
            "boss_id": job.get("encryptBossId", ""),
            
            # 状态信息
            "job_valid_status": job.get("jobValidStatus", ""),
            "job_status_desc": job.get("jobStatusDesc", ""),
            "contact_chat_im": job.get("contactChatIm", ""),
            "last_modify_time": job.get("lastModifyTime", ""),
            "prolong": job.get("prolong", ""),
            "icon_word": job.get("iconWord", ""),
        }
    
    def extract_job_list(self, job_list: List[Dict]) -> List[Dict]:
        """
        批量提取职位数据
        
        Args:
            job_list: 原始职位列表
            
        Returns:
            List[Dict]: 标准化的职位数据列表
        """
        jobs = []
        
        for job in job_list:
            try:
                job_info = self.extract_single_job(job)
                jobs.append(job_info)
            except Exception as e:
                print(f"提取职位信息失败: {e}")
                continue
        
        return jobs
    
    def validate_job_data(self, job: Dict) -> tuple[bool, str]:
        """
        验证职位数据完整性
        
        Args:
            job: 职位数据
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 必要字段检查
        required_fields = ["job_name", "job_id", "brand_name"]
        
        for field in required_fields:
            if not job.get(field):
                return False, f"缺少必要字段: {field}"
        
        # 数据类型检查
        if not isinstance(job.get("job_labels", []), list):
            return False, "job_labels 必须是列表类型"
        
        if not isinstance(job.get("skills", []), list):
            return False, "skills 必须是列表类型"
        
        if not isinstance(job.get("welfare_list", []), list):
            return False, "welfare_list 必须是列表类型"
        
        return True, ""
    
    def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        根据job_id去重职位数据
        
        Args:
            jobs: 职位列表
            
        Returns:
            List[Dict]: 去重后的职位列表
        """
        seen_ids = set()
        unique_jobs = []
        
        for job in jobs:
            job_id = job.get("job_id")
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def filter_jobs(self, jobs: List[Dict], filters: Dict) -> List[Dict]:
        """
        根据条件过滤职位
        
        Args:
            jobs: 职位列表
            filters: 过滤条件
            
        Returns:
            List[Dict]: 过滤后的职位列表
        """
        filtered_jobs = []
        
        for job in jobs:
            if self._job_matches_filters(job, filters):
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _job_matches_filters(self, job: Dict, filters: Dict) -> bool:
        """
        检查职位是否匹配过滤条件
        
        Args:
            job: 职位数据
            filters: 过滤条件
            
        Returns:
            bool: 是否匹配
        """
        # 关键词过滤
        if "keywords" in filters:
            keywords = filters["keywords"]
            if isinstance(keywords, str):
                keywords = [keywords]
            
            job_text = f"{job.get('job_name', '')} {' '.join(job.get('job_labels', []))}"
            if not any(keyword.lower() in job_text.lower() for keyword in keywords):
                return False
        
        # 城市过滤
        if "cities" in filters:
            cities = filters["cities"]
            if isinstance(cities, str):
                cities = [cities]
            
            if job.get("city_name") not in cities:
                return False
        
        # 公司规模过滤
        if "scales" in filters:
            scales = filters["scales"]
            if isinstance(scales, str):
                scales = [scales]
            
            if job.get("brand_scale_name") not in scales:
                return False
        
        return True
    
    def save_jobs_data(self, jobs: List[Dict], filename: Optional[str] = None, 
                      include_summary: bool = True) -> str:
        """
        保存职位数据到文件
        
        Args:
            jobs: 职位数据列表
            filename: 文件名，为空则自动生成
            include_summary: 是否包含汇总信息
            
        Returns:
            str: 保存的文件路径
        """
        result_dir = self.config.get_result_dir()
        
        if not filename:
            timestamp = int(time.time())
            filename = f"jobs_data_{timestamp}.json"
        
        file_path = os.path.join(result_dir, filename)
        
        # 准备保存的数据
        save_data = {
            "total_jobs": len(jobs),
            "timestamp": int(time.time()),
            "jobs": jobs
        }
        
        # 添加汇总信息
        if include_summary:
            save_data["summary"] = self.generate_jobs_summary(jobs)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            
            print(f"✅ 职位数据已保存: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ 保存职位数据失败: {e}")
            raise
    
    def save_raw_response(self, response_data: Any, filename: str = "last_search_response.json") -> str:
        """
        保存原始响应数据
        
        Args:
            response_data: 响应数据
            filename: 文件名
            
        Returns:
            str: 保存的文件路径
        """
        result_dir = self.config.get_result_dir()
        file_path = os.path.join(result_dir, filename)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(response_data, f, ensure_ascii=False, indent=4)
            
            return file_path
            
        except Exception as e:
            print(f"❌ 保存响应数据失败: {e}")
            raise
    
    def generate_jobs_summary(self, jobs: List[Dict]) -> Dict:
        """
        生成职位数据汇总信息
        
        Args:
            jobs: 职位数据列表
            
        Returns:
            Dict: 汇总信息
        """
        if not jobs:
            return {}
        
        # 统计城市分布
        city_stats = {}
        for job in jobs:
            city = job.get("city_name", "未知")
            city_stats[city] = city_stats.get(city, 0) + 1
        
        # 统计公司规模分布
        scale_stats = {}
        for job in jobs:
            scale = job.get("brand_scale_name", "未知")
            scale_stats[scale] = scale_stats.get(scale, 0) + 1
        
        # 统计学历要求分布
        degree_stats = {}
        for job in jobs:
            degree = job.get("job_degree", "未知")
            degree_stats[degree] = degree_stats.get(degree, 0) + 1
        
        # 统计经验要求分布
        experience_stats = {}
        for job in jobs:
            experience = job.get("job_experience", "未知")
            experience_stats[experience] = experience_stats.get(experience, 0) + 1
        
        return {
            "city_distribution": dict(sorted(city_stats.items(), key=lambda x: x[1], reverse=True)),
            "scale_distribution": dict(sorted(scale_stats.items(), key=lambda x: x[1], reverse=True)),
            "degree_distribution": dict(sorted(degree_stats.items(), key=lambda x: x[1], reverse=True)),
            "experience_distribution": dict(sorted(experience_stats.items(), key=lambda x: x[1], reverse=True)),
        }
    
    def load_jobs_data(self, file_path: str) -> List[Dict]:
        """
        从文件加载职位数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Dict]: 职位数据列表
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, dict) and "jobs" in data:
                return data["jobs"]
            elif isinstance(data, list):
                return data
            else:
                print("❌ 无效的职位数据格式")
                return []
                
        except Exception as e:
            print(f"❌ 加载职位数据失败: {e}")
            return []