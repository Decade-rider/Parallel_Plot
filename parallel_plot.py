import matplotlib
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import make_interp_spline
from scipy.stats import mstats

def parallel_plot(df, cols, rank_attr=None,
                    cmap='Spectral',
                    color_by='rank',  # 'rank' 或 'category'
                    color_attr=None,  # 当color_by='category'时使用的分类属性
                    color_dict=None,  # 分类到颜色的映射字典
                    transform=None,   # 全局默认变换
                    transform_map=None,  # 列到变换的映射字典
                    winsor_limits=(0.01, 0.01),
                    log_threshold=100,
                    quantiles=10,
                    spread=False,
                    curved=True,
                    curvedextend=0.05,
                    alpha=0.5,
                    title=None,
                    axis_labels=None,
                    show_plot=True,
                    save_path=None,
                    dpi=300,
                    twin_axis=False):  # 新参数，控制是否使用双坐标轴
    '''从pandas数据框生成平行坐标图，支持多种数值变换：        
    必需参数:
        df: 数据框
        cols: 用于坐标轴的列名列表
        rank_attr: 用于排名和着色的属性列名
    可选参数:
        cmap: 用于线条颜色映射的调色板
        spread: 用于分离分类值的散布参数
        curved: 是否使用样条插值创建曲线
        curvedextend: y轴扩展比例，用于容纳曲线弯曲
        alpha: 线条透明度
        title: 图表标题
        axis_labels: 自定义轴标签列表
        show_plot: 是否立即显示图表
        save_path: 图表保存路径
        dpi: 保存图表的DPI
    返回值:
        fig: 图形对象
        axes: 坐标轴对象
        x坐标和值矩阵
    新增变换参数:
        - transform=None: 仅归一化
        - transform='log': 对数变换（当最大/最小>log_threshold时）
        - transform='winsorize': 极值截断（按winsor_limits）
        - transform='robust': 基于中位数+IQR的RobustScaler
        - transform='quantile': 分位数分段（quantiles段），作为分类绘制
    
    新增颜色参数:
        - color_by='rank': 使用rank_attr作为颜色映射(原有行为)
        - color_by='category': 使用color_attr作为分类对象,按类别上色
        - color_dict: 分类值到颜色的映射字典
    
    新增双坐标轴参数:
        - twin_axis=True: 开启后，最后一个指标将显示为倒数第二个子图的副Y轴
    新增变换映射参数：
        - transform_map: 列名到变换方法的字典，优先级高于transform
        - 例如: {'列1': 'log', '列2': None, '列3': 'winsorize'}
    其他参数同原函数，保证字体、曲线、散布等功能不变。'''
    # 字体设置
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = 'Song Times'
    plt.rcParams['font.size'] = 14
    plt.rcParams['mathtext.fontset'] = 'custom'
    plt.rcParams['mathtext.rm'] = 'Song Times'
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42
    plt.rcParams['svg.fonttype'] = 'none'

    colmap = matplotlib.cm.get_cmap(cmap)
    
    # 根据双坐标轴模式确定子图数量
    use_twin_axis = twin_axis and len(cols) > 1
    n_subplots = len(cols) - 1 if use_twin_axis else len(cols)
    
    # 根据color_by模式确定all_cols
    if color_by == 'rank' and rank_attr:
        all_cols = cols + [rank_attr]
    else:
        all_cols = cols
        if color_by == 'category' and color_attr and color_attr not in cols:
            # 如果color_attr不在cols中，只需要预处理它但不画出来
            all_cols = cols.copy()  # 避免修改原始列表
    
    # 根据color_by模式确定all_cols和图形尺寸
    if color_by == 'category':
        # 使用图例时
        fig, axes = plt.subplots(1, n_subplots, sharey=False, figsize=(3*n_subplots, 5))
    else:
        # 使用颜色条时保留更多空间
        fig, axes = plt.subplots(1, n_subplots, sharey=False, figsize=(3*n_subplots+1.5, 5))
    
    # 确保axes始终是数组，即使只有一个元素
    if n_subplots == 1:
        axes = np.array([axes])

    valmat = np.ndarray((len(all_cols), len(df)))
    x = np.arange(len(all_cols))
    ax_info = {}

    # 处理所有数据列
    for i, col in enumerate(all_cols):
        vals = df[col]
        # 确定当前的列变换方法
        col_transform = transform # 默认使用全局变换
        if transform_map and col in transform_map:
            col_transform = transform_map[col]
        # 分位数分段
        if col_transform == 'quantile' and col != rank_attr and pd.api.types.is_numeric_dtype(vals) and len(np.unique(vals)) > 20:
            codes = pd.qcut(vals, quantiles, labels=False, duplicates='drop')
            max_code = codes.max() if codes.size else 1
            base_pos = codes.astype(float) / max_code
            valmat[i] = base_pos
            tick_labels = [f"Q{j+1}" for j in range(max_code+1)]
            tick_pos = [j/max_code for j in range(max_code+1)]
            ax_info[col] = [tick_labels, tick_pos]
            continue

        # 数值型变量
        if pd.api.types.is_numeric_dtype(vals) and len(np.unique(vals)) > 20:
            raw = vals.astype(float).values.copy()
            if col_transform == 'log' and raw.max()/max(raw.min(), 1e-9) > log_threshold:
                raw = np.log1p(raw - raw.min())
            if col_transform == 'winsorize':
                raw = mstats.winsorize(raw, limits=winsor_limits)
            if col_transform == 'robust':
                med = np.median(raw)
                q1, q3 = np.percentile(raw, [25, 75])
                iqr = q3 - q1
                if iqr > 0:
                    raw = (raw - med) / iqr
            minval, maxval = raw.min(), raw.max()
            vals_n = (raw - minval) / (maxval - minval)
            valmat[i] = vals_n
            nticks = 10
            tick_vals = [round(minval + j*(maxval-minval)/nticks, 2) for j in range(nticks+1)]
            tick_pos = [j/nticks for j in range(nticks+1)]
            ax_info[col] = [tick_vals, tick_pos]
        else:
            # 分类变量
            cat = vals.astype('category')
            codes = cat.cat.codes
            ncat = len(cat.cat.categories)
            if ncat > 1:
                base_pos = codes / (ncat - 1)
            else:
                base_pos = np.full_like(codes, 0.5, dtype=float)
            # 加散布偏移但不影响刻度位置
            if spread:
                offset = (np.random.rand(len(base_pos)) - 0.5) * (2e-2)
                plot_pos = base_pos + offset
            else:
                plot_pos = base_pos
            valmat[i] = plot_pos
            tick_labels = list(cat.cat.categories)
            tick_pos = [j/(ncat-1) for j in range(ncat)] if ncat>1 else [0.5]
            ax_info[col] = [tick_labels, tick_pos]

    # 获取颜色信息
    if color_by == 'category' and color_attr:
        # 处理分类颜色
        categories = df[color_attr].astype('category')
        cat_values = categories.cat.categories
        cat_codes = categories.cat.codes
        
        # 如果没有提供自定义颜色映射，则使用默认颜色映射
        if color_dict is None:
            n_cats = len(cat_values)
            default_colors = plt.cm.get_cmap(cmap, n_cats)
            color_dict = {cat: default_colors(i) for i, cat in enumerate(cat_values)}
        
        # 创建线条颜色列表
        line_colors = [color_dict.get(categories.iloc[j], 'gray') for j in range(len(df))]
        
        # 为图例准备唯一的类别-颜色对
        legend_elements = [plt.Line2D([0], [0], color=color_dict.get(cat, 'gray'), 
                                    lw=2, label=str(cat)) for cat in cat_values]
    
    # 创建双Y轴（如果启用）
    twin_ax = None
    if use_twin_axis:
        twin_ax = axes[-1].twinx()
        twin_ax.set_ylim(0-curvedextend if curved else 0-0.05, 1+(curvedextend if curved else 0.05))
        
        # 设置双Y轴的刻度和标签
        last_col = cols[-1]
        ticks, labels = ax_info[last_col][1], ax_info[last_col][0]
        twin_ax.set_yticks(ticks)
        twin_ax.set_yticklabels(labels)
        
        # 添加这一行 - 设置右侧Y轴的刻度朝内
        twin_ax.tick_params(axis='y', direction='in',pad=-8)
        
        # 设置右侧Y轴标签的水平对齐方式与左侧保持一致
        for label in twin_ax.yaxis.get_ticklabels():
            label.set_ha('right')  # 右对齐，与左侧Y轴的标签对齐方式一致
        
        # # 添加副Y轴标签
        # twin_ax.set_ylabel(axis_labels[-1] if axis_labels and len(axis_labels) >= len(cols) else last_col, 
        #                   rotation=270, labelpad=15)
        # twin_ax.yaxis.set_label_position("right")
    
    extend = curvedextend if curved else 0.05
    
    # 绘制连接线
    n_connections = len(cols) - 1  # 连接线数量总是比指标数少1
    for i in range(n_connections):
        ax = axes[min(i, len(axes)-1)]  # 防止索引越界
        
        # 确定是否是最后一条连接（如果使用双Y轴）
        is_last_connection = i == n_connections - 1 and use_twin_axis
        
        for j in range(valmat.shape[1]):
            if color_by == 'rank' and rank_attr:
                color = colmap(valmat[-1, j])
            else:
                color = line_colors[j] if color_by == 'category' else 'gray'
                
            # 获取要连接的两点坐标
            start_col_idx = i
            end_col_idx = i + 1
            start_y = valmat[start_col_idx, j]
            end_y = valmat[end_col_idx, j]
            
            if is_last_connection:
                # 最后一条连接使用双Y轴
                if curved:
                    density = 30
                    x_new = np.linspace(i, i+0.3, density)  # 在子图内绘制较短的连接线
                    # 使用与其他连接线一致的三次样条曲线
                    spline = make_interp_spline([i, i+0.3], [start_y, end_y], k=3, bc_type='clamped')
                    y_new = spline(x_new)
                    # 绘制连接线
                    axes[-1].plot(x_new, y_new, color=color, alpha=alpha, linewidth=0.1, rasterized=True)
                else:
                    # 直线连接
                    axes[-1].plot([i, i+0.3], [start_y, end_y], 
                                color=color, alpha=alpha, linewidth=0.1, rasterized=True)
            else:
                # 添加常规连接线的绘制代码
                if curved:
                    density = 30
                    x_new = np.linspace(i, i+1, density)
                    spline = make_interp_spline([i, i+1], [start_y, end_y], k=3, bc_type='clamped')
                    y_new = spline(x_new)
                    ax.plot(x_new, y_new, color=color, alpha=alpha, linewidth=0.1, rasterized=True)
                else:
                    ax.plot([i, i+1], [start_y, end_y], color=color, alpha=alpha, linewidth=0.1, rasterized=True)
    
    # 单独设置所有轴的范围属性
    for i, ax in enumerate(axes):
        if use_twin_axis and i == len(axes) - 1:
            # 最后一个子图有双Y轴，X轴范围需要更宽一些
            ax.set_xlim(i, i+0.3)  # 留出空间显示连接线
        else:
            ax.set_xlim(i, i+1)
        ax.set_ylim(0-extend, 1+extend)

    # 设置轴标签和刻度
    for i, ax in enumerate(axes):
        # 当前轴对应的列索引（考虑双Y轴模式）
        col_idx = i
        col = cols[col_idx]
        
        # 设置X轴刻度和标签
        if use_twin_axis and i == len(axes) - 1:
            # 最后一个子图有双Y轴，需要显示两个指标名称
            ax.xaxis.set_major_locator(ticker.FixedLocator([i, i+0.3]))
            
            # 设置两个标签，分别对应当前列和最后一列
            left_label = axis_labels[col_idx] if axis_labels and col_idx < len(axis_labels) else col
            right_label = axis_labels[-1] if axis_labels and len(axis_labels) >= len(cols) else cols[-1]
            ax.set_xticklabels([left_label, right_label])
            
            # 调整刻度标签位置和样式
            for tick in ax.get_xticklabels():
                tick.set_ha('center')
                tick.set_fontsize(14)
        else:
            ax.xaxis.set_major_locator(ticker.FixedLocator([i]))
            ax.set_xticklabels([axis_labels[col_idx] if axis_labels and col_idx < len(axis_labels) else col])
        
        # 设置Y轴刻度和标签
        ticks, labels = ax_info[col][1], ax_info[col][0]
        ax.yaxis.set_major_locator(ticker.FixedLocator(ticks))
        ax.set_yticklabels(labels)
        
        # 添加这一行 - 明确设置左侧Y轴刻度朝外
        ax.tick_params(axis='y', direction='out')
    
    # # 若双Y轴启用，确保其刻度方向也设置为朝外(可选，作为备份)
    # if twin_ax:
    #     twin_ax.tick_params(axis='y', direction='out')

    if title:
        plt.suptitle(title, fontsize=14)
        
    plt.subplots_adjust(wspace=0)

    # 根据颜色模式添加图例或颜色条
    if color_by == 'rank' and rank_attr:
        norm = matplotlib.colors.Normalize(0, 1)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        cbar = plt.colorbar(sm, ax=axes, pad=0.01, ticks=ax_info[rank_attr][1],
                           extend='both', extendrect=True, extendfrac=extend)
        cbar.ax.set_yticklabels(ax_info[rank_attr][0])
    elif color_by == 'category' and color_attr:
        # 添加图例
        fig.legend(handles=legend_elements,
                 loc='center right', bbox_to_anchor=(1.15, 0.5))
        plt.subplots_adjust(right=0.85)  # 为图例腾出空间

    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight', transparent=True)
    if show_plot:
        plt.show()

    return fig, axes, x, valmat