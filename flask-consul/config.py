import os

consul_token = os.environ.get('consul_token','bf04d1e8-8b2e-6d52-edac-59cb02fbb072')
consul_url = os.environ.get('consul_url','http://127.0.0.1:8500/v1')
admin_passwd = os.environ.get('admin_passwd','123456')
log_level = os.environ.get('log_level','DEBUG')

vendors = {'alicloud': '阿里云','tencent_cloud': '腾讯云','huaweicloud': '华为云'}
regions = {
    "huaweicloud": {
        "none": "无",
        "cn-east-3": "华东-上海一",
        "cn-east-2": "华东-上海二",
        "cn-south-1": "华南-广州",
        "cn-north-1": "华北-北京一",
        "cn-north-4": "华北-北京四",
        "cn-southwest-2": "西南-贵阳一",
        "ap-southeast-1": "中国-香港",
        "ap-southeast-3": "新加坡",
    },
    "alicloud": {
        "none": "无",
        "cn-qingdao": "华北1(青岛)",
        "cn-beijing": "华北2(北京)",
        "cn-zhangjiakou": "华北3(张家口)",
        "cn-huhehaote": "华北5(呼和浩特)",
        "cn-wulanchabu": "华北6(乌兰察布)",
        "cn-hangzhou": "华东1(杭州)",
        "cn-shanghai": "华东2(上海)",
        "cn-shenzhen": "华南1(深圳)",
        "cn-heyuan": "华南2(河源)",
        "cn-guangzhou": "华南3(广州)",
        "cn-chengdu": "西南1(成都)",
        "cn-hongkong": "中国(香港)",
        "cn-nanjing": "华东5(南京-本地地域)",
        "us-east-1": "美国东部1(弗吉尼亚)",
        "us-west-1": "美国(硅谷)",
        "eu-west-1": "英国(伦敦)",
        "ap-southeast-1": "新加坡",
        "ap-northeast-1": "日本(东京)",
        "ap-south-1": "印度(孟买)",
    },
    "tencent_cloud": {
        "none": "无",
        "ap-nanjing": "华东地区(南京)",
        "ap-shanghai": "华东地区(上海)",
        "ap-guangzhou": "华南地区(广州)",
        "ap-beijing": "华北地区(北京)",
        "ap-tianjin": "华北地区(天津)",
        "ap-chengdu": "西南地区(成都)",
        "ap-chongqing": "西南地区(重庆)",
        "ap-hongkong": "港澳台地区(中国香港)",
        "ap-tokyo": "亚太地区(东京)",
    },
}
