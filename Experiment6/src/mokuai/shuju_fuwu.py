"""数据管理模块：只保存数据集元信息，不接收原始样本。"""

from cunchu.dao import ShujuDao
from gonggong.fanhui import CUOWU_CANSHU, CUOWU_CHONGMING, FanhuiJieguo


class ShujuFuwu:
    """数据集登记、查询与停用。"""

    def __init__(self, shuju_dao: ShujuDao):
        self.shuju_dao = shuju_dao

    def dengji_shujuji(self, tigongfang_id: int, mingcheng: str, geshi: str,
                       daxiao: int, yangben_shu: int,
                       tuomin_guize: str = '') -> FanhuiJieguo:
        """登记数据集元信息，同一提供方下名称不能重复。"""
        if not mingcheng.strip():
            return FanhuiJieguo.shibai_fanhui(CUOWU_CANSHU, '数据集名称不能为空')
        if daxiao <= 0 or yangben_shu <= 0:
            return FanhuiJieguo.shibai_fanhui(
                CUOWU_CANSHU, '文件大小和样本数必须为正数'
            )
        if self.shuju_dao.chaxun_an_mingcheng(tigongfang_id, mingcheng) is not None:
            return FanhuiJieguo.shibai_fanhui(
                CUOWU_CHONGMING, '同一提供方下数据集名称已存在'
            )
        shujuji_id = self.shuju_dao.charru(
            tigongfang_id, mingcheng, geshi, daxiao, yangben_shu, tuomin_guize
        )
        return FanhuiJieguo.chenggong_fanhui({'shujuji_id': shujuji_id}, '数据集登记成功')

    def chaxun_shujuji(self, shujuji_id: int) -> FanhuiJieguo:
        """按编号查询数据集，供联邦训练模块校验可用性。"""
        shujuji = self.shuju_dao.chaxun_an_id(shujuji_id)
        if shujuji is None:
            return FanhuiJieguo.shibai_fanhui(CUOWU_CANSHU, '数据集不存在')
        return FanhuiJieguo.chenggong_fanhui(shujuji)

    def tingyong_shujuji(self, shujuji_id: int) -> FanhuiJieguo:
        """停用数据集，保留历史记录。"""
        if self.shuju_dao.chaxun_an_id(shujuji_id) is None:
            return FanhuiJieguo.shibai_fanhui(CUOWU_CANSHU, '数据集不存在')
        self.shuju_dao.gengxin_zhuangtai(shujuji_id, 'yitingyong')
        return FanhuiJieguo.chenggong_fanhui(None, '数据集已停用')
