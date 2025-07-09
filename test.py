import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from parallel_plot import parallel_plot

# 创建示例数据
np.random.seed(42)  # 设置随机种子以便复现结果
n_samples = 1000 # 样本数量
# 创建一个dataframe，包含企业相关数据
enterprise_data = {
    '企业名称': [f'企业{i+1}' for i in range(n_samples)],
    '营业收入_万元': np.random.lognormal(8, 1.5, n_samples),
    '员工数量_人': np.random.lognormal(5, 1, n_samples),
    '研发投入比例_%': np.random.beta(2, 5, n_samples) * 15,
    '客户满意度_分': np.random.normal(8.5, 1.2, n_samples),
    '市场份额_%': np.random.gamma(2, 2, n_samples),
    '社会责任评分': np.random.uniform(60, 95, n_samples),
    '行业类型': np.random.choice(['制造业', '服务业', '科技业', '金融业'], 
                              n_samples, p=[0.4, 0.3, 0.2, 0.1]),
    '企业规模': np.random.choice(['大型', '中型', '小型'], 
                              n_samples, p=[0.2, 0.5, 0.3]),
    '综合评分': np.random.normal(75, 12, n_samples)
}

df_enterprise = pd.DataFrame(enterprise_data)
# 对列重命名
df_enterprise.rename(columns={
    '营业收入_万元': '营业收入',
    '员工数量_人': '员工数量',
    '研发投入比例_%': '研发投入比例',
    '综合评分': '综合评分',
    '企业规模': '企业规模'
}, inplace=True)

columns_to_plot = ['营业收入', '员工数量', '研发投入比例','综合评分','企业规模']

df_enterprise['行业类型'] = df_enterprise['行业类型'].astype('category')
# 将企业规模用数字映射代替
df_enterprise['企业规模'] = df_enterprise['企业规模'].map({'大型': 3, '中型': 2, '小型': 1})

# 先给行业类型定义一个想要的顺序列表
category_order = ['金融业', '科技业', '制造业', '服务业']

# 将 df["行业类型"] 设置为有序分类
df_enterprise["行业类型"] = pd.Categorical(
    df_enterprise["行业类型"], 
    categories=category_order,  # 这里指定从底到顶的顺序
    ordered=True
)

# 按照这个有序分类进行排序
df_enterprise = df_enterprise.sort_values("行业类型")

# 创建行业类型到颜色的映射字典
color_dict = {
    "金融业": "#66B2FF",    # 蓝色
    "科技业": "#99CC99",    # 绿色
    "制造业": "#FF9999",  # 粉色
    "服务业": "#FFCC99"  # 橙色
}

# # 为每列指定不同的变换方法

transform_map = {
    '营业收入': 'log',
    '员工数量': 'log',
    '研发投入比例': None,
    '综合评分': None,
    '企业规模': None
}
# 调用修改后的函数，启用双坐标轴模式
fig, axes, _, _ = parallel_plot(
    df_enterprise,
    columns_to_plot,
    color_by='category',
    color_attr='行业类型',
    color_dict=color_dict,
    transform=None,  # 不对整个数据框进行变换
    transform_map=transform_map,  # 对每列进行单独的变换
    twin_axis=True,  # 启用双坐标轴模式      
    curved=True,            
    spread=True,            
    alpha=0.6,              
    title='',
    save_path='test/enteprise.svg',
    show_plot=False         
)

plt.show()