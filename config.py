#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : Eeyhan
# @File    : config.py

import os
import sys
import logging
import redis


# 项目根目录
BASE_DIR = os.path.dirname(__file__)

"""
自添加USER_AGENT请按照已有数据的格式来添加
"""

USER_AGENT = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)',
    'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Tri dent/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)',
    'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64;Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)',
]

"""
代理网站：自添加PROXY_URLS请按照已有数据的格式来添加
"""

PROXY_URLS = [
    {'url': 'https://www.xicidaili.com/nn', 'type': 'xici'},
    {'url': 'https://www.xicidaili.com/nt', 'type': 'xici'},
    {'url': 'https://www.xicidaili.com/wn', 'type': 'xici'},
    {'url': 'https://www.xicidaili.com/wt', 'type': 'xici'},
    {'url': 'http://www.xiladaili.com/gaoni/', 'type': 'xila'},
    {'url': 'http://www.xiladaili.com/http/', 'type': 'xila'},
    {'url': 'http://www.xiladaili.com/https/', 'type': 'xila'},
    {'url': 'http://www.xiladaili.com/putong/', 'type': 'xila'},
    {'url': 'https://www.kuaidaili.com/free/intr/', 'type': 'kuaidaili'},
    {'url': 'https://www.kuaidaili.com/free/inha/', 'type': 'kuaidaili'},
    {'url': 'https://www.kuaidaili.com/ops/', 'type': 'kuaidaili_new'},
    {'url': 'http://www.89ip.cn/', 'type': '89ip'},
    {'url': 'http://www.qydaili.com/free/', 'type': 'qydaili'},
    {'url': 'https://ip.ihuan.me/', 'type': 'ihuan'},
    {'url': 'http://www.ip3366.net/', 'type': '3366'},
    {'url': 'http://www.iphai.com/free/ng', 'type': 'iphai'},
    {'url': 'http://www.iphai.com/free/wg', 'type': 'iphai'},
    {'url': 'http://www.iphai.com/free/wp', 'type': 'iphai'},
    {'url': 'http://www.goubanjia.com/', 'type': 'goubanjia'},
    {'url': 'http://www.feiyiproxy.com/?page_id=1457', 'type': 'feiyi'},
    {'url': 'http://www.shenjidaili.com/open/', 'type': 'shenji'},
    {'url': 'http://ip.kxdaili.com/dailiip.html', 'type': 'kaixin'},
    {'url': 'http://www.superfastip.com/welcome/freeIP', 'type': 'jisu'},
    {'url': 'http://ip.jiangxianli.com/', 'type': 'jxl'},
    {'url': 'https://lab.crossincode.com/proxy/', 'type': 'cross'},
    {'url': 'http://www.nimadaili.com/gaoni/', 'type': 'nima'},
    {'url': 'http://www.nimadaili.com/http/', 'type': 'nima'},
    {'url': 'http://www.nimadaili.com/https/', 'type': 'nima'},
    {'url': 'http://www.data5u.com/', 'type': 'da5u'},
    {'url': 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list', 'type': 'github'},
    {'url': 'https://proxy.mimvp.com/freeopen.php', 'type': 'mipu'},  # 需要图片识别端口，已解决
    {'url': 'http://www.xsdaili.com/', 'type': 'xsdaili'},  # 需要爬取二级网页，已解决
    {'url': 'http://www.66ip.cn/mo.php?tqsl=1024', 'type': '66ip'},  # 需要js解密，已解决

]

"""
测试代理网站：自添加测试代理的url请按照已有数据的格式来添加
"""

TEST_PROXY_URLS = [

    # 下面的是主流搜索引擎搜ip的网址，相对比较开放，而且查询结果比较准确
    {'url': 'https://www.baidu.com/s?wd=ip', 'type': 'baidu'},
    {'url': 'https://www.sogou.com/web?query=ip', 'type': 'sogou'},
    {'url': 'https://www.so.com/s?q=ip&src=srp&fr=none&psid=2d511001ad6e91af893e0d7e561f1bba', 'type': 'so'},
    {'url': 'https://mijisou.com/?q=ip&category_general=on&time_range=&language=zh-CN&pageno=1', 'type': 'miji'},

    # 下面的是专门查询本机公网ip的网址，请求不能过于频繁
    {'url': 'http://pv.sohu.com/cityjson', 'type': 'sohu'},
    {'url': 'http://ip.taobao.com/ipSearch.html', 'type': 'taobao'},
    {'url': 'https://myip.ipip.net/', 'type': 'myip'},
    {'url': 'http://httpbin.org/ip', 'type': 'httpbin'},
    {'url': 'http://ip.chinaz.com/', 'type': 'chinaz'},
    {'url': 'https://www.ipip.net/ip.html', 'type': 'ipip'},
    {'url': 'https://ip.cn/', 'type': 'ipcn'},
    {'url': 'https://tool.lu/ip/', 'type': 'luip'},
    {'url': 'http://api.online-service.vip/ip/me', 'type': 'onlineservice'},
    {'url': 'https://ip.ttt.sh/', 'type': 'ttt'},
    # {'url': 'http://icanhazip.com/', 'type': 'ican'},  # 该网站有时会返回一个ipv6地址，导致结果有误
]

"""
招聘网站：自添加招聘网站的url请按照已有数据的格式来添加
"""

# ##### 智联招聘，智联招聘相关 ######
'如果失效可以用浏览器抓包工具重新获取'
# 智联的请求id
ZHAOPIN_CLIENT_ID = 'c309970e-8633-44e6-8ac6-98f8eda5533f'

# 卓聘网的请求id
ZHUOPIN_CLIENT_ID = 'cb0aeec2-9853-4525-92a4-3e01495f95a3'

# 拉钩的职位详情请求参数
'如果失效可以用浏览器抓包工具重新获取'
LAGOU_SHOW = '090fea62d1b84e1d982a52cf822b20bc'

# boss直聘cookie
'如果失效可以用浏览器抓包工具重新获取，只需要__zp_stoken__字段'
BOSS_COOKIE = {
    'cookie': '__zp_stoken__=1dacyg1nZUJusrAy97BCslcWJ9TsTGXif7Jl9NCFx7O7yvrvntiFb8zLCkK0pattiC9Igj99xKyLbPuzcv%2BsAu3oiQ%3D%3D'
}

REQEUST_URLS = [

    {'url': 'https://www.kanzhun.com/jobl/p{p}/?q={q}', 'args': 'python', 'type': 'kanzhun'},
    {'url': 'https://www.zhipin.com/c100010000/?query={q}&page={p}', 'args': 'python', 'type': 'boss'},
    {'url': 'https://search.51job.com/list/000000,000000,0000,00,9,99,{q},2,{p}.html', 'args': 'python',
     'type': '51job'},
    {
        'url': 'https://fe-api.zhaopin.com/c/i/sou?start={p}&pageSize=90&cityId={c}&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw={q}&kt=3&rt=76ba428eb3a249b3ae6d859337599c01&_v=0.89754140&x-zp-page-request-id=96001ea406a04e0da1e8b0230d78e5e8-1564897992518-310307&x-zp-client-id=' + ZHAOPIN_CLIENT_ID,
        'args': 'python', 'type': 'zhilian'},
    {'url': 'https://data.highpin.cn/api/JobSearch/Search?x-zp-client-id=%s' % ZHUOPIN_CLIENT_ID,
     'args': 'python', 'type': 'zhuopin'},
    {'url': 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false', 'args': 'python',
     'type': 'lagou'},
    {
        'url': 'https://so.dajie.com/job/ajax/search/filter?keyword={q}&order=0&city=&recruitType=&salary=&experience=&page={p}&positionFunction=&_CSRFToken=&ajax=1',
        'args': 'web前端', 'type': 'dajie'},
    {'url': 'http://www.job5156.com/s/result/ajax.json?keyword={q}&keywordType=0&sortBy=0&pageNo={p}', 'args': 'python',
     'type': 'zhitong'},
    {'url': 'http://s.cjol.com/service/joblistjson.aspx', 'args': 'java', 'type': 'cjol'},
    {'url': 'http://s.yingjiesheng.com/search.php?word={q}&start={p}&sort=score', 'args': 'python', 'type': 'yjs'},
    {'url': 'https://www.jobcn.com/search/result_servlet.ujson?s=search%2Ftop', 'args': 'java', 'type': 'jobcn'},
    {'url': 'http://www.jiaoshizhaopin.net/jobs/jobs-list.php?key={q}&district_id=&page={p}', 'args': '小学语文',
     'type': 'jiaoshizhaopin'},
    {'url': 'https://china.baixing.com/search/?page={p}&query={q}', 'args': '乘务员', 'type': 'baixing'},
    {'url': 'http://www.51shuobo.com/s/result/kt1_kw-{q}_pn{p}/', 'args': '工程师', 'type': 'shuobo'},
    {
        'url': 'https://www.liepin.com/zhaopin/?init=-1&headckid=78dfb15a24a00c28&fromSearchBtn=2&ckid=78dfb15a24a00c28&degradeFlag=0&key={q}&siTag=I-7rQ0e90mv8a37po7dV3Q~fA9rXquZc5IkJpXC-Ycixw&d_sfrom=search_unknown&d_ckId=86780e1c81b976658deb5a339a4071ec&d_curPage=1&d_pageSize=40&d_headId=86780e1c81b976658deb5a339a4071ec&curPage={p}',
        'args': 'python', 'type': 'liepin'},
    {'url': 'http://{c}.ganji.com/zp{q}/o{p}/', 'args': 'jiaoshi', 'type': 'ganji'},  # 普通类
    {'url': 'http://{c}.ganji.com/zhaopin/s/f{p}/_{q}/', 'args': '软件', 'type': 'ganji_it'},  # it类的
    {'url': 'https://{c}.58.com/job/pn{p}/?key={q}&classpolicy=main_null,service_B&final=1&jump=1', 'args': '工程师',
     'type': '58'},
    {'url': 'https://search.chinahr.com/{c}/job/pn{p}/?key={q}', 'args': 'java', 'type': 'chinahr'},  # 返回结果有时候很慢
    {'url': 'http://www.chinahr.com/sou/?orderField=relate&keyword={q}&page={p}', 'args': 'java',
     'type': 'chinahr_old'},
    {'url': 'http://www.job1001.com/SearchResult.php?page={p}&region_1=&jtzw={q}', 'args': 'java', 'type': 'job1001'},
    {'url': 'https://www.linkedin.com/jobs-guest/jobs/api/jobPostings/jobs?keywords={q}&location={c}&start={p}',
     'args': 'python', 'type': 'linkin'},
    {'url': 'http://www.doumi.com/search/o1/kwd_{q}/', 'args': '服务员', 'type': 'doumi'},
    {'url': 'http://www.gongzuochong.com/wapi/jobs/search?city={c}&categoryId=-1&keyword={q}&page={p}', 'args': '服务员',
     'type': 'gongzuochong'},
    {'url': 'https://hr.ofweek.com/jobs/?key={q}&page={p}', 'args': 'python', 'type': 'ofweek'},
    {'url': 'https://www.telecomhr.com/jobs/index.php?bc=&sc=&jobarea=&keyword={q}&page={p}', 'args': '软件',
     'type': 'telecomhr'},
    {'url': 'https://www.tndbjob.com/job/list/0-0-0-0_0_0_0_0_0_0-0-0-0-{p}.html?{q}', 'args': '服务员',
     'type': 'tndbjob'},
    {'url': 'https://www.wztxjob.com/job/list/0-0-0-0_0_0_0_0_0_0-0-0-0-{p}.html?{q}', 'args': '服务员',
     'type': 'wztxjob'},
    {'url': 'https://www.qcrcw.net.cn/job/list/0-0-0-0_0_0_0_0_0_0-0-0-0-{p}.html?{q}', 'args': '服务员', 'type': 'qcrcw'},
    {'url': 'https://www.pcbjob.com/job/list/0-0-0-0_0_0_0_0_0_0-0-0-0-{p}.html?{q}', 'args': '经理', 'type': 'pcbjob'},
    {
        'url': 'https://zhaopin.baidu.com/api/qzasync?query={q}&city={c}&is_adq=1&pcmod=1&token={token}&pn={p}&rn=20'
        , 'args': 'python', 'type': 'baidu'},
    {'url': 'https://zhaopin.baidu.com/api/jianzhiwiseasync?query={q}&city={c}&token={token}&pn={p}&rn=10',
     'args': '服务员', 'type': 'baidu_jianzhi'},
    {'url': 'http://www.jiaoshi.com.cn/jobs/jobs_list/key/{q}/page/{p}.html', 'args': '老师', 'type': 'jiaoshi'},
]

# 'http://pibao.pullwave.com:8080/index.php?name=%s&page=%s'

# redis数据库连接池
'可以自行设置为其他的数据库'
POOL = redis.ConnectionPool(host='127.0.0.1', max_connections=100, decode_responses=True, db=1)
POOL2 = redis.ConnectionPool(host='127.0.0.1', max_connections=5, decode_responses=True, db=2)
POOL3 = redis.ConnectionPool(host='127.0.0.1', max_connections=100, decode_responses=True, db=1)
POOL4 = redis.ConnectionPool(host='127.0.0.1', max_connections=100, decode_responses=True, db=1)
POOL5 = redis.ConnectionPool(host='127.0.0.1', max_connections=100, decode_responses=True, db=1)

# 搜索关键词
'可以自己添加关键词'
SEARCH_ARGS = ['钣金', '建筑设计师', '制片', '行政经理', '店员/营业员', '物流经理', '采购专员', '游戏原画', '活动策划', '培训师', '剪辑', '预结算', '月嫂', '图像识别',
               '地产招投标', '女装设计', '焊工', '法务', '品牌策划', '用户研究经理/主管', 'BD经理', 'Android', '中医', '电竞主持', '预定票务',
               '影视发行', '仓储物料专员', '软件测试', '架构师', '核销员', '影视媒体', '理疗师', '文案', '财务总监', '房地产评估', '物业客服', 'IDC',
               '面料辅料开发', '管理培训生', 'Flash开发', '性能测试', '会展活动执行', '拓展培训', '教育行政', '银行柜员', '酒店', '理科教师', '网络推广', '医学总监',
               '选址开发', '商业数据分析', '外贸经理', '品类运营', '安全员', '美容学徒', '舞蹈教练', '摄影', '工程造价', 'UX设计师', '铣工', '财务分析', '零部件设计',
               '用户研究总监', '工艺/制程工程师', '美容导师', '验光师', '企业管理咨询', '项目助理', '游戏测试', '权证', '海外运营', '药品生产', '总助', 'COO', '股票',
               '交互设计经理/主管', '电气工程师', '硬件交互设计师', '物业经理', '音频编辑', '热传导', '广告销售', '底盘设计', '合伙人', '供应链专员', '二手车评估师', '物仓项目',
               '保洁', '市场调研', '企业软件其它', '手游推广', '模具设计', '货运代理专员', '客服总监', '电商产品经理', '集装箱管理', '课程编辑', '材料工程师',
               '会议活动策划', '食品/饮料研发', '室内设计师', '网页交互设计师', 'PHP培训讲师', '.NET培训讲师', '房地产销售总监', '大客户代表', '铲车', '销售工程师',
               '区域总监', '大堂经理', '网站编辑', '项目主管', '客服经理', '品牌专员', '汽车销售', '地产招投标总监', '公司法务', '市场总监', '网络工程师', '锅炉工',
               '外贸助理', '商务渠道', '功能测试', '后端开发其它', '汽车工程项目管理', '旅游服务', '医生', '心理医生', '施工员', '涂料研发', '多媒体设计师', 'DB2', '主编',
               '移动开发其它', 'UI设计培训讲师', '剧情设计', '美术设计师（2D/3D）', '无线射频工程师', '普工/操作工', '物业维修', '移动web前端', '教练', '老师', '英语老师',
               '临床数据分析', '机械设备工程师', '财产保险', '总装工程师', 'CTO', '视觉设计经理/主管', '系统安全', '录音/音效', 'JAVA培训讲师', '会议活动执行', '银行',
               '采购经理', '冲压工程师', '原画师', '临床研究', '报关员', '供应链总监', '游戏体验', '社区运营', '整形师', 'Web前端', '硬件开发其它', '放射科医师',
               '美术老师', '汽车改装工程师', '算法工程师', '数据开发', '用户研究经理', 'Ruby', '物流专员', '薪资福利经理', '广告专员', '资料员', '网页设计', '总编',
               '导医', '渠道销售 ', '网站运营', '医学编辑', '化工', '咨询热线/呼叫中心客服', '零售', '撰稿人', '绩效考核经理', '插画师', '证券经纪人', '咨询总监',
               '土建工程师', '采编/写作/出版', '美容师/顾问', '电话客服', '健康顾问', '无线产品设计师', '设计师助理', '其他销售', 'APP推广', 'DSP开发', '房地产开发',
               '运营专员', '外贸业务员', '公关总监', 'IT咨询顾问', '包装设计', '投资VP', '医学影像', '大客户销售', '体育教师', '车险', '财务主管', '售后工程师',
               '游戏数值策划', '汽车销售与制造', '男装设计', '人力资源总监', '餐饮管理', '平面设计', 'Go', '面料辅料采购', '推荐算法', '主持人/DJ',
               '课程顾问', '折弯工', '微博运营', '票务', 'C++', '视觉设计', '医疗器械销售', '编剧', '客服专员/助理', '实施工程师', '财务总监/经理', '物业总监',
               '医疗器械注册', '通信项目经理', 'FAE', '培训', '销售管理', '配菜打荷', '游戏美工', '通信项目专员', '数据分析师', '知识产权', '物业管理',
               '餐饮店长', '绩效考核', '视觉设计经理', 'Erlang', '仓储物料项目', '运维经理', '网店运营', '品牌公关', '陈列员', '销售', '护士/护理', '设计总监',
               '体系工程师', '员工关系', '培训研究', '外语教师', '建筑工程师', '语音识别', '证券', '期货', '课程设计', 'CEO/总裁/总经理', '物业项目经理', '咨询/调研',
               '保险理赔', '法务总监', '品牌经理', '贸易跟单', '运营经理', '金融产品经理', '用户研究员', '车工', '语音/视频/图形开发', '生产经理/车间主任', '通信标准化工程师',
               '教师', '行政主管', '代理商销售', '营销主管', '视频编辑', '精准推荐', '采购工程师', '包装工', '金融研究', '旅游产品经理', '催收员', '漆工', '内容审核',
               '影视制作', '健身', '单片机', '质检员', '房地产销售', '通信电源工程师', '微信运营', '事业部负责人', '金融产品', '光网络工程师', '家居设计',
               '督导/巡店', '新零售产品', '生产员', '外贸专员', '化学分析', '副总裁/副总经理', '数据运营', '商务总监', '物仓调度', '软件销售支持', '.NET', '贷款',
               '导游', '律师', '叉车', '需求分析工程师', 'CDN', '营养师', '财务', '配送', '采购', '产品助理', '政府关系', '软件测试培训讲师', '婚礼策划师',
               '模具工程师', '客户代表', 'IT支持', '人力资源VP/CHO', '医药研发', '买手', '房地产招商', 'ETL工程师', '文案策划', '置业顾问', '销售运营', '领班',
               '机器学习', '客服', '助教', '游戏界面设计师', '钳工', '美甲师', '商家运营', '前台', '生产计划/物料控制', '技术合伙人', '建筑设计', '测试工程师', '游戏文案',
               '市场顾问', '礼仪迎宾', '医药代表', '俄语翻译', '操盘手', '图像算法', '电子工程设计', '销售代表', '仓储物料经理', 'SEM', '校长', '美术指导', '非视觉设计',
               '查勘定损', '人力资源专员', 'PCB工艺', '统筹制片人', '会计', '瑜伽教练', '采购主管', '留学顾问', '设计装修与市政建设', '测试总监', '网页产品设计师', '美术教师',
               '客服主管', 'F5', '投融资', '银行销售', '日语翻译', '教务', '摄影师', '品牌合作', '法务专员/助理', '注塑工', '商务主管', '机械结构工程师', '快递',
               '广告制作', '光传输工程师', '美容师', '副主编', '产品运营', '报检员', '海外市场', '质量工程师', '游戏动作', '幼教', '广告', '小学教师', 'WP', '旅游顾问',
               '地产项目总监', '区域/分公司/代表处负责人', '后端开发', '物流管理', '健身教练', '创意总监', '运营经理/主管', 'Android培训讲师', '消防', '公关媒介',
               '搜索算法', '物业租赁销售 ', '执行制片人', '广告协调', '财会培训讲师', '夹具工程师', '游戏界面', '美体教练', '注塑工程师', '董事会秘书', '旅游计调', '督导',
               'C', '城市规划设计', '光通信工程师', '薪资福利', '储备干部', '机器视觉', '汽车维修', '地产评估', '结构工程师', '内容编辑', '咨询项目管理',
               '园林设计', '咖啡师', '系统工程师', '商务司机', '高级管理职位', '销售专员', '游戏动效', '信贷', '网络安全', '售后客服', '地产中介', '汽车美容', '猎头顾问',
               '基金', '移动通信工程师', '打样/制版', 'COCOS2DX', '证券分析师', '化工工程师', '灰盒测试', '出纳', '保险销售', 'APP设计师', '投资助理', '内容运营',
               '厂长/工厂经理', '法务专员', '质量管理/测试', '担保', '数据产品经理', '理赔', '培训经理', '广告创意', '物流跟单', '运营', '发型师', '交互设计总监',
               '投资总监', '数据仓库', '健康整形', '财务咨询顾问', '产品总监', '英语翻译', '游戏场景', '媒介投放', '氩弧焊工', '仓库文员', '通信研发工程师', '有线传输工程师',
               '市场策划', '校对录入', 'Delphi', '影视策划', '收银', '司机', '医师', '审核员', '货运代理经理', '生产总监', '物业', '设备工程师', '网页产品经理',
               '收银员', '媒介经理', '其他销售管理职位', '德语翻译', '自媒体', 'IT技术支持', '教务管理', '催收', '地产策划总监', '就业老师', '测试开发', '报检报关',
               '一级建造师', '机械维修/保养', '4S店管理', '童装设计', '花艺师', '市场营销/媒体', '硬件', 'ARM开发', '空调工', '财务顾问', 'HRBP', '电信交换工程师',
               '瘦身顾问', '服务员', '铆工', '项目总监', '商务专员', '化妆/造型/服装', '外贸英语', '人力资源主管', '广告审核', '核心网工程师', 'MySQL', '小游戏开发',
               '厨师', '理财顾问', '工业工程师', '喷塑工', '咨询经理', '后厨', '通信技术工程师', '销售VP', '机械工程师', '物业主管', '技术经理', '销售总监', '并购',
               '开发报建', '水/空/陆运操作', '导购员', '广告投放', '电气设计工程师', '主播', '供应链经理', '造价员', 'SQLServer', '班主任', '采购总监', '药学编辑',
               '铸造/锻造工程师', '外贸', 'Node.js', '团队经理', '机械设计/制造', '嵌入式', '土建', '审计', 'FPGA开发', '保安', '行政专员', 'C++游戏开发',
               '数据', '服装/纺织/皮革跟单', '数据架构', '运输经理/主管', '会展活动销售', '会籍顾问', '培训策划', '地产经纪', '化妆品研发', '营业员', '机械设计师', '记者',
               '动画设计师', '硬件工程师', 'Unity 3D培训讲师', 'web前端', '战略咨询', '理货员', '牙科医生', '运输', '汽车定损理赔', '土木/土建/结构工程师', '仓储管理',
               '陈列设计', '西点师', '内外饰设计工程师', 'HR培训讲师', '编辑', '区块链', 'FLASH', '视觉设计总监', '创始人', '生产组长/拉长', '专利', '面料设计',
               '房地产经纪', '游戏编辑', 'VB', 'ios培训讲师', '产品专员', '高级建筑工程师', '家具设计', 'Perl', '数据架构师', '系统管理员', '运营总监',
               '三维/CAD/制图', '工业设计', '法律顾问', '旅游产品开发/策划', 'Shell', '韩语/朝鲜语翻译', '催乳师', '媒介策划', '出版发行', 'Java开发', '室内设计',
               'PHP', '电路设计', '医疗器械研究', '产品VP', '策略运营', '保姆', '项目专员', '销售助理', '媒介总监', '医美咨询', '动力系统设计', 'B超医生', '城市经理',
               '自动化', '游戏产品经理', '销售经理', '会议活动销售', 'Python', '移动产品经理', '珠宝设计', '病毒分析', 'Golang', '行业研究', '运维工程师', '医生助理',
               '结算', '广告文案', '执业药师/驻店药师', ' APP推广', 'CFO', '互联网金融', '投后管理', '教育产品研发', '算法研究员', '广告设计师', '文员', 'DBA其它',
               'U3D', '运维其它', '人力资源专员/助理', '媒介顾问', '酒店经理', '货运代理', '游戏特效', '电话销售', '用户运营', '活动运营', '车身设计', 'HRD/HRM',
               'CMO', '房产策划', '机修工', '游戏运营', '人力资源顾问', '游戏陪练', '数据挖掘', 'JavaScript', '融资', '可靠度工程师', '酒店管理', '采购助理',
               '实施顾问', '抛光', '广告定价', '商务拓展', '摄影/摄像', '美工', '货运司机', '预算员', '外贸跟单', '跆拳道教练', '组织发展', '招聘', 'COCOS2D-X',
               '会展活动策划', '事务所律师', '电子工程师', '合规稽查', '自动化测试', '同声传译  ', '初中教师', 'Flash', '物流运营', '新媒体运营', '淘宝客服', '英语',
               '游戏策划', '渠道销售', '硬件测试', '电镀工', '音乐教师', '篮球/羽毛球教练', '法务主管', '汽车金融', '市场营销', '班主任/辅导员', '制片人', '酒店前台',
               '药品注册', '游戏主播', '医美', '系统集成', '运营助理/专员', 'UI设计师', '计调', '商品经理', '医生/医技', '网络营销', '经纪人', '进出口贸易',
               '生产设备管理', 'html5', '房地产规划开发', 'C++培训讲师', '平面设计师', '视觉设计师', '焊接工程师', '导购', '供应链', '产品实习生', '设计经理/主管',
               '家政', 'Hive', 'DBA', '资信评估', '媒介合作', '销售顾问', 'BI工程师', '图像处理', '药剂师', '税务', '项目经理', '柜员', '化妆师', '钻工',
               '通信设备工程师', '故障分析师', '餐饮', '物流', '建筑施工现场管理', '自然语言处理', '检验科医师', '测试经理', '策划经理', '电梯工', '活动策划执行', '生物制药',
               '分析师', '保险内勤', '行政', '客房服务员', '文科教师', 'Java', '地产置业顾问', 'ASP', '页游推广', 'CNC/数控', '采编', '典当', '手机测试',
               'C#', '前端开发其它', '签证', '投资合伙人', '内衣设计', '运维开发工程师', '生产营运', '深度学习', '总裁/总经理/董事长助理', '电商运营', '纹绣师', '投资经理',
               '数据通信工程师', '店长', '房地产策划', '游戏推广', '交互设计师', '演员/配音/模特', '通信测试工程师', '法务经理', '行政专员/助理', '物业招商管理', 'IT培训',
               '服装设计', 'CEO', '线下拓展运营', '信审', 'MongoDB', '电信网络工程师', 'Hadoop', '财务经理', '售后咨询', '工程资料管理', '机电工程师', '售前咨询',
               '网络客服', '医疗器械生产/质量管理', '配/理/拣/发货', '助理', '教学管理', '移动端测试', '工程监理', '电工', '护士长', '测试其它', '实验室技术员', '安全专家',
               '会务会展', '动漫培训讲师', '市场推广', '旅游销售', '工艺工程师', '药店', '投资顾问', '门店店长', '汽车售后服务', 'Web前端培训讲师', '地产项目管理',
               '康复治疗师', '信用卡销售', '资产管理', '单证员', '弱电工程师', '机械制图', '白盒测试', 'ETL', '技术总监', '渠道推广', '物流总监', '暖通', '清算',
               '生产跟单', '育婴师', '机械设计', '游泳教练', '外贸日语', '编导', '高级翻译', '放映管理', '游戏制作人', '仓储', '信贷管理', '数据采集', 'PLC', '后勤',
               '后期制作', '行政总监', '射频工程师', '西班牙语翻译', '人力资源经理', '保险业务', '茶艺师', 'WEB安全', '人事/HR', 'H5游戏开发', '移动开发',
               '学徒工', '认证工程师', '人工智能', '汽车配件销售', '招生顾问', '高中教师', '磨工', '天猫运营', '法语翻译', '淘宝运营', '客户经理', 'Flash设计师', '木工',
               '运维总监', '精算师', '风控', 'iOS', '产品部经理', '媒介专员', '驱动开发', '导演/编导', 'Oracle', '游戏动画', '游戏项目经理', '经理助理',
               '售前工程师', 'SEO', '汽车设计', '临床协调', '无线交互设计师', '媒介', '电竞讲师', 'HTML5', '产品经理', '景观设计', '针灸推拿',
               '信用卡', '全栈工程师', '旅游策划师', '黑盒测试', '文秘', '行政总监/经理', '信托', '组装工', '餐饮学徒', '送餐员', '婚礼策划', '网页设计师', '游戏后端开发',
               '人力资源', '橱柜设计', '前端开发', '游戏角色', '精益工程师', '交易员']


# 定时自动保存已爬取的职位的间隔时间
'可自行设置，单位为秒'
INTERVAL = 30

# 爬取深度,最大页码
'可自行设置'
END_PAGE = 100

# 最大协程数
'可根据自己的电脑配置自行设置数量,协程池不能设置太大的量，因为协程的并发性能太强导致并发量太大，redis连接池无法承受，原则上不要用协程的方式爬取，容易报错'
GEVENT_POOL = 10

# 最大线程池数
THREAD_POOL = (os.cpu_count() or 1) * 4

# 设置日志等级
LOG_LEVEL = logging.INFO

# 日志文件名
LOG_NAME = 'crawling.log'