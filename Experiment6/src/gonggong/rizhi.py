"""日志组件：接口层和业务层共用，不依赖系统管理模块。"""

from cunchu.dao import RizhiDao


class RizhiZujian:
    """记录操作日志，失败不阻断主业务。"""

    def __init__(self, rizhi_dao: RizhiDao):
        self.rizhi_dao = rizhi_dao

    def rizhi(self, caozuozhe_id: int | None, caozuo_leixing: str,
              duixiang_leixing: str, duixiang_id: int | None, jieguo: str) -> None:
        """写入一条日志。"""
        self.rizhi_dao.charru(
            caozuozhe_id, caozuo_leixing, duixiang_leixing, duixiang_id, jieguo
        )
