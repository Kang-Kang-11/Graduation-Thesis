import pandas as pd
import numpy as np
import wordcloud
import math
from sklearn.cluster import KMeans
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib
from sklearn.linear_model import Lasso,LassoCV
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression
from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols
import statsmodels.formula.api as smf
import seaborn as sns
import jieba
from wordcloud import WordCloud
from collections import Counter


data = pd.read_csv("alldata.csv",encoding="gbk")
data_group=data.groupby(['user_id'])[['taken','answer_count','articles_count', 'columns_count','favorite_count','favorited_count','follower_count', 'following_columns_count','following_count','following_favlists_count', 'following_question_count','following_topic_count','hosted_live_count','logs_count','marked_answers_count','participated_live_count','pins_count','question_count', 'thanked_count',\'voteup_count']].mean().reset_index(drop=False)

# 数据预处理（选择列，以及剔除异常值）
## 添加一列，知乎收录的回答数/回答问题数量
data_group['ratio']=data_group['marked_answers_count']/data_group['answer_count']
data_group['ratio_type']=data_group['ratio'].apply(lambda x : 'low' if x==0 or pd.isnull(x) else ('medium' if x<=0.15 and x>0 else 'high'))
data_group['column_type']=data_group['columns_count'].apply(lambda x : 'low' if x==0 else ('medium' if x<=2 and x>0 else 'high'))
data_group.groupby(['column_type']).count()     #计数

## 选择列(简单平均)
columns=['user_id','taken','follower_count','following_count','voteup_count','favorited_count','articles_count','logs_count','column_type']
data_group1 = data_group[columns]

## 加权计算
data_group2=data.groupby(['user_id','short_name'],as_index=False).agg({'taken':['sum','count']})
data_group2.columns = ['user_id','short_name','taken','count']
data_group2 = data_group2.groupby(['user_id']).apply(lambda x :np.average(x['taken'],\
                               weights=x['count'])).reset_index(drop=False).\
                               rename(columns={0:'taken'})
data_group2 = pd.merge(data_group2,data_group.drop(['taken'],axis=1),on=['user_id'])
data_group2 =data_group2[columns]


# 描述性统计分析
## 词频统计
count=pd.DataFrame()
for i in set(data['short_name']):
    subject=data[data['short_name']==i].reset_index(drop=True)['subject']
    su=subject[0]
    print(i)
    for j in subject.index:
        su=su+subject[j] 
        su=su.replace('如何','')
        su_cut = " ".join(jieba.cut(su))
        dd=pd.DataFrame(dict(Counter(su_cut.split(' '))),index=['count']).T.reset_index(drop=False)
        dd['shot_name']=i
    count=count.append(dd)
count=count.sort_values(by=['shot_name','count'],ascending=False,)

## 主讲人用户群体分布
de = data_group2.describe()
stats.skew(data_group2.drop(['user_id'],axis=1))   #偏度
stats.kurtosis(data_group2.drop(['user_id'],axis=1))   #偏度

## 去除ratio为空的情况 data_group1 = data_group1.dropna()
## 每一列和每一行有多少0
(data_group1==0).sum(axis=0)
pd.value_counts((data_group2==0).sum(axis=1))

## 剔除每一行中0的值大于4的记录
data_group3 = data_group2[(data_group2==0).sum(axis=1)<=4].reset_index(drop=True)


# 数据预处理（标准化数据，log处理）
data_scaled1 = data_group3.drop(['user_id','column_type'],axis=1).applymap(lambda x :math.log(x+1) if x==0 else math.log(x))
data_scaled2 = data_scaled1.drop(['taken'],axis=1)


# 聚类
## 确定最佳聚类个数
d=[]
for i in range(1,11):   
    km=KMeans(n_clusters=i,init='k-means++',n_init=10,max_iter=300,random_state=0)
    km.fit(data_scaled2)
    d.append(km.inertia_)  #inertia簇内误差平方和

plt.plot(range(1,11),d,marker='o')
plt.xlabel('number of clusters')
plt.ylabel('distortions')
plt.show()
## 确定聚类个数为3
interation=500
kmodel=KMeans(n_clusters=3)      #n_job等于并行数，一般等于cpu比较好
kmodel.fit(data_scaled2)
r1=pd.Series(kmodel.labels_).value_counts()
r_data1=pd.DataFrame(kmodel.cluster_centers_)      #层中心
r_data1.columns = ['粉丝数量','关注人数','赞同数','被收藏数','文章数','参与公共编辑数']
finaldata1=pd.DataFrame({'group':kmodel.labels_.tolist(),
                        'user_id':data_group3['user_id'].tolist(),
                        'type':data_group3['column_type'].tolist()})
finaldata2=pd.merge(finaldata1,data_scaled1,left_index=True,right_index=True)


# 建模
## 分组数据
def dummies(num):
    group = finaldata2.loc[finaldata2['group']==num].drop(['group'],axis=1)
    group = pd.merge(finaldata2.loc[finaldata2['group']==num].drop(['group'],axis=1),\
                pd.get_dummies(group['type'], prefix='type'),left_index=True,right_index=True)  
    return group
group1 = dummies(0)    #中
group2 = dummies(1)    #低
group3 = dummies(2)    #高
finaldata2 = pd.merge(finaldata2, pd.get_dummies(finaldata2['type'], prefix='type'),left_index=True,right_index=True)

## 每一组的相关性分析
a1=group1[columns[1:8]].corr()
a2=group2[columns[1:8]].corr()
a3=group3[columns[1:8]].corr()
a=data_scaled1.corr()

## 此处 alpha 为通常值 #fit 把数据套进模型里跑,通过10折交叉验证选出最佳alpha
alphas = 10**np.linspace(-5, 10, 500)
dropcolumns = ['taken','user_id','type','type_high','type_low','type_medium']
indexnames=['intercept','follower_count','following_count','voteup_count','articles_count','logs_count']

def model(data,dropcolumn,indexname,renamecolumn):
    lasso=LassoCV(alphas = alphas,cv=10).fit(data.drop(dropcolumn,axis=1), data['taken'])
model_lasso=Lasso(alpha=lasso.alpha_).fit(data.drop(dropcolumn,axis=1),data['taken']) 
coef=pd.DataFrame([model_lasso.intercept_]+model_lasso.coef_.tolist(),index=indexname).rename(columns={0:renamecolumn}) 
    return model_lasso,coef

model_lasso1 =  model(group1, dropcolumns, indexnames, 'group1')[0]
coef1 =  model(group1, dropcolumns, indexnames, 'group1')[1]   
model_lasso2 =  model(group2, dropcolumns, indexnames, 'group2')[0]
coef2 =  model(group1, dropcolumns, indexnames, 'group2')[1]   
model_lasso3 =  model(group3, dropcolumns, indexnames, 'group3')[0]
coef3 =  model(group1, dropcolumns, indexnames, 'group3')[1]       
model_lasso = model(finaldata2, dropcolumns+['group'], indexnames,'all')[0]    
coef = model(finaldata2, dropcolumns+['group'], indexnames,'all')[1] 
tot_coef=pd.DataFrame({'变量':['截距','粉丝数量','关注人数','赞同数','文章数量','参与公共编辑数'],     
'group1':[model_lasso1.intercept_]+model_lasso1.coef_.tolist(),\
'group2':[model_lasso2.intercept_]+model_lasso2.coef_.tolist(),\
'group3':[model_lasso3.intercept_]+model_lasso3.coef_.tolist(),\
                        'all':[model_lasso.intercept_]+model_lasso.coef_.tolist()})

