import re
import time
import json
import http.cookiejar
import time
import urllib.request
import urllib.parse

#获取存在本机的cookie消息
cookie = http.cookiejar.CookieJar()
#自定义opener,并将opener跟CookieJar对象绑定
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
#安装opener,此后调用urlopen()时都会使用安装过的opener对象
urllib.request.install_opener(opener)

home_url = 'http://bj.lianjia.com'
auth_url = 'https://passport.lianjia.com/cas/login?service=http%3A%2F%2Fbj.lianjia.com%2F'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'passport.lianjia.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
}

# 获取lianjia_uuid
req = urllib.request.Request('http://bj.lianjia.com/')
opener.open(req)
# 初始化表单
req = urllib.request.Request(auth_url, headers=headers)
result = opener.open(req)

# 获取cookie和lt值
pattern = re.compile(r'JSESSIONID=(.*)')
jsessionid = pattern.findall(result.info().get('Set-Cookie').split(';')[0])[0]
#print(jsessionid)

html_content = result.read().decode('utf-8')
pattern = re.compile(r'value=\"(LT-.*)\"')
lt = pattern.findall(html_content)[0]

pattern = re.compile(r'name="execution" value="(.*)"')
execution = pattern.findall(html_content)[0]

# data
data = {
    'username': '15600564401',
    'password': '1wang23li',
    'execution': execution,
    '_eventId': 'submit',
    'lt': lt,
    'verifyCode': '',
    'redirect': '',
}

post_data=urllib.parse.urlencode(data).encode('utf-8') 

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'passport.lianjia.com',
    'Origin': 'https://passport.lianjia.com',
    'Pragma': 'no-cache',
    'Referer': 'https://passport.lianjia.com/cas/login?service=http%3A%2F%2Fbj.lianjia.com%2F',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'X-Requested-With': 'XMLHttpRequest'
}

req = urllib.request.Request(auth_url, post_data, headers)
result = opener.open(req)
print(req)
