"""系统管理：概览、用户/任务管理、日志与备份。"""

import sqlite3
from datetime import datetime
from pathlib import Path

from backend import dao
from backend.config import BEIFEN_BAOLIU, BEIFEN_MULU, SHUJUKU_LUJING
from backend.db import YewuCuowu
from backend.deps import CUOWU_QUANXIAN
from backend.security import JIAOSE_GUANLIYUAN


def _yaoqiu_guanli(yonghu: dict) -> None:
    if yonghu['jiaose'] != JIAOSE_GUANLIYUAN:
        raise YewuCuowu(CUOWU_QUANXIAN, '仅管理员可执行该操作', 403)


def zonglan(yonghu: dict) -> dict:
    """按角色返回工作台统计。"""
    if yonghu['jiaose'] == JIAOSE_GUANLIYUAN:
        shuju = dao.shujuji_tongji()
        renwu = dao.renwu_tongji()
        yonghu_tj = dao.yonghu_tongji()
        rizhi = dao.rizhi_tongji()
        zuijin = dao.renwu_liechu(None, 'guanliyuan', '', 1, 5)['items']
        return {
            'jiaose': 'guanliyuan',
            'yonghu': yonghu_tj,
            'shujuji': shuju,
            'renwu': renwu,
            'rizhi': rizhi,
            'zuijin_renwu': zuijin,
        }
    if yonghu['jiaose'] == 'tigongfang':
        shuju = dao.shujuji_tongji(yonghu['id'])
        renwu = dao.renwu_tongji(yonghu['id'], 'tigongfang')
        zuijin = dao.renwu_liechu(yonghu['id'], 'tigongfang', '', 1, 5)['items']
        return {
            'jiaose': 'tigongfang',
            'shujuji': shuju,
            'renwu': renwu,
            'zuijin_renwu': zuijin,
        }
    renwu = dao.renwu_tongji(yonghu['id'], 'shiyongfang')
    shuju = dao.shujuji_tongji()
    zuijin = dao.renwu_liechu(yonghu['id'], 'shiyongfang', '', 1, 5)['items']
    return {
        'jiaose': 'shiyongfang',
        'renwu': renwu,
        'shujuji': shuju,
        'zuijin_renwu': zuijin,
    }


def yonghu_liechu(caozuozhe: dict, ye: int, meiye: int) -> dict:
    _yaoqiu_guanli(caozuozhe)
    return dao.yonghu_liechu(ye, meiye, guanli=True)


def yonghu_gengxin(caozuozhe: dict, yonghu_id: int, zhuangtai: str,
                   ip: str = '') -> dict:
    _yaoqiu_guanli(caozuozhe)
    mubiao = dao.yonghu_an_id(yonghu_id)
    if not mubiao:
        raise YewuCuowu(4040, '用户不存在', 404)
    if mubiao['jiaose'] == 'guanliyuan':
        raise YewuCuowu(CUOWU_QUANXIAN, '不能修改管理员账号', 403)
    if mubiao['id'] == caozuozhe['id']:
        raise YewuCuowu(CUOWU_QUANXIAN, '不能修改自己的账号状态', 403)
    dao.yonghu_gengxin_zhuangtai(yonghu_id, zhuangtai)
    dao.xie_rizhi(caozuozhe['id'], '账号状态变更', 'yonghu', yonghu_id,
                  'chenggong', f'{mubiao["yonghuming"]} -> {zhuangtai}', ip)
    mubiao['zhuangtai'] = zhuangtai
    mubiao.pop('mima_hash', None)
    return mubiao


def renwu_liechu(caozuozhe: dict, zhuangtai: str, ye: int, meiye: int) -> dict:
    _yaoqiu_guanli(caozuozhe)
    return dao.renwu_liechu(None, 'guanliyuan', zhuangtai, ye, meiye)


def renwu_gengxin(caozuozhe: dict, renwu_id: int, zhuangtai: str,
                  yuanyin: str, ip: str = '') -> dict:
    """强制终止或标记异常。"""
    _yaoqiu_guanli(caozuozhe)
    renwu = dao.renwu_an_id(renwu_id)
    if not renwu:
        raise YewuCuowu(4040, '训练任务不存在', 404)
    if renwu['zhuangtai'] in ('yiwancheng', 'yiquxiao'):
        raise YewuCuowu(4004, '任务已结束，不能再修改', 409)
    if zhuangtai == 'yichang':
        dao.renwu_gengxin_zhuangtai(renwu_id, 'yichang', yuanyin)
        dao.canjiafang_gengxin_zhuangtai(renwu_id, 'diaoxian')
    else:
        dao.renwu_gengxin_zhuangtai(renwu_id, 'yiquxiao', yuanyin)
        dao.canjiafang_gengxin_zhuangtai(renwu_id, 'diaoxian')
    dao.xie_rizhi(caozuozhe['id'], '管理员变更任务状态', 'xunlian_renwu',
                  renwu_id, 'chenggong', f'{renwu["mingcheng"]} -> {zhuangtai}：{yuanyin}', ip)
    return xiangqing_guanli(renwu_id)


def xiangqing_guanli(renwu_id: int) -> dict:
    renwu = dao.renwu_an_id(renwu_id)
    if not renwu:
        raise YewuCuowu(4040, '训练任务不存在', 404)
    renwu['canjiafang'] = dao.canjiafang_an_renwu(renwu_id)
    renwu['lunci_jilu'] = dao.lunci_liechu(renwu_id)
    return renwu


def rizhi(caozuozhe: dict, leixing: str, jieguo: str, yonghuming: str,
          kaishi: str, jieshu: str, ye: int, meiye: int) -> dict:
    _yaoqiu_guanli(caozuozhe)
    return dao.rizhi_liechu(leixing, jieguo, yonghuming, kaishi, jieshu, ye, meiye)


def beifen(caozuozhe: dict, ip: str = '') -> dict:
    """使用 SQLite 在线备份 API 生成一致性备份。"""
    _yaoqiu_guanli(caozuozhe)
    BEIFEN_MULU.mkdir(parents=True, exist_ok=True)
    shijian = datetime.now().strftime('%Y%m%d_%H%M%S')
    mubiao = BEIFEN_MULU / f'pingtai_{shijian}.db'
    yuan = sqlite3.connect(str(SHUJUKU_LUJING), timeout=30)
    try:
        mudb = sqlite3.connect(str(mubiao))
        try:
            yuan.backup(mudb)
        finally:
            mudb.close()
    finally:
        yuan.close()
    jiu = sorted(BEIFEN_MULU.glob('pingtai_*.db'), key=lambda p: p.stat().st_mtime)
    for wenjian in jiu[:-BEIFEN_BAOLIU]:
        wenjian.unlink(missing_ok=True)
    daxiao = mubiao.stat().st_size
    dao.xie_rizhi(caozuozhe['id'], '创建备份', 'xitong', None, 'chenggong',
                  f'{mubiao.name}，{daxiao} 字节', ip)
    return {'wenjian': mubiao.name, 'daxiao': daxiao,
            'shijian': shijian, 'baoliu': BEIFEN_BAOLIU}


def beifen_liechu(caozuozhe: dict) -> list[dict]:
    _yaoqiu_guanli(caozuozhe)
    jieguo = []
    for wenjian in sorted(BEIFEN_MULU.glob('pingtai_*.db'),
                          key=lambda p: p.stat().st_mtime, reverse=True):
        jieguo.append({'wenjian': wenjian.name, 'daxiao': wenjian.stat().st_size})
    return jieguo


def beifen_lujing(caozuozhe: dict, wenjian: str) -> Path:
    _yaoqiu_guanli(caozuozhe)
    lujing = (BEIFEN_MULU / wenjian).resolve()
    if lujing.parent != BEIFEN_MULU.resolve() or not lujing.exists():
        raise YewuCuowu(4040, '备份文件不存在', 404)
    return lujing
