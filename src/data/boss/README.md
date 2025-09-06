# Boss直聘爬虫 - 重构版本

原来的 `boss_scraper.py` 文件太长了（759行），现已重构为模块化架构，功能更加清晰分离。

## 📁 文件结构

```
src/data/boss/
├── __init__.py          # 模块入口
├── boss_scraper.py      # 主入口类（兼容旧接口）
├── config.py            # 配置管理
├── auth.py              # 认证管理（支持cookies/token）
├── browser.py           # 浏览器管理
├── url_builder.py       # URL构建器
├── data_processor.py    # 数据处理器
├── scraper.py           # 爬虫核心
├── examples.py          # 使用示例
└── README.md           # 说明文档
```

## 🚀 主要改进

### 1. 模块化架构
- **BossConfig**: 配置管理，支持自定义延时、超时、限制等参数
- **BossAuth**: 认证管理，支持多种认证方式
- **BossBrowser**: 浏览器管理，封装DrissionPage操作
- **BossUrlBuilder**: URL构建器，处理搜索参数和URL生成
- **BossDataProcessor**: 数据处理器，负责数据提取、验证、保存
- **BossScraper**: 爬虫核心，协调各模块完成爬取
- **BossJobScraper**: 主入口类，保持向后兼容

### 2. 认证方式支持
- ✅ 手动登录（原有方式）
- ✅ Cookie字符串
- ✅ Cookies列表
- ✅ Cookie文件加载
- ✅ Authorization Token
- ✅ 自动保存当前cookies

### 3. 功能增强
- 更好的错误处理和日志
- 配置文件支持
- 数据验证和去重
- 统计信息生成
- 上下文管理器支持

## 📖 使用方法

### 快速开始

```python
from src.data.boss import BossJobScraper

# 创建爬虫实例
scraper = BossJobScraper()

# 初始化（会提示手动登录）
scraper.initialize()

# 搜索参数
search_params = {
    "query": "Python开发",
    "city": "上海", 
    "experience": "1-3年",
    "degree": "本科",
    "salary": "10-20K"
}

# 搜索职位
result = scraper.search_jobs(search_params)
print(f"获得 {len(result['data']['jobList'])} 个职位")

# 关闭爬虫
scraper.close()
```

### 使用Cookie认证

#### 方式1：Cookie字符串
```python
cookie_string = "wt2=xxx; __zp_stoken__=yyy; _uab_collina=zzz"

scraper = BossJobScraper()
scraper.initialize(cookie_string=cookie_string)
```

#### 方式2：Cookies列表
```python
cookies = [
    {"name": "wt2", "value": "xxx", "domain": ".zhipin.com"},
    {"name": "__zp_stoken__", "value": "yyy", "domain": ".zhipin.com"}
]

scraper = BossJobScraper()
scraper.initialize(cookies=cookies)
```

#### 方式3：Cookie文件
```python
# cookies.json 格式：
[
    {"name": "wt2", "value": "xxx", "domain": ".zhipin.com"},
    {"name": "__zp_stoken__", "value": "yyy", "domain": ".zhipin.com"}
]

scraper = BossJobScraper()
scraper.initialize(cookie_file="cookies.json")
```

### 批量搜索多页
```python
result = scraper.batch_search(search_params, max_pages=5)
print(f"批量搜索获得 {result['total_jobs']} 个职位")
```

### 滚动搜索更多数据
```python
# 自动滚动
result = scraper.search_jobs_with_scrolling(
    search_params, 
    manual_scroll=False,
    max_scroll_times=10
)

# 手动滚动（需要用户手动操作）
result = scraper.search_jobs_with_scrolling(
    search_params, 
    manual_scroll=True
)
```

### 保存当前Cookies
```python
# 登录后保存cookies供下次使用
scraper.save_current_cookies("my_cookies.json")
```

## 🔧 配置自定义

```python
from src.data.boss import BossConfig, BossJobScraper

# 创建自定义配置
config = BossConfig()

# 修改延时设置
config.update_scraper_config(
    delays={
        "page_load": (5, 10),    # 页面加载等待时间
        "scroll": (3, 6),        # 滚动间隔
        "request": (3, 8)        # 请求间隔
    }
)

# 修改限制设置
config.update_scraper_config(
    limits={
        "max_scroll_times": 20,  # 最大滚动次数
        "max_pages": 10         # 最大页数
    }
)

# 使用自定义配置
scraper = BossJobScraper(config)
```

## 📝 API接口（兼容原版）

```python
from src.data.boss import search_boss_jobs

# 原API接口仍然可用，现在支持认证参数
result = search_boss_jobs(
    params={
        "query": "Python开发",
        "city": "上海",
        "max_pages": 3
    },
    # 认证参数（新增）
    cookie_string="your_cookie_string"
)
```

## 🧪 测试

```python
from src.data.boss import test_scraper

# 手动登录测试
test_scraper()

# Cookie字符串测试
test_scraper(cookie_string="your_cookie_string")

# Cookie文件测试
test_scraper(cookie_file="cookies.json")
```

## 📊 数据输出

搜索结果会自动保存到 `result/` 目录：
- `last_search_response.json`: 最新搜索的原始响应
- `jobs_data_timestamp.json`: 格式化的职位数据（包含汇总信息）

## ⚠️ 注意事项

1. **Cookie获取**: 可以通过浏览器开发工具获取，或使用 `save_current_cookies()` 方法
2. **反爬机制**: 内置了反检测措施，建议合理控制请求频率
3. **数据完整性**: 自动去重和数据验证，确保数据质量
4. **资源清理**: 使用 `close()` 方法或上下文管理器确保浏览器正确关闭

## 🔄 从旧版本迁移

旧的 `BossJobScraper` 类接口保持兼容，现有代码基本不需要修改：

```python
# 旧代码仍然可用
scraper = BossJobScraper()
result = scraper.search_jobs(search_params)

# 新增功能
scraper.initialize(cookie_string="your_cookies")  # 支持cookie认证
scraper.save_current_cookies("cookies.json")      # 保存cookies
```

## 📚 更多示例

查看 `examples.py` 文件获取更多详细的使用示例。