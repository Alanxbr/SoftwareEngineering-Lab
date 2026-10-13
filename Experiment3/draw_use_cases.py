# -*- coding: utf-8 -*-
"""实验3 UML 用例图绘制脚本
使用 matplotlib 绘制两张用例图：
  1) 核心业务用例图（数据提供方 / 数据使用方）
  2) 系统管理用例图（系统管理员）
输出 PNG（高分辨率）与 SVG。
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Circle

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

BLACK = '#111111'
GRAY = '#333333'


def draw_actor(ax, x, y, name, s=1.0):
    """绘制参与者（火柴人）+ 名字"""
    r = 0.16 * s
    ax.add_patch(Circle((x, y + 0.35 * s), r, fill=False, lw=1.7, color=BLACK, zorder=4))
    ax.plot([x, x], [y + 0.19 * s, y - 0.12 * s], color=BLACK, lw=1.7, zorder=4)
    ax.plot([x - 0.22 * s, x + 0.22 * s], [y + 0.02 * s, y + 0.02 * s], color=BLACK, lw=1.7, zorder=4)
    ax.plot([x, x - 0.18 * s], [y - 0.12 * s, y - 0.40 * s], color=BLACK, lw=1.7, zorder=4)
    ax.plot([x, x + 0.18 * s], [y - 0.12 * s, y - 0.40 * s], color=BLACK, lw=1.7, zorder=4)
    ax.text(x, y - 0.62 * s, name, ha='center', va='top', fontsize=11, color=BLACK, zorder=5)


def draw_usecase(ax, x, y, name, w=2.0, h=0.85, fontsize=10):
    """绘制用例（椭圆）"""
    ax.add_patch(Ellipse((x, y), w, h, fill=False, lw=1.4, color=BLACK, zorder=4))
    ax.text(x, y, name, ha='center', va='center', fontsize=fontsize, color=BLACK, zorder=5)


def _arrow(ax, p1, p2, dashed=False, shrinkA=0, shrinkB=0):
    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle='->', lw=1.25, color=BLACK,
                                linestyle='dashed' if dashed else 'solid',
                                shrinkA=shrinkA, shrinkB=shrinkB),
                zorder=3)


def _rel_label(ax, p1, p2, label, dx=0, dy=0.14):
    mx, my = (p1[0] + p2[0]) / 2 + dx, (p1[1] + p2[1]) / 2 + dy
    ax.text(mx, my, label, ha='center', va='bottom', fontsize=8.5,
            style='italic', color=GRAY, zorder=6,
            bbox=dict(fc='white', ec='none', pad=1.2))


def assoc(ax, p1, p2):
    _arrow(ax, p1, p2, shrinkA=6, shrinkB=30)


def include(ax, p1, p2, dx=0, dy=0.14):
    _arrow(ax, p1, p2, dashed=True, shrinkA=28, shrinkB=30)
    _rel_label(ax, p1, p2, '<<include>>', dx=dx, dy=dy)


def extend(ax, p1, p2, dx=0, dy=0.14):
    _arrow(ax, p1, p2, dashed=True, shrinkA=28, shrinkB=30)
    _rel_label(ax, p1, p2, '<<extend>>', dx=dx, dy=dy)


def new_axes(w=12.5, h=8.6, xr=(0, 13), yr=(0, 8.6)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xr)
    ax.set_ylim(*yr)
    ax.axis('off')
    return fig, ax


def system_box(ax, x0, y0, x1, y1, title):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                           lw=1.3, color=BLACK, linestyle=(0, (5, 4)), zorder=2))
    ax.text((x0 + x1) / 2, y1 - 0.28, title, ha='center', va='center',
            fontsize=12.5, weight='bold', color=BLACK, zorder=5)


def save(fig, name):
    fig.savefig(f'{name}.png', dpi=220, bbox_inches='tight', facecolor='white')
    fig.savefig(f'{name}.svg', bbox_inches='tight', facecolor='white')
    plt.close(fig)


# ======================================================================
# 用例图 1：隐私计算数据共享平台 —— 核心业务用例图
# ======================================================================
def diagram1():
    fig, ax = new_axes()
    # 系统边界
    system_box(ax, 3.2, 0.5, 12.4, 7.7, '隐私计算数据共享平台')

    # 参与者
    draw_actor(ax, 0.9, 6.6, '数据提供方')
    draw_actor(ax, 0.9, 1.9, '数据使用方')

    # 用例
    draw_usecase(ax, 5.1, 7.1, '注册登录')
    draw_usecase(ax, 5.1, 5.7, '数据本地导入')
    draw_usecase(ax, 8.4, 6.35, '数据格式校验')
    draw_usecase(ax, 8.4, 5.05, '数据脱敏处理')
    draw_usecase(ax, 5.1, 4.05, '本地模型训练')
    draw_usecase(ax, 8.4, 4.05, '差分隐私加噪')
    draw_usecase(ax, 5.1, 2.55, '模型参数加密上传')
    draw_usecase(ax, 5.1, 1.35, '创建联邦训练任务')
    draw_usecase(ax, 8.4, 1.35, '联邦聚合')
    draw_usecase(ax, 11.0, 5.7, '查看训练结果')
    draw_usecase(ax, 11.0, 4.35, '训练曲线展示')

    # 关联（参与者 -> 用例）
    assoc(ax, (1.12, 6.6), (4.1, 7.1))     # 数据提供方 -> 注册登录
    assoc(ax, (1.12, 6.6), (4.1, 5.7))     # 数据提供方 -> 数据本地导入
    assoc(ax, (1.12, 6.6), (4.1, 4.05))    # 数据提供方 -> 本地模型训练
    assoc(ax, (1.12, 6.6), (4.1, 2.55))    # 数据提供方 -> 模型参数加密上传
    assoc(ax, (1.12, 1.9), (4.1, 7.1))     # 数据使用方 -> 注册登录
    assoc(ax, (1.12, 1.9), (4.1, 1.35))    # 数据使用方 -> 创建联邦训练任务
    assoc(ax, (1.12, 1.9), (10.0, 5.7))    # 数据使用方 -> 查看训练结果

    # 包含 / 扩展关系
    include(ax, (5.9, 5.7), (7.4, 6.35))   # 数据本地导入 include 数据格式校验
    include(ax, (5.9, 5.7), (7.4, 5.05))   # 数据本地导入 include 数据脱敏处理
    include(ax, (5.9, 4.05), (7.4, 4.05))  # 本地模型训练 include 差分隐私加噪
    include(ax, (5.9, 1.35), (7.4, 1.35))  # 创建联邦训练任务 include 联邦聚合
    extend(ax, (10.35, 4.35), (10.35, 5.0))  # 训练曲线展示 extend 查看训练结果

    save(fig, 'use_case_diagram_1_核心业务')
    print('图1 完成')


# ======================================================================
# 用例图 2：隐私计算数据共享平台 —— 系统管理用例图
# ======================================================================
def diagram2():
    fig, ax = new_axes(w=11.5, h=7.6, xr=(0, 12), yr=(0, 7.8))
    system_box(ax, 3.2, 0.5, 11.5, 7.2, '隐私计算数据共享平台 · 系统管理')

    draw_actor(ax, 0.9, 3.8, '系统管理员')

    draw_usecase(ax, 5.1, 6.6, '管理员登录')
    draw_usecase(ax, 5.1, 5.2, '用户管理')
    draw_usecase(ax, 8.5, 5.8, '角色权限控制')
    draw_usecase(ax, 5.1, 3.7, '训练任务管理')
    draw_usecase(ax, 8.5, 3.1, '隐私预算追踪')
    draw_usecase(ax, 5.1, 2.1, '系统日志查看')
    draw_usecase(ax, 8.5, 1.3, '数据审计')

    assoc(ax, (1.12, 3.8), (4.1, 6.6))     # -> 管理员登录
    assoc(ax, (1.12, 3.8), (4.1, 5.2))     # -> 用户管理
    assoc(ax, (1.12, 3.8), (4.1, 3.7))     # -> 训练任务管理
    assoc(ax, (1.12, 3.8), (4.1, 2.1))     # -> 系统日志查看

    include(ax, (5.9, 5.2), (7.4, 5.8))    # 用户管理 include 角色权限控制
    include(ax, (5.9, 3.7), (7.4, 3.1))    # 训练任务管理 include 隐私预算追踪
    extend(ax, (7.55, 1.3), (6.05, 2.1))   # 数据审计 extend 系统日志查看

    save(fig, 'use_case_diagram_2_系统管理')
    print('图2 完成')


if __name__ == '__main__':
    diagram1()
    diagram2()
    print('全部完成')
