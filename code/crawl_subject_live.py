import requests
import urllib3
import re
from bs4 import BeautifulSoup
import numpy as pyd
import pandas as pd
import json
url="https://api.zhihu.com/lives/special_lists?limit=161&subtype=special_list"
header={}
header['User-Agent']='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36'

r=requests.get(url,headers=header)  #get the request of website
con=r.content.decode('utf-8',"ignore")
con_json = json.loads(con)      #convert to dict
data_list = con_json['data']
id = [i['id'] for i in data_list]
item = [i['subject'] for i in data_list]   #return subject
dic = dict(zip(id,item))     #return the dictionary of id and item
tot_data = pd.DataFrame()
for i in id[19:]:        
    url_1 = "https://api.zhihu.com/lives/special_lists/%s/lives" %i
    header_1 = {}
    header_1['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36'
    r1 = requests.get(url_1, headers=header)  # get the request of website
    con1 = r1.content.decode('utf-8', "ignore")
    con_json1 = json.loads(con1)  # convert to dict
    data = con_json1['data']
    dat1 = pd.DataFrame()
    for j in data:
        if 'starts_at' not in list(j.keys()):
            started = "none"
        started = j['created_at']        #start time
        if 'ends_at' not in list(j.keys()):
            end = "none"
        end = j['ends_at']               #end time
        subject = j['subject']        #此次live的主题
        if 'original_price' not in list(j['fee'].keys()):
            fee = "none"
        fee = j['fee']['original_price']/100 #paid fee
        taken = j['seats']['taken']      # number of people attending
        max = j['seats']['max']
        comment_count = j['review']['count']  # number of comments
        score = j['review']['score']  # 评论总分
        liked_num = j['liked_num']
        message_count = j['speaker_message_count'] # 主讲人说话的次数
        user_type = j['speaker']['member']['user_type']   # user属于group还是people
        user_id = user_id = j['speaker']['member']['id']    # 用来爬取用户的相关数据
        headline = j['speaker']['member']['headline']
        gender = j['speaker']['member']['gender']   # 性别(1为女性）
        #identity = j['speaker']['member']['badge']['description']   #主讲人身份
        auth_description = j['auth_description']          # 主讲人是否通过实名认证
        auditionmessage_count = j['audition_message_count']   # 语音数目
        status = j['status']           # end or not
        id = j['id']           #可用来爬取相关的live
        name = j['tags'][0]['name']        # 所属类别全名
        short_name = j['tags'][0]['short_name']   #简称
        live_num = j['tags'][0]['live_num']  # 在此类别下live总数
        available_num = j['tags'][0]['available_num']  # 可用的live数目
        great_num = j['tags'][0]['great_num']

        dat = pd.DataFrame({ 'started':[started], 'end':[end],  'subject':[subject],'fee':[fee], 'taken':[taken],
                             'comment_count': [comment_count], 'score':[score], 'message_count':[message_count],
                             'user_type': [user_type], 'user_id':[str(user_id)],  'headline':[headline], 'gender':[gender],
                             'auth_description': [auth_description], 'auditionmessage_count':[auditionmessage_count],
                             'status': [status], 'id': [str(id)], 'name':[name], 'short_name':[short_name], 'live_num':[live_num],
                             'available_num':[available_num], 'great_num':[great_num]}
                              )
        dat1 = dat1.append(dat)
    tot_data = tot_data.append(dat1)

tot_data.to_csv('totdata.csv', encoding='utf_8_sig',encoding="utf_8_sig")
print(tot_data)
