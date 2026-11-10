"""数据访问对象：全部 SQL 集中在本模块，业务层不拼接 SQL。"""

from typing import Any

from cunchu.shujuku import Shujuku


class DaoJichu:
    """DAO 公共基类，统一持有连接。"""

    def __init__(self, shujuku: Shujuku):
        self.shujuku = shujuku

    @property
    def lianjie(self):
        if self.shujuku.lianjie is None:
            raise RuntimeError('数据库尚未打开')
        return self.shujuku.lianjie

    def chaxun_yitiao(self, sql: str, canshu: tuple) -> dict | None:
        """查询单条记录并转成字典。"""
        hang = self.lianjie.execute(sql, canshu).fetchone()
        return dict(hang) if hang is not None else None

    def chaxun_duotiao(self, sql: str, canshu: tuple = ()) -> list[dict]:
        """查询多条记录并转成字典列表。"""
        return [dict(hang) for hang in self.lianjie.execute(sql, canshu).fetchall()]


class YonghuDao(DaoJichu):
    """用户表访问。"""

    def charru(self, yonghuming: str, mima_hash: str, youxiang: str, jiaose: str) -> int:
        with self.lianjie:
            youbiao = self.lianjie.execute(
                'INSERT INTO yonghu (yonghuming, mima_hash, youxiang, jiaose) '
                'VALUES (?, ?, ?, ?)',
                (yonghuming, mima_hash, youxiang, jiaose),
            )
        return int(youbiao.lastrowid)

    def chaxun_an_id(self, yonghu_id: int) -> dict | None:
        return self.chaxun_yitiao('SELECT * FROM yonghu WHERE id = ?', (yonghu_id,))


class ShujuDao(DaoJichu):
    """数据集表访问。"""

    def charru(self, tigongfang_id: int, mingcheng: str, geshi: str,
               daxiao: int, yangben_shu: int, tuomin_guize: str = '') -> int:
        with self.lianjie:
            youbiao = self.lianjie.execute(
                'INSERT INTO shujuji '
                '(tigongfang_id, mingcheng, geshi, daxiao, yangben_shu, tuomin_guize) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (tigongfang_id, mingcheng, geshi, daxiao, yangben_shu, tuomin_guize),
            )
        return int(youbiao.lastrowid)

    def chaxun_an_id(self, shujuji_id: int) -> dict | None:
        return self.chaxun_yitiao('SELECT * FROM shujuji WHERE id = ?', (shujuji_id,))

    def chaxun_an_mingcheng(self, tigongfang_id: int, mingcheng: str) -> dict | None:
        return self.chaxun_yitiao(
            'SELECT * FROM shujuji WHERE tigongfang_id = ? AND mingcheng = ?',
            (tigongfang_id, mingcheng),
        )

    def gengxin_zhuangtai(self, shujuji_id: int, zhuangtai: str) -> None:
        with self.lianjie:
            self.lianjie.execute(
                'UPDATE shujuji SET zhuangtai = ? WHERE id = ?',
                (zhuangtai, shujuji_id),
            )


class RenwuDao(DaoJichu):
    """训练任务表访问。"""

    def charru(self, chuangjianzhe_id: int, mingcheng: str, lunshu: int,
               piliang_daxiao: int, xuexilv: float, yinsipi: float,
               jiancai_yuzhi: float, yusuan_shangxian: float) -> int:
        with self.lianjie:
            youbiao = self.lianjie.execute(
                'INSERT INTO xunlian_renwu '
                '(chuangjianzhe_id, mingcheng, lunshu, piliang_daxiao, xuexilv, '
                ' yinsipi, jiancai_yuzhi, yusuan_shangxian) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (chuangjianzhe_id, mingcheng, lunshu, piliang_daxiao, xuexilv,
                 yinsipi, jiancai_yuzhi, yusuan_shangxian),
            )
        return int(youbiao.lastrowid)

    def chaxun_an_id(self, renwu_id: int) -> dict | None:
        return self.chaxun_yitiao('SELECT * FROM xunlian_renwu WHERE id = ?', (renwu_id,))

    def gengxin_zhuangtai(self, renwu_id: int, zhuangtai: str) -> None:
        with self.lianjie:
            self.lianjie.execute(
                'UPDATE xunlian_renwu SET zhuangtai = ? WHERE id = ?',
                (zhuangtai, renwu_id),
            )


class CanjiaFangDao(DaoJichu):
    """任务参与方表访问。"""

    def charru(self, renwu_id: int, yonghu_id: int, shujuji_id: int,
               yangben_shu: int) -> int:
        with self.lianjie:
            youbiao = self.lianjie.execute(
                'INSERT INTO renwu_canjiafang (renwu_id, yonghu_id, shujuji_id, yangben_shu) '
                'VALUES (?, ?, ?, ?)',
                (renwu_id, yonghu_id, shujuji_id, yangben_shu),
            )
        return int(youbiao.lastrowid)

    def chaxun_an_renwu(self, renwu_id: int) -> list[dict]:
        return self.chaxun_duotiao(
            'SELECT * FROM renwu_canjiafang WHERE renwu_id = ? ORDER BY id',
            (renwu_id,),
        )

    def gengxin_zhuangtai(self, renwu_id: int, yonghu_id: int, zhuangtai: str) -> None:
        with self.lianjie:
            self.lianjie.execute(
                'UPDATE renwu_canjiafang SET zhuangtai = ? WHERE renwu_id = ? AND yonghu_id = ?',
                (zhuangtai, renwu_id, yonghu_id),
            )


class LunciDao(DaoJichu):
    """轮次记录表访问。"""

    def charru(self, renwu_id: int, lunci_hao: int, sunshi: float,
               zhunquelv: float, haoshi: float, canshu_wenjian: str) -> int:
        with self.lianjie:
            youbiao = self.lianjie.execute(
                'INSERT INTO lunci_jilu '
                '(renwu_id, lunci_hao, sunshi, zhunquelv, haoshi, canshu_wenjian) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (renwu_id, lunci_hao, sunshi, zhunquelv, haoshi, canshu_wenjian),
            )
        return int(youbiao.lastrowid)

    def chaxun_an_renwu(self, renwu_id: int) -> list[dict]:
        return self.chaxun_duotiao(
            'SELECT * FROM lunci_jilu WHERE renwu_id = ? ORDER BY lunci_hao',
            (renwu_id,),
        )


class YusuanDao(DaoJichu):
    """隐私预算表访问。"""

    def charru(self, renwu_id: int, lunci_hao: int, benlun_eps: float,
               leiji_eps: float) -> int:
        with self.lianjie:
            youbiao = self.lianjie.execute(
                'INSERT INTO yinsi_yusuan (renwu_id, lunci_hao, benlun_eps, leiji_eps) '
                'VALUES (?, ?, ?, ?)',
                (renwu_id, lunci_hao, benlun_eps, leiji_eps),
            )
        return int(youbiao.lastrowid)

    def leiji(self, renwu_id: int) -> float:
        """返回任务累计消耗的 ε。"""
        hang = self.chaxun_yitiao(
            'SELECT COALESCE(SUM(benlun_eps), 0) AS heji FROM yinsi_yusuan WHERE renwu_id = ?',
            (renwu_id,),
        )
        return float(hang['heji']) if hang is not None else 0.0

    def chaxun_an_renwu(self, renwu_id: int) -> list[dict]:
        return self.chaxun_duotiao(
            'SELECT * FROM yinsi_yusuan WHERE renwu_id = ? ORDER BY lunci_hao',
            (renwu_id,),
        )


class RizhiDao(DaoJichu):
    """系统日志表访问。"""

    def charru(self, caozuozhe_id: int | None, caozuo_leixing: str,
               duixiang_leixing: str, duixiang_id: int | None, jieguo: str) -> int:
        with self.lianjie:
            youbiao = self.lianjie.execute(
                'INSERT INTO xitong_rizhi '
                '(caozuozhe_id, caozuo_leixing, duixiang_leixing, duixiang_id, jieguo) '
                'VALUES (?, ?, ?, ?, ?)',
                (caozuozhe_id, caozuo_leixing, duixiang_leixing, duixiang_id, jieguo),
            )
        return int(youbiao.lastrowid)

    def chaxun_quanbu(self) -> list[dict[str, Any]]:
        return self.chaxun_duotiao('SELECT * FROM xitong_rizhi ORDER BY id')
