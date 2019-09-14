#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : Eeyhan
# @File    : v1.py

import gevent
from gevent import monkey
from gevent.pool import Pool

monkey.patch_all()
import requests
import urllib.parse
from lxml import etree
import random
import time
import json
import chardet
import asyncio
import os
import urllib3
import sys

sys.path.append(os.path.dirname(__file__))
from datetime import datetime
from datetime import timedelta
import re
import redis
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from proxy.proxy import get_redis as get_proxy_redis
from config import USER_AGENT, REQEUST_URLS, ZHUOPIN_CLIENT_ID, LAGOU_SHOW, POOL, POOL2, POOL4
from config import POOL3, BOSS_COOKIE, SEARCH_ARGS, INTERVAL, END_PAGE, GEVENT_POOL, THREAD_POOL
from logger import logger

requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5
CRAWL_LOG = logger()


class RequestHeader(object):
    """请求类"""

    def __init__(self):
        self.user_agent = USER_AGENT
        self.flag = False  # 爬取标志位

    def request_headers(self):
        """
        请求头
        :return:
        """
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,application/json, text/javascript,*/*;q=0.8',
            'User-Agent': random.choice(self.user_agent),
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Connection': 'keep-alive',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate',
            'Upgrade-Insecure-Requests': '1'
        }
        return headers


class ProxyHandler(object):
    """代理"""

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(ProxyHandler, "proxy_list"):
            ProxyHandler.proxy_list = get_proxy_redis()
        return ProxyHandler

    @classmethod
    def get_proxies(cls):
        """
        从redis里获取proxy
        :return:
        """
        if cls.proxy_list:
            return cls.proxy_list


class TargetUrlHandler(object):
    """目标url"""

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(TargetUrlHandler, "target_urls"):
            TargetUrlHandler.target_urls = get_url_redis()
        return TargetUrlHandler

    @classmethod
    def get_target_urls(cls):
        """
        从redis里获取proxy
        :return:
        """
        if cls.target_urls:
            return cls.target_urls


class BaseCrawl(RequestHeader):
    """爬虫类"""

    DOUMI_COOKIE_URL = 'http://www.doumi.com/%s/'
    BAIDU_COOKIE_URL = 'https://zhaopin.baidu.com/quanzhi'
    BAIDU_COOKIE_JIANZHI_URL = 'https://zhaopin.baidu.com/jianzhi'

    def __init__(self):
        super(BaseCrawl, self).__init__()
        self.header = self.get_header
        self.request_urls = self.get_request_urls
        self.proxy_list = None
        self.target_urls = None
        self.invalid_urls = set()
        self.jobs = []
        self.search_args = SEARCH_ARGS

    def get_args(self):
        """
        返回一个搜索关键词
        :return:
        """
        count = len(self.search_args)
        i = random.randint(0, count)
        args = self.search_args.pop(i)
        return args

    def get_doumi_city_codes(self):
        """
        返回斗米网的城市代码
        :return:
        """
        codes = ['aba', 'akesu', 'alaer', 'alashan', 'aletai', 'ali', 'ankang', 'anqing', 'anshan', 'anshun', 'anyang',
                 'aomen', 'bj', 'baicheng', 'baise', 'baishan', 'baiyin', 'baoding', 'baoji', 'baoshan', 'baotou',
                 'bayannaoer', 'bayinguoleng', 'bazhong', 'beihai', 'bengbu', 'benxi', 'bijie', 'binzhou', 'boertala',
                 'bozhou', 'cc', 'cs', 'cd', 'cq', 'cangzhou', 'changde', 'changdu', 'changji', 'changshu', 'changzhi',
                 'changzhou', 'chaohu', 'chaoyang', 'chaozhou', 'chengde', 'chenzhou', 'chifeng', 'chizhou', 'chongzuo',
                 'chuxiong', 'chuzhou', 'cixi', 'dl', 'dg', 'dali', 'dandong', 'danzhou', 'daqing', 'datong',
                 'daxinganling', 'dazhou', 'dehong', 'deyang', 'dezhou', 'dingxi', 'diqing', 'dongying', 'eerduosi',
                 'enshi', 'ezhou', 'foshan', 'fz', 'fangchenggang', 'fushun', 'fuxin', 'fuyang', 'jxfuzhou', 'gz', 'gy',
                 'gannan', 'ganzhou', 'ganzi', 'guangan', 'guangyuan', 'guigang', 'gl', 'guoluo', 'guyuan', 'hrb', 'hn',
                 'hz', 'hf', 'nmg', 'haibei', 'haidong', 'hainanzhou', 'haixi', 'hami', 'handan', 'hanzhong', 'hebi',
                 'hechi', 'hegang', 'heihe', 'hengshui', 'hengyang', 'hetian', 'heyuan', 'heze', 'hezhou', 'hljyichun',
                 'honghe', 'huaian', 'huaibei', 'huaihua', 'huainan', 'huanggang', 'huangnan', 'huangshan', 'huangshi',
                 'huizhou', 'huludao', 'hulunbeier', 'huzhou', 'jn', 'jiamusi', 'jian', 'jiangmen', 'jiaozhou',
                 'jiaozuo', 'jiaxing', 'jiayuguan', 'jieyang', 'jilin', 'jimo', 'jinchang', 'jincheng', 'jingdezhen',
                 'jingmen', 'jingzhou', 'jinhua', 'jining', 'jinzhong', 'jinzhou', 'jiujiang', 'jiuquan', 'jixi',
                 'jiyuan', 'km', 'kaifeng', 'kashi', 'kelamayi', 'kezilesu', 'kuerle', 'kunshan', 'lz', 'linyi',
                 'laibin', 'laiwu', 'langfang', 'xz', 'leshan', 'liangshan', 'lianyungang', 'liaocheng', 'liaoyang',
                 'liaoyuan', 'lijiang', 'lincang', 'linfen', 'linxia', 'linzhi', 'lishui', 'liupanshui', 'liuzhou',
                 'longnan', 'longyan', 'loudi', 'luan', 'luohe', 'luoyang', 'luzhou', 'lvliang', 'maanshan', 'maoming',
                 'meishan', 'meizhou', 'mianyang', 'mudanjiang', 'nj', 'nn', 'nb', 'nc', 'nanchong', 'nanping',
                 'nantong', 'nanyang', 'naqu', 'neijiang', 'ningde', 'nujiang', 'panjin', 'panzhihua', 'pingdingshan',
                 'pingliang', 'pingxiang', 'pixian', 'puer', 'putian', 'puyang', 'qd', 'qiandongnan', 'qianjiang',
                 'qiannan', 'qianxinan', 'qingyang', 'qingyuan', 'qinhuangdao', 'qinzhou', 'qh', 'qiqihaer', 'qitaihe',
                 'quanzhou', 'qujing', 'quzhou', 'rikaze', 'rizhao', 'sh', 'sy', 'sz', 'sjz', 'su', 'sanmenxia',
                 'sanming', 'sanya', 'shangluo', 'shangqiu', 'shangrao', 'shannan', 'shantou', 'shanwei', 'shaoguan',
                 'shaoxing', 'shaoyang', 'shennongjia', 'shihezi', 'shiyan', 'shizuishan', 'shuangliu', 'shuangyashan',
                 'shuozhou', 'siping', 'songyuan', 'suihua', 'suining', 'suizhou', 'suqian', 'ahsuzhou', 'ty', 'tj',
                 'jstaizhou', 'tacheng', 'taian', 'tangshan', 'tianmen', 'tianshui', 'tieling', 'tongchuan', 'tonghua',
                 'tongliao', 'tongling', 'tongren', 'tulufan', 'tumushuke', 'zjtaizhou', 'weifang', 'wei', 'wh', 'xj',
                 'wx', 'weinan', 'wenshan', 'wenzhou', 'wuhai', 'wuhu', 'wujiaqu', 'wulanchabu', 'wuwei', 'wuzhishan',
                 'wuzhong', 'wuzhou', 'xm', 'xa', 'xianggang', 'xiangtan', 'xiangxi', 'xiangyang', 'xianning',
                 'xiantao', 'xianyang', 'xiaogan', 'xilinguole', 'xingan', 'xingtai', 'xn', 'xinxiang', 'xinyang',
                 'xinyu', 'xinzhou', 'xishuangbanna', 'xuancheng', 'xuchang', 'xuzhou', 'yantai', 'jxyichun', 'sxyulin',
                 'yaan', 'yanan', 'yanbian', 'yancheng', 'yangjiang', 'yangquan', 'yangzhou', 'yibin', 'yichang',
                 'yili', 'yc', 'yingkou', 'yingtan', 'yiwu', 'yiyang', 'yongzhou', 'yueyang', 'gxyulin', 'yuncheng',
                 'yunfu', 'yushu', 'yuxi', 'zz', 'zibo', 'zaozhuang', 'zhangjiajie', 'zhangjiakou', 'zhangye',
                 'zhangzhou', 'zhanjiang', 'zhaoqing', 'zhaotong', 'zhenjiang', 'zhongshan', 'zhongwei', 'zhoukou',
                 'zhoushan', 'zhuhai', 'zhumadian', 'zhuzhou', 'zigong', 'ziyang', 'zunyi', 'quanguo']
        return codes

    def ganji_city_codes(self):
        """
        赶集网的城市代码
        :return:
        """
        codes = ['anshan', 'anyang', 'anqing', 'ankang', 'akesu', 'anshun', 'aletai', 'alashan', 'aba', 'ali', 'alaer',
                 'aomen', 'bj', 'baoding', 'binzhou', 'baotou', 'baoji', 'benxi', 'bengbu', 'beihai', 'bayannaoer',
                 'baicheng', 'baishan', 'bozhou', 'bazhong', 'baiyin', 'baise', 'bijie', 'bayinguoleng', 'baoshan',
                 'boertala', 'cd', 'cq', 'cs', 'cc', 'changzhou', 'cangzhou', 'chifeng', 'chengde', 'changde',
                 'changzhi', 'chenzhou', 'chuzhou', 'chaohu', 'chaozhou', 'changji', 'chizhou', 'chuxiong', 'chongzuo',
                 'changdu', 'chaoyang', 'changshu', 'cixi', 'dl', 'dg', 'dezhou', 'dongying', 'daqing', 'datong',
                 'dandong', 'danzhou', 'deyang', 'dazhou', 'dali', 'daxinganling', 'dingxi', 'dehong', 'diqing',
                 'diaoyudao', 'eerduosi', 'enshi', 'ezhou', 'fz', 'foshan', 'fushun', 'fuyang', 'fuxin', 'jxfuzhou',
                 'fangchenggang', 'gz', 'gy', 'gl', 'ganzhou', 'guangyuan', 'guangan', 'guigang', 'guyuan', 'gannan',
                 'ganzi', 'guoluo', 'hz', 'huizhou', 'hrb', 'hf', 'nmg', 'hn', 'handan', 'heze', 'hengshui', 'huaian',
                 'hengyang', 'huludao', 'huainan', 'hanzhong', 'huaihua', 'huaibei', 'huanggang', 'huzhou', 'huangshi',
                 'hulunbeier', 'heyuan', 'hebi', 'hegang', 'huangshan', 'honghe', 'hechi', 'hami', 'heihe', 'hezhou',
                 'haixi', 'hetian', 'haibei', 'haidong', 'huangnan', 'jn', 'jining', 'jilin', 'jinzhou', 'jinhua',
                 'jiaxing', 'jiangmen', 'jingzhou', 'jiaozuo', 'jinzhong', 'jiamusi', 'jiujiang', 'jincheng', 'jingmen',
                 'jixi', 'jian', 'jieyang', 'jingdezhen', 'jiyuan', 'jiuquan', 'jinchang', 'jiayuguan', 'jiaozhou',
                 'jimo', 'km', 'kaifeng', 'kashi', 'kelamayi', 'kuerle', 'kezilesu', 'kunshan', 'lz', 'xz', 'langfang',
                 'linyi', 'luoyang', 'liaocheng', 'liuzhou', 'lianyungang', 'linfen', 'luohe', 'liaoyang', 'leshan',
                 'luzhou', 'luan', 'loudi', 'laiwu', 'longyan', 'lvliang', 'lishui', 'liangshan', 'lijiang',
                 'liupanshui', 'liaoyuan', 'laibin', 'lincang', 'longnan', 'linxia', 'linzhi', 'mianyang', 'mudanjiang',
                 'maoming', 'meizhou', 'maanshan', 'meishan', 'nj', 'nb', 'nn', 'nc', 'nantong', 'nanyang', 'nanchong',
                 'neijiang', 'nanping', 'ningde', 'nujiang', 'naqu', 'pingdingshan', 'puyang', 'panjin', 'putian',
                 'panzhihua', 'pingxiang', 'pingliang', 'puer', 'pixian', 'qd', 'qh', 'qinhuangdao', 'quanzhou',
                 'qiqihaer', 'qingyuan', 'qujing', 'quzhou', 'qingyang', 'qitaihe', 'qinzhou', 'qianjiang',
                 'qiandongnan', 'qiannan', 'qianxinan', 'rizhao', 'rikaze', 'sh', 'sz', 'sy', 'sjz', 'su', 'shantou',
                 'shangqiu', 'sanya', 'suqian', 'shaoxing', 'shiyan', 'siping', 'sanmenxia', 'shaoyang', 'shangrao',
                 'suining', 'sanming', 'suihua', 'shihezi', 'ahsuzhou', 'shaoguan', 'songyuan', 'suizhou', 'shanwei',
                 'shuangyashan', 'shuozhou', 'shizuishan', 'shangluo', 'shennongjia', 'shannan', 'shuangliu', 'tj',
                 'ty', 'tangshan', 'taian', 'zjtaizhou', 'jstaizhou', 'tieling', 'tongliao', 'tonghua', 'tianshui',
                 'tongling', 'tongchuan', 'tongren', 'tianmen', 'tacheng', 'tulufan', 'tumushuke', 'wh', 'wx', 'xj',
                 'wei', 'weifang', 'wenzhou', 'wuhu', 'weinan', 'wuhai', 'wuzhou', 'wulanchabu', 'wuwei', 'wenshan',
                 'wuzhong', 'wujiaqu', 'wuzhishan', 'xa', 'xm', 'xn', 'xuzhou', 'xianyang', 'xingtai', 'xiangyang',
                 'xinxiang', 'xiangtan', 'xuchang', 'xinyang', 'xiaogan', 'xinzhou', 'xianning', 'xinyu', 'xuancheng',
                 'xiantao', 'xilinguole', 'xiangxi', 'xingan', 'xishuangbanna', 'xianggang', 'yc', 'yichang', 'yantai',
                 'yangzhou', 'yancheng', 'yingkou', 'yueyang', 'yuncheng', 'sxyulin', 'yibin', 'yangquan', 'yanan',
                 'yiyang', 'yongzhou', 'gxyulin', 'jxyichun', 'yangjiang', 'yanbian', 'yuxi', 'yili', 'yunfu',
                 'hljyichun', 'yaan', 'yingtan', 'yushu', 'yiwu', 'zz', 'zhuhai', 'zibo', 'zhongshan', 'zaozhuang',
                 'zhangjiakou', 'zhuzhou', 'zhenjiang', 'zhoukou', 'zhanjiang', 'zhumadian', 'zhaoqing', 'zigong',
                 'zunyi', 'zhangzhou', 'zhoushan', 'zhangye', 'ziyang', 'zhangjiajie', 'zhaotong', 'zhongwei']

        return codes

    def get_ganji_search_args(self):
        """
        返回赶集网普通类的搜索关键词
        :return:
        """
        args_dict = {'销售': 'shichangyingxiao', '技工工人': 'jigongyibangongren', '行政后勤': 'xingzhenghouqin',
                     '营业员': 'yingyeyuan', '财务': 'caiwushenji', '教师': 'jiaoshi', '保安': 'baoan', '淘宝职位': 'taobao',
                     '销售代表': 'xiaoshoudaibiao', '普工': 'xuetugong', '助理秘书': 'wenmiwenyuan', '收银员': 'shouyinyuan',
                     '会计': 'caikuai', '司机': 'siji', '保洁/清洁工': 'baojie', '快递员': 'kuaidi', '电话销售': 'dianhuaxiaoshou',
                     '操作工': 'caozuogong', '行政专员': 'xingzhengzhuli', '服务员': 'judianfuwuyuan', '美术创意': 'meishusheji',
                     '汽车制造服务': 'qiche', '保姆护工': 'baomu', '仓库管理员': 'cangkuguanli', '销售助理': 'xiaoshouzhuli',
                     '焊工': 'hangong', '人力资源': 'renliziyuan', '客服': 'kefu', '平面设计': 'pingmiansheji',
                     '房产经纪人': 'fdcjingjiren', '小时工': 'xiaoshigong', '美容/美发': 'meirongmeifa', '跟单员': 'gendanyuan',
                     '餐饮/酒店': 'jiudiancanyin', '人事专员': 'renshizhuli', '导购': 'daogou', '市场公关媒介': 'shichanggongguan',
                     '保险': 'baoxianjingjiren', '物业管理': 'wuyeguanlizhiwei'}
        return args_dict

    def get_58_city_code(self):
        """
        获取58网的城市代码
        :return:
        """
        # codes = ['hf', 'wuhu', 'bengbu', 'fy', 'hn', 'anqing', 'suzhou', 'la', 'huaibei', 'chuzhou', 'mas', 'tongling',
        #          'xuancheng', 'bozhou', 'huangshan', 'chizhou', 'ch', 'hexian', 'hq', 'tongcheng', 'ningguo',
        #          'tianchang', 'dongzhi', 'wuweixian', 'fz', 'xm', 'qz', 'pt', 'zhangzhou', 'nd', 'sm', 'np', 'ly',
        #          'wuyishan', 'shishi', 'jinjiangshi', 'nananshi', 'longhai', 'shanghangxian', 'fuanshi', 'fudingshi',
        #          'anxixian', 'yongchunxian', 'yongan', 'zhangpu', 'sz', 'gz', 'dg', 'fs', 'zs', 'zh', 'huizhou', 'jm',
        #          'st', 'zhanjiang', 'zq', 'mm', 'jy', 'mz', 'qingyuan', 'yj', 'sg', 'heyuan', 'yf', 'sw', 'chaozhou',
        #          'taishan', 'yangchun', 'sd', 'huidong', 'boluo', 'haifengxian', 'kaipingshi', 'lufengshi', 'nn',
        #          'liuzhou', 'gl', 'yulin', 'wuzhou', 'bh', 'gg', 'qinzhou', 'baise', 'hc', 'lb', 'hezhou', 'fcg',
        #          'chongzuo', 'guipingqu', 'beiliushi', 'bobaixian', 'cenxi', 'gy', 'zunyi', 'qdn', 'qn', 'lps', 'bijie',
        #          'tr', 'anshun', 'qxn', 'renhuaishi', 'qingzhen', 'lz', 'tianshui', 'by', 'qingyang', 'pl', 'jq',
        #          'zhangye', 'wuwei', 'dx', 'jinchang', 'ln', 'linxia', 'jyg', 'gn', 'dunhuang', 'haikou', 'sanya',
        #          'wzs', 'sansha', 'qh', 'wenchang', 'wanning', 'tunchang', 'qiongzhong', 'lingshui', 'df', 'da', 'cm',
        #          'baoting', 'baish', 'danzhou', 'zz', 'luoyang', 'xx', 'ny', 'xc', 'pds', 'ay', 'jiaozuo', 'sq',
        #          'kaifeng', 'puyang', 'zk', 'xy', 'zmd', 'luohe', 'smx', 'hb', 'jiyuan', 'mg', 'yanling', 'yuzhou',
        #          'changge', 'lingbaoshi', 'qixianqu', 'ruzhou', 'xiangchengshi', 'yanshiqu', 'changyuan', 'huaxian',
        #          'linzhou', 'qinyang', 'mengzhou', 'wenxian', 'weishixian', 'lankaoxian', 'tongxuxian', 'lyxinan',
        #          'yichuan', 'mengjinqu', 'lyyiyang', 'wugang', 'yongcheng', 'suixian', 'luyi', 'yingchixian', 'shenqiu',
        #          'taikang', 'shangshui', 'qixianq', 'junxian', 'fanxian', 'gushixian', 'huaibinxian', 'dengzhou',
        #          'xinye', 'hrb', 'dq', 'qqhr', 'mdj', 'suihua', 'jms', 'jixi', 'sys', 'hegang', 'heihe', 'yich', 'qth',
        #          'dxal', 'shanda', 'shzhaodong', 'zhaozhou', 'wh', 'yc', 'xf', 'jingzhou', 'shiyan', 'hshi', 'xiaogan',
        #          'hg', 'es', 'jingmen', 'xianning', 'ez', 'suizhou', 'qianjiang', 'tm', 'xiantao', 'snj', 'yidou',
        #          'hanchuan', 'zaoyang', 'wuxueshi', 'zhongxiangshi', 'jingshanxian', 'shayangxian', 'songzi',
        #          'guangshuishi', 'chibishi', 'laohekou', 'gucheng', 'yichengshi', 'nanzhang', 'yunmeng', 'anlu', 'dawu',
        #          'xiaochang', 'dangyang', 'zhijiang', 'jiayuxian', 'suixia', 'cs', 'zhuzhou', 'yiyang', 'changde', 'hy',
        #          'xiangtan', 'yy', 'chenzhou', 'shaoyang', 'hh', 'yongzhou', 'ld', 'xiangxi', 'zjj', 'liling', 'lixian',
        #          'czguiyang', 'zixing', 'yongxing', 'changningshi', 'qidongxian', 'hengdong', 'lengshuijiangshi',
        #          'lianyuanshi', 'shuangfengxian', 'shaoyangxian', 'shaodongxian', 'yuanjiangs', 'nanxian', 'qiyang',
        #          'xiangyin', 'huarong', 'cilixian', 'zzyouxian', 'sjz', 'bd', 'ts', 'lf', 'hd', 'qhd', 'cangzhou', 'xt',
        #          'hs', 'zjk', 'chengde', 'dingzhou', 'gt', 'zhangbei', 'zx', 'zd', 'qianan', 'renqiu', 'sanhe', 'wuan',
        #          'xionganxinqu', 'lfyanjiao', 'zhuozhou', 'hejian', 'huanghua', 'cangxian', 'cixian', 'shexian',
        #          'bazhou', 'xianghe', 'lfguan', 'zunhua', 'qianxixian', 'yutianxian', 'luannanxian', 'shaheshi', 'su',
        #          'nj', 'wx', 'cz', 'xz', 'nt', 'yz', 'yancheng', 'ha', 'lyg', 'taizhou', 'suqian', 'zj', 'shuyang',
        #          'dafeng', 'rugao', 'qidong', 'liyang', 'haimen', 'donghai', 'yangzhong', 'xinghuashi', 'xinyishi',
        #          'taixing', 'rudong', 'pizhou', 'xzpeixian', 'jingjiang', 'jianhu', 'haian', 'dongtai', 'danyang',
        #          'baoyingx', 'guannan', 'guanyun', 'jiangyan', 'jintan', 'szkunshan', 'sihong', 'siyang', 'jurong',
        #          'sheyang', 'funingxian', 'xiangshui', 'xuyi', 'jinhu', 'nc', 'ganzhou', 'jj', 'yichun', 'ja', 'sr',
        #          'px', 'fuzhou', 'jdz', 'xinyu', 'yingtan', 'yxx', 'lepingshi', 'jinxian', 'fenyi', 'fengchengshi',
        #          'zhangshu', 'gaoan', 'yujiang', 'nanchengx', 'fuliangxian', 'cc', 'jl', 'sp', 'yanbian', 'songyuan',
        #          'bc', 'th', 'baishan', 'liaoyuan', 'gongzhuling', 'meihekou', 'fuyuxian', 'changlingxian', 'huadian',
        #          'panshi', 'lishu', 'sy', 'dl', 'as', 'jinzhou', 'fushun', 'yk', 'pj', 'cy', 'dandong', 'liaoyang',
        #          'benxi', 'hld', 'tl', 'fx', 'pld', 'wfd', 'dengta', 'fengcheng', 'beipiao', 'kaiyuan', 'yinchuan',
        #          'wuzhong', 'szs', 'zw', 'guyuan', 'hu', 'bt', 'chifeng', 'erds', 'tongliao', 'hlbe', 'bycem', 'wlcb',
        #          'xl', 'xam', 'wuhai', 'alsm', 'hlr', 'xn', 'hx', 'haibei', 'guoluo', 'haidong', 'huangnan', 'ys',
        #          'hainan', 'geermushi', 'qd', 'jn', 'yt', 'wf', 'linyi', 'zb', 'jining', 'ta', 'lc', 'weihai',
        #          'zaozhuang', 'dz', 'rizhao', 'dy', 'heze', 'bz', 'lw', 'zhangqiu', 'kl', 'zc', 'shouguang', 'longkou',
        #          'caoxian', 'shanxian', 'feicheng', 'gaomi', 'guangrao', 'huantaixian', 'juxian', 'laizhou', 'penglai',
        #          'qingzhou', 'rongcheng', 'rushan', 'tengzhou', 'xintai', 'zhaoyuan', 'zoucheng', 'zouping', 'linqing',
        #          'chiping', 'hzyc', 'boxing', 'dongming', 'juye', 'wudi', 'qihe', 'weishan', 'yuchengshi', 'linyixianq',
        #          'leling', 'laiyang', 'ningjin', 'gaotang', 'shenxian', 'yanggu', 'guanxian', 'pingyi', 'tancheng',
        #          'yiyuanxian', 'wenshang', 'liangshanx', 'lijin', 'yinanxian', 'qixia', 'ningyang', 'dongping',
        #          'changyishi', 'anqiu', 'changle', 'linqu', 'juancheng', 'ty', 'linfen', 'dt', 'yuncheng', 'jz',
        #          'changzhi', 'jincheng', 'yq', 'lvliang', 'xinzhou', 'shuozhou', 'linyixian', 'qingxu', 'liulin',
        #          'gaoping', 'zezhou', 'xiangyuanxian', 'xiaoyi', 'xa', 'xianyang', 'baoji', 'wn', 'hanzhong', 'yl',
        #          'yanan', 'ankang', 'sl', 'tc', 'shenmu', 'hancheng', 'fugu', 'jingbian', 'dingbian', 'cd', 'mianyang',
        #          'deyang', 'nanchong', 'yb', 'zg', 'ls', 'luzhou', 'dazhou', 'scnj', 'suining', 'panzhihua', 'ms', 'ga',
        #          'zy', 'liangshan', 'guangyuan', 'ya', 'bazhong', 'ab', 'ganzi', 'anyuexian', 'guanghanshi',
        #          'jianyangshi', 'renshouxian', 'shehongxian', 'dazu', 'xuanhan', 'qux', 'changningx', 'xj', 'changji',
        #          'bygl', 'yili', 'aks', 'ks', 'hami', 'klmy', 'betl', 'tlf', 'ht', 'shz', 'kzls', 'ale', 'wjq', 'tmsk',
        #          'kel', 'alt', 'tac', 'lasa', 'rkz', 'sn', 'linzhi', 'changdu', 'nq', 'al', 'rituxian', 'gaizexian',
        #          'km', 'qj', 'dali', 'honghe', 'yx', 'lj', 'ws', 'cx', 'bn', 'zt', 'dh', 'pe', 'bs', 'lincang',
        #          'diqing', 'nujiang', 'milexian', 'anningshi', 'xuanwushi', 'hz', 'nb', 'wz', 'jh', 'jx', 'tz', 'sx',
        #          'huzhou', 'lishui', 'quzhou', 'zhoushan', 'yueqingcity', 'ruiancity', 'yiwu', 'yuyao', 'zhuji',
        #          'xiangshanxian', 'wenling', 'tongxiang', 'cixi', 'changxing', 'jiashanx', 'haining', 'deqing',
        #          'dongyang', 'anji', 'cangnanxian', 'linhai', 'yongkang', 'yuhuan', 'pinghushi', 'haiyan', 'wuyix',
        #          'shengzhou', 'xinchang', 'jiangshanshi', 'pingyangxian', 'hk', 'am', 'tw', 'quanguo', 'cn',
        #          'gllosangeles', 'glsanfrancisco', 'glnewyork', 'gltoronto', 'glvancouver', 'glgreaterlondon',
        #          'glmoscow', 'glseoul', 'gltokyo', 'glsingapore', 'glbangkok', 'glchiangmai', 'gldubai', 'glauckland',
        #          'glsydney', 'glmelbourne', 'city']
        # return codes
        return ['changningx', 'gaizexian']

    def get_chinahr_city_code(self):
        """
        获取中华英才网的城市代码
        :return:
        """

        codes = ['bj', 'sh', 'tj', 'cq', 'hf', 'wuhu', 'bengbu', 'fy', 'hn', 'anqing', 'suzhou', 'la', 'huaibei',
                 'chuzhou', 'mas', 'tongling', 'xuancheng', 'bozhou', 'huangshan', 'chizhou', 'ch', 'hexian', 'hq',
                 'tongcheng', 'ningguo', 'tianchang', 'dongzhi', 'wuweixian', 'fz', 'xm', 'qz', 'pt', 'zhangzhou', 'nd',
                 'sm', 'np', 'ly', 'wuyishan', 'shishi', 'jinjiangshi', 'nananshi', 'longhai', 'shanghangxian',
                 'fuanshi', 'fudingshi', 'anxixian', 'yongchunxian', 'yongan', 'zhangpu', 'sz', 'gz', 'dg', 'fs', 'zs',
                 'zh', 'huizhou', 'jm', 'st', 'zhanjiang', 'zq', 'mm', 'jy', 'mz', 'qingyuan', 'yj', 'sg', 'heyuan',
                 'yf', 'sw', 'chaozhou', 'taishan', 'yangchun', 'sd', 'huidong', 'boluo', 'haifengxian', 'kaipingshi',
                 'lufengshi', 'nn', 'liuzhou', 'gl', 'yulin', 'wuzhou', 'bh', 'gg', 'qinzhou', 'baise', 'hc', 'lb',
                 'hezhou', 'fcg', 'chongzuo', 'guipingqu', 'beiliushi', 'bobaixian', 'cenxi', 'gy', 'zunyi', 'qdn',
                 'qn', 'lps', 'bijie', 'tr', 'anshun', 'qxn', 'renhuaishi', 'qingzhen', 'lz', 'tianshui', 'by',
                 'qingyang', 'pl', 'jq', 'zhangye', 'wuwei', 'dx', 'jinchang', 'ln', 'linxia', 'jyg', 'gn', 'dunhuang',
                 'haikou', 'sanya', 'wzs', 'sansha', 'qh', 'wenchang', 'wanning', 'tunchang', 'qiongzhong', 'lingshui',
                 'df', 'da', 'cm', 'baoting', 'baish', 'danzhou', 'zz', 'luoyang', 'xx', 'ny', 'xc', 'pds', 'ay',
                 'jiaozuo', 'sq', 'kaifeng', 'puyang', 'zk', 'xy', 'zmd', 'luohe', 'smx', 'hb', 'jiyuan', 'mg',
                 'yanling', 'yuzhou', 'changge', 'lingbaoshi', 'qixianqu', 'ruzhou', 'xiangchengshi', 'yanshiqu',
                 'changyuan', 'huaxian', 'linzhou', 'qinyang', 'mengzhou', 'wenxian', 'weishixian', 'lankaoxian',
                 'tongxuxian', 'lyxinan', 'yichuan', 'mengjinqu', 'lyyiyang', 'wugang', 'yongcheng', 'suixian', 'luyi',
                 'yingchixian', 'shenqiu', 'taikang', 'shangshui', 'qixianq', 'junxian', 'fanxian', 'gushixian',
                 'huaibinxian', 'dengzhou', 'xinye', 'hrb', 'dq', 'qqhr', 'mdj', 'suihua', 'jms', 'jixi', 'sys',
                 'hegang', 'heihe', 'yich', 'qth', 'dxal', 'shanda', 'shzhaodong', 'zhaozhou', 'wh', 'yc', 'xf',
                 'jingzhou', 'shiyan', 'hshi', 'xiaogan', 'hg', 'es', 'jingmen', 'xianning', 'ez', 'suizhou',
                 'qianjiang', 'tm', 'xiantao', 'snj', 'yidou', 'hanchuan', 'zaoyang', 'wuxueshi', 'zhongxiangshi',
                 'jingshanxian', 'shayangxian', 'songzi', 'guangshuishi', 'chibishi', 'laohekou', 'gucheng',
                 'yichengshi', 'nanzhang', 'yunmeng', 'anlu', 'dawu', 'xiaochang', 'dangyang', 'zhijiang', 'jiayuxian',
                 'suixia', 'cs', 'zhuzhou', 'yiyang', 'changde', 'hy', 'xiangtan', 'yy', 'chenzhou', 'shaoyang', 'hh',
                 'yongzhou', 'ld', 'xiangxi', 'zjj', 'liling', 'lixian', 'czguiyang', 'zixing', 'yongxing',
                 'changningshi', 'qidongxian', 'hengdong', 'lengshuijiangshi', 'lianyuanshi', 'shuangfengxian',
                 'shaoyangxian', 'shaodongxian', 'yuanjiangs', 'nanxian', 'qiyang', 'xiangyin', 'huarong', 'cilixian',
                 'zzyouxian', 'sjz', 'bd', 'ts', 'lf', 'hd', 'qhd', 'cangzhou', 'xt', 'hs', 'zjk', 'chengde',
                 'dingzhou', 'gt', 'zhangbei', 'zx', 'zd', 'qianan', 'renqiu', 'sanhe', 'wuan', 'xionganxinqu',
                 'lfyanjiao', 'zhuozhou', 'hejian', 'huanghua', 'cangxian', 'cixian', 'shexian', 'bazhou', 'xianghe',
                 'lfguan', 'zunhua', 'qianxixian', 'yutianxian', 'luannanxian', 'shaheshi', 'su', 'nj', 'wx', 'cz',
                 'xz', 'nt', 'yz', 'yancheng', 'ha', 'lyg', 'taizhou', 'suqian', 'zj', 'shuyang', 'dafeng', 'rugao',
                 'qidong', 'liyang', 'haimen', 'donghai', 'yangzhong', 'xinghuashi', 'xinyishi', 'taixing', 'rudong',
                 'pizhou', 'xzpeixian', 'jingjiang', 'jianhu', 'haian', 'dongtai', 'danyang', 'baoyingx', 'guannan',
                 'guanyun', 'jiangyan', 'jintan', 'szkunshan', 'sihong', 'siyang', 'jurong', 'sheyang', 'funingxian',
                 'xiangshui', 'xuyi', 'jinhu', 'nc', 'ganzhou', 'jj', 'yichun', 'ja', 'sr', 'px', 'fuzhou', 'jdz',
                 'xinyu', 'yingtan', 'yxx', 'lepingshi', 'jinxian', 'fenyi', 'fengchengshi', 'zhangshu', 'gaoan',
                 'yujiang', 'nanchengx', 'fuliangxian', 'cc', 'jl', 'sp', 'yanbian', 'songyuan', 'bc', 'th', 'baishan',
                 'liaoyuan', 'gongzhuling', 'meihekou', 'fuyuxian', 'changlingxian', 'huadian', 'panshi', 'lishu', 'sy',
                 'dl', 'as', 'jinzhou', 'fushun', 'yk', 'pj', 'cy', 'dandong', 'liaoyang', 'benxi', 'hld', 'tl', 'fx',
                 'pld', 'wfd', 'dengta', 'fengcheng', 'beipiao', 'kaiyuan', 'yinchuan', 'wuzhong', 'szs', 'zw',
                 'guyuan', 'hu', 'bt', 'chifeng', 'erds', 'tongliao', 'hlbe', 'bycem', 'wlcb', 'xl', 'xam', 'wuhai',
                 'alsm', 'hlr', 'xn', 'hx', 'haibei', 'guoluo', 'haidong', 'huangnan', 'ys', 'hainan', 'geermushi',
                 'qd', 'jn', 'yt', 'wf', 'linyi', 'zb', 'jining', 'ta', 'lc', 'weihai', 'zaozhuang', 'dz', 'rizhao',
                 'dy', 'heze', 'bz', 'lw', 'zhangqiu', 'kl', 'zc', 'shouguang', 'longkou', 'caoxian', 'shanxian',
                 'feicheng', 'gaomi', 'guangrao', 'huantaixian', 'juxian', 'laizhou', 'penglai', 'qingzhou',
                 'rongcheng', 'rushan', 'tengzhou', 'xintai', 'zhaoyuan', 'zoucheng', 'zouping', 'linqing', 'chiping',
                 'hzyc', 'boxing', 'dongming', 'juye', 'wudi', 'qihe', 'weishan', 'yuchengshi', 'linyixianq', 'leling',
                 'laiyang', 'ningjin', 'gaotang', 'shenxian', 'yanggu', 'guanxian', 'pingyi', 'tancheng', 'yiyuanxian',
                 'wenshang', 'liangshanx', 'lijin', 'yinanxian', 'qixia', 'ningyang', 'dongping', 'changyishi', 'anqiu',
                 'changle', 'linqu', 'juancheng', 'ty', 'linfen', 'dt', 'yuncheng', 'jz', 'changzhi', 'jincheng', 'yq',
                 'lvliang', 'xinzhou', 'shuozhou', 'linyixian', 'qingxu', 'liulin', 'gaoping', 'zezhou',
                 'xiangyuanxian', 'xiaoyi', 'xa', 'xianyang', 'baoji', 'wn', 'hanzhong', 'yl', 'yanan', 'ankang', 'sl',
                 'tc', 'shenmu', 'hancheng', 'fugu', 'jingbian', 'dingbian', 'cd', 'mianyang', 'deyang', 'nanchong',
                 'yb', 'zg', 'ls', 'luzhou', 'dazhou', 'scnj', 'suining', 'panzhihua', 'ms', 'ga', 'zy', 'liangshan',
                 'guangyuan', 'ya', 'bazhong', 'ab', 'ganzi', 'anyuexian', 'guanghanshi', 'jianyangshi', 'renshouxian',
                 'shehongxian', 'dazu', 'xuanhan', 'qux', 'changningx', 'xj', 'changji', 'bygl', 'yili', 'aks', 'ks',
                 'hami', 'klmy', 'betl', 'tlf', 'ht', 'shz', 'kzls', 'ale', 'wjq', 'tmsk', 'kel', 'alt', 'tac', 'lasa',
                 'rkz', 'sn', 'linzhi', 'changdu', 'nq', 'al', 'rituxian', 'gaizexian', 'km', 'qj', 'dali', 'honghe',
                 'yx', 'lj', 'ws', 'cx', 'bn', 'zt', 'dh', 'pe', 'bs', 'lincang', 'diqing', 'nujiang', 'milexian',
                 'anningshi', 'xuanwushi', 'hz', 'nb', 'wz', 'jh', 'jx', 'tz', 'sx', 'huzhou', 'lishui', 'quzhou',
                 'zhoushan', 'yueqingcity', 'ruiancity', 'yiwu', 'yuyao', 'zhuji', 'xiangshanxian', 'wenling',
                 'tongxiang', 'cixi', 'changxing', 'jiashanx', 'haining', 'deqing', 'dongyang', 'anji', 'cangnanxian',
                 'linhai', 'yongkang', 'yuhuan', 'pinghushi', 'haiyan', 'wuyix', 'shengzhou', 'xinchang',
                 'jiangshanshi', 'pingyangxian', 'hk', 'am', 'tw']
        return codes

    def get_gzc_city_code(self):
        """
        获取工作虫网站的城市代码
        :return:
        """
        codes = ['bj', 'sh', 'gz', 'sz', 'tj', 'cq', 'wh', 'cd', 'hz', 'zz', 'jn', 'xa', 'dl', 'fz', 'nn', 'dg', 'xm',
                 'wx', 'qd', 'ty', 'sjz', 'nj', 'hf', 'su', 'cc', 'cs', 'hrb', 'sy', 'jincheng', 'hu', 'tangshan',
                 'qinhuangdao', 'handan', 'xingtai', 'zjk', 'chengde', 'cangzhou', 'langfang', 'hengshui', 'datong',
                 'changzhi', 'jingzhong', 'yuncheng', 'linfen', 'bd', 'cz', 'xz', 'nt', 'nb', 'wz', 'yz', 'jh', 'fs',
                 'zs', 'zh', 'huizhou', 'qz', 'nc', 'gy', 'mianyang', 'km', 'luoyang', 'xx', 'ny', 'linyi', 'dz', 'wf',
                 'lz', 'sx', 'tz', 'jx', 'jm', 'st', 'zhanjiang', 'haikou', 'sanya', 'liuzhou', 'gl', 'deyang', 'lasa',
                 'xc', 'ay', 'jiaozuo', 'sq', 'kaifeng', 'zk', 'yt', 'zb', 'jining', 'dy', 'wuhu', 'bengbu', 'fy', 'yc',
                 'xy', 'yy', 'changde', 'hy', 'xj', 'xn', 'yinchuan', 'bt', 'chifeng', 'pingxiang']
        return codes

    def get_baidu_city_code(self):
        """
        获取百度百聘的城市代码
        :return:
        """
        codes = ['北京', '天津', '太原', '大同', '呼和浩特', '包头', '石家庄', '廊坊', '邯郸',
                 '上海', '杭州', '宁波', '温州', '南京', '济南', '青岛', '台州', '嘉兴', '金华', '绍兴', '苏州', '无锡', '常州', '南通', '扬州', '徐州',
                 '连云港', '福州', '厦门', '泉州', '烟台', '潍坊', '临沂', '淄博', '菏泽', '威海', '合肥', '马鞍山', '芜湖',
                 '广州', '深圳', '海口', '三亚', '南宁', '桂林', '玉林', '百色',
                 '武汉', '南昌', '郑州', '长沙', '九江', '赣州', '株洲', '常德', '宜昌', '十堰', '荆州', '洛阳', '南阳', '新乡', '安阳',
                 '重庆', '成都', '绵阳', '贵阳', '遵义', '昆明', '大理', '拉萨',
                 '西安', '宝鸡', '西宁', '银川', '兰州', '咸阳', '天水', '乌鲁木齐', '昌吉', '固原',
                 '沈阳', '大连', '哈尔滨', '长春', '吉林', '朝阳', '锦州', '四平', '大庆', '牡丹江', ]

        return codes

    def get_zhilian_city_code(self):
        """
        获取智联招聘的城市代码
        :return:
        """
        return ['530', '538', '763', '531', '801', '653', '736', '600', '613', '635', '702', '703', '639',
                '599', '854', '719', '749', '551', '622', '636', '654', '681', '682', '565', '664', '773']

    def handle_time(self, timestamp):
        """
        处理时间格式，返回一个日期格式
        :param timestamp:
        :return:
        """
        date = str(timestamp)
        while date.endswith('0'):
            date = date[:-1]
        new_date = int(date)
        temp_time = time.localtime(new_date)
        # format_date = time.strftime("%Y-%m-%d %H:%M:%S", temp_time)
        format_date = time.strftime("%Y-%m-%d", temp_time)
        return format_date

    def get_proxy(self):
        """
        获取代理
        :return:
        """
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            return proxy

    def get_session(self, url_name, url=None):
        """
        获取session对象
        :param url_name: url别名
        :param url: 请求的url
        :return:
        """
        session = requests.session()
        if not url:
            if 'parser_baidu' == url_name:
                session.get(self.BAIDU_COOKIE_URL, headers=self.header, timeout=(3, 7))
            elif 'parser_baidu_jianzhi' == url_name:
                session.get(self.BAIDU_COOKIE_JIANZHI_URL, headers=self.header, timeout=(3, 7))
        else:
            session.get(url, headers=self.header, timeout=(3, 7))
        return session

    def get_baidu_token(self, token_url, url_name):
        """
        获取百度百聘的api所需的token数据
        :param token_url: 获取token的url
        :param url_name: url别名
        :return:
        """
        if token_url:
            session = self.get_session(url_name)
            req = session.get(token_url, headers=self.header, timeout=(3, 7))
            res = req.content.decode('utf-8')
            session.close()
            if 'parser_baidu' == url_name:
                token = re.findall(r'"nekot"] = "(.*)";', res)[0][::-1]
            elif 'parser_baidu_jianzhi' == url_name:
                token = re.findall(r"zp_pc_nekot = '(.*)';", res)[0][::-1]
            else:
                token = ''
            if token:
                new_token = urllib.parse.quote(token)
                return new_token

    @property
    def get_header(self):
        """
        获取请求头
        :return:
        """
        return self.request_headers()

    @property
    def get_request_urls(self):
        """
        获取所有的待爬取的网址,格式化url的参数
        :return:
        """
        urls = []
        for item in REQEUST_URLS:
            item['type'] = 'parser_' + item['type']
            urls.append(item)
        return urls

    def get_already_crawl_site(self):
        """
        已有的招聘网站域名
        :return:
        """
        sites = []
        for item in REQEUST_URLS:
            temp_url = item.get('url').split('/')
            url = temp_url[2].split('.', 1)[1]
            sites.append(url)

        return sites

    def request_site(self):
        """
        遍历请求所有的url
        :return:
        """

        for urls in self.request_urls:
            url = urls.get('url')
            url_name = urls.get('type')
            domain = url_name.split('_', 1)[1]
            print('正在爬取 %s 网站的数据' % domain)
            # args = urls.get('args')
            # if not args:
            #     args = self.get_args()
            for args in self.search_args:
                proxy = self.get_proxy()
                args_urlencode = urllib.parse.quote(args)
                self.request_url(url, url_name, proxy, args_urlencode, args)

    def get_cookie(self, url, url_name=None, args=None):
        """
        访问对应网页获取cookie
        :param url: 指定网页url
        :param url_name: 目标网址别名
        :param args: 搜索关键词
        :return:
        """
        req = requests.session()
        headers = self.header
        if url_name and 'dajie' in url_name:
            headers.update({
                'referer': 'https://so.dajie.com/job/search?keyword={q}'.format(q=args),
                'dnt': '1',
                'accept-language': 'zh-CN,zh;q=0.9',
            })
            dajie_url = 'https://so.dajie.com/job/search?keyword={q}&from=job&clicktype=blank'.format(q=args)
            req.get(dajie_url, headers=headers, timeout=(3, 7))
        elif url_name and 'chinahr_old' in url_name:
            headers.update({
                'Host': 'www.chinahr.com',
                'Referer': 'http://www.chinahr.com/jobs/',
            })
            req.get(url, headers=headers, timeout=(3, 7))
        else:
            headers.update({
                'Referer': url,
            })
            req.get(url, headers=headers, timeout=(3, 7))
        cookie = req.cookies
        return cookie

    def get_city_codes(self, url_name):
        """
        获取城市代码
        :param url_name: url别名
        :return:
        """
        if 'zhilian' in url_name:
            city_codes = self.get_zhilian_city_code()
        elif 'parser_ganji' == url_name:
            city_codes = self.ganji_city_codes()
        elif 'parser_ganji_it' == url_name:
            city_codes = self.ganji_city_codes()
        elif '58' in url_name:
            city_codes = self.get_58_city_code()
        elif 'parser_chinahr' == url_name:
            city_codes = self.get_chinahr_city_code()
        elif 'gongzuochong' in url_name:
            city_codes = self.get_gzc_city_code()
        elif 'baidu' in url_name:
            city_codes = self.get_baidu_city_code()
        else:
            city_codes = []
        return city_codes

    def get_scheduler(self):
        cls = BlockingScheduler
        return cls()

    def request_url(self, url, url_name, proxy=None, args_urlencode=None, args=None):
        """
        请求对应的网址
        :param url: url
        :param url_name: url别名
        :param proxy: 代理
        :param args_urlencode: 已编码的搜索职位名参数
        :param args: 未编码的搜索职位名参数
        :return:
        """

        market_urls = get_url_redis('market_urls')  # 已爬取的url
        db_target_urls = get_url_redis()  # 所有的url
        if market_urls and db_target_urls and market_urls == db_target_urls:
            print('全部url已请求爬取完毕')
            CRAWL_LOG.info('all target urls request finished')
        else:
            CRAWL_LOG.info('to request target urls')
            # 索引字段
            index = args
            if not args_urlencode:
                args_urlencode = urllib.parse.quote('python')

            # 获取城市代码
            city_codes = self.get_city_codes(url_name)

            # 如果有城市代码
            if city_codes:
                for city_code in city_codes:
                    self.enumerate_request_urls(url, url_name, args, args_urlencode, proxy, index, city_code)
            else:
                self.enumerate_request_urls(url, url_name, args, args_urlencode, proxy, index)

    def enumerate_request_urls(self, url, url_name, args, args_urlencode, proxy, index, city_code=None):
        """
        枚举所有的url
        :param url: 待请求为格式化的url
        :param url_name: url的别名
        :param args: 搜索关键词
        :param args_urlencode: 已编码的搜索关键词
        :param proxy: 代理
        :param index: 索引
        :param city_code: 城市代码，如果为空则表示为全国地区
        :return:
        """

        # 如果数据库内无值，生成值并存入数据库(第一次运行程序)
        if not self.target_urls:

            # 生成所有的目标url
            target_urls = self.generate_reqeust_target_urls(url, url_name, proxy, city_code, args, args_urlencode,
                                                            index, is_generate=True)

            # 保存所有的目标url，这里如果是协程或者多线程，可能会导致页码和真实情况有少量偏移，正常现象
            if target_urls:
                self.target_urls = target_urls
                save_url_redis(target_urls)

            # 开始遍历请求
            self.generate_reqeust_target_urls(url, url_name, proxy, city_code, args, args_urlencode,
                                              index)

        # 如果数据库有值(第二次及之后的运行程序)
        else:
            # 生成所有的目标url
            db_target_urls = get_url_redis()
            page = get_market_page_redis()  # 已爬取的页码
            generate_target_urls = self.generate_reqeust_target_urls(url, url_name, proxy, city_code, args,
                                                                     args_urlencode, index, is_generate=True)
            # 如果上一次爬取时没有生成完成所有的url
            if db_target_urls != generate_target_urls:
                db_target_urls = generate_target_urls

            market_urls = get_url_redis('market_urls')  # 已爬取的url
            if market_urls == db_target_urls:
                print('全部url已爬取完毕')
            else:
                if market_urls:
                    target_urls = db_target_urls - market_urls  # 未爬取的url
                else:
                    target_urls = db_target_urls
                self.target_urls = target_urls
                save_url_redis(target_urls)  # 重新保存所有的目标url

                # 开始遍历请求
                self.generate_reqeust_target_urls(url, url_name, proxy, city_code, args, args_urlencode, index,
                                                  page=page)

    def generate_reqeust_invalid_urls(self, url, city_code, url_name, args, args_urlencode, page=None):
        """
        生成无效的url
        :param url: url
        :param city_code: 城市代码
        :param url_name: url别名
        :param args: 搜索关键词
        :param args_urlencode: 已url编码的搜索关键词
        :param page: 页码
        :return:
        """

        invalid_target_urls = set()
        if not page:
            page = 1

        for i in range(page, END_PAGE):
            end_url = self.distribute_urls(url, url_name, city_code, args, args_urlencode, i, set())
            invalid_target_urls.update(end_url)

        # print('invalid_target_urls', invalid_target_urls)
        print('删除无效的url')
        return invalid_target_urls

    def generate_reqeust_target_urls(self, url, url_name, proxy, city_code, args, args_urlencode, index,
                                     is_generate=False, page=None):
        """
        生成所有的url和遍历请求
        :param url: 待爬取的url
        :param url_name: url的别名
        :param proxy: 代理
        :param city_code: 城市代码
        :param args: 关键词
        :param args_urlencode: 已url编码好的关键词
        :param index: 索引
        :param is_generate: 是否是生成所有的目标url
        :param page: 页码
        :return: 返回所有的待爬取的目标url
        """

        # 最后的目标url
        if is_generate:
            target_urls = set()
        else:
            target_urls = self.target_urls
        if not page:
            page = 1
        # for i in range(1, 2):  # 作测试使用
        for i in range(page, END_PAGE):  # 页码总数随意，但一般情况下每个网站搜出来的职位最多就100页左右
            # 当标志位为真，即标志该站某一页已经没有数据，该网站停止爬取，终止循环
            if self.flag:
                # 为其他网站的url设置初始值
                self.flag = False
                print('网站 %s 已无 %s 相关数据，已切换到其他网站继续爬取.....' % (url_name, index))

                # 删除对应的无效url
                invalid_url = self.generate_reqeust_invalid_urls(url, city_code, url_name, args, args_urlencode, page)
                if invalid_url:
                    self.invalid_urls.update(invalid_url)
                    self.target_urls -= self.invalid_urls
                    target_urls = self.target_urls
                    save_url_redis(self.target_urls)
                break

            temp_urls = self.distribute_urls(url, url_name, city_code, args, args_urlencode, i, target_urls)
            target_urls.update(temp_urls)

            # 请求
            if not is_generate:
                try:
                    self.request_format_site(target_urls, url_name, proxy, args_urlencode, i, index)
                    save_market_page_redis(i)  # 保存已爬取的页码
                except BaseException as e:
                    print(e)
                    CRAWL_LOG.error('request exception occurred:%s' % e)
                    save_redis(self.jobs)

        if is_generate:
            return target_urls

    def distribute_urls(self, url, url_name, city_code, args, args_urlencode, i, target_urls):
        """
        分发生成url
        :param url: url
        :param url_name: url别名
        :param city_code: 城市代码
        :param args: 搜索关键词
        :param args_urlencode: 已url编码的搜索关键词
        :param i: 页码
        :param target_urls: 目标url
        :return:
        """
        if 'zhilian' in url_name:
            i *= 90
            temp_url = url.format(c=city_code, p=i, q=args_urlencode)
            target_urls.add(temp_url)

        elif 'parser_ganji' == url_name:
            ganji_args = self.get_ganji_search_args()
            if args in ganji_args:
                args_value = ganji_args.get(args)
                temp_url = url.format(c=city_code, p=i, q=args_value)
                target_urls.add(temp_url)

        elif 'parser_ganji_it' == url_name:
            i = (i - 1) * 32
            temp_url = url.format(c=city_code, p=i, q=args_urlencode)
            target_urls.add(temp_url)

        elif '58' in url_name:
            temp_url = url.format(c=city_code, p=i, q=args_urlencode)
            target_urls.add(temp_url)

        elif 'parser_chinahr' == url_name:
            temp_url = url.format(c=city_code, p=i, q=args_urlencode)
            target_urls.add(temp_url)

        elif 'gongzuochong' in url_name:
            temp_url = url.format(c=city_code, p=i, q=args_urlencode)
            target_urls.add(temp_url)

        elif 'baidu' in url_name:
            city_code1 = urllib.parse.quote(city_code)
            city_code2 = urllib.parse.quote(city_code1)
            if 'parser_baidu' == url_name:
                # 百度百聘的api把城市参数做了两层url编码
                token_url = 'https://zhaopin.baidu.com/quanzhi?city={c}&query={q}'.format(c=city_code1,
                                                                                          q=args_urlencode)

            elif 'parser_baidu_jianzhi' == url_name:
                # 百度百聘的api把城市参数做了两层url编码
                token_url = 'https://zhaopin.baidu.com/jianzhi?city={c}&query={q}'.format(c=city_code1,
                                                                                          q=args_urlencode)
            else:
                token_url = ''
            token = self.get_baidu_token(token_url, url_name)
            if i == 1:
                i -= 1
            i *= 20
            temp_url = url.format(c=city_code2, p=i, q=args_urlencode, token=token)
            target_urls.add(temp_url)

        elif 'yjs' in url_name:
            i -= 1
            if i < 0:
                i = 0
            i *= 10
            temp_url = url.format(p=i, q=args_urlencode)
            target_urls.add(temp_url)

        elif 'jobcn' in url_name:
            target_urls.add(url)

        elif 'parser_jiaoshizhaopin' == url_name:
            args = urllib.parse.quote(args, encoding='gb2312')
            temp_url = url.format(p=i, q=args)
            target_urls.add(temp_url)

        elif 'shuobo' in url_name and i == 1:
            temp_url = 'http://www.51shuobo.com/s/result/kt1_kw-{q}/'.format(q=args_urlencode)
            target_urls.add(temp_url)

        elif 'liepin' in url_name:
            i -= 1
            temp_url = url.format(p=i, q=args_urlencode)
            target_urls.add(temp_url)

        elif 'job1001' in url_name:
            i -= 1
            temp_url = url.format(p=i, q=args_urlencode)
            target_urls.add(temp_url)

        elif 'linkin' in url_name:
            city = '中国'
            c = urllib.parse.quote(city)
            if i == 1:
                i = 0
            i *= 25
            temp_url = url.format(c=c, p=i, q=args_urlencode)
            target_urls.add(temp_url)

        elif 'telecomhr' in url_name:
            args = urllib.parse.quote(args, encoding='gb2312')
            temp_url = url.format(p=i, q=args)
            target_urls.add(temp_url)
        else:
            temp_url = url.format(p=i, q=args_urlencode)
            target_urls.add(temp_url)
        return target_urls

    def request_format_site(self, target_urls, url_name, proxy, args_urlencode, i, index):
        """
        请求格式化好的所有url
        :param target_urls: 所有目标url,类型为集合
        :param url_name: url别名
        :param proxy: 代理
        :param args_urlencode: url编码后后的搜索关键词
        :param i: 页码
        :param index: 搜索关键词
        :return:
        """
        # 遍历请求
        # print(target_urls)

        # 获取最新待爬取的url

        for target_url in target_urls:
            try:
                self.request_format_url(target_url, url_name, proxy, args_urlencode, i, index)

            # except requests.exceptions.ContentDecodingError:
            #     time.sleep(1)
            # except requests.exceptions.ConnectTimeout:
            #     time.sleep(1)
            # except requests.exceptions.ReadTimeout:
            #     time.sleep(1)
            # except urllib3.exceptions.ReadTimeoutError:
            #     time.sleep(1)
            # except urllib3.exceptions.ConnectTimeoutError:
            #     time.sleep(1)
            # except urllib3.exceptions.MaxRetryError:
            #     time.sleep(1)
            # except urllib3.exceptions.ProtocolError:
            #     time.sleep(1)
            except BaseException:
                CRAWL_LOG.error('request exception occurred')
                time.sleep(3)
                proxy = None
                if self.proxy_list:
                    if proxy in self.proxy_list:
                        self.proxy_list.remove(proxy)
                    proxy = self.get_proxy()
                try:
                    self.request_format_url(target_url, url_name, proxy, args_urlencode, i, index)

                except BaseException as e:
                    print(e)
                    save_redis(self.jobs)
                    CRAWL_LOG.error('request exception occurred:%s' % e)

    def request_format_url(self, url, url_name, proxy, args_urlencode, i, index):
        """
        请求已经格式化好的url
        :param url: 格式化好的url
        :param url_name: url别名
        :param proxy: 代理
        :param args_urlencode: 已编码的搜索职位名参数
        :param i: 页码
        :param index: 搜索的关键词
        :return:
        """
        # 中华英才网相关
        chinahr_url = 'http://www.chinahr.com/jobs/'

        # 卓聘相关
        zhuopin_data = {
            'CID': '',
            'Q': args_urlencode,
            'pageIndex': i,
            'pageSize': '20',
            'ReferrerType': '',
            'qTitle': '1',
            'JobLocation': '',
            'CompanyIndustry': '',
            'JobType': '',
            'AnnualSalaryMin': '-1',
            'AnnualSalaryMax': '-1',
            'CompanyType': '',
            'ReleaseDate': '',
            'GID': '1e597c4a-7bae-483e-9807-41a583778abc'
        }

        # 拉钩相关
        lagou_data = {
            'first': 'false',
            'pn': i,
            'kd': args_urlencode,
        }

        lagou_start_url = 'https://www.lagou.com/jobs/list_{args}?px=default&city=%E5%85%A8%E5%9B%BD'.format(
            args=args_urlencode)

        # 大街网相关
        dajie_start_url = 'https://so.dajie.com/job/search?keyword={args}'.format(args=args_urlencode)

        # 中国人才热线相关
        cjol_data = {
            'KeywordType': '3',
            'KeyWord': args_urlencode,
            'SearchType': '3',
            'ListType': '2',
            'page': i
        }

        # 卓聘人才网
        jobcn_data = {
            'p.querySwitch': '0',
            'p.searchSource': 'default',
            'p.keyword': args_urlencode,
            'p.keyword2': '',
            'p.keywordType': '0',
            'p.pageNo': i,
            'p.pageSize': '40',
            'p.sortBy': 'postdate',
            'p.statistics': 'false',
            'p.totalRow': '72',
            'p.cachePageNo': i,
            'p.cachePosIds': '3996831,3867032,3854083,4025644,200431,4049685,4093100,4049690,3410415,3955832,4073900,4041020,3574331,3574330,4021063,3319026,4022062,4076046,4076044,4065380,4067051,3939390,4082129,3920851,4025383,4046472,4089204,4064692,4061820,4093697,3852019,4087419,4087053,2269732,3933028,4071237,4042056,4063573,4037702,3663255,3145932,3915673,3908465,3776789,4025742,4071540,3095066,4052562,4052555,4052546,4052543,4025179,3741319,3812596,4045056,4033451,4033373,3615871,3782627,4022040,4005016,3727904,3996067,3903386,3903347,2977257,3697238,3992534,3908819,3865892,3795130,3737555',
            'p.cachePosUpddates': '201908111448,201908111448,201908111422,201908111330,201908111319,201908111000,201908110823,201908110711,201908101150,201908101143,201908091725,201908091506,201908091133,201908091133,201908091100,201908091057,201908091020,201908090839,201908090839,201908090839,201908080951,201908080850,201908080823,201908071523,201908070846,201908061025,201908061000,201908050854,201908031518,201908031339,201908011610,201907301006,201907221455,201907171044,201907161443,201907110813,201907071014,201907011744,201906300818,201906211309,201906181016,201906091016,201906091016,201906030906,201905290840,201905240300,201904271038,201904020300,201904020300,201904020300,201904020300,201903290918,201903281543,201903271520,201903150300,201902190300,201902190300,201902101649,201901190854,201901021430,201901010910,201811211054,201811141644,201810311054,201810311054,201810170953,201810150929,201810101042,201810101042,201809130935,201809130935,201808271719',
            'p.jobnature': '15',
            'p.comProperity': '0',
            'p.JobLocationTown': '',
            'p.salary': '-1',
            'p.highSalary': '100000',
            'p.salarySearchType': '1',
            'p.includeNeg': '1',
            'p.inputSalary': '-1',
            'p.workYear1': '-1',
            'p.workYear2': '11',
            'p.degreeId1': '10',
            'p.degreeId2': '70',
            'p.posPostDate': '366',
            'p.otherFlag': '3',
        }

        # 开始请求
        response = None
        try:
            if 'zhuopin' in url_name:
                response = requests.post(url, headers=self.header, data=zhuopin_data, proxies=proxy,
                                         timeout=(3, 7), verify=False)
            elif 'lagou' in url_name:
                cookie = self.get_cookie(lagou_start_url)
                response = requests.post(url, headers=self.header, data=lagou_data, proxies=proxy,
                                         timeout=(3, 7), verify=False, cookies=cookie)
            elif 'dajie' in url_name:

                # 神奇，大街网不能更新header，只能直接设置header,应该有字段顺序关系
                header = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'User-Agent': random.choice(USER_AGENT),
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    'Accept-Encoding': 'gzip, deflate',
                    'Upgrade-Insecure-Requests': '1',
                    'dnt': '1',
                    'x-requested-with': 'XMLHttpRequest',
                    'referer': 'https://so.dajie.com/job/search?keyword={q}&from=job&clicktype=blank'.format(
                        q=args_urlencode)
                }

                cookie = self.get_cookie(dajie_start_url, url_name, args_urlencode)
                response = requests.get(url, headers=header, proxies=proxy, timeout=(3, 7), verify=False,
                                        cookies=cookie)
            elif 'chinahr_old' in url_name:
                cookie = self.get_cookie(chinahr_url, url_name, args_urlencode)
                response = requests.get(url, header=self.header, proxies=proxy, timeout=(3, 7), verify=False,
                                        cookies=cookie)

            elif 'cjol' in url_name:
                header = self.header
                header.update({
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'dnt': '1',
                    'x-requested-with': 'XMLHttpRequest',
                })
                response = requests.post(url, headers=header, proxies=proxy, timeout=(3, 7), verify=False,
                                         data=cjol_data)
            elif 'jobcn' in url_name:
                response = requests.post(url, headers=self.header, proxies=proxy, timeout=(3, 7), verify=False,
                                         data=jobcn_data)
            elif 'doumi' in url_name:
                city_code = self.get_doumi_city_codes()
                # city_code = 'bj'
                doumi_url = self.DOUMI_COOKIE_URL % city_code
                session = self.get_session(url_name, doumi_url)
                response = session.get(url, headers=self.header, proxies=proxy, timeout=(3, 7), verify=False)

            elif 'boss' in url_name:
                header = self.header
                header.update(BOSS_COOKIE)
                response = requests.get(url, headers=header, proxies=proxy, timeout=(3, 7), verify=False)

            else:
                response = requests.get(url, headers=self.header, proxies=proxy, timeout=(3, 7), verify=False)
        except BaseException as e:
            pass

        # 解析网站
        if response:
            if response.status_code == 200:
                # 成功请求一次url就保存一次url
                save_url_redis({url}, 'market_urls')
                html = self.decode_request(response)
                self.parser(html, url_name, url, args_urlencode, index=index)

    def decode_request(self, response):
        """
        解密请求到的结果
        :param response:
        :return:
        """

        # code = response.apparent_encoding
        # html = response.content.decode(code)

        try:
            html = response.content.decode('utf-8')
        except Exception as s:
            # print(s)
            CRAWL_LOG.error('decode response occurred:%s' % s)
            html = response.content.decode('gb2312', 'ignore')

        return html

    def parser(self, html, url_name, url=None, *args, **kwargs):
        """
        分发解析器，根据url别名做分发
        :param url: 网址链接
        :param html: 网址源码
        :param url_name: url别名
        :param args:
        :param kwargs:
        :return:
        """

        func = getattr(self, url_name)
        if func:
            func(html, url_name, url, *args, **kwargs)

    def second_request_parser(self, link, url_name, *args, **kwargs):
        """
        二次请求二级网页并分发解析
        :param link: 二级网页链接
        :param url_name: 网址的别名
        :param args:
        :param kwargs:
        :return:
        """
        time.sleep(1)
        try:
            result = self.second_requetst_parser_body(link, url_name, *args, **kwargs)
            return result
        except BaseException as e:
            CRAWL_LOG.error('second request exception occurred:%s' % e)
            time.sleep(3)
            try:
                result = self.second_requetst_parser_body(link, url_name, *args, **kwargs)
                return result
            except BaseException as s:
                CRAWL_LOG.error('second request exception occurred:%s' % s)

    def second_requetst_parser_body(self, link, url_name, *args, **kwargs):
        """
        第二次请求的请求主体
        :param link: 二次网页的链接
        :param url_name: url别名
        :param args:
        :param kwargs:
        :return:
        """
        proxy = self.get_proxy()
        if 'baidu' in url_name:
            session = self.get_session(url_name)
            response = session.get(url=link, headers=self.header, proxies=proxy, verify=False, timeout=(3, 7))
            session.close()
        else:
            response = requests.get(url=link, headers=self.header, proxies=proxy, verify=False, timeout=(3, 7))
            response.close()
        result = self.decode_request(response)
        if hasattr(self, url_name):
            func = getattr(self, 'second_' + url_name)
            result = func(result, link, *args, **kwargs)
            return result

    def get_format_salary(self, salary, args=None):
        """
        统一工资格式
        :param salary: 待格式化的薪水
        :param args: 单位关键词
        :return:
        """
        if not args:
            args = '/月'
        temp_salary = str(salary)
        if '/月' in temp_salary:
            temp_salary = temp_salary.replace('/月', '')
        if '/年' in temp_salary:
            temp_salary = temp_salary.replace('/年', '')
            if not args:
                args = '/年'
        if '以上' in temp_salary:
            temp_salary = temp_salary.replace('以上', '')
        if '-' in temp_salary:
            min_salary, max_salary = temp_salary.split('-')
            if '万' in max_salary:
                if args and '年' in args:
                    min_salary = float('%.2f' % eval(min_salary)) / 1.2
                    max_salary = float('%.2f' % eval(max_salary.replace('万', ''))) / 1.2
                    args = '/月'
                else:
                    min_salary = float('%.2f' % eval(min_salary)) * 10
                    max_salary = float('%.2f' % eval(max_salary.replace('万', '')))
                    max_salary *= 10
            else:
                min_salary = self.handler_end_salary(min_salary)
                max_salary = self.handler_end_salary(max_salary)
            current_salary = str(min_salary) + '-' + str(max_salary)
            format_salary = '￥' + current_salary + 'k' + args
            return format_salary, current_salary
        elif salary.count('0') == 3:
            current_salary = self.handler_end_salary(temp_salary)
            format_salary = '￥' + current_salary + 'k' + args
            return format_salary, current_salary

        return '', ''

    def handler_end_salary(self, salary):
        """
        拆分处理
        :param salary:
        :return:
        """
        # if salary.count('0') >= 3:
        if salary.isdigit() and int(salary) > 1000 and len(salary) >= 4:
            format_salary = salary[:-3]
            return format_salary

    def parser_kanzhun(self, html, url_name, url=None, *args, **kwargs):
        """
        看准网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        response = etree.HTML(html)
        etree_html = response.xpath('//div[@class="sparrow"]')
        if etree_html:
            for item in etree_html:
                href = item.xpath('./dl/dd/h3/a/@href')[0]
                link = 'https://www.kanzhun.com' + href
                self.second_request_parser(link, url_name, *args, **kwargs)

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_kanzhun(self, html, link=None, *args, **kwargs):
        """
        对看准网二层网页进行抓取
        :param html: 二层网页的源码
        :param link: 二层网页的url
        :return:
        """
        etree_html = etree.HTML(html)
        index = kwargs.get('index')
        company_comment_title = ''
        company_comment_content = ''
        job_evaluate_content = ''
        job_evaluate_title = ''
        job_title = etree_html.xpath('//div[@class="company_profile"]/div/h1/text()')[0].strip()
        job_area = etree_html.xpath('//div[@class="job"]/p[@class="info"]/a/text()')[0]

        job_brief = etree_html.xpath('//div[@class="job-desc_container"]/p[2]/text()')
        company_name = etree_html.xpath('//p[@class="c_name"]/a/text()')[0].split(' ')[0]
        company_type = etree_html.xpath('//div[@class="c_property"]/p/a[1]/text()')[0]
        company_scale = ''.join(etree_html.xpath('//div[@class="c_property"]/p/text()')).strip()
        salary = etree_html.xpath('//div[@class="job"]/p[@class="job_salary"]/text()')
        if salary:
            salary, i_salary = self.get_format_salary(salary[0])
        if job_brief:
            job_brief = job_brief
        company_brief = etree_html.xpath('//div[@class="job-desc_container"]/p[4]/text()')
        if company_brief:
            company_brief = company_brief[0].strip()
        info = etree_html.xpath('//div[@class="job"]/p[@class="info"]/text()')
        edu = info[3].replace('\n', '')
        ex = info[2].replace('\n', '')
        job_property = info[-1].replace('\n', '')
        company_comment_title = etree_html.xpath('//*[@id="j-job-review"]/dl/dd/h2/a/text()')
        company_comment_content = etree_html.xpath('//*[@id="j-job-review"]/dl/dd/p[2]/text()')
        company_comment = ''.join(company_comment_title).strip() + ',' + ''.join(company_comment_content).strip()

        job_evaluate_title = etree_html.xpath('//*[@id="j-job-interview"]/dl/dd/h2/a/text()')
        job_evaluate_content = etree_html.xpath('//p[@class="c_s_result_text mb15"]/text()')
        job_evaluate = ''.join(job_evaluate_title).strip() + ',' + ''.join(job_evaluate_content).strip()

        # print({
        #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '', 'job_property': job_property,
        #     'job_status': '', 'job_area': job_area, 'major': '', 'job_addr': '', 'pub_date': '', 'end_time': '',
        #     'age': '', 'sex': '', 'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
        #     'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': job_evaluate,
        #     'company_name': company_name, 'company_type': company_type, 'company_status': '', 'phone': '',
        #     'driver_license': '', 'company_scale': company_scale, 'company_brief': company_brief, 'contact_person': '',
        #     'company_comment': company_comment
        # })
        self.jobs.append({
            'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '', 'job_property': job_property,
            'job_status': '', 'job_area': job_area, 'major': '', 'job_addr': '', 'pub_date': '', 'end_time': '',
            'age': '', 'sex': '', 'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
            'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': job_evaluate,
            'company_name': company_name, 'company_type': company_type, 'company_status': '', 'phone': '',
            'driver_license': '', 'company_scale': company_scale, 'company_brief': company_brief, 'contact_person': '',
            'company_comment': company_comment
        })

    def parser_boss(self, html, url_name, url=None, *args, **kwargs):
        """
        boss直聘网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[@class="job-primary"]')
        if response:
            for item in response:
                link = 'https://www.zhipin.com' + item.xpath('./div[@class="info-primary"]/h3/a/@href')[0]
                self.second_request_parser(link, url_name, *args, **kwargs)

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_boss(self, html, link=None, *args, **kwargs):
        """
        boss直聘的二级详情页数据
        :param html: 二级网站的源码
        :param link: 二级网站的网址
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        company_status = ''
        job_tags = []
        job_status = etree_html.xpath('//div[@class="job-status"]/text()')
        if job_status:
            job_status = job_status[0]
        job_title = etree_html.xpath(
            '//div[@class="job-primary detail-box"]/div[@class="info-primary"]/div[@class="name"]/h1/text()')
        if job_title:
            job_title = job_title[0]
        salary = etree_html.xpath(
            '//div[contains(@class,"job-primary")]/div[@class="info-primary"]/div[@class="name"]/span/text()')
        if salary:
            salary = '￥' + salary[0] + '/月'
        info = etree_html.xpath('//div[@class="job-primary detail-box"]/div[@class="info-primary"]/p/text()')
        job_area = info[0]
        ex = info[1]
        edu = info[2]
        job_tags1 = etree_html.xpath(
            '//div[@class="job-primary detail-box"]/div[@class="info-primary"]/div[@class="tag-container"]/div[@class="job-tags"]//span/text()')
        job_tags2 = etree_html.xpath('//div[@class="detail-content"]/div[2]/div[@class="job-tags"]//span/text()')
        if job_tags1:
            job_tags.extend(job_tags1)
        if job_tags2:
            job_tags.extend(job_tags2)
        job_brief = etree_html.xpath('//div[@class="detail-content"]/div[@class="job-sec"]/div[@class="text"]/text()')
        job_addr = etree_html.xpath('//div[@class="location-address"]/text()')[0]
        company_name = etree_html.xpath('//div[@class="sider-company"]/div[@class="company-info"]/a/@title')[0].strip()
        company_type = etree_html.xpath('//a[@ka="job-detail-brandindustry"]/text()')[0]
        company_status1 = etree_html.xpath('//li[@class="manage-state"]/text()')
        company_status2 = etree_html.xpath('//div[@class="sider-company"]/p[2]/text()')
        if company_status1:
            company_status += company_status1[0] + '/'
        if company_status2:
            company_status += company_status2[0]
        company_scale = etree_html.xpath('//div[@class="sider-company"]/p[3]/text()')[0]
        pub_date = etree_html.xpath('//div[@class="sider-company"]/p[6]/text()')
        if pub_date:
            pub_date = pub_date[0].split('：')[1]
        company_brief = etree_html.xpath('//div[@class="job-sec company-info"]/div[@class="text"]/text()')
        contact_person = etree_html.xpath('//h2[@class="name"]/text()')[0]
        # print({
        #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '', 'job_property': '',
        #     'job_status': job_status, 'job_area': job_area, 'major': '', 'job_addr': job_addr, 'pub_date': pub_date,
        #     'end_time': '', 'age': '', 'sex': '', 'edu': edu, 'ex': ex, 'marriage': '', 'lang': '',
        #     'job_brief': job_brief, 'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
        #     'company_name': company_name, 'company_type': company_type, 'company_status': company_status, 'phone': '',
        #     'driver_license': '', 'company_scale': company_scale, 'company_brief': company_brief,
        #     'contact_person': contact_person, 'company_comment': ''
        # })
        self.jobs.append({
            'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '', 'job_property': '',
            'job_status': job_status, 'job_area': job_area, 'major': '', 'job_addr': job_addr, 'pub_date': pub_date,
            'end_time': '', 'age': '', 'sex': '', 'edu': edu, 'ex': ex, 'marriage': '', 'lang': '',
            'job_brief': job_brief, 'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
            'company_name': company_name, 'company_type': company_type, 'company_status': company_status, 'phone': '',
            'driver_license': '', 'company_scale': company_scale, 'company_brief': company_brief,
            'contact_person': contact_person, 'company_comment': ''
        })

    def parser_51job(self, html, url_name, url=None, *args, **kwargs):
        """
        前程无忧(51job)网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[@id="resultList"]/div[@class="el"]')
        if response:
            for item in response:
                link = item.xpath('./p/span/a/@href')[0]
                self.second_request_parser(link, url_name, *args, **kwargs)

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_51job(self, html, link=None, *args, **kwargs):
        """
        请求51job网站二层网页
        :param html: 二层网址的源码
        :param link: 二层网址的url
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        job_title = etree_html.xpath('//div[@class="cn"]/h1/@title')
        if job_title:
            job_title = ''.join(job_title).strip()
        salary = etree_html.xpath('//div[@class="cn"]/strong/text()')
        if salary:
            salary = salary[0]
            salary, i_salary = self.get_format_salary(salary)
        job_tags = etree_html.xpath('//div[@class="t1"]//span/text()')
        job_type = etree_html.xpath('//div[@class="mt10"]/p[1]//a/text()')
        if job_type:
            job_type = ','.join(job_type)
        company_name = etree_html.xpath('//p[@class="cname"]/a/@title')[0]
        temp_info = etree_html.xpath('//p[@class="msg ltype"]/text()')
        if temp_info:
            job_area = temp_info[0].strip().replace('\xa0', '')
            ex = temp_info[1].strip().replace('\xa0', '')
            edu = temp_info[2].strip().replace('\xa0', '')
            number_recruits = temp_info[3].strip().replace('\xa0', '')
            temp_pub_date = temp_info[4].strip().replace('\xa0', '').replace('发布', '')
            pub_date = self.get_current_date(temp_pub_date)
        job_brief = etree_html.xpath('//div[contains(@class,"job_msg")]/p/text()')
        job_addr = etree_html.xpath('//div[@class="bmsg inbox"]/p[@class="fp"]/text()')
        if job_addr:
            job_addr = ''.join(job_addr).strip()
        company_type = etree_html.xpath('//div[@class="com_tag"]/p[1]/@title')[0]
        company_scale = etree_html.xpath('//div[@class="com_tag"]/p[2]/@title')[0] + '/' + \
                        etree_html.xpath('//div[@class="com_tag"]/p[3]/@title')[0]
        company_brief = etree_html.xpath('//div[contains(@class,"tmsg")]/text()')[0].strip()
        # print({
        #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type, 'job_property': '',
        #     'job_status': '', 'job_area': job_area, 'major': '', 'job_addr': job_addr, 'pub_date': pub_date,
        #     'end_time': '', 'age': '', 'sex': '', 'edu': edu, 'ex': ex, 'marriage': '', 'lang': '',
        #     'job_brief': job_brief, 'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits,
        #     'job_evaluate': '', 'company_name': company_name, 'company_type': company_type,
        #     'company_status': '', 'phone': '', 'driver_license': '', 'company_scale': company_scale,
        #     'company_brief': company_brief, 'contact_person': '', 'company_comment': ''
        # })
        self.jobs.append({
            'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type, 'job_property': '',
            'job_status': '', 'job_area': job_area, 'major': '', 'job_addr': job_addr, 'pub_date': pub_date,
            'end_time': '', 'age': '', 'sex': '', 'edu': edu, 'ex': ex, 'marriage': '', 'lang': '',
            'job_brief': job_brief, 'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits,
            'job_evaluate': '', 'company_name': company_name, 'company_type': company_type,
            'company_status': '', 'phone': '', 'driver_license': '', 'company_scale': company_scale,
            'company_brief': company_brief, 'contact_person': '', 'company_comment': ''
        })

    def parser_zhilian(self, html, url_name, url=None, *args, **kwargs):
        """
        智联招聘网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        response = json.loads(html).get('data').get('results')
        if response:
            for item in response:
                job_type = ''
                job_title = item.get('jobName')
                job_status = item.get('timeState').replace('最新', '招聘中')
                salary = '￥' + item.get('salary') + '/月'
                job_area = item.get('city').get('display')
                if item.get('jobType'):
                    temp_jobs = item.get('jobType').get('items')
                    for j in temp_jobs:
                        job_type += j.get('name') + ','
                if item.get('emplType'):
                    job_property = item.get('emplType')
                    edu = item.get('eduLevel').get('name')
                    ex = item.get('workingExp').get('name')
                company_name = item.get('company').get('name')
                company_type = item.get('company').get('type').get('name')
                company_scale = item.get('company').get('size').get('name') + '/' + ''.join(
                    [i.get('name') for i in item.get('jobType').get('items')])
                pub_date = item.get('updateDate').split(' ')[0]
                link = item.get('positionURL')
                job_addr, job_brief, job_tags, company_brief, number_recruits = self.second_request_parser(link,
                                                                                                           url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': job_property, 'job_status': job_status, 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '', 'edu': edu,
                #     'ex': ex,
                #     'marriage': '', 'lang': '', 'job_brief': job_brief, 'job_tags': job_tags, 'job_link': link,
                #     'number_recruits': number_recruits, 'job_evaluate': '', 'company_name': company_name,
                #     'company_type': company_type, 'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': company_brief, 'contact_person': '',
                #     'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': job_property, 'job_status': job_status, 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '', 'edu': edu,
                    'ex': ex,
                    'marriage': '', 'lang': '', 'job_brief': job_brief, 'job_tags': job_tags, 'job_link': link,
                    'number_recruits': number_recruits, 'job_evaluate': '', 'company_name': company_name,
                    'company_type': company_type, 'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': company_brief, 'contact_person': '',
                    'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_zhilian(self, html, link=None, *args, **kwargs):
        """
        解析智联招聘二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :return:
        """

        etree_html = etree.HTML(html)
        job_brief = etree_html.xpath('//div[@class="describtion__detail-content"]//text()')
        job_addr = etree_html.xpath('//span[@class="job-address__content-text"]/text()')
        if job_addr:
            job_addr = ''.join(job_addr).strip()
        job_tags = etree_html.xpath('//span[@class="highlights__content-item"]/text()')
        company_brief = etree_html.xpath('//div[@class="company__description"]/text()')
        if company_brief:
            company_brief = company_brief[0]
        number_recruits = etree_html.xpath('//ul[@class="summary-plane__info"]/li[last()]/text()')
        if number_recruits:
            number_recruits = number_recruits[0].replace('招', '')
        return job_addr, job_brief, job_tags, company_brief, number_recruits

    def parser_zhuopin(self, html, url_name, url=None, *args, **kwargs):
        """
        智联卓聘网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        res = json.loads(html)
        response = res.get('body').get('JobList')
        if response:
            for item in response:
                job_title = item.get('JobTitle')
                job_area = item.get('JobLactionStr')
                company_name = item.get('CompanyName')
                pub_date = item.get('PublishDate')
                edu = item.get('JobDegree')
                ex = item.get('WorkExperience')
                company_type = item.get('CompanyIndustry')
                company_scale = item.get('CompanyScale') + '/' + item.get('CompanyType')
                job_id = item.get('JobID')
                job_tags = item.get('JobTags')
                link = 'https://www.highpin.cn/api/job/GetPositionDetail?jobID=%s&referrerType=2&x-zp-client-id=%s' % (
                    job_id, ZHUOPIN_CLIENT_ID)
                job_addr, salary, job_brief, company_brief, job_type, number_recruits, lang, age = self.second_request_parser(
                    link, url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '', 'edu': edu,
                #     'ex': ex,
                #     'marriage': '', 'lang': lang, 'job_brief': job_brief, 'job_tags': job_tags, 'job_link': link,
                #     'number_recruits': number_recruits, 'job_evaluate': '', 'company_name': company_name,
                #     'company_type': company_type, 'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': company_brief, 'contact_person': '',
                #     'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '', 'edu': edu,
                    'ex': ex,
                    'marriage': '', 'lang': lang, 'job_brief': job_brief, 'job_tags': job_tags, 'job_link': link,
                    'number_recruits': number_recruits, 'job_evaluate': '', 'company_name': company_name,
                    'company_type': company_type, 'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': company_brief, 'contact_person': '',
                    'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_zhuopin(self, html, link=None, *args, **kwargs):
        """
        解析智联卓聘二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :return:
        """
        response = json.loads(html).get('body')
        job_addr = response.get('JobAddress')
        temp_salary = response.get('YearlySalary')
        salary, i_salary = self.get_format_salary(temp_salary, '/年')
        job_brief = response.get('Responsibility')
        company_brief = response.get('Company')
        if company_brief:
            company_brief = company_brief.get('Introduction')
        job_type = response.get('Type')
        number_recruits = response.get('RecruitCount')
        lang = response.get('Language')
        age = response.get('Age')

        return job_addr, salary, job_brief, company_brief, job_type, number_recruits, lang, age

    def parser_lagou(self, html, url_name, url=None, *args, **kwargs):
        """
        拉钩网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        res = json.loads(html)
        if res:
            temp = res.get('content')
            if temp:
                temp = temp.get('positionResult')
                if temp:
                    response = temp.get('result')
                    for item in response:
                        job_title = item.get('positionName')
                        salary = '￥' + item.get('salary') + '/月'
                        job_area = item.get('city')
                        job_type = item.get('firstType')
                        company_name = item.get('companyFullName')
                        pub_date = item.get('createTime')
                        job_property = item.get('jobNature')
                        edu = item.get('education')
                        ex = item.get('workYear')
                        company_type = item.get('industryField')
                        company_status = item.get('financeStage')
                        size = item.get('companySize')
                        tags1 = item.get('positionAdvantage')
                        tags2 = item.get('hitags')
                        if not tags1:
                            tags1 = ''
                        if not tags2:
                            tags2 = []
                        job_tags = ' '.join(tags2) + tags1
                        job_id = str(item.get('positionId'))
                        if not size:
                            size = ''
                        company_scale = size
                        link = 'https://www.lagou.com/jobs/%s.html?show=%s' % (job_id, LAGOU_SHOW)
                        job_brief, job_addr, job_evaluate, contact_person = self.second_request_parser(link, url_name)
                        if not job_evaluate:
                            job_evaluate = '暂无评价'
                        # print({
                        #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                        #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                        #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                        #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                        #     'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': job_evaluate,
                        #     'company_name': company_name, 'company_type': company_type,
                        #     'company_status': company_status, 'phone': '', 'driver_license': '',
                        #     'company_scale': company_scale, 'company_brief': '',
                        #     'contact_person': contact_person, 'company_comment': ''
                        # })
                        self.jobs.append({
                            'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                            'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                            'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                            'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                            'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': job_evaluate,
                            'company_name': company_name, 'company_type': company_type,
                            'company_status': company_status, 'phone': '', 'driver_license': '',
                            'company_scale': company_scale, 'company_brief': '',
                            'contact_person': contact_person, 'company_comment': ''
                        })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_lagou(self, html, link=None, *args, **kwargs):
        """
        解析拉钩二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :return:
        """
        etree_html = etree.HTML(html)
        job_brief = etree_html.xpath('//div[@class="job-detail"]/p/text()')
        job_addr = etree_html.xpath('//div[@class="work_addr"]/a/text()')
        if job_addr:
            job_addr = job_addr[:-1]
            job_addr = ''.join(job_addr)
        temp_evaluate = etree_html.xpath('//li[contains(@class,"review-area")]')
        contact_person = etree_html.xpath('//span[@class="name"]/text()')[0]
        job_evaluate = []
        for item in temp_evaluate:
            data = item.xpath(
                './div[@class="review-right"]/div[@class="review-content"]/div/div[@class="interview-process"]/text()')
            job_evaluate.extend(data)
        return job_brief, job_addr, job_evaluate, contact_person

    def parser_dajie(self, html, url_name, url=None, *args, **kwargs):
        """
        大街网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        res = json.loads(html)
        if res:
            response = res.get('data').get('list')
            if response:
                for item in response:
                    job_title = item.get('jobName')
                    salary = item.get('salary')
                    if '面议' not in salary:
                        salary = '￥' + salary
                    job_area = item.get('pubCity')
                    company_type = item.get('industryName')
                    company_name = item.get('compName')
                    edu = item.get('pubEdu')
                    ex = item.get('pubEx')
                    if not edu:
                        edu = '不限'
                    if not ex:
                        ex = '不限'
                    company_scale = item.get('scaleName')
                    link = 'https:' + item.get('liHref')
                    job_tags, job_people_number, job_brief, job_addr, company_property, company_brief, job_property, number_recruits, contact_person = self.second_request_parser(
                        link, url_name)
                    company_scale = company_property + '/' + company_scale

                    # print({
                    #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                    #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    #     'job_addr': job_addr, 'pub_date': '', 'end_time': '', 'age': '', 'sex': '',
                    #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                    #     'company_name': company_name, 'company_type': company_type,
                    #     'company_status': '', 'phone': '', 'driver_license': '',
                    #     'company_scale': company_scale, 'company_brief': company_brief,
                    #     'contact_person': contact_person, 'company_comment': ''
                    # })
                    self.jobs.append({
                        'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                        'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                        'job_addr': job_addr, 'pub_date': '', 'end_time': '', 'age': '', 'sex': '',
                        'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                        'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                        'company_name': company_name, 'company_type': company_type,
                        'company_status': '', 'phone': '', 'driver_license': '',
                        'company_scale': company_scale, 'company_brief': company_brief,
                        'contact_person': contact_person, 'company_comment': ''
                    })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_dajie(self, html, link=None, *args, **kwargs):
        """
        解析大街二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :return:
        """
        etree_html = etree.HTML(html)
        job_tags = etree_html.xpath('//div[@class="job-msg-bottom"]/ul/li/text()')
        job_people_number = etree_html.xpath('//div[@class="job-msg-bottom"]/span[1]/text()')
        job_brief = etree_html.xpath('//*[@id="jp_maskit"]/pre[2]/text()')
        job_addr = etree_html.xpath('//div[@class="ads-msg"]/span[1]/text()')
        if job_addr:
            job_addr = ''.join(job_addr).replace(' ', '')
        company_property = etree_html.xpath('//ul[@class="info"]/li[3]/span/text()')[0]
        company_brief = etree_html.xpath('//div[@class="i-corp-desc"]/p/text()')
        job_property = etree_html.xpath('//li[@class="full-time"]/span/text()')[0]
        number_recruits = etree_html.xpath('//li[@class="recruiting"]/span/text()')[0]
        contact_person = etree_html.xpath('//a[@class="person-name"]/text()')[0].strip()

        return job_tags, job_people_number, job_brief, job_addr, company_property, company_brief, job_property, number_recruits, contact_person

    def parser_zhitong(self, html, url_name, url=None, *args, **kwargs):
        """
        智通招聘网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        res = json.loads(html)
        if res:
            temp = res.get('page')
            if temp:
                response = temp.get('items')
                if response:
                    for item in response:
                        job_title = item.get('posName')
                        if '<em>' in job_title:
                            job_title = job_title.replace('<em>', '')
                        if '</em>' in job_title:
                            job_title = job_title.replace('</em>', '')
                        salary = '￥' + item.get('salaryStr').replace('千', 'k')
                        pub_date = item.get('refreshDate')
                        if pub_date:
                            pub_date = self.handle_time(pub_date)
                        job_tags = item.get('taoLabelList')
                        job_brief = item.get('posDesc')
                        job_area = item.get('workLocationsStr')
                        job_type = item.get('industryStr')
                        job_property = item.get('propertyStr')
                        company_name = item.get('comName')
                        edu = item.get('educationDegreeStr')
                        ex = item.get('reqWorkYearStr')
                        if not edu:
                            edu = '不限'
                        if not ex:
                            ex = '不限'
                        if not job_property:
                            job_property = ''
                        company_info = item.get('comInfo')
                        if company_info:
                            company_brief = company_info.get('companyIntroduction')
                            company_type = company_info.get('propertyStr')
                            company_number = company_info.get('employeeNumStr')
                        if not company_type:
                            company_type = ''
                        if not company_number:
                            company_number = ''
                        company_scale = company_number + '人/' + company_type
                        link = item.get('posDetailUrl')
                        if link:
                            link = 'http://www.job5156.com' + link
                            self.second_request_parser(link, url_name)
                        number_recruits, job_addr, age, lang = self.second_request_parser(link, url_name)

                        # print({
                        #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                        #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                        #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '',
                        #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': lang, 'job_brief': job_brief,
                        #     'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                        #     'company_name': company_name, 'company_type': company_type,
                        #     'company_status': '', 'phone': '', 'driver_license': '',
                        #     'company_scale': company_scale, 'company_brief': company_brief,
                        #     'contact_person': '', 'company_comment': ''
                        # })
                        self.jobs.append({
                            'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                            'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                            'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '',
                            'edu': edu, 'ex': ex, 'marriage': '', 'lang': lang, 'job_brief': job_brief,
                            'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                            'company_name': company_name, 'company_type': company_type,
                            'company_status': '', 'phone': '', 'driver_license': '',
                            'company_scale': company_scale, 'company_brief': company_brief,
                            'contact_person': '', 'company_comment': ''
                        })

                else:
                    # 如果为空，将标志位置为真
                    self.flag = True

    def second_parser_zhitong(self, html, link=None, *args, **kwargs):
        """
        智通人才二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :return:
        """
        etree_html = etree.HTML(html)
        number_recruits = etree_html.xpath('//ul[@class="requirements"]/li[4]/p/text()')
        if number_recruits:
            number_recruits = number_recruits[0]
        job_addr = etree_html.xpath('//div[@class="work_addr_detail"]/p/text()')
        if job_addr:
            job_addr = job_addr[0]
        else:
            job_addr = '暂无详细地址'
        age = etree_html.xpath('//ul[@class="pos_need"]/li[1]/text()')[0].strip()
        lang = etree_html.xpath('//ul[@class="pos_need"]/li[2]/text()')[0].strip()
        return number_recruits, job_addr, age, lang

    def parser_cjol(self, html, url_name, url=None, *args, **kwargs):
        """
        中国人才热线网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        res = json.loads(html)
        response = res.get('JobListHtml')
        if response:
            html = etree.HTML(response)
            etree_html = html.xpath('//div[@id="searchlist"]/ul[@class="results_list_box"]')
            for item in etree_html:
                job_title = item.xpath('./li[@class="list_type_first"]/h3/a/text()')
                job_area = item.xpath('./li[@class="list_type_third"]/text()')[0]
                edu = item.xpath('./li[@class="list_type_fifth"]/text()')
                company_name = item.xpath('./li[@class="list_type_second"]/a/text()')[0]
                link = item.xpath('./li[@class="list_type_first"]/h3/a/@href')[0]
                salary, ex, number_recruits, job_property, pub_date, job_addr, job_brief, company_type, company_scale, job_tags, job_type = self.second_request_parser(
                    link, url_name)
                if job_title:
                    job_title = ''.join(job_title)
                if not edu:
                    edu = '不限'
                else:
                    edu = edu[0]
                if not ex:
                    ex = '不限'

                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': '',
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': '',
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_cjol(self, html, link=None, *args, **kwargs):
        """
        中国人才热线二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :return:
        """
        etree_html = etree.HTML(html)
        salary = etree_html.xpath('//ul[contains(@class,"require-jobintro")]/li[1]/em/text()')
        ex = etree_html.xpath('//ul[contains(@class,"require-jobintro")]/li[3]/text()')
        number_recruits = etree_html.xpath('//ul[contains(@class,"require-jobintro")]/li[4]/text()')
        job_property = etree_html.xpath('//ul[contains(@class,"require-jobintro")]/li[5]/text()')[0]
        pub_date = etree_html.xpath('//div[contains(@class,"pubtime-jobintro")]/text()')
        job_addr = etree_html.xpath('//div[@class="txtinfo-address"]/text()')
        job_brief = etree_html.xpath('//div[@class="coninfo-jobdesc"]/p/text()')
        company_type = etree_html.xpath('//ul[@class="ul-combscintro"]/li[1]/a/text()')[0]
        temp_info1 = etree_html.xpath('//ul[@class="ul-combscintro"]/li[6]/text()')
        temp_info2 = etree_html.xpath('//ul[@class="ul-combscintro"]/li[7]/text()')
        job_tags = etree_html.xpath('//ul[contains(@class,"taglist-jobintro")]//li/text()')
        job_type = etree_html.xpath('//div[@class="coninfo-otherinfo"]/dl[2]/dd/a/text()')[0]
        if salary:
            salary = '￥' + salary[0] + '/月'
        if ex:
            ex = ex[0].replace('经验', '')

        if number_recruits:
            number_recruits = number_recruits[0]
        if job_property:
            job_property = job_property[0]
        if job_addr:
            job_addr = job_addr[0]
        else:
            job_addr = '暂无详细地址'
        if pub_date:
            pub_date = pub_date[0].replace('更新', '')
        if not temp_info1:
            temp_info1 = '暂无'
        if not temp_info2:
            temp_info2 = '暂无'
        if temp_info1 and temp_info2:
            company_scale = temp_info1[0] + '/' + temp_info2[0]
        else:
            company_scale = ''
        return salary, ex, number_recruits, job_property, pub_date, job_addr, job_brief, company_type, company_scale, job_tags, job_type

    def parser_yjs(self, html, url_name, url=None, *args, **kwargs):
        """
        应届生招聘网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//ul[@class="searchResult"]/li')
        if response:
            for item in response:
                link = item.xpath('./div/h3/a/@href')[0]
                something = item.xpath('./div/p/text()')
                pub_date = item.xpath('./div/p/span/text()')[0]
                if something:
                    something = something[0].strip()
                    split_things = something.split('|')
                    job_area = split_things[-1]
                    job_property = split_things[-2]
                    information_source = split_things[0].split('：')[1]
                    # 如果是前程无忧的就忽略，已经有单独爬取前程无忧的
                    if '前程无忧' in information_source:
                        pass
                    elif '本站' in information_source:
                        job_title, company_name, number_recruits, company_scale, company_brief, job_brief, company_type, job_type = self.second_request_parser(
                            link, url_name, 'local')
                    else:
                        job_title, company_name, number_recruits, company_scale, company_brief, job_brief, company_type, job_type = self.second_request_parser(
                            link, url_name)

                    # print({
                    #     'index': index, 'job_title': job_title, 'salary': '', 'job_type': job_type,
                    #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    #     'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                    #     'edu': '', 'ex': '', 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    #     'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    #     'company_name': company_name, 'company_type': company_type,
                    #     'company_status': '', 'phone': '', 'driver_license': '',
                    #     'company_scale': company_scale, 'company_brief': '',
                    #     'contact_person': '', 'company_comment': ''
                    # })
                    self.jobs.append({
                        'index': index, 'job_title': job_title, 'salary': '', 'job_type': job_type,
                        'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                        'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                        'edu': '', 'ex': '', 'marriage': '', 'lang': '', 'job_brief': job_brief,
                        'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                        'company_name': company_name, 'company_type': company_type,
                        'company_status': '', 'phone': '', 'driver_license': '',
                        'company_scale': company_scale, 'company_brief': '',
                        'contact_person': '', 'company_comment': ''
                    })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_yjs(self, html, link=None, *args, **kwargs):
        """
        应届生求职网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :return:
        """
        etree_html = etree.HTML(html)

        company_type = ''
        number_recruits = ''
        company_scale = ''
        company_brief = ''
        job_type = ''
        if args:
            job_title = etree_html.xpath('//div[@id="wordDiv1"]/h2/a/text()')[0]
            job_brief = etree_html.xpath('//div[@class="j_i"]/text()')
            company_name = etree_html.xpath('//div[@class="main"]/div[1]/h1/a/text()')[0]
            number_recruits = etree_html.xpath('//div[@class="job_list"]/ul/li[3]/span/text()')
            company_type = etree_html.xpath('//ul[contains(@class,"company_detail")]/li[1]/span/text()')[0]
            company_scale = etree_html.xpath('//ul[contains(@class,"company_detail")]/li[2]/span/text()')
            company_property = etree_html.xpath('//ul[contains(@class,"company_detail")]/li[3]/span/text()')
            company_brief = etree_html.xpath('//div[@id="wordDiv2"]/p/text()')

            if not number_recruits:
                number_recruits = ''
            else:
                number_recruits = number_recruits[0]
            if not company_scale:
                company_scale = ''
            else:
                company_scale = company_scale[0]
            if not company_property:
                company_property = ''
            else:
                company_property = company_property[0]
            company_scale = company_property + '/' + company_scale
        else:
            job_title = etree_html.xpath('//div[contains(@class,"info")]/ol/li[5]/u/text()')
            if job_title:
                job_title = ''.join(job_title)
            job_type = etree_html.xpath('//div[@class="main mleft"]/div[2]/a/text()')
            if job_type:
                job_type = job_type[0]
            job_brief = etree_html.xpath('//div[@class="jobIntro"]//text()')
            company_name = etree_html.xpath('//div[contains(@class,"main")]/h1/text()')
            if company_name:
                company_name = company_name[0].split(']')[1]
        return job_title, company_name, number_recruits, company_scale, company_brief, job_brief, company_type, job_type

    def parser_jobcn(self, html, url_name, url=None, *args, **kwargs):
        """
        jobcn网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        res = json.loads(html)
        response = res.get('rows')
        if response:
            for item in response:
                job_title = item.get('posName')
                edu = item.get('reqDegreeDesc')
                ex = item.get('workYearDesc')
                age = item.get('ageDesc')
                sex = item.get('sexDesc')
                salary = item.get('salaryDesc').replace('&#165;', '￥') + '/月'
                job_area = item.get('jobLocation')
                company_name = item.get('comName')
                job_tags = item.get('benefitTags')
                job_brief = item.get('posDescription')
                pub_date = item.get('postDate').split(' ')[0]
                contact_person = item.get('contactPerson')
                job_addr1 = item.get('examAddress')
                job_addr2 = item.get('address')
                job_addr = job_addr2 if job_addr1 != job_addr2 else job_addr1

                job_id = item.get('posId')
                com_id = item.get('comId')

                link = 'https://www.jobcn.com/position/detail.xhtml?redirect=0&posId={job}&comId={com}&s=search/advanced&acType=1'.format(
                    job=job_id, com=com_id)
                company_type, company_scale, company_link, number_recruits = self.second_request_parser(
                    link, url_name)

                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': '',
                #     'contact_person': contact_person, 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': '',
                    'contact_person': contact_person, 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_jobcn(self, html, link=None, *args, **kwargs):
        """
        卓聘人才求职网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :return:
        """
        etree_html = etree.HTML(html)
        company_type = etree_html.xpath('//div[@class="base"]/div[1]/dl[1]/dd/a/text()')[0]
        company_scale = etree_html.xpath('//div[@class="base"]/div[1]/dl[2]/dd/text()')[0]
        company_link = etree_html.xpath('//div[@class="base"]/div[1]/dl[3]/dd/a/@href')[0]
        number_recruits = etree_html.xpath('//div[@class="name_pos"]/div/dl[2]/dd/text()')[0]
        # ocr提取邮箱和联系电话
        # email = etree_html.xpath('//div[contains(@class,"contactUs_pos")]/div/dl[2]/dd/img/@src')
        # if email:
        #     email = 'https://www.jobcn.com' + email[0]
        # phone = etree_html.xpath('//div[contains(@class,"contactUs_pos")]/div/dl[3]/dd/img/@src')
        # if phone:
        #     phone = 'https://www.jobcn.com' + phone[0]
        return company_type, company_scale, company_link, number_recruits

    def parser_jiaoshizhaopin(self, html, url_name, url=None, *args, **kwargs):
        """
        教师招聘求职网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//ul[@class="job_list"]/li')
        if response:
            for item in response:
                job_area = item.xpath('./div[1]/p/text()')[0]
                salary = item.xpath('./div[2]/p/span/text()')[0].replace('~', '-').replace('元', '')
                salary, i_salary = self.get_format_salary(salary)
                link = item.xpath('./div[2]/a/@href')[0]
                company_name, job_title, number_recruits, edu, ex, sex, job_tags, pub_date, job_brief, job_addr, end_time = self.second_request_parser(
                    link, url_name)

                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '教职教师',
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': end_time, 'age': '', 'sex': sex,
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': '学校/兴趣班/培训机构',
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': '', 'company_brief': '',
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '教职教师',
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': end_time, 'age': '', 'sex': sex,
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    'company_name': company_name, 'company_type': '学校/兴趣班/培训机构',
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': '', 'company_brief': '',
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_jiaoshizhaopin(self, html, link=None, *args, **kwargs):
        """
        教师招聘求职网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :return:
        """
        etree_html = etree.HTML(html)
        company_name = etree_html.xpath('//*[@id="content"]/div[1]/div/div[1]/h1/a/text()')[0]
        job_title = etree_html.xpath('//*[@id="content"]/div[1]/div/div[1]/h2/text()')[0]

        pub_date = etree_html.xpath('//li[@class="time"]/span/text()')
        if pub_date:
            pub_date = pub_date[0].split(' ')[0]
        job_brief = etree_html.xpath('//div[@class="des_box"]/div[@class="item_content"]/text()')
        job_addr = etree_html.xpath('//div[@class="address_box"]/h3/@title')
        if not job_addr[0]:
            job_addr = etree_html.xpath('//*[@id="content"]/div[4]/div/div[1]/div[2]/div/span/text()')[0]
        job_end_time = etree_html.xpath('//*[@id="content"]/div[4]/div/div[1]/div[3]/div/p/text()')
        if job_end_time:
            job_end_time = job_end_time[0].replace('截止', '')
        if job_addr:
            job_addr = ''.join(job_addr)
        info = etree_html.xpath('//*[@id="content"]/div[1]/div/div[1]/p/text()')
        if info:
            info = info[0].split('\xa0/\xa0')
        info = [i for i in info if i]
        ex = info[2]
        edu = info[3]
        number_recruits = info[4]
        sex = info[-1]
        temp_job_tags = etree_html.xpath('//ul[@class="label"]/li')
        job_tags = []
        for item in temp_job_tags:
            tag = item.xpath('./p/text()')[0]
            job_tags.append(tag)
        if not job_tags:
            job_tags = []
        return company_name, job_title, number_recruits, edu, ex, sex, job_tags, pub_date, job_brief, job_addr, job_end_time

    def parser_baixing(self, html, url_name, url=None, *args, **kwargs):
        """
        百姓网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//ul[@class="list-ad-items"]/li')
        if response:
            for item in response:
                job_title = item.xpath('./div/div[1]/a[1]//text()')
                if job_title:
                    job_title = ''.join(job_title)
                link_type = item.xpath('./div/div[1]/a[@class="tag tag-category"]/text()')
                if link_type:
                    link_type = link_type[0]
                    if '培训' in link_type or '其他' in link_type or '教育' in link_type:
                        # print('job_title', job_title)
                        continue

                if '培训' in job_title or '班' in job_title or '课程' in job_title or '教程' in job_title:
                    # print('job_title', job_title)
                    continue
                job_area = item.xpath('./div/div[2]/text()')
                if job_area:
                    job_area = job_area[0].split(' ')[0]
                salary = item.xpath('./div/div[1]/span/text()')
                if salary:
                    salary = salary[0].replace('元', '')
                    salary, i_salary = self.get_format_salary(salary, '/月')
                link = item.xpath('./div/div[1]/a[1]/@href')[0]
                company_name, company_brief, company_type, edu, ex, number_recruits, sex, job_tags, job_addr, job_type, contact_person, pub_date, job_brief = self.second_request_parser(
                    link, url_name)
                if not edu:
                    edu = ''
                if not ex:
                    ex = ''
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': sex,
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': '', 'company_brief': company_brief,
                #     'contact_person': contact_person, 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': sex,
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': '', 'company_brief': company_brief,
                    'contact_person': contact_person, 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_baixing(self, html, link=None, *args, **kwargs):
        """
        网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        pub_date = etree_html.xpath('//div[@class="viewad-actions"]/span[2]/text()')
        if pub_date:
            pub_date = pub_date[0].strip().split('日')[0].replace('月', '-')
            pub_date = self.get_current_date(pub_date)
        job_brief = etree_html.xpath('//div[@class="viewad-text-hide"]/text()')
        temp_job_tags = etree_html.xpath('//div[@class="fuli-detail"]/label')
        job_tags = []
        if temp_job_tags:
            for item in temp_job_tags:
                tags = item.xpath('./text()')[0]
                job_tags.append(tags)
        infor_obj = etree_html.xpath('//div[contains(@class,"viewad-meta2-item")]')
        infor = {}
        for item in infor_obj:
            label = item.xpath('./label[1]/text()')
            if label:
                label = label[0].replace('：', '')
            span = item.xpath('./span/text()')
            if span:
                span = span[0]
            elif item.xpath('./label[2]/text()'):
                span = item.xpath('./label[2]/text()')[0]
            elif item.xpath('./a/text()'):
                span = item.xpath('./a/text()')[0]
            infor.update({label: span})
        job_addr = infor.get('工作地点') if infor.get('工作地点') else ''
        number_recruits = infor.get('招聘人数')
        edu = infor.get('学历要求')
        ex = infor.get('工作年限')
        sex = infor.get('性别要求')
        job_type = infor.get('职位类别')
        contact_person = infor.get('联系人')
        company_name = etree_html.xpath('//div[contains(@class,"viewad-meta-item")]/span/text()')
        if company_name:
            company_name = ''.join(company_name)
        company_type = etree_html.xpath('//div[@class="company-cont"]/p/text()')
        if company_type:
            company_type = company_type[0]
            if '万元' in company_type:
                company_type = ''
        else:
            company_type = ''
        company_brief = etree_html.xpath('//div[@class="company-description"]/p/text()')
        if not company_brief:
            company_brief = ''

        return company_name, company_brief, company_type, edu, ex, number_recruits, sex, job_tags, job_addr, job_type, contact_person, pub_date, job_brief

    def parser_shuobo(self, html, url_name, url=None, *args, **kwargs):
        """
        硕博网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//ul[contains(@class,"search-result-list")]/li')
        if response:
            for item in response:
                job_title = item.xpath('./div[1]/a/@title')[0]
                temp_info = item.xpath('./div[1]/p/text()')
                if temp_info:
                    infos = temp_info[0].split('|')
                    infos = [i.strip() for i in infos]
                    job_property = infos[-1]
                    edu = infos[1]
                    ex = infos[0].replace('经验', '')
                salary = item.xpath('./div[1]/span/text()')
                salary = ''.join(salary).strip().replace('元', '')
                if not salary:
                    salary = '面议'
                else:
                    salary, i_salary = self.get_format_salary(salary)
                company_name = item.xpath('./div[2]/a/text()')[0]
                temp_job_tags = item.xpath('./div[2]/p//text()')
                job_tags = []
                for tag in temp_job_tags:
                    if '\r\n' in tag:
                        continue
                    job_tags.append(tag.strip())
                job_area = item.xpath('./div[3]/p/span[1]/text()')[0].strip()
                pub_date = item.xpath('./div[3]/p/span[2]/text()')[0].strip()
                link = item.xpath('./div[1]/a/@href')[0]
                number_recruits, job_type, job_brief, job_addr, company_type, company_scale, company_brief = self.second_request_parser(
                    link, url_name)
                #
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': company_brief,
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': company_brief,
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_shuobo(self, html, link=None, *args, **kwargs):
        """
        硕博网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        number_recruits = etree_html.xpath('//ul[@class="requirements"]/li[4]/p/text()')[0]
        job_type = etree_html.xpath('//div[@class="desc content"]/p/text()')[0]
        if job_type:
            job_type = job_type.split('：')[1]
        job_brief = etree_html.xpath('//div[@class="desc content"]/pre/text()')
        job_addr = etree_html.xpath('//span[@class="addr"]/parent::p/text()')[0].strip()
        company_type = etree_html.xpath('//p[@class="base-info-content"]/span[1]/span/text()')[0].strip()
        company_scale = etree_html.xpath('//p[@class="base-info-content"]/span[2]/span/text()')
        company_property = etree_html.xpath('//p[@class="base-info-content"]/span[3]/span/text()')
        if not company_scale:
            company_scale = ''
        else:
            company_scale = company_scale[0].strip()
        if not company_property:
            company_property = ''
        else:
            company_property = company_property[0].strip()
        company_scale = company_scale + '人/' + company_property
        company_brief = etree_html.xpath('//pre[@class="com_intro_text"]/text()')
        if company_brief:
            company_brief = company_brief[:80]
        return number_recruits, job_type, job_brief, job_addr, company_type, company_scale, company_brief

    def parser_liepin(self, html, url_name, url=None, *args, **kwargs):
        """
        猎聘网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//ul[@class="sojob-list"]/li')
        if response:
            for item in response:
                job_title = item.xpath('./div/div[1]/h3/a/text()')[0].strip()

                job_area = item.xpath('./div/div[1]/p[1]/a/text()')
                if job_area:
                    job_area = ''.join(job_area).strip()
                edu = item.xpath('./div/div[1]/p[1]/span[2]/text()')[0]
                ex = item.xpath('./div/div[1]/p[1]/span[3]/text()')[0]
                temp_info = item.xpath('./div/div[1]/p[1]/@title')
                if temp_info:
                    salary, job_area, edu, ex = temp_info[0].split('_')
                    salary, i_salary = self.get_format_salary(salary, '/年')
                pub_date = item.xpath('./div/div[1]/p[2]/time/@title')
                if pub_date:
                    pub_date = pub_date[0].replace('月', '-').replace('日', '').replace('年', '-')
                company_name = item.xpath('./div/div[2]/p[@class="company-name"]/a/text()')[0]
                company_type = item.xpath('./div/div[2]/p[2]/span[1]/text()')[0].strip()
                company_status = item.xpath('./div/div[2]/p[2]/span[2]/text()')
                if company_status:
                    company_status = company_status[0]
                else:
                    company_status = ''
                link = item.xpath('./div/div[1]/h3/a/@href')[0]
                lang, age, job_tags, job_brief, job_addr, company_scale, company_brief = self.second_request_parser(
                    link, url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '',
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': lang, 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': company_status, 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': company_brief,
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '',
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': lang, 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': company_status, 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': company_brief,
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_liepin(self, html, link=None, *args, **kwargs):
        """
        猎聘网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        lang = etree_html.xpath('//div[@class="job-qualifications"]/span[3]/text()')[0]
        age = etree_html.xpath('//div[@class="job-qualifications"]/span[4]/text()')[0]
        job_tags = etree_html.xpath('//ul[contains(@class,"comp-tag-list")]//li/span/text()')
        job_brief = etree_html.xpath('//div[contains(@class,"content-word")]/text()')
        company_brief = etree_html.xpath('//div[@class="info-word"]/text()')
        company_scale = etree_html.xpath('//ul[@class="new-compintro"]/li[2]/text()')
        if company_scale:
            company_scale = company_scale[0].split('：')[1]
        else:
            company_scale = ''
        job_addr = etree_html.xpath('//ul[@class="new-compintro"]/li[3]/text()')
        if job_addr:
            job_addr = job_addr[0].split('：')[1]
        else:
            job_addr = ''
        return lang, age, job_tags, job_brief, job_addr, company_scale, company_brief

    def get_current_date(self, html_date):
        """
        计算真实时间
        :param html_date: 网页源码的时间
        :return:
        """

        pub_date = ''
        now_time = datetime.now()
        if '前' in html_date:
            times = html_date.split('前')[0]
            if times:
                split_number = re.match(r'\d*', times).group()
                number = int(split_number)
                time_args = times.split(split_number)[1]
                if time_args == '天':
                    count = timedelta(days=number)
                elif time_args == '小时':
                    count = timedelta(hours=number)
                elif time_args == '分钟':
                    count = timedelta(minutes=number)
                elif time_args == '秒':
                    count = timedelta(seconds=number)
                else:
                    count = timedelta()
                format_time = now_time - count
                # pub_date = format_time.strftime('%Y-%m-%d %H:%M:%S')
                pub_date = format_time.strftime('%Y-%m-%d')
        elif '今天' == html_date:
            pub_date = now_time.strftime('%Y-%m-%d')
        elif '-' in html_date:
            if html_date.count('-') == 1:
                pub_date = str(now_time.year) + '-' + html_date
            elif html_date.count('-') == 2:
                pass
            else:
                pass
        return pub_date

    def parser_ganji(self, html, url_name, url=None, *args, **kwargs):
        """
        赶集网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//dl[contains(@class,"job-list")]')
        if response:
            for item in response:
                job_title = item.xpath('./dt/a/text()')[0].strip()
                salary = item.xpath('./dd[@class="company"]/div/text()')[0].strip().replace('元', '')
                if '面议' not in salary:
                    salary, i_salary = self.get_format_salary(salary)
                job_area = item.xpath('./dd[@class="pay"]/text()')[0]
                link = item.xpath('./dt/a/@href')[0]
                temp_pub_date = item.xpath('./dd[@class="pub-time"]/span/text()')[0]
                pub_date = self.get_current_date(temp_pub_date)
                job_tags, job_addr, number_recruits, edu, ex, job_brief, age, company_name, company_scale, company_type, company_brief = self.second_request_parser(
                    link, url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '',
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': '',
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '',
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': '',
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_ganji(self, html, link=None, *args, **kwargs):
        """
        ganji网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        job_tags = etree_html.xpath('//ul[contains(@class,"welfare-line")]//li/span/text()')
        job_addr = etree_html.xpath('//div[contains(@class,"location-line")]/p/text()')
        if job_addr:
            job_addr = job_addr[0].strip().replace(' ', '')
        number_recruits = etree_html.xpath('//div[@class="description-label"]/span[1]/text()')
        if number_recruits:
            number_recruits = number_recruits[0]

        edu = etree_html.xpath('//div[@class="description-label"]/span[2]/text()')
        if edu:
            edu = edu[0].replace('学历', '')
        else:
            edu = '不限'
        ex = etree_html.xpath('//div[@class="description-label"]/span[3]/text()')
        if ex:
            ex = ex[0].replace('要求', '')
        else:
            ex = '不限'
        age = etree_html.xpath('//div[@class="description-label"]/span[4]/text()')
        if age:
            age = age[0].replace('年龄', '').replace('要求', '')
        else:
            age = ''
        job_brief = etree_html.xpath('//div[@class="description-content"]//text()')
        company_type = etree_html.xpath('//div[@class="introduce"]/span[3]/text()')
        if company_type:
            company_type = ''.join(company_type)
        temp1 = etree_html.xpath('//div[@class="introduce"]/span[1]/text()')
        temp2 = etree_html.xpath('//div[@class="introduce"]/span[2]/text()')
        if temp1:
            temp1 = temp1[0]
        else:
            temp1 = ''
        if temp2:
            temp2 = temp2[0]
        else:
            temp2 = ''
        company_scale = temp1 + '/' + temp2
        company_name = etree_html.xpath('//div[@class="company-info"]/h3/a/text()')
        if company_name:
            company_name = ''.join(company_name)
        company_brief = etree_html.xpath('//div[@class="info-text"]/div/text()')

        return job_tags, job_addr, number_recruits, edu, ex, job_brief, age, company_name, company_scale, company_type, company_brief

    def parser_ganji_it(self, html, url_name, url=None, *args, **kwargs):
        """
        赶集网it类解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[@id="list-job-id"]/dl')
        current_url = url.split('/zhao')[0]
        if response:
            for item in response:
                job_title = item.xpath('./dt/div[@class="fl ml-5"]/div/div[@class="fl j-title"]/a//text()')
                if job_title:
                    job_title = ''.join(job_title).strip()
                job_type = item.xpath('./dt/div[@class="fl ml-5"]/p[1]/em[1]/text()')
                if job_type:
                    job_type = job_type[0].strip().split('：')[1]
                salary = item.xpath('./dt/div[@class="fl ml-5"]/p[1]/em[3]/i//text()')
                if salary:
                    salary = ''.join(salary).strip()
                    salary, i_salary = self.get_format_salary(salary)
                job_area = item.xpath('./dt/div[@class="fl ml-5"]/p[2]/a/text()')
                if job_area:
                    job_area = job_area[0].split('：')[1]
                temp_pub_date = item.xpath('./dd/p[2]/text()')
                if temp_pub_date:
                    temp_pub_date = temp_pub_date[0].replace('月', '-').replace('日', '')
                    pub_date = self.get_current_date(temp_pub_date)
                temp_link = item.xpath('./dt/div[@class="fl ml-5"]/div/div[@class="fl j-title"]/a/@href')[0]
                link = current_url + temp_link
                job_tags, job_addr, number_recruits, edu, ex, job_brief, age, company_name, company_scale, company_type, company_brief = self.second_request_parser(
                    link, url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': '',
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': '',
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_ganji_it(self, html, link=None, *args, **kwargs):
        """
        ganji网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """

        job_tags, job_addr, number_recruits, edu, ex, job_brief, age, company_name, company_scale, company_type, company_brief = self.second_parser_ganji(
            html, link, *args, **kwargs)

        return job_tags, job_addr, number_recruits, edu, ex, job_brief, age, company_name, company_scale, company_type, company_brief

    def parser_58(self, html, url_name, url=None, *args, **kwargs):
        """
        58网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        # 58同城搜索的结果如果没有的话会只能推荐当地与搜索关键词无关的招聘信息

        index = kwargs.get('index')
        etree_html = etree.HTML(html)

        response = etree_html.xpath('//ul[@id="list_con"]/li[contains(@class,"job_item")]')
        if response:
            for item in response:
                link = item.xpath('./div[@class="item_con job_title"]/div[contains(@class,"job_name")]/a/@href')[0]
                temp_job_title = item.xpath(
                    './div[@class="item_con job_title"]/div[contains(@class,"job_name")]/a//text()')
                if temp_job_title:
                    temp_job_title = ''.join(temp_job_title).strip()
                    job_area, job_title = temp_job_title.split('|')
                    job_area = job_area.strip()
                    job_title = job_title.strip()
                salary = item.xpath('./div[@class="item_con job_title"]/p//text()')
                salary = ''.join(salary)
                if '面议' not in salary:
                    salary = salary.replace('元', '')
                    salary, i_salary = self.get_format_salary(salary)
                job_tags = item.xpath(
                    './div[@class="item_con job_title"]/div[contains(@class,"job_wel")]//span/text()')
                company_name = item.xpath('./div[@class="item_con job_comp"]/div[@class="comp_name"]/a/text()')[
                    0].strip()
                job_type = item.xpath('./div[@class="item_con job_comp"]/p[@class="job_require"]/span[1]/text()')[0]
                edu = item.xpath('./div[@class="item_con job_comp"]/p[@class="job_require"]/span[2]/text()')
                ex = item.xpath('./div[@class="item_con job_comp"]/p[@class="job_require"]/span[3]/text()')
                if edu:
                    edu = edu[0]
                else:
                    edu = ''
                if ex:
                    ex = ex[0]
                else:
                    ex = ''
                number_recruits, pub_date, job_addr, job_brief, company_brief, company_type, company_scale = self.second_request_parser(
                    link, url_name)

                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': company_brief,
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': company_brief,
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_58(self, html, link=None, *args, **kwargs):
        """
        58网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        number_recruits = etree_html.xpath('//span[@class="item_condition pad_left_none"]/text()')
        if number_recruits:
            number_recruits = number_recruits[0].strip().replace('招', '')
        temp_pub_date = etree_html.xpath('//span[@class="pos_base_num pos_base_update"]/span//text()')
        if temp_pub_date:
            temp_pub_date = ''.join(temp_pub_date).replace(' ', '')
            pub_date = self.get_current_date(temp_pub_date)
        else:
            pub_date = temp_pub_date
        job_addr = etree_html.xpath('//div[@class="pos-area"]//text()')
        if job_addr:
            job_addr = ''.join(job_addr).strip().replace(' ', '')
        job_brief = etree_html.xpath(
            '//div[@class="item_con pos-intro"]/div[contains(@class,"pos_description")]/div[@class="posDes"]/div[@class="des"]/text()')
        if not job_brief:
            job_brief = etree_html.xpath('//div[@class="des"]/text()')
        company_brief = etree_html.xpath(
            '//div[@class="item_con pos-intro"]/div[contains(@class,"comp_intro")]/div[@class="txt"]/div/div/div/p/text()')
        if not company_brief:
            company_brief = etree_html.xpath('//div[@class="shiji"]/p/text()')
        company_type = etree_html.xpath('//a[@class="comp_baseInfo_link"]/text()')
        if company_type:
            company_type = company_type[0]
        company_scale = etree_html.xpath('//p[@class="comp_baseInfo_scale"]/text()')
        if company_scale:
            company_scale = company_scale[0]
        return number_recruits, pub_date, job_addr, job_brief, company_brief, company_type, company_scale

    def parser_chinahr(self, html, url_name, url=None, *args, **kwargs):
        """
        中华英才网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[contains(@class,"jobList")]')
        if response:
            for item in response:
                pub_source = item.xpath('./ul[@class="l1"]/li[@class="fabu-date"]/span/text()')
                link = item.xpath('./@data-detail')[0]
                if pub_source:
                    # 发布于第三方网站，导致二级网站太多，无法一一分析，所以跳过解析
                    # print(pub_source)
                    continue
                if 'https://www.chinahr.com' not in link:
                    # print(link)
                    continue
                job_title = item.xpath('./ul[@class="l1"]/li[@class="job-name"]/text()')[0]
                pub_date = item.xpath('./ul[@class="l1"]/li[@class="fabu-date"]/text()')[0].strip()
                salary = item.xpath('./ul[@class="l2"]/li[@class="job-salary"]/text()')[0].strip().replace(' 元', '')
                salary, i_salary = self.get_format_salary(salary)
                temp_info = item.xpath('./ul[@class="l2"]/li[@class="job-address"]/text()')
                if temp_info:
                    job_area, ex, edu = temp_info[0].split('|')
                    job_area = job_area.strip()
                job_type = item.xpath('./ul[@class="l2"]/li[@class="job-address"]/span/text()')[0].replace('|',
                                                                                                           '').strip()
                company_name = item.xpath('./ul[@class="l2"]/li[@class="job-company"]/text()')[0].strip()
                job_tags = item.xpath('./ul[@class="l4"]/li[@class="job-fuli"]div/span/text()')
                number_recruits, job_brief, job_addr, company_brief, company_type, company_scale, job_evaluate = self.second_request_parser(
                    link, url_name)
                company_comment = []
                comment_url = 'https://chinahr.58.com/enterprise/name/%s/comment?version=1.0' % urllib.parse.quote(
                    company_name)
                req = requests.get(comment_url, headers=self.header, timeout=(3, 7), verify=False)
                res = req.content.decode('utf-8')
                comments = json.loads(res).get('data').get('comments')
                for com in comments:
                    if isinstance(com, dict):
                        c = com.get('content')
                        company_comment.append(c)
                    elif isinstance(com, str):
                        company_comment.append(com)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits,
                #     'job_evaluate': job_evaluate,
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': company_brief,
                #     'contact_person': '', 'company_comment': company_comment
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits,
                    'job_evaluate': job_evaluate,
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': '',
                    'contact_person': '', 'company_comment': comments
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_chinahr(self, html, link=None, *args, **kwargs):
        """
        中国英才网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """

        etree_html = etree.HTML(html)
        number_recruits = etree_html.xpath('//span[@class="job_addr"]/text()')
        if number_recruits:
            number_recruits = number_recruits[0].split('|')[3]
        job_addr = etree_html.xpath('//span[@class="job_address"]/text()')[0].strip().replace('\t', '')
        temp_company = etree_html.xpath('//span[@class="job_enterprisetype"]/text()')
        if temp_company:
            company_type, company_scale = temp_company[0].split('|')
        else:
            company_type = ''
            company_scale = ''
        job_brief = etree_html.xpath('//div[@class="desc_text"]/text()')
        company_brief = etree_html.xpath('//div[@class="details_text"]/text()')
        job_evaluate = etree_html.xpath('//span[@class="title-score-number"]/text()')
        if job_evaluate:
            job_evaluate = ''.join(job_evaluate)
        return number_recruits, job_brief, job_addr, company_brief, company_type, company_scale, job_evaluate

    def parser_chinahr_old(self, html, url_name, url=None, *args, **kwargs):
        """
        中华英才网旧版解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[@class="jobList"]')
        if response:
            for item in response:
                job_title = item.xpath('./ul/li[@class="l1"]/span[@class="e1"]/a//text()')
                if job_title:
                    job_title = ''.join(job_title).strip().replace(' ', '')
                temp_pub_date = item.xpath('./ul/li[@class="l1"]/span[@class="e2"]/text()')[0]
                pub_date = self.get_current_date(temp_pub_date)
                temp_info = item.xpath('./ul/li[@class="l2"]/span[@class="e1"]/text()')
                if temp_info:
                    temp_info = ''.join(temp_info)
                    job_area, e = temp_info.split(']')
                    job_area = job_area.replace('[', '').strip()[:-1]
                    ex, edu = e.split('/')
                    edu = edu.strip()
                    ex = ex.strip()
                salary = item.xpath('./ul/li[@class="l2"]/span[@class="e2"]/text()')[0] + '/月'
                salary, i_salary = self.get_format_salary(salary)
                company_info = item.xpath('./ul/li[@class="l2"]/span[@class="e3"]//em/text()')
                if company_info:
                    company_type, company_property, company_scale = company_info
                    if company_property and company_scale:
                        company_scale = company_scale + '/' + company_property
                link = item.xpath('./ul/li[@class="l1"]/span[@class="e1"]/a/@href')[0]
                company_name, job_tags, sex, driver_license, job_brief, company_brief, job_property = self.second_request_parser(
                    link, url_name)

                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': sex,
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': driver_license,
                #     'company_scale': company_scale, 'company_brief': company_brief,
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                    'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': sex,
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': driver_license,
                    'company_scale': company_scale, 'company_brief': company_brief,
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_chinahr_old(self, html, link=None, *args, **kwargs):
        """
        中华英才网旧版二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        job_tags = etree_html.xpath('//div[@class="job_fit_tags"]/ul//li/text()')
        sex = etree_html.xpath('//div[@class="job_intro_tag"]/span[1]/text()')
        if sex:
            sex = sex[0].split('：')[1]
        driver_license = etree_html.xpath('//div[@class="job_intro_tag"]/span[2]/text()')
        if driver_license:
            driver_license = driver_license[0].split('：')[1]
        job_brief = etree_html.xpath('//div[@class="job_intro_info"]/text()')
        company_brief = etree_html.xpath('//div[@class="company_service"]/text()')
        company_name = etree_html.xpath('//div[@class="job-detail-r"]/div[1]/h4/a/text()')[0]
        job_property = etree_html.xpath('//div[@class="job_require"]/span[3]/text()')[0]
        return company_name, job_tags, sex, driver_license, job_brief, company_brief, job_property

    def parser_job1001(self, html, url_name, url=None, *args, **kwargs):
        """
        一览英才网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[@class="search_data"]/ul[position()>1]')
        if response:
            for item in response:
                job_title = item.xpath('./li[@class="search_post"]/a//text()')
                if job_title:
                    job_title = ''.join(job_title).strip()
                company_name = item.xpath('./li[@class="search_company"]/a/text()')[0]
                salary = item.xpath('./li[@class="search_salary"]/text()')[0]
                salary, i_salary = self.get_format_salary(salary)
                link = item.xpath('./li[@class="search_post"]/a/@href')[0]
                job_tags, number_recruits, job_addr, job_area, job_brief, company_type, contact_person, age, major, pub_date, company_scale, edu, ex = self.second_request_parser(
                    link, url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': major,
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '',
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': '',
                #     'contact_person': contact_person, 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': major,
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': '',
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': '',
                    'contact_person': contact_person, 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_job1001(self, html, link=None, *args, **kwargs):
        """
        一览英才网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        company_scale = ''
        company_type = ''
        company_property = ''
        job_tags = etree_html.xpath(
            '//div[@class="company_tag"]//div[@class="tag_box"]/div[@class="tag_box_center"]/text()')
        edu = etree_html.xpath('//div[@class="job_info_interrelated"]/ul[1]/li[@class="info_left"]/span/text()')
        edu = ''.join(edu).strip() if edu else ''
        ex = etree_html.xpath('//div[@class="job_info_interrelated"]/ul[1]/li[@class="info_center"]/span/text()')
        ex = ''.join(ex).strip() if ex else ''
        pub_date = etree_html.xpath('//div[@class="job_info_interrelated"]/ul[1]/li[@class="info_right"]/span/text()')
        pub_date = ''.join(pub_date).strip() if pub_date else ''
        number_recruits = etree_html.xpath(
            '//div[@class="job_info_interrelated"]/ul[2]/li[@class="info_left"]/span/text()')
        number_recruits = ''.join(number_recruits).strip() if number_recruits else ''
        job_area = etree_html.xpath('//div[@class="job_info_interrelated"]/ul[2]/li[@class="info_right"]/span/text()')
        job_area = ''.join(job_area).strip() if job_area else ''
        age = etree_html.xpath('//div[@class="job_info_interrelated"]/ul[3]/li[@class="info_left"]/span/text()')
        age = ''.join(age).strip() if age else ''
        major = etree_html.xpath('//div[@class="job_info_interrelated"]/ul[3]/li[@class="info_center"]/span/text()')
        major = ''.join(major).strip() if major else ''
        job_brief = etree_html.xpath('//div[@class="job_depict"]/text()')
        company_info = etree_html.xpath(
            '//div[@class="main_right"]/div[1]/div[@class="job_info_detail"]/ul//li/text()')
        if len(company_info) == 4:
            company_scale = company_info[0] + '/' + company_info[1]
            company_type = company_info[2]
        elif len(company_info) == 2:
            company_type = company_info[0]
        else:
            for item in company_info:
                if '人' in item:
                    company_scale = item
                elif '企业' in item or '公司' in item:
                    company_property = item
                elif '-' in item:
                    continue
                elif item == '请选择':
                    continue
                else:
                    company_type = item
        if company_type == '请选择':
            company_type = ''
        if company_scale and company_property:
            company_scale = company_property + '/' + company_scale
        contact_person = \
            etree_html.xpath('//div[@class="main_right"]/div[2]/div[@class="job_info_detail"]/ul/li[1]/text()')
        if contact_person:
            contact_person = contact_person[0]
        else:
            contact_person = ''
        job_addr = etree_html.xpath('//div[@class="main_right"]/div[3]/div[@class="job_info_detail"]/ul/li[1]/text()')
        if job_addr:
            job_addr = job_addr[0].split('：')[1]
        else:
            job_addr = ''
        return job_tags, number_recruits, job_addr, job_area, job_brief, company_type, contact_person, age, major, pub_date, company_scale, edu, ex

    def parser_linkin(self, html, url_name, url=None, *args, **kwargs):
        """
        领英网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//li[contains(@class,"result-card")]')
        if response:
            for item in response:
                link = item.xpath('./a/@href')[0]
                job_title = item.xpath('./a/span/text()')[0]
                company_name = item.xpath('./div/h4/a/text()')[0]
                job_area = item.xpath('./div/div/span[1]/text()')[0]
                pub_date = item.xpath('./div/div/time/@datetime')[0]
                job_brief, job_level, job_type, company_type, job_property = self.second_request_parser(link, url_name)

                # print({
                #     'index': index, 'job_title': job_title, 'salary': '', 'job_type': job_type,
                #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                #     'edu': '', 'ex': job_level, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': '', 'company_brief': '',
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': '', 'job_type': job_type,
                    'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                    'edu': '', 'ex': job_level, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': '', 'company_brief': '',
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_linkin(self, html, link=None, *args, **kwargs):
        """
        领英网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        job_brief = etree_html.xpath('//div[@class="description__text description__text--rich"]//text()')
        job_level = etree_html.xpath('//ul[@class="job-criteria__list"]/li[1]/span/text()')[0]
        job_property = etree_html.xpath('//ul[@class="job-criteria__list"]/li[2]/span/text()')[0]
        job_type = etree_html.xpath('//ul[@class="job-criteria__list"]/li[3]/span/text()')[0]
        company_type = etree_html.xpath('//ul[@class="job-criteria__list"]/li[4]/span/text()')[0]
        return job_brief, job_level, job_type, company_type, job_property

    def parser_doumi(self, html, url_name, url=None, *args, **kwargs):
        """
        斗米网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[contains(@class,"jzList-item")]')
        if response:
            for item in response:
                job_title = item.xpath('./div[@class="jzList-txt"]/div/h3/a/text()')
                if job_title:
                    job_title = job_title[0].strip()
                job_property = item.xpath('./div[@class="jzList-txt"]/ul/li[1]/text()')[0].replace(' ', '').replace(
                    '\n',
                    '')
                job_type = item.xpath('./div[@class="jzList-txt"]/ul/li[2]/text()')[0]
                job_area = item.xpath('./div[@class="jzList-txt"]/ul/li[3]/text()')
                job_area = ''.join(job_area).replace(' ', '').replace('\n', '')
                number_recruits = item.xpath('./div[@class="jzList-txt"]/ul/li[4]/text()')[0]
                salary = item.xpath('./div[@class="jzList-salary"]/span[@class="money"]//text()')
                if salary:
                    salary = '￥' + ''.join(salary).strip().replace(' ', '').replace('\n', '').replace('元', '')
                link = item.xpath('./div[@class="jzList-txt"]/div/h3/a/@href')
                if link:
                    link = 'http://www.doumi.com' + link[0]
                sex, age, job_brief, job_addr, company_type, company_name, edu, ex = self.second_request_parser(link,
                                                                                                                url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': '', 'end_time': '', 'age': age, 'sex': sex,
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': '', 'job_link': link, 'number_recruits': number_recruits,
                #     'job_evaluate': '', 'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': '', 'company_brief': '', 'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': '', 'end_time': '', 'age': age, 'sex': sex,
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': '', 'job_link': link, 'number_recruits': number_recruits,
                    'job_evaluate': '', 'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': '', 'company_brief': '', 'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_doumi(self, html, link=None, *args, **kwargs):
        """
        斗米网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        edu = ''
        ex = ''
        sex = ''
        age = ''
        temp_info = etree_html.xpath('//ul[contains(@class,"jz-condition")]//text()')
        if len(temp_info) == 4:
            sex = temp_info[1]
            age = temp_info[2]
            edu = temp_info[3].strip()
            ex = temp_info[4].strip()
        else:
            for item in temp_info:
                if '经验' in item:
                    ex = item
                elif '以上' in item:
                    edu = item
                elif '岁' in item:
                    age = item
                elif '男' in item or '女' in item or '性别' in item:
                    sex = item.replace('性别', '')

        job_brief = etree_html.xpath('//p[@data-name="contentBox"]/text()')
        job_addr = etree_html.xpath('//div[@id="work-addr-fold"]/div[@class="jz-d-area"]/text()')
        if job_addr:
            job_addr = ''.join(job_addr).replace(' ', '').replace('\n', '').replace('\xa0', '')
        company_name = etree_html.xpath('//div[@class="cpy-name"]/a/text()')[0].strip()
        company_type = etree_html.xpath('//span[contains(text(),"行业类型")]/following-sibling::span[1]/text()')
        # company_type = etree_html.xpath('//span[contains(text(),"行业类型")]/../span[2]/text()')
        if company_type:
            company_type = company_type[0]
        else:
            company_type = ''
        return sex, age, job_brief, job_addr, company_type, company_name, edu, ex

    def parser_gongzuochong(self, html, url_name, url=None, *args, **kwargs):
        """
        工作虫网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        json_html = json.loads(html)
        data = json_html.get('data')
        if data:
            response = data.get('content')
            if response:
                for item in response:
                    job_title = item.get('title')
                    salary = item.get('payDesc')
                    job_type = item.get('categoriesDesc')
                    age = item.get('ageDesc')
                    sex = item.get('sexDesc')
                    job_area = item.get('districtsDesc')
                    job_link_args = item.get('cityObj').get('sName')
                    temp_pub_date = item.get('postTime')
                    if temp_pub_date:
                        pub_date = temp_pub_date.split('T')[0]
                    company_name = item.get('entName')
                    edu = item.get('educationDesc')
                    job_tags = []
                    tags = item.get('tagsArr')
                    for t in tags:
                        job_tags.append(t.get('text'))
                    city_code = item.get('cityObj').get('sName')
                    job_id = item.get('id')
                    link = 'http://www.gongzuochong.com/wapi/jobs/{c}/{id}'.format(c=city_code, id=job_id)
                    contact_person, ex, job_brief, job_addr, company_type, company_scale, company_brief = self.second_request_parser(
                        link, url_name)
                    link = 'http://www.gongzuochong.com/{c}/{tg}/{id}'.format(c=city_code, tg=job_link_args, id=job_id)
                    # print({
                    #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                    #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    #     'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    #     'company_name': company_name, 'company_type': company_type,
                    #     'company_status': '', 'phone': '', 'driver_license': '',
                    #     'company_scale': company_scale, 'company_brief': company_brief,
                    #     'contact_person': contact_person, 'company_comment': ''
                    # })
                    self.jobs.append({
                        'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                        'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                        'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                        'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                        'job_tags': job_tags, 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                        'company_name': company_name, 'company_type': company_type,
                        'company_status': '', 'phone': '', 'driver_license': '',
                        'company_scale': company_scale, 'company_brief': company_brief,
                        'contact_person': contact_person, 'company_comment': ''
                    })

            else:
                # 如果为空，将标志位置为真
                self.flag = True

    def second_parser_gongzuochong(self, html, link=None, *args, **kwargs):
        """
        工作虫网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        json_html = json.loads(html)
        data = json_html.get('data')
        if data:
            contact_person = data.get('contactName')
            ex = data.get('workingYearDesc')
            job_brief = data.get('content')
            company_info = data.get('entInfo')
            if company_info:
                company_type = company_info.get('industryDesc')
                company_property = company_info.get('entNatureDesc')
                company_scale = company_info.get('scalaDesc')
                job_addr = company_info.get('address')
                company_brief = company_info.get('description')
                company_scale = company_scale + '/' + company_property
        return contact_person, ex, job_brief, job_addr, company_type, company_scale, company_brief

    def parser_ofweek(self, html, url_name, url=None, *args, **kwargs):
        """
        ofweek人才网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        edu = ''
        ex = ''
        response = etree_html.xpath('//div[contains(@class,"tab_itme")]')
        if response:
            for item in response:
                job_title = item.xpath('./div[contains(@class,"itme_left")]/a//text()')
                if job_title:
                    job_title = ''.join(job_title)
                salary = item.xpath('./div[contains(@class,"itme_left")]/span/span/text()')[0]
                if '面议' not in salary:
                    salary = '￥' + salary.replace('k-', '-') + '/月'
                temp_info = item.xpath('./div[contains(@class,"itme_left")]/span/text()')
                if temp_info:
                    job_area, new_temp_info = ''.join(temp_info).strip().split(' ')
                    if new_temp_info:
                        edu, ex = new_temp_info.split('/')
                company_name = item.xpath('./div[contains(@class,"itme_mid")]/a/text()')[0]
                pub_date = item.xpath('./div[contains(@class,"itme_mid")]/span/text()')[0]
                link = item.xpath('./div[contains(@class,"itme_left")]/a/@href')
                if link:
                    link = 'https://hr.ofweek.com' + link[0]
                company_type, job_addr, job_property, number_recruits, age, job_brief = self.second_request_parser(link,
                                                                                                                   url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': '', 'company_brief': '',
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                    'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': '', 'sex': '',
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': '', 'job_link': link, 'number_recruits': '', 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': '', 'company_brief': '',
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_ofweek(self, html, link=None, *args, **kwargs):
        """
        OFweek人才网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        company_type = etree_html.xpath('//*[@id="content"]/div[2]/dl/dd/a/text()')
        if company_type:
            company_type = ''.join(company_type)
        job_addr = etree_html.xpath('//*[@id="content"]/div[2]/dl/dd/text()')
        if job_addr:
            job_addr = ''.join(job_addr).strip().replace('\n', '').replace('\t', '').replace(' ', '')
            job_addr = job_addr.split('：')[-1]
        job_property = etree_html.xpath('//*[@id="content"]/div[4]/div/div/p/span[5]/text()')[0]
        number_recruits = etree_html.xpath('//*[@id="content"]/div[4]/div/div/p/span[6]/text()')[0]
        age = etree_html.xpath('//*[@id="content"]/div[4]/div/div/p/span[7]/text()')[0]
        job_brief = etree_html.xpath('//div[contains(@class,"zwdesc")]/p/text()')
        return company_type, job_addr, job_property, number_recruits, age, job_brief

    def parser_telecomhr(self, html, url_name, url=None, *args, **kwargs):
        """
        通信人才网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//table[@class="joblist"]/tr[position()>1]')
        if response:
            for item in response:
                flag = item.xpath('./td[@colspan="6"]')
                if flag:
                    continue
                job_title = item.xpath('./td[1]/a/text()')[0]
                company_name = item.xpath('./td[2]/a/text()')[0]
                number_recruits = item.xpath('./td[3]/text()')[0]
                edu = item.xpath('./td[4]/text()')[0].strip()
                ex = item.xpath('./td[5]/text()')[0].strip()
                pub_date = item.xpath('./td[6]/text()')[0].strip()
                link = item.xpath('./td[1]/a/@href')[0]
                job_type, job_area, sex, age, lang, job_brief, company_scale, company_type, company_brief, salary = self.second_request_parser(
                    link, url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                #     'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': lang, 'job_brief': job_brief,
                #     'job_tags': '', 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': company_brief,
                #     'contact_person': '', 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    'job_property': '', 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': '', 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': company_brief,
                    'contact_person': '', 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_telecomhr(self, html, link=None, *args, **kwargs):
        """
        通信人才网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        company_scale = ''
        job_type = etree_html.xpath('//div[@class="qyzpxq_con_yqdy_left"]/p[1]/em/text()')[0]
        job_area = etree_html.xpath('//div[@class="qyzpxq_con_yqdy_left"]/p[2]/span/em/text()')[0].strip()
        salary = etree_html.xpath('//div[@class="qyzpxq_con_yqdy_left"]/p[3]/span[2]/i/text()')
        if salary:
            salary = ''.join(salary).replace(' ', '').replace('元', '')
            salary, i_salary = self.get_format_salary(salary)
        sex = etree_html.xpath('//div[@class="qyzpxq_con_yqdy_left"]/p[5]/span[1]/em/text()')[0].strip()
        age = etree_html.xpath('//div[@class="qyzpxq_con_yqdy_left"]/p[5]/span[2]/em/text()')[0]
        lang = etree_html.xpath('//div[@class="qyzpxq_con_yqdy_left"]/p[5]/span[1]/em/text()')[0].strip()
        job_brief = etree_html.xpath('//span[@class="wzzz"]/p/text()')
        company_type = etree_html.xpath('//div[@class="qyzpxq_con_yqdy_right"]/ul/li[1]/em/text()')[0]
        company_property = etree_html.xpath('//div[@class="qyzpxq_con_yqdy_right"]/ul/li[2]/em/text()')[0]
        temp_company_scale = etree_html.xpath('//div[@class="qyzpxq_con_yqdy_right"]/ul/li[4]/em/text()')[0]
        if company_property:
            company_scale += company_property + '/'
        if temp_company_scale:
            company_scale += temp_company_scale
        company_brief = etree_html.xpath('//div[@class="rz"]/following-sibling::span[1]/text()')
        return job_type, job_area, sex, age, lang, job_brief, company_scale, company_type, company_brief, salary

    def parser_tndbjob(self, html, url_name, url=None, *args, **kwargs):
        """
        天南地北人才网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[contains(@class,"search_job_list")]')
        if response:
            for item in response:
                company_scale = ''
                temp_company_scale = ''
                company_property = ''
                job_title = item.xpath('./div[@class="search_job_left_siaber"]/div[1]/a//text()')
                if job_title:
                    job_title = ''.join(job_title).strip()
                salary = item.xpath('./div[@class="search_job_left_siaber"]/div[2]/span[1]/text()')[0].replace('￥', '')
                if '面议' not in salary:
                    salary, i_salary = self.get_format_salary(salary)
                ex = item.xpath('./div[@class="search_job_left_siaber"]/div[2]/span[2]/em/text()')[0].strip().replace(
                    '经验',
                    '')
                edu = item.xpath('./div[@class="search_job_left_siaber"]/div[2]/span[4]/em/text()')[0].strip().replace(
                    '学历',
                    '')
                job_area = item.xpath('./div[@class="search_job_left_siaber"]/div[2]/span[6]/em/text()')[0]
                company_name = item.xpath('./div[@class="company_det_c_name"]/div[1]/a/text()')[0]
                temp_company_info = item.xpath('./div[@class="company_det_c_name"]/div[2]/div[1]/text()')
                company_type = temp_company_info[0]
                if len(temp_company_info) > 1:
                    company_property = temp_company_info[1]
                    temp_company_scale = temp_company_info[-1]
                    if company_property:
                        company_scale += company_property
                    if company_property != temp_company_scale:
                        if temp_company_scale:
                            company_scale += '/' + temp_company_scale
                link = item.xpath('./div[@class="search_job_left_siaber"]/div[1]/a/@href')[0]
                job_brief, marriage, contact_person, job_tags, age, sex, number_recruits, pub_date, company_brief, job_property = self.second_request_parser(
                    link, url_name)

                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits,
                #     'job_evaluate': '', 'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': '', 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': company_brief,
                #     'contact_person': contact_person, 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '',
                    'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': '', 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits,
                    'job_evaluate': '', 'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': '', 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': company_brief,
                    'contact_person': contact_person, 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_tndbjob(self, html, link=None, *args, **kwargs):
        """
        天南地北人才网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        job_brief = etree_html.xpath('//div[@class="Job_Description"]//text()')
        marriage = etree_html.xpath(
            '//div[contains(@class,"Company_Basic_information_list") and position()=1]/div/span[contains(text(),"婚")]/text()')
        if marriage:
            marriage = ''.join(marriage)
        else:
            marriage = ''
        number_recruits = etree_html.xpath(
            '//div[contains(@class,"Company_Basic_information_list") and position()>1]/div/span[contains(text(),"招聘")]/text()')
        if number_recruits:
            number_recruits = ''.join(number_recruits)
        else:
            number_recruits = ''
        contact_person = etree_html.xpath('//div[@class="jobshow_telman"]/text()')[0]
        job_tags = etree_html.xpath('//div[@class="Company_Basic_information_r mt20"]//span/text()')
        age = etree_html.xpath(
            '//div[contains(@class,"Company_Basic_information_list") and position()=1]/div/span[contains(text(),"年龄")]/text()')
        if age:
            age = age[0].replace('年龄', '')
        sex = etree_html.xpath(
            '//div[contains(@class,"Company_Basic_information_list") and position()=1]/div/span[contains(text(),"性别")]/text()')
        if sex:
            sex = sex[0].replace('性别', '')
        pub_date = etree_html.xpath('//div[contains(@class,"Company_post_State_time")]/text()')
        if pub_date:
            pub_date = ''.join(pub_date).split('更新')[0].strip()
        company_brief = etree_html.xpath('//div[@id="job_content"]//text()')
        job_property = etree_html.xpath('//span[@class="yun_com_fl_dy "]/text()')
        if job_property:
            job_property = job_property[0]
        else:
            job_property = ''
        return job_brief, marriage, contact_person, job_tags, age, sex, number_recruits, pub_date, company_brief, job_property

    def parser_wztxjob(self, html, url_name, url=None, *args, **kwargs):
        """
        网招天下人才网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        # 网招天下网与天南地北人才网网站结构相同，直接分发给天南地北人才网解析部分
        self.parser_tndbjob(html, 'parser_tndbjob', url=None)

    def parser_qcrcw(self, html, url_name, url=None, *args, **kwargs):
        """
        前程人才网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :return:
        """
        # 前程人才网与天南地北人才网网站结构相同，直接分发给天南地北人才网解析部分
        self.parser_tndbjob(html, 'parser_tndbjob', url=None)

    def parser_pcbjob(self, html, url_name, url=None, *args, **kwargs):
        """
        pcb人才网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :return:
        """
        # pcb人才网与天南地北人才网网站结构相同，直接分发给天南地北人才网解析部分
        self.parser_tndbjob(html, 'parser_tndbjob', url=None)

    def parser_baidu(self, html, url_name, url=None, *args, **kwargs):
        """
        百度百聘网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        res = json.loads(html)
        data = res.get('data')
        args_urlencode = args[0]
        if data:
            response = data.get('disp_data')
            if response:
                for item in response:
                    # 如果已经有过针对该职位来源网站的分析爬取则跳过
                    source = item.get('sourcelink')
                    if source:
                        source_url = source.split('.', 1)[1]
                        source_url = source_url.replace('/', '')
                        already_sites = self.get_already_crawl_site()
                        already_sites.remove('baidu.com')
                        if source_url in already_sites:
                            continue
                    company_scale = ''
                    job_area = ''
                    job_title = item.get('title')
                    job_property = item.get('type')
                    job_type = item.get('jobfirstclass')
                    job_tags = item.get('ori_welfare')
                    ex = item.get('ori_experience')
                    edu = item.get('ori_education')
                    sex = item.get('ori_sex')
                    age = item.get('ori_age')
                    pub_date = item.get('lastmod')
                    salary = item.get('salary')
                    salary, i_salary = self.get_format_salary(salary)
                    phone = item.get('phone')
                    if not phone:
                        phone = ''
                    company_name = item.get('commonname')
                    company_type = item.get('second_level_label')
                    company_property = item.get('ori_employertype')
                    company_brief = item.get('companydescription')
                    job_addr = item.get('companyaddress')
                    temp_company_scale = item.get('ori_size')
                    number_recruits = item.get('number')
                    end_time = item.get('enddate')
                    province = item.get('province')
                    city = item.get('city')
                    area = item.get('area')
                    if province:
                        job_area += province
                    if city:
                        if province != city:
                            job_area += city
                    if area:
                        job_area += area
                    if company_property:
                        company_scale += company_property + '/'
                    if temp_company_scale:
                        company_scale += temp_company_scale
                    url_id = item.get('loc')
                    quote_city = urllib.parse.quote(city)
                    link = 'https://zhaopin.baidu.com/szzw?id={id}&query={q}&city={c}&is_promise=0&is_direct=1&vip_sign=&asp_ad_job='.format(
                        id=url_id, c=quote_city, q=args_urlencode)
                    job_addr2, job_brief = self.second_request_parser(link, url_name)
                    if not job_addr:
                        job_addr = job_addr2
                    # print({
                    #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': end_time, 'age': age, 'sex': sex,
                    #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                    #     'company_name': company_name, 'company_type': company_type,
                    #     'company_status': '', 'phone': phone, 'driver_license': '',
                    #     'company_scale': company_scale, 'company_brief': company_brief,
                    #     'contact_person': '', 'company_comment': ''
                    # })
                    self.jobs.append({
                        'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                        'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                        'job_addr': job_addr, 'pub_date': pub_date, 'end_time': end_time, 'age': age, 'sex': sex,
                        'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                        'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                        'company_name': company_name, 'company_type': company_type,
                        'company_status': '', 'phone': phone, 'driver_license': '',
                        'company_scale': company_scale, 'company_brief': company_brief,
                        'contact_person': '', 'company_comment': ''
                    })

            else:
                # 如果为空，将标志位置为真
                self.flag = True

    def second_parser_baidu(self, html, link=None, *args, **kwargs):
        """
        百度百聘网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)
        job_brief = etree_html.xpath('//div[@class="job-detail"]//text()')
        job_addr = etree_html.xpath('//p[@class="job-addr-txt" and position()=2]/text()')
        if job_addr:
            job_addr = job_addr[0]
        return job_addr, job_brief

    def parser_baidu_jianzhi(self, html, url_name, url=None, *args, **kwargs):
        """
        百度百聘网兼职类解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :param args:
        :param kwargs:
        :return:
        """
        index = kwargs.get('index')
        res = json.loads(html)
        data = res.get('data')
        args_urlencode = args[0]
        if data:
            response = data.get('disp_data')
            if response:
                for item in response:
                    # 如果已经有过针对该职位来源网站的分析爬取则跳过
                    source = item.get('sourcelink')
                    if source:
                        source_url = source.split('.', 1)[1]
                        source_url = source_url.replace('/', '')
                        already_sites = self.get_already_crawl_site()
                        already_sites.remove('baidu.com')
                        if source_url in already_sites:
                            continue
                    job_title = item.get('title')
                    job_property = item.get('ftype')
                    job_type = item.get('type')
                    job_tags = item.get('welfare')
                    if job_tags:
                        job_tags = job_tags.split('+')
                    else:
                        job_tags = ''
                    sex = item.get('sex') if item.get('sex') else ''
                    age = item.get('age_need') if item.get('age_need') else ''
                    pub_date = item.get('lastmod')
                    number_recruits = item.get('number')
                    salary = item.get('salary')
                    salary = '￥' + salary.replace('元', '')
                    company_name = item.get('employer')
                    company_brief = item.get('description')
                    job_addr = item.get('address')
                    end_time = item.get('deaddate') if item.get('deaddate') else ''
                    job_area = ''
                    city = item.get('city')
                    area = item.get('area')
                    if city:
                        job_area += city
                    if area:
                        if city != area:
                            job_area += area
                    url_id = item.get('loc')
                    quote_city = urllib.parse.quote(city)
                    link = 'https://zhaopin.baidu.com/jzzw?id={id}&query={q}&city={c}'.format(id=url_id, c=quote_city,
                                                                                              q=args_urlencode)

                    job_addr2, job_brief = self.second_request_parser(link, url_name)
                    if not job_addr:
                        job_addr = job_addr2
                    # print({
                    #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                    #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': end_time, 'age': age, 'sex': sex,
                    #     'edu': '', 'ex': '', 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                    #     'company_name': company_name, 'company_type': '',
                    #     'company_status': '', 'phone': '', 'driver_license': '',
                    #     'company_scale': '', 'company_brief': company_brief,
                    #     'contact_person': '', 'company_comment': ''
                    # })
                    self.jobs.append({
                        'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
                        'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                        'job_addr': job_addr, 'pub_date': pub_date, 'end_time': end_time, 'age': age, 'sex': sex,
                        'edu': '', 'ex': '', 'marriage': '', 'lang': '', 'job_brief': job_brief,
                        'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                        'company_name': company_name, 'company_type': '',
                        'company_status': '', 'phone': '', 'driver_license': '',
                        'company_scale': '', 'company_brief': company_brief,
                        'contact_person': '', 'company_comment': ''
                    })

            else:
                # 如果为空，将标志位置为真
                self.flag = True

    def second_parser_baidu_jianzhi(self, html, link=None, *args, **kwargs):
        """
        百度百聘网兼职类二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        job_addr, job_brief = self.second_parser_baidu(html, link, *args, **kwargs)
        return job_addr, job_brief

    def parser_jiaoshi(self, html, url_name, url=None, *args, **kwargs):
        """
        中国教师人才网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[contains(@class,"J_jobsList")]')
        if response:
            for item in response:
                job_title = item.xpath('./div[2]/div[@class="td-j-name"]/a/@title')[0]
                company_name = item.xpath('./div[3]/a/text()')[0]
                salary = ''.join(item.xpath('./div[4]/text()'))
                if '面议' not in salary:
                    salary = '￥' + salary.replace('K-', '-')
                job_tags = item.xpath('./div[@class="detail"]/div[@class="ltx"]/div[2]//div/text()')
                info = item.xpath('./div[@class="detail"]/div[@class="ltx"]/div[1]//text()')
                edu = info[0].split('：')[1]
                ex = info[2].split('：')[1]
                job_property = info[4].split('：')[1]
                number_recruits = info[6].split('：')[1]
                job_area = info[-1].split('：')[1]
                link = item.xpath('./div[2]/div[@class="td-j-name"]/a/@href')[0]
                pub_date, sex, age, job_addr, job_brief, contact_person, phone, company_scale, company_type = self.second_request_parser(
                    link, url_name)
                # print({
                #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '教职教师',
                #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                #     'company_name': company_name, 'company_type': company_type,
                #     'company_status': '', 'phone': phone, 'driver_license': '',
                #     'company_scale': company_scale, 'company_brief': '',
                #     'contact_person': contact_person, 'company_comment': ''
                # })
                self.jobs.append({
                    'index': index, 'job_title': job_title, 'salary': salary, 'job_type': '教职教师',
                    'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
                    'job_addr': job_addr, 'pub_date': pub_date, 'end_time': '', 'age': age, 'sex': sex,
                    'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
                    'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
                    'company_name': company_name, 'company_type': company_type,
                    'company_status': '', 'phone': phone, 'driver_license': '',
                    'company_scale': company_scale, 'company_brief': '',
                    'contact_person': contact_person, 'company_comment': ''
                })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_jiaoshi(self, html, link=None, *args, **kwargs):
        """
        中国教师人才网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        company_scale = ''
        etree_html = etree.HTML(html)
        pub_date = etree_html.xpath('//div[@class="timebg"]/text()')[0]
        sex = etree_html.xpath('//div[@class="item"]/div[8]/text()')[0]
        age = etree_html.xpath('//div[@class="item"]/div[10]/text()')[0]
        job_addr = etree_html.xpath('//div[@class="add"]/text()')[0]
        contact_person = etree_html.xpath('//div[@class="contact"]/div[2]/text()')
        if contact_person:
            contact_person = contact_person[0].split('：')[1].strip()
        phone = etree_html.xpath('//div[@class="contact"]/div[4]/span/text()')[0]
        job_brief = etree_html.xpath('//div[@class="describe"]/div[2]/text()')
        company_property = etree_html.xpath('//div[@class="cominfo link_gray6"]/div[3]/text()')
        company_type = etree_html.xpath('//div[@class="cominfo link_gray6"]/div[4]/text()')[0]
        temp_company_scale = etree_html.xpath('//div[@class="cominfo link_gray6"]/div[5]/text()')
        if company_property:
            company_scale += company_property[0]
        if temp_company_scale:
            company_scale += '/' + temp_company_scale[0]
        return pub_date, sex, age, job_addr, job_brief, contact_person, phone, company_scale, company_type

    def parser_xxx(self, html, url_name, url=None, *args, **kwargs):
        """
        网解析
        :param url: 网址
        :param html:网站源码
        :param url_name: 网站别名
        :return:
        """
        index = kwargs.get('index')
        etree_html = etree.HTML(html)
        response = etree_html.xpath('//div[contains(@class,"jobList")]')
        if response:
            for item in response:
                job_title = item.xpath('./')
            # self.jobs.append({
            #     'index': index, 'job_title': job_title, 'salary': salary, 'job_type': job_type,
            #     'job_property': job_property, 'job_status': '', 'job_area': job_area, 'major': '',
            #     'job_addr': job_addr, 'pub_date': pub_date, 'end_time': end_time, 'age': age, 'sex': sex,
            #     'edu': edu, 'ex': ex, 'marriage': '', 'lang': '', 'job_brief': job_brief,
            #     'job_tags': job_tags, 'job_link': link, 'number_recruits': number_recruits, 'job_evaluate': '',
            #     'company_name': company_name, 'company_type': company_type,
            #     'company_status': '', 'phone': phone, 'driver_license': '',
            #     'company_scale': company_scale, 'company_brief': company_brief,
            #     'contact_person': '', 'company_comment': ''
            # })

        else:
            # 如果为空，将标志位置为真
            self.flag = True

    def second_parser_xxx(self, html, link=None, *args, **kwargs):
        """
        网二级网页
        :param html: 二级网页源码
        :param link: 二级网页的url
        :param args:
        :param kwargs:
        :return:
        """
        etree_html = etree.HTML(html)

    def run(self):
        try:
            sched = self.get_scheduler()
            sched.add_job(save_redis, 'interval', seconds=INTERVAL, args=[self.jobs])
            sched.start()
            self.request_site()
        except KeyboardInterrupt as e:
            # 如果中断程序，把已获取到的数据先保存
            print(e)
            save_redis(self.jobs)
            CRAWL_LOG.error('entered keyboard ctrl + c')
            sys.exit()
        return self.jobs


class GeventCrawl(BaseCrawl):
    """协程式"""

    def request_site(self):
        """
        协程式遍历请求所有的url
        :return:
        """
        tasks = []
        gevent_pool = Pool(GEVENT_POOL)
        for urls in self.request_urls:
            url = urls.get('url')
            url_name = urls.get('type')
            domain = url_name.split('_', 1)[1]
            print('正在爬取 %s 网站的数据' % domain)
            # args = urls.get('args')
            # if not args:
            #     args = self.get_args()
            for args in self.search_args:
                proxy = self.get_proxy()
                args_urlencode = urllib.parse.quote(args)
                task = gevent_pool.spawn(self.request_url, url, url_name, proxy, args_urlencode, args)
                tasks.append(task)
        done = gevent.joinall(tasks)
        if done:
            gevent.killall(tasks)
        data = duplicate_removal(self.jobs)
        self.jobs = data

    def request_format_site(self, target_urls, url_name, proxy, args_urlencode, i, index):
        """
        请求格式化好的所有url
        :param target_urls: 所有目标url
        :param url_name: url别名
        :param proxy: 代理
        :param args_urlencode: url编码后后的搜索关键词
        :param i: 页码
        :param index: 搜索关键词
        :return:
        """
        # 遍历请求
        # print(target_urls)
        tasks = []
        try:
            for target_url in target_urls:
                task = gevent.spawn(self.request_format_url, target_url, url_name, proxy, args_urlencode, i, index)
                tasks.append(task)
            done = gevent.joinall(tasks)
            if done:
                gevent.killall(tasks)
        except BaseException as e:
            print(e)
            CRAWL_LOG.error('request exception occurred:%s' % e)

    def get_scheduler(self):
        cls = GeventScheduler
        return cls()


class ThreadPoolCrawl(BaseCrawl):
    """线程池式"""

    def request_site(self):
        """
        线程池式的请求所有url
        :return:
        """

        thread = ThreadPoolExecutor(THREAD_POOL)
        tasks = []
        for urls in self.request_urls:
            url = urls.get('url')
            url_name = urls.get('type')
            domain = url_name.split('_', 1)[1]
            print('正在爬取 %s 网站的数据' % domain)
            # args = urls.get('args')
            # if not args:
            #     args = self.get_args()
            for args in self.search_args:
                proxy = self.get_proxy()
                args_urlencode = urllib.parse.quote(args)
                task = thread.submit(self.request_url, url, url_name, proxy, args_urlencode, args)
                tasks.append(task)
        wait(tasks)
        data = duplicate_removal(self.jobs)
        self.jobs = data

    def request_format_site(self, target_urls, url_name, proxy, args_urlencode, i, index):
        """
        请求格式化好的所有url
        :param target_urls: 所有目标url
        :param url_name: url别名
        :param proxy: 代理
        :param args_urlencode: url编码后后的搜索关键词
        :param i: 页码
        :param index: 搜索关键词
        :return:
        """
        thread = ThreadPoolExecutor(THREAD_POOL)
        # 遍历请求
        # print(target_urls)
        try:
            tasks = [thread.submit(self.request_format_url, url, url_name, proxy, args_urlencode, i, index) for url in
                     target_urls]
            wait(tasks)
        except BaseException as e:
            print(e)
            CRAWL_LOG.error('request exception occurred:%s' % e)

    def get_scheduler(self):
        cls = BackgroundScheduler
        return cls()


class ThreadPoolAsynicCrawl(BaseCrawl):
    """线程池+异步"""

    def request_site(self):
        """
        线程池+异步的方式遍历请求所有的url
        :return:
        """
        loop = asyncio.get_event_loop()
        thread = ThreadPoolExecutor(THREAD_POOL)
        tasks = []
        for urls in self.request_urls:
            url = urls.get('url')
            url_name = urls.get('type')
            domain = url_name.split('_', 1)[1]
            print('正在爬取 %s 网站的数据' % domain)
            # args = urls.get('args')
            # if not args:
            #     args = self.get_args()
            for args in self.search_args:
                proxy = self.get_proxy()
                args_urlencode = urllib.parse.quote(args)
                task = loop.run_in_executor(thread, self.request_url, url, url_name, proxy, args_urlencode, args)
                tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))
        # 异步操作会有重复的数据,去重
        data = duplicate_removal(self.jobs)
        self.jobs = data

    def request_format_site(self, target_urls, url_name, proxy, args_urlencode, i, index):
        """
        请求格式化好的所有url
        :param target_urls: 所有目标url
        :param url_name: url别名
        :param proxy: 代理
        :param args_urlencode: url编码后后的搜索关键词
        :param i: 页码
        :param index: 搜索关键词
        :return:
        """
        # 异步的loop下不能再开loop，所以直接继承父类的该方法
        super(ThreadPoolAsynicCrawl, self).request_format_site(target_urls, url_name, proxy, args_urlencode, i, index)

    def get_scheduler(self):
        """
        获取一个调取器类
        :return:
        """
        cls = AsyncIOScheduler
        return cls()


def duplicate_removal(lists):
    """
    对数据去重
    :return:
    """
    new_jobs = []
    for item in lists:
        if item not in new_jobs:
            new_jobs.append(item)
    return new_jobs


def save_redis(jobs, key=None):
    """
    存储到redis
    :param jobs: 职位数据
    :param key: redis的key
    :return:
    """
    conn = redis.Redis(connection_pool=POOL2)
    if not key:
        key = 'jobs'
    if jobs:
        # 检测是否已有值
        cont = conn.get(key)
        if cont:
            cont = eval(cont)
            jobs.extend(cont)
        jobs = duplicate_removal(jobs)
        print('数据库内已存有 %s 个职位信息' % len(jobs))
        conn.set(key, str(jobs))


def save_url_redis(se, key=None):
    """
    存储到redis
    :param se: 集合
    :param key: redis的key
    :return:
    """
    conn = redis.Redis(connection_pool=POOL)
    cont = ''
    if not key:
        key = 'target_urls'
    if se:
        # 检测是否已有值
        try:
            cont = conn.get(key)
        except redis.exceptions.ConnectionError as e:
            print('协程因为并发性能太强导致并发量太大,redis数据库无法承受,请去掉一部分待爬取网站或者改用线程池的方式', e)
            gevent.sleep(5)
        if cont:
            cont = eval(cont)
            se.update(cont)
        conn.set(key, str(se))
        if key == 'target_urls':
            print('数据库内存有 %s 个目标url待爬取' % len(se))
        if key == 'market_urls':
            print('已爬取了 %s 个目标url' % len(se))


def save_market_page_redis(page, key=None):
    """
    存储到redis
    :param page: 已爬取的页码
    :param key: redis的key
    :return:
    """
    conn = redis.Redis(connection_pool=POOL)
    if not key:
        key = 'page'
    if page:
        conn.set(key, str(page))


def get_market_page_redis(key=None):
    """
    存储到redis
    :param page: 已爬取的页码
    :param key: redis的key
    :return:
    """
    conn = redis.Redis(connection_pool=POOL)
    if not key:
        key = 'page'
    page = conn.get(key)
    return eval(page)


def get_url_redis(key=None):
    """
    从redis获取值
    :param key: redis的key
    :return:
    """
    conn = redis.Redis(connection_pool=POOL)
    cont = ''
    if not key:
        key = 'target_urls'
    try:
        cont = conn.get(key)
    except redis.exceptions.ConnectionError as e:
        print('协程因为并发性能太强导致并发量太大,redis数据库无法承受,请去掉一部分待爬取网站或者改用线程池的方式', e)
    if cont:
        urls = eval(cont)
        print('数据库内存有 %s 个目标url待爬取' % len(urls))
        return urls


def main(cls=None):
    """
    主函数
    :param cls: 不同的爬虫类名
    :return:
    """
    if not cls:
        cls = GeventCrawl
    # 实例化proxy类，方便后期单例模式调用
    proxy_obj = ProxyHandler()
    proxies = duplicate_removal(proxy_obj.get_proxies())

    # 实例化目标url类，方便后期单例模式调用
    target_obj = TargetUrlHandler()
    target_urls = target_obj.get_target_urls()
    print('开始爬取.........')
    start = time.time()
    crawl = cls()
    crawl.proxy_list = proxies  # 测试时防止代理报错影响结果可以先注释掉

    crawl.target_urls = target_urls  # 测试时防止代理报错影响结果可以先注释掉
    result = crawl.run()
    save_redis(result)  # 存入redis数据库
    # print(result)
    end = time.time() - start
    print('总共用时：%s' % end)


if __name__ == '__main__':
    
    main()  # 协程方式, 测试时需要查看报错结果可以使用gevent协程的方法
    # main(ThreadPoolCrawl)  # 线程池的方式
    # main(ThreadPoolAsynicCrawl)  # 线程池+异步的方式

    # t = get_url_redis()
    # m = get_url_redis('market_urls')
    # print(t,len(t))
    # print(m,len(m))
