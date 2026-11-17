"""本地训练数据：合成数据生成与 CSV 读取。"""

import csv
from functools import lru_cache
from pathlib import Path

import numpy as np

from backend.federated.moxing import SHURU_WEIDU

# 所有参与方与评估集共享同一对类中心，保证标签语义一致；
# 各方仅以不同随机种子抽取样本，模拟“数据分布相同、样本不同”的横向联邦场景。
QUANJU_ZHONGZI = 2024103365


@lru_cache(maxsize=None)
def _zhongxin(weidu: int) -> tuple[np.ndarray, np.ndarray]:
    """固定类中心，进程内只生成一次。"""
    suijishu = np.random.default_rng(QUANJU_ZHONGZI)
    zhongxin0 = suijishu.normal(0.0, 0.6, weidu)
    zhongxin1 = zhongxin0 + suijishu.normal(0.0, 2.2, weidu)
    return zhongxin0, zhongxin1


def shengcheng(yangben_shu: int, zhongzi: int,
               weidu: int = SHURU_WEIDU) -> tuple[np.ndarray, np.ndarray]:
    """生成两类高斯簇，模拟参与方本地数据。"""
    zhongxin0, zhongxin1 = _zhongxin(weidu)
    suijishu = np.random.default_rng(zhongzi)
    biaoqian = suijishu.integers(0, 2, yangben_shu)
    zhongxin = np.where(biaoqian[:, None] == 0, zhongxin0, zhongxin1)
    tezheng = zhongxin + suijishu.normal(0.0, 1.0, (yangben_shu, weidu))
    return tezheng, biaoqian.astype(int)


def jiazai_csv(lujing: str | Path,
               weidu: int = SHURU_WEIDU) -> tuple[np.ndarray, np.ndarray]:
    """读取 CSV：最后一列为标签，其余为数值特征。"""
    lujing = Path(lujing)
    if not lujing.exists():
        raise FileNotFoundError(f'数据文件不存在：{lujing}')
    tezheng, biaoqian = [], []
    with lujing.open('r', encoding='utf-8-sig', newline='') as wenjian:
        duqu = csv.reader(wenjian)
        for hang in duqu:
            if not hang or all(not x.strip() for x in hang):
                continue
            try:
                shuzhi = [float(x) for x in hang]
            except ValueError:
                continue
            if len(shuzhi) < 2:
                continue
            tezheng.append(shuzhi[:-1])
            biaoqian.append(int(shuzhi[-1]))
    if not tezheng:
        raise ValueError('CSV 中没有可用的数值样本')
    X = np.asarray(tezheng, dtype=float)
    if X.shape[1] < weidu:
        X = np.pad(X, ((0, 0), (0, weidu - X.shape[1])))
    elif X.shape[1] > weidu:
        X = X[:, :weidu]
    y = np.asarray(biaoqian, dtype=int)
    y = np.where(y > 0, 1, 0)
    return X, y


def chaiFen(X: np.ndarray, y: np.ndarray,
            bilv: float = 0.8) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """按比例切分训练集与本地验证集。"""
    qie = max(1, int(len(X) * bilv))
    return X[:qie], y[:qie], X[qie:], y[qie:]
