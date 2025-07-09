'''
Author: Kamenrider 1161949421@qq.com
Date: 2025-05-02 16:30:00
LastEditors: Kamenrider 1161949421@qq.com
LastEditTime: 2025-05-14 11:20:25
FilePath: \weibo_微博及评论合集\交互内容可视化_sub_自定义列变换.py
Description: 使用parallel_plot_legend实现平行坐标图绘制
Copyright (c) 2025 by 潘崇林, All Rights Reserved. 
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from parallel_plot import parallel_plot

# 读取CSV文件
df = pd.read_csv('news_conference/four_period/luobote/TOPSIS评价结果_20250428.csv')

# 对列重命名
df.rename(columns={'交互内容得分': '交互内容','交互效果得分': '交互效果','影响力得分': '影响力','可靠性得分': '可靠性'}, inplace=True)

# 选择要绘制的列
# columns_to_plot = ['信息量', '形式多样性', '情感强度', '交互及时性', '知识性']
# columns_to_plot = ['粉丝数','微博数','认证信息']
# columns_to_plot = ['可读性','交互一致性','持续性','主题相关性']
columns_to_plot = ['安全性','准确性','新颖性']

# # 为不同用户类型设置编码值(0-1之间),以便于颜色映射
# user_types = {'发帖者': 0.9, '评论罗伯特': 0.5, '回帖者': 0.1}
# df['用户类型编码'] = df['用户标记'].map(user_types)

# 先给用户标记定义一个想要的顺序列表
category_order = ["回帖", "发帖", "评论罗伯特"]

# 将 df["用户标记"] 设置为有序分类
df["用户标记"] = pd.Categorical(
    df["用户标记"], 
    categories=category_order,  # 这里指定从底到顶的顺序
    ordered=True
)

# 按照这个有序分类进行排序，顺序会从“回帖者”到“发帖者”再到“评论罗伯特”
df = df.sort_values("用户标记")

# 创建用户标记到颜色的映射字典
color_dict = {
    "回帖": "#66B2FF",    # 蓝色
    "发帖": "#99CC99",    # 绿色
    "评论罗伯特": "#FF9999"  # 粉色
}

# # 为每列指定不同的变换方法
# transform_map = {
#     '信息量': 'log',
#     '形式多样性': None,
#     '情感强度': None,
#     '交互及时性': 'log',
#     '知识性': 'log',
# }

# transform_map = {
#     '粉丝数': 'log',
#     '微博数': 'log',
#     '认证信息': None,
# }

# transform_map = { 
#     '可读性': 'log',
#     '交互一致性': None,
#     '持续性': None,
#     '主题相关性': None,
# }

transform_map = {
    '安全性': None,
    '准确性': None,
    '新颖性': None,
}
# 调用修改后的函数，启用双坐标轴模式
fig, axes, _, _ = parallel_plot(
    df,
    columns_to_plot,
    color_by='category',
    color_attr='用户标记',
    color_dict=color_dict,
    transform=None,  # 不对整个数据框进行变换
    transform_map=transform_map,  # 对每列进行单独的变换
    twin_axis=True,  # 启用双坐标轴模式      
    curved=True,            
    spread=True,            
    alpha=0.6,              
    title='',
    save_path='C:/Users/panchonglin/Desktop/平行坐标图_20250428/可靠性_0514.svg',
    show_plot=False         
)

plt.show()
