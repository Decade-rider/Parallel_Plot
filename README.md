# 平行坐标图绘制工具

本项目是基于 [parallel-coordinates-plot-dataframe](https://github.com/jraine/parallel-coordinates-plot-dataframe) 的改进版本，增加了更多的功能和自定义选项，面临分类数据时可以选择不调用颜色条也能正确映射线条颜色，能更灵活地处理可视化过程中遇到的量纲不统一、数据分布差异较大等情况。此外，还通过启用矢量绘图的栅格设置保证了数据量较大时能加快绘图速度，并且可以将保存的矢量图(svg、pdf)导入visio、Ai等进一步进行精调。

## 功能特性

### 🎨 多种颜色映射模式

- **按排名着色** (`color_by='rank'`): 使用数值属性进行颜色映射
- **按类别着色** (`color_by='category'`): 使用分类属性进行颜色映射，支持自定义颜色字典

### 📊 丰富的数据变换选项

- **归一化** (`transform=None`): 仅进行标准归一化
- **对数变换** (`transform='log'`): 当数据范围较大时自动应用对数变换
- **极值截断** (`transform='winsorize'`): 截断极端值以减少异常值影响
- **鲁棒缩放** (`transform='robust'`): 基于中位数和四分位距的鲁棒缩放
- **分位数分段** (`transform='quantile'`): 将连续变量转换为分位数段
- **列级变换映射** (`transform_map`): 为不同列指定不同的变换方法

### 🎯 高级可视化功能

- **双坐标轴支持** (`twin_axis=True`): 最后一个指标可显示为副Y轴，建议在不需要颜色条的时候打开
- **平滑曲线** (`curved=True`): 使用样条插值创建平滑的连接线
- **散布效果** (`spread=True`): 为分类变量添加随机偏移以避免重叠
- **自定义透明度和样式**: 支持线条透明度、颜色映射等自定义

## 安装要求

```bash
pip install matplotlib numpy pandas scipy
```

## 字体配置

建议提前配置Song Times字体，可以在其他绘图中直接显示中文宋体，英文、数字均为Times Newroman字体。配置可参照[字体和并工具](https://www.wolai.com/matplotlib/bjA8MaBAjCo5W6Jvc9PZYW)

## 基本用法

```python
import pandas as pd
import matplotlib.pyplot as plt
from parallel_plot import parallel_plot

# 准备数据
df = pd.read_csv('your_data.csv')

# 基本用法
fig, axes, x, valmat = parallel_plot(
    df=df,
    cols=['指标1', '指标2', '指标3', '指标4'],
    rank_attr='综合得分'
)
```

## 高级用法示例

### 1. 按类别着色

```python
# 按类别着色，使用自定义颜色映射
color_dict = {
    '类别A': 'red',
    '类别B': 'blue', 
    '类别C': 'green'
}

parallel_plot(
    df=df,
    cols=['指标1', '指标2', '指标3'],
    color_by='category',
    color_attr='分类列',
    color_dict=color_dict,
    title='按类别着色的平行坐标图'
)
```

### 2. 使用不同的数据变换

```python
# 为不同列指定不同的变换方法
transform_map = {
    '收入': 'log',          # 对数变换
    '年龄': None,           # 仅归一化
    '评分': 'winsorize',    # 极值截断
    '排名': 'quantile'      # 分位数分段
}

parallel_plot(
    df=df,
    cols=['收入', '年龄', '评分', '排名'],
    rank_attr='综合得分',
    transform_map=transform_map,
    curved=True
)
```

### 3. 双坐标轴模式

```python
# 启用双坐标轴，最后一个指标显示为副Y轴
parallel_plot(
    df=df,
    cols=['指标1', '指标2', '指标3', '指标4'],
    rank_attr='综合得分',
    twin_axis=True,
    axis_labels=['自定义标签1', '自定义标签2', '自定义标签3', '自定义标签4']
)
```

## 参数说明

### 必需参数

- `df`: pandas数据框
- `cols`: 用于坐标轴的列名列表
- `rank_attr`: 用于排名和着色的属性列名（当`color_by='rank'`时）

### 颜色控制参数

- `cmap`: 颜色映射名称，默认'Spectral'
- `color_by`: 着色模式，'rank'或'category'
- `color_attr`: 分类属性列名（当`color_by='category'`时）
- `color_dict`: 分类值到颜色的映射字典

### 数据变换参数

- `transform`: 全局默认变换方法
- `transform_map`: 列名到变换方法的映射字典
- `winsor_limits`: 极值截断的限制比例，默认(0.01, 0.01)
- `log_threshold`: 应用对数变换的阈值，默认100
- `quantiles`: 分位数分段的段数，默认10

### 可视化控制参数

- `twin_axis`: 是否启用双坐标轴，默认False
- `curved`: 是否使用平滑曲线，默认True
- `curvedextend`: Y轴扩展比例，默认0.05
- `spread`: 是否为分类变量添加散布效果，默认False
- `alpha`: 线条透明度，默认0.5

### 输出控制参数

- `title`: 图表标题
- `axis_labels`: 自定义轴标签列表
- `show_plot`: 是否显示图表，默认True
- `save_path`: 保存路径
- `dpi`: 保存分辨率，默认300

## 返回值

函数返回一个包含四个元素的元组：

- `fig`: matplotlib图形对象
- `axes`: 坐标轴对象数组
- `x`: X坐标数组
- `valmat`: 归一化后的值矩阵

## 改进内容

相比原始版本，本项目主要改进包括：

1. **新增双坐标轴功能**: 支持将最后一个指标显示为副Y轴
2. **扩展颜色映射**: 支持按类别着色和自定义颜色字典
3. **丰富数据变换**: 新增对数、极值截断、鲁棒缩放、分位数分段等变换
4. **列级变换映射**: 支持为不同列指定不同的变换方法
5. **优化视觉效果**: 改进字体设置、刻度显示等细节，支持中文宋体，英文Times Newroman的字体显示，对科研更友好
6. **支持图片进一步加工**：保证输出后的矢量图的文字、刻度等可以在其他绘图软件进行调整

## 完整应用示例

以下是一个完整的企业评价分析示例，展示了多种功能的综合使用：

```python
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
```

![alt text](test/enteprise.png)

这个示例展示了：

- 🔄 **多种数据变换**：对数变换处理跨度大的数据，鲁棒变换处理异常值
- 🎨 **两种着色模式**：按数值排名着色和按类别分组着色
- 📊 **双坐标轴功能**：突出显示关键的结果指标
- 💾 **多种保存格式**：SVG矢量图、PDF文档、PNG图片

## 说明

该项目关于图例部分显示与图之间存在一定的距离影响观感，建议要么在其他软件微调，要么注释掉

## 致谢

本项目基于 [jraine/parallel-coordinates-plot-dataframe](https://github.com/jraine/parallel-coordinates-plot-dataframe) 进行改进和扩展。感谢原作者的贡献！

## 许可证

请参考原项目的许可证要求。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！
