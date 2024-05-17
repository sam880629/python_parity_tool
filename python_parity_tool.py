#導入模組
import tkinter as T 
from tkinter import messagebox
import sys
import requests
from bs4 import BeautifulSoup
import json
import tkinter.ttk as TTK
import urllib.parse
import os
import csv


    
# 按鈕點擊事件
def btn_out_click(W, web_name_array):
  
    target_name = itemsInput.get()  #查詢值
    if target_name.strip() == '':
        messagebox.showwarning('warning', '請輸入商品的名稱!!')
        return
    else:
        print(web_name_array)
        label.config(text='wait', foreground="red")
        W.update()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, target_name+'商品比價.csv')
        with open(file_path, 'w', newline='') as F:
            W = csv.writer(F)
            for web_name in web_name_array:  
                STORE = web_name
                print('Search item \'%s\' from %s...' % (target_name, STORE))
                get_data_write_to_csv(web_name, target_name, W)
            print('search end')
            
    
            F.close( )   
    label.config(text='ready', foreground="green")
    messagebox.showwarning('finished', '輸出完成!!路徑:'+current_dir)
    
# 將資料寫入CSV
def get_data_write_to_csv(web_name, target_name, csv_writer):
    # print(web_name)
    if web_name == 'Yahoo':
        set_title = ['YAHOO']
    elif web_name == '樂天':
        set_title = ['樂天']
    elif web_name == 'Momo':
        set_title = ['Momo']
    else:
        return
    
    csv_writer.writerow(set_title)
    set_title = ['品名', '價格', '公司','訂購連結']
    csv_writer.writerow(set_title)
    
    # 根據網站名稱取得資料
   
    if web_name == 'Yahoo':
        GetReturn = get_yahoo(target_name)
    elif web_name == '樂天':
        GetReturn = get_rakuten(target_name)
    elif web_name == 'Momo':
        GetReturn = get_momo(target_name)
    else:
        return
    
    for r in GetReturn:
        csv_writer.writerow(r)

#取得 yahoo
def get_yahoo(goods):
    if order_text.get() == '找低價':
        URL = 'https://tw.buy.yahoo.com/search/product?p=' + goods + '&sort=price'
    elif order_text.get() == '找高價':
        URL = 'https://tw.buy.yahoo.com/search/product?p=' + goods + '&sort=-price'
    else:
        URL = 'https://tw.buy.yahoo.com/search/product?p=' + goods
    # print(URL)
    USER_AGENT_VALUE = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    headers = {'User-Agent': USER_AGENT_VALUE}
    
    r = requests.get(URL, headers=headers)
    r.encoding = 'utf8'
    sp = BeautifulSoup( r.text, 'lxml')

    sp = sp.find('div',class_='ResultList_resultList_IpWJt')
    if sp == None:
        print('查無資料')
        sys.exit(0)
        
    first_a = sp.find('a').get('class')

    datas = sp.find_all('a', class_=first_a)

    ReturnList = []
    try:
        for i in range(10):
            name = datas[i].find('span', class_='sc-dlyefy sc-gKcDdr sc-1drl28c-5')#商品名稱
            price = datas[i].find('div', class_='sc-shnyN').find('span')#商品價錢
            url =  datas[i].get('href')#商品連結
            
            setList = []
        
            setList.append(name.text.strip())
            setList.append(price.text.strip())
            setList.append(" ")
            setList.append(url)
            ReturnList = ReturnList + [setList]
    except:
       return ReturnList
    return ReturnList

# 取得 樂天
def get_rakuten(goods):
    if order_text.get() == '找低價':
        URL = 'https://www.rakuten.com.tw/search/' + goods + '/?s=2'
    elif order_text.get() == '找高價':
        URL = 'https://www.rakuten.com.tw/search/' + goods + '/?s=3'
    else:
        URL = 'https://www.rakuten.com.tw/search/' + goods
        
    # print(URL)
    
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}

    r = requests.get(URL,headers=headers)
    r.encoding = 'utf8'
    sp = BeautifulSoup( r.content, 'html.parser')

    name = sp.find_all('script',type ='application/json')

    name_str = name[1].text

    results = json.loads(name_str)
    # print(results)
    
    results = results['initialData']
    results = results['searchPage']
    results = results['result']
    results = results['items']
   
    ReturnList = []
    try:
        for i in range(10):
            resultsSHOW = results[i]
            item_name = resultsSHOW['itemName']
            shop_name = resultsSHOW['shopName']
            price_min = resultsSHOW['itemPrice']['min']
            price_max = resultsSHOW['itemPrice']['max']
            url = resultsSHOW['itemUrl']
            setList = []
            
            #print('商品名稱: ', Show1)
            #print('來源商家: ', Show2)
            #print('商品金額: ', price_min, '~', price_max) 
            #print('商品連結: ', url) 
            setList.append(item_name)
            setList.append(str(price_min) + '~' + str(price_max))
            setList.append(shop_name)
            setList.append(url)
            ReturnList = ReturnList + [setList]
    except:
         return ReturnList
    return ReturnList
    
def get_web_content(query):

    MOMO_QUERY_URL = 'https://m.momoshop.com.tw/search.momo?searchKeyword=%s&searchType=%s'
    USER_AGENT_VALUE = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    encoded_query = urllib.parse.quote(query)#搜尋值
    search_type = '1' #價格排序
    if order_text.get() == '找低價':
        search_type = '2'
    elif order_text.get() == '找高價':
        search_type = '3'
    query_url = MOMO_QUERY_URL % (encoded_query, search_type)
    # print(query_url)
    headers = {'User-Agent': USER_AGENT_VALUE}
    resp = requests.get(query_url, headers=headers)
    if not resp:
        return []
    resp.encoding = 'UTF-8'
    return BeautifulSoup(resp.text, 'html.parser')

# 搜尋momo
def search_momo(query):
    dom = get_web_content(query)
    
    if dom:
        items = []
        for element in dom.find('article', class_='prdListArea').ul.find_all('li'):
           
            item_url = element.find('a').get('href')
            item_url = 'https://m.momoshop.com.tw' + item_url
            item_name = element.find('h3', 'prdName').text
            item_price = element.find('b', 'price').text.replace(',', '')
            if not item_price:
                continue
            item_price = int(item_price)
       
            item = {
                'name' : item_name,
                'price' : item_price,
                'url' : item_url
            }
    
            items.append(item)
        return items

#取得 momo
def get_momo(goods):
    query_str = goods
    items = search_momo(query_str)
  
    # print('Search %d records on %s' % (len(items), today))
    ReturnList = []
    try:
        for (i,item) in enumerate(items):
            setList = []
            #print(item)
            setList.append(item['name'])
            setList.append(item['price'])
            setList.append(' ')
            setList.append(item['url'])
            ReturnList = ReturnList + [setList]
            if i == 9:
                break
    except:
         return ReturnList
    return ReturnList

def update_check(all_check, all_check_val, web_name_array):
    
    web_name_array.clear()
    if all(item_val.get() == 1 for item_val in all_check_val):
        for check_item,check_val in zip(all_check,all_check_val):
            item_text = check_item.cget('text')
            web_name_array.append(item_text)
            check_val.set(0)
    else:
        for check_item,check_val in zip(all_check,all_check_val):
            if check_val.get() ==1:
                item_text = check_item.cget('text')
                web_name_array.append(item_text)
        
    check_none_val.set(int(all(item_val.get() == 0 for item_val in all_check_val)))
        
    # print(web_name_array)
  
def update_none_check(all_check, all_check_val, web_name_array):
    
    web_name_array.clear()
    for check_item,check_val in zip(all_check,all_check_val):
        check_val.set(0)
        item_text = check_item.cget('text')
        web_name_array.append(item_text)
            
    check_none_val.set(1)
            
    
      
W = T.Tk( )
W.geometry('300x250')
W.title( "比價小程式")

#提醒文字
initial_text = "ready"
label = T.Label(W, text=initial_text, font=('bold', 16), foreground="green")
label.place(x=180, y=120)

LBedInput = T.Label(W, text ='商品名稱', width = 10).place(x=15, y= 40)

#搜尋產品名稱
itemsInput = T.StringVar()
edInput = T.Entry(W, width = 20, textvariable = itemsInput)
edInput.place(x=80, y =40)

# 輸出按鈕
btnOut = T.Button(W, text ='產生csv ', command = lambda:btn_out_click(W, web_name_array))
btnOut.place(x=120, y=200)

#價錢排序下拉選單
order_text = T.StringVar()
cboOrder = TTK.Combobox(W,values=['不限','找低價', '找高價'],width=5, textvariable = order_text)
cboOrder.place(x=170, y=88)
cboOrder.set('不限')
T.Label(W, text='價錢排序').place(x=165, y=65)

#複選框
check_none_val = T.IntVar(value=1)
check_yahoo_val = T.IntVar()
check_rakuten_val = T.IntVar()
check_momo_val = T.IntVar()

check_none = T.Checkbutton(W, text="不限", variable=check_none_val,  command= lambda:update_none_check(all_check, all_check_val, web_name_array))
check_yahoo = T.Checkbutton(W, text="Yahoo", variable=check_yahoo_val, command= lambda: update_check(all_check, all_check_val, web_name_array))
check_rakuten  = T.Checkbutton(W, text="樂天", variable=check_rakuten_val, command= lambda: update_check(all_check, all_check_val, web_name_array))
check_momo= T.Checkbutton(W, text="Momo", variable=check_momo_val, command= lambda: update_check(all_check, all_check_val, web_name_array))

all_check_val = [check_yahoo_val, check_rakuten_val, check_momo_val]
all_check = [check_yahoo, check_rakuten, check_momo]
web_name_array = []   
for check_item in all_check:
    item_text = check_item.cget('text')
    web_name_array.append(item_text)
    
check_none.place(x=50, y=80)
check_yahoo.place(x=50, y=105)
check_rakuten.place(x=50, y=130)
check_momo.place(x=50, y=155)

W.mainloop( )