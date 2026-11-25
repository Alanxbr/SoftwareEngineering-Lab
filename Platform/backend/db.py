"""SQLite 连接、建表与通用查询函数。"""

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from backend.config import SHUJUKU_LUJING, chushihua_mulu


JIANTUO_SQL = """
CREATE TABLE IF NOT EXISTS yonghu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    yonghuming TEXT NOT NULL UNIQUE,
    mima_hash TEXT NOT NULL,
    youxiang TEXT NOT NULL,
    jiaose TEXT NOT NULL CHECK (jiaose IN ('tigongfang', 'shiyongfang', 'guanliyuan')),
    zhuangtai TEXT NOT NULL DEFAULT 'zhengchang'
        CHECK (zhuangtai IN ('zhengchang', 'tingyong')),
    chuangjian_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shujuji (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tigongfang_id INTEGER NOT NULL REFERENCES yonghu(id),
    mingcheng TEXT NOT NULL,
    geshi TEXT NOT NULL,
    daxiao INTEGER NOT NULL CHECK (daxiao > 0),
    yangben_shu INTEGER NOT NULL CHECK (yangben_shu > 0),
    ziduan TEXT NOT NULL DEFAULT '[]',
    benzhi_lujing TEXT NOT NULL DEFAULT '',
    tuomin_guize TEXT NOT NULL DEFAULT '',
    zhuangtai TEXT NOT NULL DEFAULT 'yijiaoyan'
        CHECK (zhuangtai IN ('daijiaoyan', 'yijiaoyan', 'yitingyong')),
    jiaoyan_jielun TEXT NOT NULL DEFAULT '',
    chuangjian_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tigongfang_id, mingcheng)
);

CREATE TABLE IF NOT EXISTS xunlian_renwu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chuangjianzhe_id INTEGER NOT NULL REFERENCES yonghu(id),
    mingcheng TEXT NOT NULL,
    moxing_leixing TEXT NOT NULL DEFAULT 'mlp_8_16_2',
    lunshu INTEGER NOT NULL CHECK (lunshu > 0),
    piliang_daxiao INTEGER NOT NULL CHECK (piliang_daxiao > 0),
    xuexilv REAL NOT NULL CHECK (xuexilv > 0),
    yinsipi REAL NOT NULL CHECK (yinsipi > 0),
    jiancai_yuzhi REAL NOT NULL CHECK (jiancai_yuzhi > 0),
    yusuan_shangxian REAL NOT NULL CHECK (yusuan_shangxian > 0),
    yunxing_moshi TEXT NOT NULL DEFAULT 'moni'
        CHECK (yunxing_moshi IN ('moni', 'zhenshi')),
    zhuangtai TEXT NOT NULL DEFAULT 'daichufa'
        CHECK (zhuangtai IN ('daichufa', 'xunlianzhong', 'yiwancheng', 'yichang', 'yiquxiao')),
    dangqian_lunci INTEGER NOT NULL DEFAULT 0,
    cuowu_xiaoxi TEXT NOT NULL DEFAULT '',
    chuangjian_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    qidong_shijian TEXT,
    jieshu_shijian TEXT
);

CREATE TABLE IF NOT EXISTS renwu_canjiafang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    renwu_id INTEGER NOT NULL REFERENCES xunlian_renwu(id) ON DELETE CASCADE,
    yonghu_id INTEGER NOT NULL REFERENCES yonghu(id),
    shujuji_id INTEGER NOT NULL REFERENCES shujuji(id),
    yangben_shu INTEGER NOT NULL CHECK (yangben_shu > 0),
    zhuangtai TEXT NOT NULL DEFAULT 'daixunlian'
        CHECK (zhuangtai IN ('daixunlian', 'xunlianzhong', 'yiwancheng', 'diaoxian')),
    UNIQUE (renwu_id, yonghu_id)
);

CREATE TABLE IF NOT EXISTS lunci_jilu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    renwu_id INTEGER NOT NULL REFERENCES xunlian_renwu(id) ON DELETE CASCADE,
    lunci_hao INTEGER NOT NULL CHECK (lunci_hao > 0),
    sunshi REAL NOT NULL,
    zhunquelv REAL NOT NULL,
    haoshi REAL NOT NULL,
    canshu_wenjian TEXT NOT NULL,
    canjia_shu INTEGER NOT NULL DEFAULT 0,
    chuangjian_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (renwu_id, lunci_hao)
);

CREATE TABLE IF NOT EXISTS yinsi_yusuan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    renwu_id INTEGER NOT NULL REFERENCES xunlian_renwu(id) ON DELETE CASCADE,
    lunci_hao INTEGER NOT NULL CHECK (lunci_hao > 0),
    benlun_eps REAL NOT NULL CHECK (benlun_eps > 0),
    leiji_eps REAL NOT NULL CHECK (leiji_eps > 0),
    jilu_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (renwu_id, lunci_hao)
);

CREATE TABLE IF NOT EXISTS renwu_gengxin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    renwu_id INTEGER NOT NULL REFERENCES xunlian_renwu(id) ON DELETE CASCADE,
    lunci_hao INTEGER NOT NULL CHECK (lunci_hao > 0),
    yonghu_id INTEGER NOT NULL REFERENCES yonghu(id),
    gengxin TEXT NOT NULL,
    yangben_shu INTEGER NOT NULL CHECK (yangben_shu > 0),
    sunshi REAL NOT NULL DEFAULT 0,
    zhunquelv REAL NOT NULL DEFAULT 0,
    haoshi REAL NOT NULL DEFAULT 0,
    tijiao_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (renwu_id, lunci_hao, yonghu_id)
);

CREATE TABLE IF NOT EXISTS xitong_rizhi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caozuozhe_id INTEGER REFERENCES yonghu(id),
    caozuo_leixing TEXT NOT NULL,
    duixiang_leixing TEXT NOT NULL,
    duixiang_id INTEGER,
    jieguo TEXT NOT NULL CHECK (jieguo IN ('chenggong', 'shibai', 'yuequan')),
    xiangqing TEXT NOT NULL DEFAULT '',
    kehu_ip TEXT NOT NULL DEFAULT '',
    rizhi_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shujuji_tigongfang ON shujuji(tigongfang_id);
CREATE INDEX IF NOT EXISTS idx_renwu_chuangjianzhe ON xunlian_renwu(chuangjianzhe_id);
CREATE INDEX IF NOT EXISTS idx_canjiafang_renwu ON renwu_canjiafang(renwu_id);
CREATE INDEX IF NOT EXISTS idx_lunci_renwu ON lunci_jilu(renwu_id, lunci_hao);
CREATE INDEX IF NOT EXISTS idx_yusuan_renwu ON yinsi_yusuan(renwu_id);
CREATE INDEX IF NOT EXISTS idx_gengxin_renwu ON renwu_gengxin(renwu_id, lunci_hao);
CREATE INDEX IF NOT EXISTS idx_rizhi_shijian ON xitong_rizhi(rizhi_shijian);
"""


class YewuCuowu(Exception):
    """业务异常，由全局异常处理器转换成统一响应。"""

    def __init__(self, cuowu_ma: int, xiaoxi: str, http_zhuangtai: int = 400):
        super().__init__(xiaoxi)
        self.cuowu_ma = cuowu_ma
        self.xiaoxi = xiaoxi
        self.http_zhuangtai = http_zhuangtai


@contextmanager
def lianjie() -> Iterator[sqlite3.Connection]:
    """每次操作使用独立连接，避免多线程共享 SQLite 连接。"""
    chushihua_mulu()
    lian = sqlite3.connect(str(SHUJUKU_LUJING), timeout=30)
    lian.row_factory = sqlite3.Row
    lian.execute('PRAGMA foreign_keys = ON')
    lian.execute('PRAGMA busy_timeout = 30000')
    try:
        yield lian
        lian.commit()
    except Exception:
        lian.rollback()
        raise
    finally:
        lian.close()


def zhixing(sql: str, canshu: tuple = ()) -> int:
    """执行写操作，返回最后插入编号。"""
    with lianjie() as lian:
        youbiao = lian.execute(sql, canshu)
        return int(youbiao.lastrowid or 0)


def zhixing_hang(sql: str, canshu: tuple = ()) -> int:
    """执行写操作并返回受影响行数，用于条件更新。"""
    with lianjie() as lian:
        return int(lian.execute(sql, canshu).rowcount)


def chaxun_yi(sql: str, canshu: tuple = ()) -> dict | None:
    """查询单条记录。"""
    with lianjie() as lian:
        hang = lian.execute(sql, canshu).fetchone()
        return dict(hang) if hang is not None else None


def chaxun_duo(sql: str, canshu: tuple = ()) -> list[dict]:
    """查询多条记录。"""
    with lianjie() as lian:
        return [dict(hang) for hang in lian.execute(sql, canshu).fetchall()]


def chushi_hua() -> None:
    """建表并启用 WAL。"""
    with lianjie() as lian:
        lian.execute('PRAGMA journal_mode = WAL')
        lian.executescript(JIANTUO_SQL)


def qu_banben() -> int:
    """读取演示数据版本号（PRAGMA user_version）。"""
    with lianjie() as lian:
        return int(lian.execute('PRAGMA user_version').fetchone()[0])


def she_banben(banben: int) -> None:
    with lianjie() as lian:
        lian.execute(f'PRAGMA user_version = {int(banben)}')
