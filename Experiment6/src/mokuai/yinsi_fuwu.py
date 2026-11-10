"""隐私保护模块：先做 L2 裁剪，再加拉普拉斯噪声。"""

import math
import random

from cunchu.dao import RenwuDao, YusuanDao
from gonggong.fanhui import FanhuiJieguo


class YinsiFuwu:
    """隐私预算检查与差分隐私加噪，均为纯函数式接口。"""

    def __init__(self, renwu_dao: RenwuDao, yusuan_dao: YusuanDao):
        self.renwu_dao = renwu_dao
        self.yusuan_dao = yusuan_dao

    def jiancai_gengxin(self, gengxin: list[float],
                        jiancai_yuzhi: float) -> list[float]:
        """把模型更新的 L2 范数裁剪到阈值以内。"""
        if jiancai_yuzhi <= 0:
            raise ValueError('裁剪阈值必须为正数')
        fanzhi = math.sqrt(sum(x * x for x in gengxin))
        if fanzhi == 0 or fanzhi <= jiancai_yuzhi:
            return list(gengxin)
        bili = jiancai_yuzhi / fanzhi
        return [x * bili for x in gengxin]

    def jiazao_gengxin(self, gengxin: list[float], eps: float,
                       jiancai_yuzhi: float,
                       suijishu: random.Random | None = None) -> list[float]:
        """裁剪后按拉普拉斯机制加噪，返回可直接上传的更新。"""
        if eps <= 0:
            raise ValueError('隐私预算 ε 必须为正数')
        suijishu = suijishu or random.Random()
        jiancai = self.jiancai_gengxin(gengxin, jiancai_yuzhi)
        biliang = jiancai_yuzhi / eps
        return [x + self._laplace_suijishu(biliang, suijishu) for x in jiancai]

    @staticmethod
    def _laplace_suijishu(biliang: float, suijishu: random.Random) -> float:
        """逆变换采样生成拉普拉斯噪声。"""
        jingdu = suijishu.random() - 0.5
        duishu = math.log(1.0 - 2.0 * abs(jingdu))
        return -biliang * math.copysign(1.0, jingdu) * duishu

    def jiancha_yusuan(self, renwu_id: int, benlun_eps: float) -> bool:
        """判断累计消耗加上本轮后是否仍在上限内。"""
        renwu = self.renwu_dao.chaxun_an_id(renwu_id)
        if renwu is None:
            return False
        leiji = self.yusuan_dao.leiji(renwu_id)
        return leiji + benlun_eps <= float(renwu['yusuan_shangxian'])

    def jilu_yusuan(self, renwu_id: int, lunci_hao: int,
                    benlun_eps: float) -> FanhuiJieguo:
        """写入本轮预算并返回累计消耗和剩余额度。"""
        renwu = self.renwu_dao.chaxun_an_id(renwu_id)
        if renwu is None:
            return FanhuiJieguo.shibai_fanhui(4005, '任务不存在')
        leiji = self.yusuan_dao.leiji(renwu_id) + benlun_eps
        self.yusuan_dao.charru(renwu_id, lunci_hao, benlun_eps, leiji)
        shengyu = float(renwu['yusuan_shangxian']) - leiji
        return FanhuiJieguo.chenggong_fanhui(
            {'lunci_hao': lunci_hao, 'benlun_eps': benlun_eps,
             'leiji_eps': leiji, 'shengyu_yusuan': shengyu},
            '隐私预算已记录',
        )

    def chaxun_leiji(self, renwu_id: int) -> float:
        """查询任务累计消耗的 ε。"""
        return self.yusuan_dao.leiji(renwu_id)
