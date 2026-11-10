"""模块装配：集中创建数据库连接、DAO 和业务服务。"""

from cunchu.dao import (
    CanjiaFangDao,
    LunciDao,
    RenwuDao,
    RizhiDao,
    ShujuDao,
    YonghuDao,
    YusuanDao,
)
from cunchu.shujuku import Shujuku
from gonggong.rizhi import RizhiZujian
from mokuai.shuju_fuwu import ShujuFuwu
from mokuai.xunlian_fuwu import XunlianFuwu
from mokuai.yinsi_fuwu import YinsiFuwu


class Zhuangpei:
    """把各层对象组装成可运行的服务集合。"""

    def __init__(self, shujuku_lujing: str, canshu_mulu: str):
        self.shujuku = Shujuku(shujuku_lujing)
        self.shujuku.dakai()
        self.shujuku.jianbiao()
        self.yonghu_dao = YonghuDao(self.shujuku)
        self.shuju_dao = ShujuDao(self.shujuku)
        self.renwu_dao = RenwuDao(self.shujuku)
        self.canjia_dao = CanjiaFangDao(self.shujuku)
        self.lunci_dao = LunciDao(self.shujuku)
        self.yusuan_dao = YusuanDao(self.shujuku)
        self.rizhi_dao = RizhiDao(self.shujuku)
        self.rizhi_zujian = RizhiZujian(self.rizhi_dao)
        self.shuju_fuwu = ShujuFuwu(self.shuju_dao)
        self.yinsi_fuwu = YinsiFuwu(self.renwu_dao, self.yusuan_dao)
        self.xunlian_fuwu = XunlianFuwu(
            self.renwu_dao,
            self.canjia_dao,
            self.lunci_dao,
            self.shuju_fuwu,
            self.yinsi_fuwu,
            canshu_mulu,
        )

    def guanbi(self) -> None:
        """关闭数据库连接。"""
        self.shujuku.guanbi()
