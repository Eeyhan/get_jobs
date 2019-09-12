#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : geek_yang
# @File    : tests.py

import requests
import js2py


def main():
    response = requests.get("http://www.66ip.cn/mo.php?tqsl=1024",
                            headers={
                                "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
                            })
    # 保存第一段cookie
    cookie = response.headers["Set-Cookie"]
    js = response.text.encode("utf8").decode("utf8")
    # 删除script标签并替换eval。
    js = js.replace("<script>", "").replace("</script>", "").replace("{eval(", "{var data1 = (").replace(chr(0),
                                                                                                         chr(32))
    # 使用js2py的js交互功能获得刚才赋值的data1对象
    context = js2py.EvalJs()
    context.execute(js)
    js_temp = context.data1

    # 找到cookie生成语句的起始位置
    index1 = js_temp.find("document.")
    index2 = js_temp.find("};if((")
    # 故技重施，替换代码中的对象以获得数据
    js_temp = js_temp[index1:index2].replace("document.cookie", "data2")
    context.execute(js_temp)
    data = context.data2

    # 合并cookie，重新请求网站。
    cookie += ";" + data
    response = requests.get("http://www.66ip.cn/mo.php?tqsl=1024", headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
        "cookie": cookie,
    })
    return response


if __name__ == "__main__":
    res = main()
    print(res.content.decode('utf-8'))
