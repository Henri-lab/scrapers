import os
import requests
import json


def fetch_json_data(url):
    """通用API请求函数"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        exit()


def traverse_hierarchical_data(data_list, result_dict, deep=0):
    deep -= 1
    """递归遍历层级数据的通用函数"""
    if not isinstance(data_list, list):
        return

    for item in data_list:
        if not isinstance(item, dict):
            continue

        if "name" in item and "code" in item:
            result_dict[item["name"]] = item["code"]

        if (
            deep > 0
            and "subLevelModelList" in item
            and isinstance(item["subLevelModelList"], list)
            and item["subLevelModelList"]
        ):
            traverse_hierarchical_data(item["subLevelModelList"], result_dict, deep)


def save_to_json_file(data, filename):
    """保存数据到JSON文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def getCityCodes():
    url = "https://www.zhipin.com/wapi/zpCommon/data/city.json"

    citycode = fetch_json_data(url)
    citys = citycode["zpData"]["cityList"]
    result = {}

    traverse_hierarchical_data(citys, result, 2)
    save_to_json_file(result, "city_code_map.json")
    return result


def getBusinessDistrictCodes(cityName):
    citys = getCityCodes()
    cityCode = citys.get(cityName)
    if cityCode is None:
        print(f"未找到城市: {cityName}")
        return
    url = (
        f"https://www.zhipin.com/wapi/zpgeek/businessDistrict.json?cityCode={cityCode}"
    )

    citycode = fetch_json_data(url)
    citys = [citycode["zpData"]["businessDistrict"]]
    result = {}

    traverse_hierarchical_data(citys, result, 5)
    save_to_json_file(result, "business_code_map.json")
    return result


getBusinessDistrictCodes("上海")
