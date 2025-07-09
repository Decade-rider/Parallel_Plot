# 平行坐标图绘制工具

本项目是基于 [parallel-coordinates-plot-dataframe](https://github.com/jraine/parallel-coordinates-plot-dataframe) 的改进版本，增加了更多的功能和自定义选项。

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

- **双坐标轴支持** (`twin_axis=True`): 最后一个指标可显示为副Y轴
- **平滑曲线** (`curved=True`): 使用样条插值创建平滑的连接线
- **散布效果** (`spread=True`): 为分类变量添加随机偏移以避免重叠
- **自定义透明度和样式**: 支持线条透明度、颜色映射等自定义

## 安装要求

```bash
pip install matplotlib numpy pandas scipy
```

## 基本用法

```python
import pandas as pd
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
5. **优化视觉效果**: 改进字体设置、刻度显示等细节

## 示例数据

```python
import numpy as np
import pandas as pd

# 创建示例数据
np.random.seed(42)
n_samples = 100

data = {
    '收入': np.random.lognormal(10, 1, n_samples),
    '年龄': np.random.normal(35, 10, n_samples),
    '教育年限': np.random.randint(8, 20, n_samples),
    '工作经验': np.random.normal(10, 5, n_samples),
    '满意度': np.random.uniform(1, 10, n_samples),
    '城市类型': np.random.choice(['一线', '二线', '三线'], n_samples),
    '综合评分': np.random.normal(7, 2, n_samples)
}

df = pd.DataFrame(data)

# 绘制平行坐标图
parallel_plot(
    df=df,
    cols=['收入', '年龄', '教育年限', '工作经验', '满意度'],
    rank_attr='综合评分',
    color_by='category',
    color_attr='城市类型',
    transform_map={'收入': 'log'},
    curved=True,
    title='个人档案平行坐标图'
)
```

## 致谢

本项目基于 [jraine/parallel-coordinates-plot-dataframe](https://github.com/jraine/parallel-coordinates-plot-dataframe) 进行改进和扩展。感谢原作者的贡献！

## 许可证

请参考原项目的许可证要求。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！
