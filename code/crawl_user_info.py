import requests
import urllib3
import re
import numpy as pyd
import pandas as pd
import json

user = pd.read_csv(r'C:\Users\USER\Desktop\毕设\数据\user_id.csv',engine='python')
user_id = user['user_id'].tolist()
tot_data=pd.DataFrame()

user_url = "https://www.zhihu.com/api/v4/members/{user}?include={include}"
user_query = "locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics"

header = {}
header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36'
tot_user = pd.DataFrame()
for i in user_id:
    print(i)
    user = requests.get(user_url.format(user=i, include=user_query), headers=header)
    user = user.content.decode('utf-8','ignore')
    print(i)
    user_json = json.loads(user)  # convert to dict
    user1 = pd.DataFrame([user_json])
    tot_user = tot_user.append(user1)
tot_user.to_csv('totuser1.csv', encoding='utf_8_sig')
print(tot_user)

























