import pandas as pd
import json
import numpy as np
import requests

tot_user = pd.read_csv("totuser1.csv")
tot_user['business_name'] = tot_user['business'].apply(lambda x:np.nan if pd.isnull(x) else eval(x)['name'])
def diploma(x):
    if pd.isnull(x) or not eval(x):
        return np.nan
    elif 'diploma' not in list(eval(x)[0].keys()):
        return np.nan
    else:
        return eval(x)[0]['diploma']

def school(x):
    if pd.isnull(x) or not eval(x):
        return np.nan
    elif 'school' in list(eval(x)[0].keys()):
        return eval(x)[0]['school']['name']
    else:
        return eval(x)[0]['major']['name']

def company(x):
    if pd.isnull(x) or not eval(x):
        return np.nan
    elif 'company' in list(eval(x)[0].keys()):
        return eval(x)[0]['company']['name']
    else:
        return eval(x)[0]['job']['name']

def location(x):
    if pd.isnull(x) or not eval(x):
        return np.nan
    else:
        return eval(x)[0]['name']

tot_user['diploma'] = tot_user['educations'].apply(lambda x:diploma(x))
tot_user['school'] = tot_user['educations'].apply(lambda x:school(x))
tot_user['location'] = tot_user['locations'].apply(lambda x:location(x))

tot_user = tot_user.drop(['business','commercial_question_count',\
                          'cover_url','description','educations',\
                          'employments','error','headline','is_active',\
                          'is_advertiser','is_bind_sina','is_blocked','is_blocking',\
                          'is_followed','is_following','is_force_renamed','is_org',\
                          'is_privacy_protected','locations','marked_answers_text',\
                          'mutual_followees_count','message_thread_token',\
                          'show_sina_weibo','thank_from_count','thank_to_count','url',\
                          'url_token','vip_info','vote_from_count','vote_to_count',\
                          'Unnamed: 0','account_status','allow_message','avatar_hue',\
                          'avatar_url','avatar_url_template','badge','industry_category',\
                          'org_homepage','org_name','type'],axis=1)
tot_user=tot_user.dropna(how="all")
tot_user.to_csv('userinformation.csv', encoding='utf_8_sig')

livedata = pd.read_csv("live_original.csv",encoding='gbk').drop_duplicates()
livedata = livedata.loc[(livedata['user_type']=='people')&(livedata['status']=='ended')].drop(['name'],axis=1)
livedata.to_csv('liveinformation.csv', encoding='utf_8_sig')
alldata = pd.merge(livedata,tot_user,left_on='user_id',right_on='id',how='left')
alldata = alldata.drop(['id','user_type_x','gender_x'],axis=1).rename(columns={'user_type_y':'user_type','gender_y':'gender'})
alldata.to_csv('alldata.csv', encoding='utf_8_sig')
print(alldata)
