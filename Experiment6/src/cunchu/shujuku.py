"""SQLite 连接管理与建表脚本。"""

import sqlite3
from pathlib import Path


JIANTUO_SQL = """
CREATE TABLE IF NOT EXISTS yonghu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    yonghuming TEXT NOT NULL UNIQUE,
    mima_hash TEXT NOT NULL,
    youxiang TEXT NOT NULL,
    jiaose TEXT NOT NULL CHECK (jiaose IN ('tigongfang', 'shiyongfang', 'guanliyuan')),
    zhuangtai TEXT NOT NULL DEFAULT 'zhengchang',
    chuangjian_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shujuji (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tigongfang_id INTEGER NOT NULL REFERENCES yonghu(id),
    mingcheng TEXT NOT NULL,
    geshi TEXT NOT NULL,
    daxiao INTEGER NOT NULL CHECK (daxiao > 0),
    yangben_shu INTEGER NOT NULL CHECK (yangben_shu > 0),
    tuomin_guize TEXT,
    zhuangtai TEXT NOT NULL DEFAULT 'yijiaoyan'
        CHECK (zhuangtai IN ('daijiaoyan', 'yijiaoyan', 'yitingyong')),
    chuangjian_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tigongfang_id, mingcheng)
);

CREATE TABLE IF NOT EXISTS xunlian_renwu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chuangjianzhe_id INTEGER NOT NULL REFERENCES yonghu(id),
    mingcheng TEXT NOT NULL,
    moxing_leixing TEXT NOT NULL DEFAULT 'mlp_64_32',
    lunshu INTEGER NOT NULL CHECK (lunshu > 0),
    piliang_daxiao INTEGER NOT NULL CHECK (piliang_daxiao > 0),
    xuexilv REAL NOT NULL CHECK (xuexilv > 0),
    yinsipi REAL NOT NULL CHECK (yinsipi > 0),
    jiancai_yuzhi REAL NOT NULL CHECK (jiancai_yuzhi > 0),
    yusuan_shangxian REAL NOT NULL CHECK (yusuan_shangxian > 0),
    zhuangtai TEXT NOT NULL DEFAULT 'daichufa'
        CHECK (zhuangtai IN ('daichufa', 'xunlianzhong', 'yiwancheng', 'yichang')),
    chuangjian_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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

CREATE TABLE IF NOT EXISTS xitong_rizhi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caozuozhe_id INTEGER REFERENCES yonghu(id),
    caozuo_leixing TEXT NOT NULL,
    duixiang_leixing TEXT NOT NULL,
    duixiang_id INTEGER,
    jieguo TEXT NOT NULL CHECK (jieguo IN ('chenggong', 'shibai', 'yuequan')),
    rizhi_shijian TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class Shujuku:
    """管理一个 SQLite 连接。"""

    def __init__(self, lujing: str):
        self.lujing = str(lujing)
        self.lianjie: sqlite3.Connection | None = None

    def dakai(self) -> sqlite3.Connection:
        """打开连接并启用外键约束。"""
        Path(self.lujing).parent.mkdir(parents=True, exist_ok=True)
        self.lianjie = sqlite3.connect(self.lujing)
        self.lianjie.row_factory = sqlite3.Row
        self.lianjie.execute('PRAGMA foreign_keys = ON')
        return self.lianjie

    def jianbiao(self) -> None:
        """创建全部数据表，重复执行不会报错。"""
        if self.lianjie is None:
            raise RuntimeError('数据库尚未打开')
        with self.lianjie as lianjie:
            lianjie.executescript(JIANTUO_SQL)

    def guanbi(self) -> None:
        """关闭连接。"""
        if self.lianjie is not None:
            self.lianjie.close()
            self.lianjie = None
