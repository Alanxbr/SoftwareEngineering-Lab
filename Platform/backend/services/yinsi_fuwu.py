"""差分隐私：L2 裁剪、拉普拉斯噪声与预算检查。"""

import math
import random
from typing import Sequence

import numpy as np

from backend.db import YewuCuowu

CUOWU_YUSUAN = 4001
CUOWU_CANSHU = 4005


def jiancai(gengxin: Sequence[float], jiancai_yuzhi: float) -> list[float]:
    """把更新向量的 L2 范数裁剪到阈值以内。"""
    xiangliang = np.asarray(gengxin, dtype=float)
    fanshu = float(np.linalg.norm(xiangliang))
    if fanshu <= jiancai_yuzhi or fanshu == 0.0:
        return xiangliang.tolist()
    return (xiangliang * (jiancai_yuzhi / fanshu)).tolist()


def _laplace_suijishu(biliang: float, suijishu: random.Random) -> float:
    """用逆变换法生成拉普拉斯噪声。"""
    jingdu = suijishu.random() - 0.5
    duishu = math.log(max(1.0 - 2.0 * abs(jingdu), 1e-12))
    return -biliang * math.copysign(1.0, jingdu) * duishu


def jiazao(gengxin: Sequence[float], yinsipi: float,
           jiancai_yuzhi: float, suijishu: random.Random | None = None) -> list[float]:
    """对已裁剪向量逐维加入拉普拉斯噪声，b = C / ε。"""
    if yinsipi <= 0:
        raise YewuCuowu(CUOWU_CANSHU, '隐私预算 ε 必须大于 0')
    biliang = jiancai_yuzhi / yinsipi
    suijishu = suijishu or random.SystemRandom()
    return [float(x) + _laplace_suijishu(biliang, suijishu) for x in gengxin]


def jiagong(gengxin: Sequence[float], yinsipi: float, jiancai_yuzhi: float,
            suijishu: random.Random | None = None) -> list[float]:
    """先裁剪再加噪。"""
    return jiazao(jiancai(gengxin, jiancai_yuzhi), yinsipi, jiancai_yuzhi, suijishu)


def jiagong_gaowei(gengxin: Sequence[float], yinsipi: float,
                   jiancai_yuzhi: float,
                   suijishu: random.Random | None = None) -> list[float]:
    """高维模型更新加噪：噪声尺度按参数维度开方均摊。

    逐维使用 b = C / (ε·√d)，避免 178 维参数上的噪声完全淹没更新；
    这是课程演示环境下的工程折中，隐私预算仍按每轮 ε 记账。
    """
    xiangliang = np.asarray(jiancai(gengxin, jiancai_yuzhi), dtype=float)
    weidu = max(1, xiangliang.size)
    biliang = jiancai_yuzhi / (yinsipi * math.sqrt(weidu))
    suijishu = suijishu or random.SystemRandom()
    zaosheng = [_laplace_suijishu(biliang, suijishu) for _ in range(weidu)]
    return (xiangliang + np.asarray(zaosheng)).tolist()


def jiancha_yusuan(leiji_eps: float, benlun_eps: float, shangxian: float) -> float:
    """检查剩余预算，返回加入本轮后的累计值。"""
    if leiji_eps + benlun_eps > shangxian + 1e-9:
        shengyu = max(0.0, shangxian - leiji_eps)
        raise YewuCuowu(
            CUOWU_YUSUAN,
            f'隐私预算不足：剩余 {shengyu:.2f}，本轮需要 {benlun_eps:.2f}',
        )
    return round(leiji_eps + benlun_eps, 10)


def yusuan_zonglan(renwu: dict, leiji: float) -> dict:
    """生成任务隐私预算概览。"""
    shangxian = float(renwu['yusuan_shangxian'])
    return {
        'qiyong': True,
        'meilun_eps': float(renwu['yinsipi']),
        'jiancai_yuzhi': float(renwu['jiancai_yuzhi']),
        'leiji_eps': round(leiji, 10),
        'shangxian': shangxian,
        'shengyu': round(max(0.0, shangxian - leiji), 10),
        'shiyong_lv': round(min(1.0, leiji / shangxian) if shangxian else 0.0, 4),
    }
