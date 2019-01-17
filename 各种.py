# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 13:37:59 2018

@author: CChain
"""

import pandas as pd
import numpy as np
import os
import datetime
from matplotlib import pyplot as plt

monlen = 11

#=======================================全量通信数据
# 读取文件
path1 = 'D:/Project/数据/全量通信'
filepath1 = np.array(os.listdir(path1))
os.chdir(path1)

# 读取多个csv
pieces_name1 = []
for file in filepath1[1:]:
    f = open(file,encoding='utf8',errors='ignore')#遇到中文y
    frame = pd.read_csv(f,sep='|',header='infer',usecols=['用户号码','用户状态','活跃天数','所属分公司','用户网龄','ARPU值','MOU值','DOU值'])
    frame['入网月份'] = int(file[4:6])-frame['用户网龄']
    frame.drop_duplicates(inplace=True)
    pieces_name1.append(frame)


#======================================新增数据
# 读取文件
path9 = 'D:/Project/数据/新增/'
filepath9 = np.array(os.listdir(path9))
os.chdir(path9)

# 读取多个csv
pieces_name9 = []
for file in filepath9:
    f = open(file,encoding='utf8')#遇到中文
    frame = pd.read_csv(f,sep='|',header='infer',usecols=['统计月份','用户号码','号码品牌','是否不限量叠加包用户','是否4GSIM卡','归属分公司','客户类型'])
    frame.drop_duplicates(inplace=True)
    frame['入网月份'] = int(file[0:2])
    frame.rename(columns={'归属分公司':'所属分公司'},inplace=True)
    pieces_name9.append(frame)
    
new_users = pd.concat(pieces_name9,ignore_index=True)

#================================ 出账数据
# 读取文件
path7 = 'D:/Project/数据/出账/'
filepath7 = np.array(os.listdir(path7))
os.chdir(path7)

# 8-10月份数据
pieces_name7 = []
for file in filepath7[1:]:
    f = open(file,encoding='utf8')#遇到中文
    frame = pd.read_csv(f,sep='|',header='infer',usecols=['统计月份','用户号码','用户网龄'])
    frame.dropna(inplace=True)
    frame.drop_duplicates(inplace=True)
    pieces_name7.append(frame)

pieces_name7[0]['用户网龄'] = pieces_name7[0]['用户网龄']-2
pieces_name7[1]['用户网龄'] = pieces_name7[1]['用户网龄']-1

for i in range(3):
    pieces_name7[i]['入网月份'] = pieces_name7[i]['统计月份']-pieces_name7[i]['用户网龄']

bill8_10 = pd.concat(pieces_name7,ignore_index=True)
#a = pd.pivot_table(bill8_10.loc[bill8_10['入网月份']>=201801],index='入网月份',columns='统计月份',values='用户号码',aggfunc=len)

# 1-7月份数据
f = open(filepath7[0],encoding='gbk')#遇到中文
bill1_7 = pd.read_csv(f,sep=',',header='infer')

bill1_7.columns
bill1_7.head(20)

bill1_7.rename(columns={'号码':'用户号码','月份':'统计月份'},inplace=True)
bill1_7['入网月份'] = bill1_7['激活日期'].astype('str').str.slice(0,6).astype('int')
bill1_7['用户网龄'] = bill1_7['统计月份']-bill1_7['入网月份']

# 11月数据
f = open('D:/Project/数据/全量/11月全量用户数据(含非通信).txt',encoding='utf8')
bill11 = pd.read_csv(f,sep='|',header='infer',usecols=['统计月份','用户号码','用户网龄','是否出账用户'])
bill11['入网月份'] = bill11['统计月份']-bill11['用户网龄']
bill11 = bill11.loc[bill11['是否出账用户']=='是']

# 合并数据
bill_all = pd.concat([bill1_7,bill8_10,bill11],ignore_index=True)

monthes = np.sort(bill_all['统计月份'].unique())

pieces_name8 = []
for i in range(11):
    frame = bill_all.loc[bill_all['统计月份']==monthes[i]].copy()
    pieces_name8.append(frame)

#=====================================新增结构
# 改变类型
new_users.loc[(new_users['客户类型'].str.contains('飞享'))&(new_users['是否不限量叠加包用户']=='是'),'客户类型'] = '8/18/38元4G飞享+叠加型'
new_users.loc[new_users['用户号码'].astype('str').str.contains('^368'),'客户类型'] = '其他-宽带'
new_users.loc[(new_users['客户类型']!='其他-宽带')&(new_users['客户类型']!='日租卡')&(new_users['客户类型']!='不限量主套')&(new_users['客户类型']!='万能副卡')&(new_users['客户类型']!='8/18/38元4G飞享+叠加型'),'客户类型'] = '普通全球通/预付费'

# 每月类型
mon_type = pd.pivot_table(new_users,index='客户类型',columns='统计月份',values='用户号码',aggfunc=len)
mon_type.sort_index(inplace=True)

# 每月类型分公司
mon_type_branch = pd.pivot_table(new_users,index=['统计月份','客户类型'],columns='所属分公司',values='用户号码',aggfunc=len)

branch_sort = ['端州','高要','四会','怀集','广宁','德庆','封开','鼎湖','大旺','沉默']
mon_type_branch = mon_type_branch[branch_sort]
mon_type_branch['总规模'] = mon_type_branch.sum(1)

mon_type_branch.reset_index(inplace=True)
mon_type_branch.sort_values(by=['统计月份','客户类型'],inplace=True)


#================================ 出账规模与出账率
frame_bill = pd.pivot_table(bill_all.loc[bill_all['入网月份']>=201801],index='入网月份',columns='统计月份',values='用户号码',aggfunc=len)
frame_bill.columns=[(str(i)+'月出账') for i in range(1,monlen+1)]
frame_bill.index = [(str(i)+'月新增') for i in range(1,monlen+1)]

# 出账率
mon_count = new_users['月份'].value_counts().sort_index()
mon_count.index = [(str(i)+'月新增') for i in range(1,monlen+1)]
frame_bill2 = (frame_bill).div(mon_count,axis=0)

#================================ 通信留存
# 方法1
# 总规模
frame_retent = pd.DataFrame()
for i in range(monlen):
    index_2018 = pieces_name1[i]['入网月份']>=1
    frame = pd.pivot_table(pieces_name1[i].loc[index_2018],values='用户号码',index='入网月份',aggfunc=len)
    frame_retent = pd.concat([frame_retent,frame],axis=1)

frame_retent.columns=[(str(i)+'月留存') for i in range(1,monlen+1)]
frame_retent.index = [(str(i)+'月新增') for i in range(1,monlen+1)]
# 留存率
mon_count = new_users['统计月份'].value_counts().sort_index()
mon_count.index = [(str(i)+'月新增') for i in range(1,monlen+1)]
frame_retent2 = (frame_retent).div(mon_count,axis=0)
'''
# 方法2
frame_retent2 = pd.DataFrame(np.array(np.arange(monlen*monlen)).reshape(monlen,monlen))
frame_retent2.iloc[:,:] = 0
for i in range(monlen):
    for j in range(i,monlen):
        index1 = pieces_name1[j]['用户号码'].isin(list(pieces_name9[i]['用户号码']))
        index2 = pieces_name1[j]['用户网龄'] == j-i
        frame_retent2.iloc[i,j-1] = sum(index1 & index2)

frame_retent2.columns=[(str(i)+'月留存') for i in range(1,monlen+1)]
frame_retent2.index = [(str(i)+'月新增') for i in range(1,monlen+1)]
frame_retent2[frame_retent2==0] = np.nan

# 留存率
mon_count = new_users['月份'].value_counts().sort_index()
mon_count.index = [(str(i)+'月新增') for i in range(1,monlen+1)]
frame_retent3 = (frame_retent2).div(mon_count,axis=0)
'''
# 分公司规模
frame_retent_branch = pd.DataFrame()
for i in range(monlen):
        index1 = pieces_name1[i]['入网月份']>=1
        frame = pd.pivot_table(pieces_name1[i].loc[index1],values='用户号码',index=['入网月份','所属分公司'],aggfunc=len)
        frame_retent_branch = pd.concat([frame_retent_branch,frame],axis=1)

frame_retent_branch.columns = [(str(i)+'月留存') for i in range(1,monlen+1)]
frame_retent_branch.reset_index(inplace=True)
frame_retent_branch['入网月份'] = [(str(i)+'月新增') for i in range(1,monlen+1) for j in range(10)]

# 指定顺序
frame_retent_branch2 = pd.concat([pd.DataFrame([(str(i)+'月新增') for i in range(1,monlen+1) for j in range(10)]),pd.DataFrame(branch_sort*monlen)],axis=1)
frame_retent_branch2.columns=['入网月份','所属分公司']
frame_retent_branch3 = pd.merge(frame_retent_branch2,frame_retent_branch,on=['入网月份','所属分公司'],how='left')
frame_retent_branch3.fillna(0,inplace=True)

# 分公司留存率
mon_branch_count = pd.pivot_table(new_users,index=['入网月份','所属分公司'],values='用户号码',aggfunc=len)
mon_branch_count.reset_index(inplace=True)
mon_branch_count['入网月份'] = [(str(i)+'月新增') for i in range(1,monlen+1) for j in range(10)]
mon_branch_count = pd.merge(frame_retent_branch3[['入网月份','所属分公司']],mon_branch_count,how='left',on=['入网月份','所属分公司'])

mon_branch_count.set_index(['入网月份','所属分公司'],inplace=True)
mon_branch_count = pd.Series(mon_branch_count['用户号码'].values,index=mon_branch_count.index)

frame_retent_branch3.set_index(['入网月份','所属分公司'],inplace=True)
frame_retent_branch4 = (frame_retent_branch3).div(mon_branch_count,axis=0)
frame_retent_branch4.fillna(0,inplace=True)
'''
# 第二种方法
pieces = []
for k in branch_sort:
    frame_retent2 = pd.DataFrame(np.array(np.arange(monlen*monlen)).reshape(monlen,monlen))
    frame_retent2.iloc[:,:] = 0
    for i in range(monlen):
        for j in range(i,monlen):
            index1 = pieces_name1[j]['用户号码'].isin(list(pieces_name9[i]['用户号码']))
            index2 = pieces_name1[j]['用户网龄'] == j-i
            index3 = pieces_name1[j]['所属分公司'] == k
            frame_retent2.iloc[i,j] = sum(index1 & index2 & index3)
    
    frame_retent2.columns=[(str(i)+'月留存') for i in range(1,monlen+1)]
    frame_retent2.index = [(str(i)+'月新增') for i in range(1,monlen+1)]
    frame_retent2[frame_retent2==0] = np.nan
    frame_retent2['所属分公司'] = k
    pieces.append(frame_retent2)

frame_retent_branch = pd.concat(pieces)
frame_retent_branch.reset_index(inplace=True)
frame_retent_branch.rename(columns={'index':'入网月份'},inplace=True)
'''
# 客户类型
# 添加客户类型
for i in range(monlen):
    pieces_name1[i] = pd.merge(pieces_name1[i],new_users[['用户号码','入网月份','客户类型']],on=['用户号码','入网月份'],how='left')

frame_act_branch = pd.DataFrame()
for i in range(monlen):
    index1 = pieces_name1[i]['入网月份']>=1
    frame = pd.pivot_table(pieces_name1[i].loc[index1],values='用户号码',index=['客户类型','入网月份'],aggfunc=len)
    frame_act_branch = pd.concat([frame_act_branch,frame],axis=1)

frame_act_branch.columns = [(str(i)+'月留存') for i in range(1,monlen+1)]
frame_act_branch.reset_index(inplace=True)
frame_act_branch['入网月份'] = [(str(i)+'月新增') for j in range(5) for i in range(1,11)]#客户类型有5种(去掉宽带)
frame_act_branch.fillna(0,inplace=True)

mon_type_count = pd.pivot_table(new_users,index=['入网月份','客户类型'],values='用户号码',aggfunc=len)
mon_type_count.reset_index(inplace=True)
mon_type_count['入网月份'] = [(str(i)+'月新增') for i in range(1,monlen+1) for j in range(6)]
mon_type_count = mon_type_count[mon_type_count['客户类型']!='其他-宽带']
mon_type_count.set_index(['入网月份','客户类型'],inplace=True)

mon_type_count = pd.Series(mon_type_count['用户号码'].values,index=mon_type_count.index)

frame_act_branch.set_index(['入网月份','客户类型'],inplace=True)
frame_act_branch2 = (frame_act_branch).div(mon_type_count,axis=0)
frame_act_branch2.fillna(0,inplace=True)
frame_act_branch2.reset_index(inplace=True)
frame_act_branch2.sort_values(by=['客户类型','入网月份'],inplace=True)

#================================通信正使用规模
frame_retent_using = pd.DataFrame()
for i in range(monlen):
    index1 = pieces_name1[i]['入网月份']>=1
    index2 = pieces_name1[i]['用户状态']=='正使用'
    frame = pd.pivot_table(pieces_name1[i].loc[index1 & index2],values='用户号码',index='入网月份',aggfunc=len)
    frame_retent_using = pd.concat([frame_retent_using,frame],axis=1)

frame_retent_using.columns=[(str(i)+'月正使用留存') for i in range(1,monlen+1)]
frame_retent_using.index = [(str(i)+'月新增') for i in range(1,monlen+1)]
frame_retent_using.fillna(0,inplace=True)
# 正使用留存率
frame_retent_using2 = (frame_retent_using).div(mon_count,axis=0)

# 正使用分公司规模
frame_using_branch = pd.DataFrame()
for i in range(monlen):
        index1 = pieces_name1[i]['入网月份']>=1
        index2 = pieces_name1[i]['用户状态']=='正使用'
        frame = pd.pivot_table(pieces_name1[i].loc[index1 & index2],values='用户号码',index=['入网月份','所属分公司'],aggfunc=len)
        frame_using_branch = pd.concat([frame_using_branch,frame],axis=1)

frame_using_branch.columns = [(str(i)+'月留存') for i in range(1,monlen+1)]
frame_using_branch.reset_index(inplace=True)
frame_using_branch['入网月份'] = [(str(i)+'月新增') for i in range(1,monlen+1) for j in range(10)]

#================================渠道类型
f = open('D:/Project/11.09放号质量分析/提供数据/渠道明细/渠道类型.csv',encoding='gbk')
channel_type = pd.read_csv(f,sep=',',header='infer')

f = open('D:/Project/11.09放号质量分析/提供数据/新增用户数据v4.txt',encoding='utf8')
channel = pd.read_csv(f,sep='|',header='infer')

channel['新增月份'].value_counts().sort_index()

channel['渠道类型'] = '未知'
channel.loc[channel['渠道编码'].isin(channel_type.loc[channel_type['渠道类型']=='社会渠道(含带店)','渠道编码']),'渠道类型']='社会渠道(含带店)'
channel.loc[channel['渠道编码'].isin(channel_type.loc[channel_type['渠道类型']=='自有渠道','渠道编码']),'渠道类型']='自有渠道'
channel.loc[channel['渠道编码'].isin(channel_type.loc[channel_type['渠道类型']=='铁通服务站','渠道编码']),'渠道类型']='铁通服务站'
channel.loc[channel['渠道编码']=='ZQ_HAZQ1530Q','渠道类型']='电子渠道'

# 每月渠道占比
mon_chan = pd.pivot_table(channel,index='新增月份',columns='渠道类型',values='用户号码',aggfunc=len)
mon_chan2 = mon_chan.div(mon_chan.sum(1),axis=0)

#================================ARPU值,DOU值，MOU值
for i in range(monlen):
    pieces_name1[i]['DOU值'] = pieces_name1[i]['DOU值']/1024

value_item = ['ARPU值','DOU值','MOU值']
func = [np.mean,np.sum]
pieces_value = []
for j in value_item:
    for m in func:
        frame_sumean = pd.DataFrame()
        for i in range(monlen):
            index1 = pieces_name1[i]['入网月份']>=1
            index2 = pieces_name1[i]['客户类型']!='万能副卡'
            index3 = pieces_name1[i]['ARPU值']<10000
            frame = pd.pivot_table(pieces_name1[i].loc[index1 & index2 & index3],values=j,index='入网月份',aggfunc=m)
            frame_sumean = pd.concat([frame_sumean,frame],axis=1)
        frame_sumean.columns=[(str(k)+'月'+j) for k in range(1,monlen+1)]
        frame_sumean.index = [(str(k)+'月新增') for k in range(1,monlen+1)]
        pieces_value.append(frame_sumean)


#=================================DOU值分层
# 离散化
def cut_col(df,cols1,cols2,bins,labs):
    df[cols2] = pd.cut(df[cols1],bins,labels=labs,right=False)
    df[cols2] = df[cols2].astype('str')

data = pieces_name1[monlen-1].copy()
cut_col(data,'DOU值','DOU值分层',[data['DOU值'].min()-1,0.001,100,500,1000,3000,5000,data['DOU值'].max()],['0','(0-100M)','[100M-500M)','[500M-1G)','[1G-3G)','[3G-5G)','5G及以上'])

frame_dou = data.loc[data['入网月份']>=1].pivot_table('用户号码',index='入网月份',columns='DOU值分层',aggfunc=len)
frame_no = data.loc[data['入网月份']>=1].pivot_table('用户号码',index='入网月份',aggfunc=len)
frame_dou = pd.merge(frame_no,frame_dou,how='left',left_index=True,right_index=True)
