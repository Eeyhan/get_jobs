# get_jobs

+ 爬取各大招聘网站的数据

# 声明：

### 其自身并不是招聘平台，仅供个人学习使用，本人严格保证遵纪守法，不以爬虫的手段侵害他人网络服务器，且保证爬取到的数据永远不以商业形式售卖

### 二次开发者请遵纪守法，且爬到的数据永远不以商业形式售卖，否则后果自负

+ 说明：如果遇到这个提示：

	“UserWarning: libuv only supports millisecond timer resolution; all times less will be set to 1 ms  self.timer = get_hub().loop.timer(seconds or 0.0, ref=ref, priority=priority)”
	
	* 这是一个gevent的已知bug，对程序运行没有任何影响，可以忽略

## 更新进度：

+ 2019/9/14更新：

	* 优化协程并发问题
	* 优化断点续爬功能
	* 优化已知的小bug

+ 2019/9/12更新：

	* 支持定时自动存储数据
	* 添加日志
	* 优化断点续爬功能

+ 2019/9/11更新：

	* 优化页码问题，去除无效（不必要）的页码，节省爬取时间
	* 支持断点续爬功能
	* 优化爬取时间，以协程，线程池，线程池+异步的三种方式提升速度(可以自行选择不同的运行方式)
	

## 简介：

+ 利用爬虫技术抓取各大平台的招聘数据，然后存储到服务器的数据库内，用于学术分析

+ 已抓取以下招聘平台的公开数据(对以下网站并无恶意，以学术研究分析为目的)			
    	
	* 看准网
	* boss直聘
	* 前程无忧
	* 智联招聘								
	* 智联卓聘
	* 拉钩				
	* 大街网
	* 智通人才网
	* 中国人才热线
	* 应届生求职网
	* 卓博人才
	* 教师招聘网
	* 中国教师人才网
	* 百姓网招聘
	* 智通硕博网
	* 猎聘
	* 赶集招聘
	* 赶集招聘it类
	* 58招聘
	* 中华英才网新版
	* 中华英才网旧版
	* 一览英才网
	* 领英
	* 斗米
	* 工作虫
	* OFweek人才网
	* 通信人才网
	* 天南地北人才网			
	* 网招天下人才网
	* 前程人才网
	* pcb人才网
	* 百度百聘全职类
	* 百度百聘兼职类
	* (更多待补充......)

## 主要功能：

+ 爬虫部分：
    * 使用requests先实现爬虫，UA，IP代理
    * IP代理用爬虫实现每天自动更新，自动检测有效性
    * 使用IO模型+线程池，进程池加速
    * 破解反爬机制：登录账户，验证码，滑动验证码，图形验证码
	* 爬取各大招聘网站的数据，存入数据库
	* 使用Apscheduler定时任务框架自动定时存储数据
	
	
+ 爬取的数据存入mongodb或者redis数据库内

## 待更新功能：

+ 后期考虑借用elasticsearch做数据索引

## 开发环境：

+ Python3.7
+ lxml
+ beautifulsoup
+ mysql/mongodb/redis

+ 进入根目录，使用  ``pip install -r requirements.txt`` 安装相关模块或包

+ 注：可能有忘掉的模块，如果提示未安装某个第三方包或模块，自行安装即可

## 文件说明：

+ │  config.py			# 配置文件
+ │  v1.py				# 主程序文件
+ │  logger.py			# 日志文件
+ │  __init__.py
  │
+ │─proxy				# 代理相关文件夹
+ │   │  headers.py		# 请求头文件
+ │   │  main.py		# flask入口文件
+ │   │  proxy.py		# 爬取代理主程序文件
+ │   └─ __init__.py
+ │
+ │
+ └─log					# 日志文件夹
+    └─ crawling.log	# 存入的日志文件

## 运行说明：

+ 1.自行配置redis数据库，如果不想用redis数据库可自行修改其他数据库

+ 2。在运行v1.py文件之前，请使用浏览器访问boss直聘网，利用抓包工具将__zp_stoken__字段拿到，替换掉config.py里的__zp_stoken__字段即可(因为boss直聘更新，目前暂时未找到boss直聘的token来源,希望有能力的老哥可以解决这个问题)

+ 3.直接运行v1.py文件即可，其有三种运行方式：

	* main()  # 协程方式, 测试时需要查看报错结果可以使用gevent协程的方法
    * main(ThreadPoolCrawl)  # 线程池的方式
    * main(ThreadPoolAsynicCrawl)  # 线程池+异步的方式
	
	默认是协程方式，建议选用线程池+异步的方式，需要用哪种方式取消该注释即可
	
+ 4.如果需要解决IP封禁问题：先进入proxy文件夹，运行proxy.py爬取好代理并组成代理池，再运行v1.py文件即可  


+ 更多配置说明请自行阅读config.py的文件说明，支持自定制，自添加，二次开发（再次强调，请遵纪手法，否则后果自负）

+ 有问题请提交issue，有空我会更新

### 运行结果：

![启动运行](https://raw.githubusercontent.com/Eeyhan/pictures/master/job_1.png)
![运行中](https://raw.githubusercontent.com/Eeyhan/pictures/master/job_2.png)
![redis数据库结果](https://raw.githubusercontent.com/Eeyhan/pictures/master/job_3.png)

## 更多代理池说明：[IPproxy](https://github.com/Eeyhan/IPproxy "IPproxy")

## 个人的技术文章请移步：[博客文章](https://www.cnblogs.com/Eeyhan/ "博客文章")
