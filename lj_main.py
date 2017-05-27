import re
import time
import requests
import random
import threading
import pymysql
import math
from bs4 import BeautifulSoup


headers=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
         {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
         {'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},\
         {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},\
         {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},\
         {'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
         {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
         {'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},\
         {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
         {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},\
         {'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},\
         {'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]

#连接数据库
def conn_open():
    global conn,cur
    conn = pymysql.connect(host='localhost',
                           port=3306,user='root',
                           passwd='root',
                           db='lianjia',
                           charset='UTF8')
    cur = conn.cursor()

#关闭数据库链接
def conn_close():
    cur.close()
    conn.close()

#建立空字典，用以存放字段名称和字段值 
info_dict = {}
#记录数据库插入
def room_insert(info_dict,cur):
    info_list=['href','name','style','area','orientation','floor','year','signtime','unit_price','total_price','fangchan_class','school','subline','distance']
    t=[]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    t = tuple(t)
    sql = "insert into room_onsale (href,name,style,area,orientation,floor,year,signtime,unit_price,total_price,fangchan_class,school,subline,distance) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cur.execute(sql,t)
    conn.commit()
    

def room_spider(list_url):
    try:
        htmlorg = requests.get(list_url,headers=headers[random.randint(0,len(headers)-1)],timeout=20)
        htmlorg.encoding = htmlorg.apparent_encoding
        bs = BeautifulSoup(htmlorg.text,'lxml')
    except:
        return False
    page_info = bs.find('div',{'class':'page-box house-lst-page-box'}).attrs['page-data']
    page_num = int(midt("\"totalPage\":",",\"curPage\"",page_info))
    count = 0
    for page in range(1,page_num+1):
        page_link = list_url + "pg" + str(page)
        pagehtml = requests.get(page_link,headers=headers[random.randint(0,len(headers)-1)],timeout=20)
        pagehtml.encoding = pagehtml.apparent_encoding
        page_bs = BeautifulSoup(pagehtml.text,'lxml')
        sell_list = page_bs.find('ul',{'class':'sellListContent'}).find_all('div',{'class':'info clear'})
        for sell_item in sell_list:
            info_dict.update({'href':sell_item.find('div',{'class':'title'}).a.attrs['href']})
            house_info = sell_item.find('div',{'class':'houseInfo'}).text.split(' | ')
            info_dict.update({'name':house_info[0]})
            info_dict.update({'style':house_info[1]})
            info_dict.update({'area':house_info[2].split('平米')[0]})
            info_dict.update({'orientation':house_info[3]})
            info_dict.update({'floor':sell_item.find('div',{'class':'positionInfo'}).text.split(')')[0]+')'})
            info_dict.update({'year':midt(')','年',sell_item.find('div',{'class':'positionInfo'}).text)})
            info_dict.update({'unit_price':midt('单价','元',sell_item.find('div',{'class':'unitPrice'}).span.text)})
            info_dict.update({'total_price':sell_item.find('div',{'class':'totalPrice'}).span.text})
            taxfree = sell_item.find('span',{'class':'taxfree'})
            five = sell_item.find('span',{'class':'five'})
            if taxfree:
                info_dict.update({'fangchan_class':taxfree.text})
            elif five:
                info_dict.update({'fangchan_class':five.text})
            info_dict.update({'subline':midt('距离','站',sell_item.find('span',{'class':'subway'}).text)})
            info_dict.update({'distance':midt('站','米',sell_item.find('span',{'class':'subway'}).text)})
            try:
                room_insert(info_dict,cur)
            except:
                count = count+1
            'print(count)'

def room_spider_line(line_url):
    html = requests.get(line_url,headers=headers[random.randint(0,len(headers)-1)],timeout=20)
    html.encoding = html.apparent_encoding
    bs = BeautifulSoup(html.text,'lxml')
    line_list = (bs.find('div',{'data-role':'ditiefang'}).find_all('div'))[1].find_all('a')
    conn_open()
    for line in line_list:
        url = 'http://bj.lianjia.com'+line.attrs['href']
        room_spider(url)
    conn_close()
        
    print(line_list)

#获取字符串中间一段   
def midt(start_str, end, html):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()
room_spider_line("http://bj.lianjia.com/ditiefang/li651/")



































