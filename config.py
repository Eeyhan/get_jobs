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
    'cookie': '__zp_stoken__=f9a3lmcMsXcux%2FyUgfzudRYPuFETGRCDlQeXPmU%2FD16o1CQ9654j3VWHwsfEBLL%2B3Qi3OsARDOiYp9HP%2BaATU3A4SA%3D%3D'
}

# 各大招聘网站
'可自定制，可增加，但同时也要给定对应的解析方法'
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
POOL2 = redis.ConnectionPool(host='127.0.0.1', max_connections=100, decode_responses=True, db=2)
POOL3 = redis.ConnectionPool(host='127.0.0.1', max_connections=100, decode_responses=True, db=1)

# 搜索关键词
'可以自己添加关键词,以下是各大网站的职位的总和，建议不要使用全部关键词，根据实际情况选择少数的职位关键词即可'

# '测试时使用'
SEARCH_ARGS = ['python', 'php', 'java', 'c', 'golang','C++','安卓','ios','前端','小程序','后端开发','数据库管理员','网络管理员','运维','自动化','测试','产品','运营','推广','文案','销售','客服','顾问']

# SEARCH_ARGS = ['运维', '总编', '土木工程', '薪资福利经理', '文案策划', '图像处理', '推广', '内容审核', '基金', '理货员', '搜索', 'U3D', '美术设计师', '软件测试',
#                '药品注册', '高中教师', '零售', '组长', '药师', '交易员', 'DB2', 'SEO', '篮球/羽毛球', '售后工程师', '物仓项目', '外贸业务员', '设备工程师', '配音',
#                'HTML5', '采购工程师', '药品生产', '品牌合作', '培训', '旅游计调', '硬件工程师', '医学影像', '广告', 'C++', '工程资料', '通信研发工程师',
#                '货运代理专员', '外贸', 'ETL工程师', '市场策划', 'ios', '仓储物料', '质检员', 'MySQL', 'WP', '信审', '机械制图', '电器维修', '进出口贸易',
#                '采购专员', '演员', '车工', '自动化测试', '语音/视频/图形开发', '内容编辑', '秘书', 'HR', '保洁', '医药研发', '婚礼', '整形师', 'DSP开发',
#                '通信技术工程师', '磨工', '审核', '工业工程师', '建筑工程师', '音频编辑', '铣工', '行政经理', '铆工', '制片', '定损理赔', '旅游', '保险理赔', '药剂师',
#                '医生', '运输', '育婴师', '广告销售', '催乳师', '英语', 'Ruby', '汽车销售与制造', '自然语言处理', '保姆', '剧情设计', 'JAVA', '灰盒测试', '发型师',
#                '数据分析师', '广告创意', '技术总监', '留学', '幼教', '游戏测试', 'PCB', 'WEB安全', '面料', '辅导员', '保安', '用户研究', '中介', '公司法务',
#                '音乐', '手机维修', '行业分析', '供应链总监', '生物制药', '跆拳道', '写作', '病毒分析', '教师', '律师', '婚庆', '大堂经理', '无线交互设计师', '核销员',
#                '嵌入式', '光网络工程师', '游戏策划', '店员/营业员', '康复治疗师', '培训师', '健身', '药学编辑', '护士/护理', '后勤', '光传输工程师', 'COO', '票务',
#                '绩效考核经理', '自媒体', '化工工程师', '厨师', '互联网金融', '售前工程师', '产品经理', '网页设计师', '可靠度工程师', '机械工程师', '语音识别', '区块链',
#                '锅炉工', '普工', '投资', '文案', '药店', '产品助理', 'IDC', '美工', '铸造', '中医', '多媒体设计师', '前端开发', 'CDN', '公关', '汽车',
#                '海外运营', '采购', '电气工程师', '编导', '贷款', '设计装修', '包装设计', '视觉设计', '有线传输工程师', '原画师', '单证员', '地产评估', '副主编', '调研',
#                '供应链专员', '校长', 'Java开发', '化工', '物业招商管理', '主任', '茶艺师', '通信工程师', '网络客服', '化妆/造型', '主管', 'Golang', 'FPGA',
#                '经理', '融资', '影视媒体', '二手车评估师', '主持人', '信托', '线下拓展', '陈列设计', 'HRD/HRM', '瑜伽', '电路设计', '并购', '财务', '礼仪迎宾',
#                '买手', '汽车销售', '运维工程师', '算法工程师', '权证', 'ASP', '汽车金融', '导演', '橱柜设计', '数据挖掘', '西点师', 'IT', '市场营销', '督导',
#                '游戏原画', 'UX设计师', '财务咨询顾问', '微博运营', '内衣设计', '分析师', '催收员', '咨询总监', '租赁', '班主任', '移动产品', '美容', '编剧', '顾问',
#                '车身设计', 'B超', '机械设计', '开发报建', 'H5游戏开发', '保险', '游戏美工', 'Delphi', '放射科医师', '汽车改装', '调度', '数据通信工程师', '学徒',
#                '临床协调', '机械保养', 'Hive', '验光师', '网络工程师', '客户代表', '咨询项目管理', '体系工程师', '性能测试', '机电工程师', '工业设计', '土建', '清算',
#                '汽车设计', '项目总监', '珠宝', '快递', '通信测试工程师', '深度学习', '行政', '社区运营', '模具工程师', '底盘设计', '注塑工', '创意', '动力系统设计',
#                '城市规划', '公关总监', 'Web前端', '产品总监', '负责人', '网页交互设计师', '文员', '移动通信工程师', '系统集成', '合伙人', 'APP设计师', '白盒测试',
#                '销售', '技术支持', '翻译', '数据分析', '司机', '人事/HR', '销售代表', '模具设计', '客服主管', '通信设备工程师', 'Flash', '室内设计', '质量工程师',
#                '送餐员', 'CFO', '后厨', '放映', '收银', '影视制作', '专利', '预结算', '法律', '股票', '总监', '报检员', '理财', '电梯工', '安全专家', '收银员',
#                '导购', '美甲师', '后端开发', '工程造价', '生产总监', '医师', '主播', '餐饮', 'Go', '美术', '合规稽查', '市场顾问', '服装设计', '招聘', '操盘手',
#                '木工', '系统工程师', '漆工', '喷塑工', '健康整形', '零部件', 'web前端', '精益工程师', '置业', '小游戏开发', '财务分析', '策划', '咖啡师', '实习生',
#                '特效', '造价员', '期货', '氩弧焊工', '银行', '记者', '投资总监', 'BI工程师', '物流经理', '硬件测试', '教练', '冲压工程师', 'ETL', '非视觉设计',
#                '担保', '安全员', 'CEO', '助理', 'VB', 'JavaScript', '模特', '区域总监', '证券', '配菜打荷', '厂长', '会计', '制程工程师', '售前咨询',
#                '媒介投放', '外语', 'F5', '签证', '投融资', '资产管理', '车险', '报检报关', '游戏动画', '总装工程师', '地产置业', '游戏文案', '店长', '投资助理',
#                '教育', '机械结构工程师', '测试工程师', '护士长', '图像识别', '财务主管', '花艺师', '录音', '运营', '运营专员', '系统管理员', '系统安全', '实施工程师',
#                'COCOS2D-X', '仓储管理', '空调工', '活动运营', 'Unity 3D培训讲师', '媒介', '折弯工', '助教', '游戏陪练', '女装设计', '用户研究经理', '报关员',
#                '资料员', '月嫂', '电子工程设计', '男装', '通信电源工程师', 'IT咨询顾问', '电镀工', '策略', '交互设计', '算法', '热传导', '医疗器械', '全栈工程师',
#                '编辑', '物流', '课程设计', '实验室技术员', '射频工程师', '银行柜员', '医学', '地产项目总监', '核心网工程师', 'CAD', '针灸推拿', '单片机', '广告制作',
#                '建造师', '商务拓展', '医疗器械销售', '游戏角色', '教务', '导游', '项目主管', '项目助理', '精算师', '渠道推广', '酒店前台', '柜员', '企业管理咨询',
#                '活动策划', '包装工', '品牌专员', '网页设计', '集装箱', '汽车维修', '自动化', 'UI设计', 'Node.js', '知识产权', '纹绣师', 'SEM', '理疗师',
#                '工程监理', '渠道销售', '食品/饮料', '钳工', '猎头', '页游推广', '需求分析', '跟单', '游戏后端开发', '微信运营', '电商产品', 'HRBP', '典当', '插画师',
#                '医美', '餐饮店长', 'Java', '分拣员', '工艺工程师', '房地产评估', 'C++游戏开发', '土建工程师', '供应链', '会籍', '领班', '地产招投标', '驱动开发',
#                '硬件', 'Hadoop', '制版', '临床', '组装工', '叉车', 'Python', '房地产', '钣金', '前台', '网络推广', '.NET', '生产员', '陈列员',
#                '游戏界面设计师', '游戏场景', 'DBA', '电工', 'CTO', '摄影师', '机械设计师', 'DJ', '广告投放', '电气设计工程师', 'ARM开发', '新媒体', '牙医',
#                '移动开发', '物业维修', '出版发行', '校对录入', '涂料', '预算员', '酒店管理', '管理', '机修工', '后期制作', '销售工程师', '信贷', '副总裁', '经纪人',
#                '品牌策划', '理赔', '查勘定损', '夹具工程师', 'web后端', '大客户销售', 'C++培训讲师', '化学', '会务会展', '施工员', '婚礼策划师', '黑盒测试',
#                '证券经纪人', '游戏界面', '老师', '仓储', '电信交换工程师', '同声传译', '消防', '生产设备管理', '董事长', '机械设备工程师', '家具设计', '汽车配件销售',
#                '弱电工程师', '审核员', '建筑设计师', '文秘', '资信评估', '手游推广', 'Erlang', '审计', '商务总监', '机器视觉', '园林设计', '内外饰设计工程师', '出纳',
#                '金融产品', '网站运营', 'COCOS2DX', '电子工程师', '设计总监', '市场调研', '人力资源专员', '采编', '结构工程师', '面料辅料', '机器学习', 'PHP',
#                '新媒体运营', '故障分析师', '景观设计', '注塑工程师', '营业员', '平面设计', '家居设计', '财会', 'Android', '架构师', '网络安全', '通信项目', '钻工',
#                'C', '仓储物料专员', '计调', '电竞讲师', '化妆师', 'PLC', '营养师', '银行销售', '税务', '美术指导', 'Oracle', '剪辑', '家政', '数控',
#                '证券分析', '主编', '物业', '建筑设计', 'UI设计师', 'C#', '导医', '生产跟单', '会议活动执行', '暖通', 'html5', '摄影', '销售运营', 'IOS',
#                '法务', '人力资源', '电信网络工程师', '硬件交互', '酒店', '投资VP', '抛光', 'Perl', '投后管理', '体育教师', '运维开发工程师', '大客户代表', '生产营运',
#                '汽车售后服务', '人工智能', 'FAE', '材料工程师', '淘宝客服', '数据仓库', '制片人', '光通信工程师', '配送', '焊工', '仓库文员', '信用卡', '医疗器械研究',
#                '焊接工程师', '电竞主持', '选址开发', 'MongoDB', 'SQLServer', '图像算法', '家电维修', '客服', '无线产品设计师', '视频编辑', '新零售', '测试开发',
#                '电商运营', '售后', '撰稿人', '服务员', '化妆品', 'Shell', '风控', '铲车', '无线射频工程师', '动画设计', '总助', '数据', 'CMO', '采购助理',
#                '行政总监']

# 定时自动保存已爬取的职位的间隔时间
'可自行设置，单位为秒'
INTERVAL = 30

# 爬取深度,最大页码
'可自行设置，但一般情况下每个网站搜出来的职位最多就50页左右'
END_PAGE = 30

# 最大协程数
'可根据自己的电脑配置自行设置数量,协程池不能设置太大的量，因为协程的并发性能太强导致并发量太大，redis连接池无法承受，原则上不要用协程的方式爬取，容易报错'
GEVENT_POOL = 10

# 最大线程池数
THREAD_POOL = (os.cpu_count() or 1) * 4

# 设置日志等级
LOG_LEVEL = logging.INFO

# 日志文件名
LOG_NAME = 'crawling.log'
