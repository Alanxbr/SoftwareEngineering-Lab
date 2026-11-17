"""模拟参与方的本地训练。"""

import os
import time

import numpy as np

from backend.federated import shuju
from backend.federated.moxing import MlpMoxing
from backend.services import yinsi_fuwu

# 单方单轮参与训练的样本上限，默认两万条；
# 可通过 PINGTAI_YANGBEN_SHANGXIAN 调低，避免低配机器上训练过慢。
YANGBEN_SHANGXIAN = int(os.environ.get('PINGTAI_YANGBEN_SHANGXIAN', '20000'))


def moni_xunlian(quanju_canshu: list[float], yangben_shu: int, zhongzi: int,
                 xuexilv: float, piliang: int, yinsipi: float,
                 jiancai_yuzhi: float) -> dict:
    """在本地数据上训练一轮，返回加噪后的模型更新与本地指标。"""
    kaishi = time.time()
    yangben = min(max(64, yangben_shu), YANGBEN_SHANGXIAN)
    X, y = shuju.shengcheng(yangben, zhongzi)
    Xxun, yxun, Xce, yce = shuju.chaiFen(X, y)
    moxing = MlpMoxing(zhongzi=zhongzi)
    moxing.she_canshu(quanju_canshu)
    suijishu = np.random.default_rng(zhongzi + 17)
    moxing.xunlian_yilun(Xxun, yxun, xuexilv, piliang, suijishu)
    gengxin = moxing.qu_canshu() - np.asarray(quanju_canshu, dtype=float)
    gengxin = yinsi_fuwu.jiagong_gaowei(gengxin.tolist(), yinsipi, jiancai_yuzhi)
    sunshi = moxing.sunshi(Xce, yce) if len(Xce) else moxing.sunshi(Xxun, yxun)
    zhunquelv = moxing.zhunquelv(Xce, yce) if len(Xce) else moxing.zhunquelv(Xxun, yxun)
    return {
        'gengxin': gengxin,
        'sunshi': round(float(sunshi), 6),
        'zhunquelv': round(float(zhunquelv), 6),
        'haoshi': round(time.time() - kaishi, 4),
    }
