import os
import json


class QueryCreater:
    def __init__(self):
        """初始化查询创建器，加载条件映射数据"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        conditions_file = os.path.join(script_dir, "conditions.json")
        
        with open(conditions_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.conditions = data["zpData"]
        
        # 创建名称到代码的映射字典
        self.mapping = {}
        for list_name, items in self.conditions.items():
            category = list_name.replace("List", "")  # 去掉List后缀作为分类名
            self.mapping[category] = {}
            for item in items:
                self.mapping[category][item["name"]] = item["code"]
    
    def get_code(self, category, name):
        """
        根据分类和名称获取对应的代码
        
        Args:
            category (str): 分类名称 (payType, experience, salary, stage, scale, partTime, degree, jobType)
            name (str): 选项名称
            
        Returns:
            int: 对应的代码，如果未找到返回None
        """
        return self.mapping.get(category, {}).get(name)
    
    def get_pay_type_code(self, name):
        """获取薪资结算方式代码"""
        return self.get_code("payType", name)
    
    def get_experience_code(self, name):
        """获取工作经验代码"""
        return self.get_code("experience", name)
    
    def get_salary_code(self, name):
        """获取薪资范围代码"""
        return self.get_code("salary", name)
    
    def get_stage_code(self, name):
        """获取融资阶段代码"""
        return self.get_code("stage", name)
    
    def get_scale_code(self, name):
        """获取公司规模代码"""
        return self.get_code("scale", name)
    
    def get_part_time_code(self, name):
        """获取兼职类型代码"""
        return self.get_code("partTime", name)
    
    def get_degree_code(self, name):
        """获取学历要求代码"""
        return self.get_code("degree", name)
    
    def get_job_type_code(self, name):
        """获取工作类型代码"""
        return self.get_code("jobType", name)
    
    def get_all_options(self, category):
        """
        获取某个分类的所有选项
        
        Args:
            category (str): 分类名称
            
        Returns:
            dict: 名称到代码的映射字典
        """
        return self.mapping.get(category, {})
    
    def list_categories(self):
        """列出所有可用的分类"""
        return list(self.mapping.keys())


# 使用示例
if __name__ == "__main__":
    creator = QueryCreater()
    
    # 测试各种查询
    print("薪资结算方式 - 月结:", creator.get_pay_type_code("月结"))
    print("工作经验 - 1-3年:", creator.get_experience_code("1-3年"))
    print("薪资范围 - 10-20K:", creator.get_salary_code("10-20K"))
    print("融资阶段 - A轮:", creator.get_stage_code("A轮"))
    print("公司规模 - 100-499人:", creator.get_scale_code("100-499人"))
    print("兼职类型 - 周末/节假日:", creator.get_part_time_code("周末/节假日"))
    print("学历要求 - 本科:", creator.get_degree_code("本科"))
    print("工作类型 - 全职:", creator.get_job_type_code("全职"))
    
    print("\n所有分类:", creator.list_categories())
    print("\n薪资范围所有选项:", creator.get_all_options("salary"))