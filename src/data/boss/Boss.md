boss直聘搜索示例

点击职位卡片； 
并输入城市：上海市， 区域：黄浦区， 职业：律师；学历要求：硕士
https://www.zhipin.com/web/geek/jobs?city=101020100&multiBusinessDistrict=310101&degree=204&query=律师

根据实际测试,携带比较全面的查询字段的url：
https://www.zhipin.com/wapi/zpgeek/search/joblist.json?page=1&pageSize=15&city=101030100&multiBusinessDistrict=&experience=106&degree=204&expectInfo=&query=%E5%BE%8B%E5%B8%88&multiSubway=&position=&jobType=&salary=&industry=&scale=&stage=&scene=1


获取query字段的url ：https://www.zhipin.com/wapi/zpgeek/pc/all/filter/conditions.json
其结果应该是比较稳定的，可以进行缓存
查询结果 可以使用queryCreater.py

citycode字段查询的url: https://www.zhipin.com/wapi/zpCommon/data/city.json
映射表 查询结果在 src/data/boss/city_code_map.json


获取BusinessDistrict字段的url：https://www.zhipin.com/wapi/zpgeek/businessDistrict.json?cityCode=101020100
映射表 查询结果在src/data/boss/business_code_map.json


重点!
要求：
1. 此项目为node后台提供爬虫服务 
2. api接受node后台发来的用户查询的详细条件
3. python服务端应该通过读取映射表拿到城市和区域编码 并使用queryCreater.py生产正确的可访问url 
4. 具体爬虫功能参考boss_sms_scraper.py 等文件
