"""数据访问层：集中存放全部 SQL。"""

import json
from typing import Any

from backend.db import chaxun_duo, chaxun_yi, lianjie, zhixing

XIANZAI = "datetime('now', 'localtime')"


def _fenyie(tiaojian: str, canshu: list, biaoming: str,
            paixu: str, ye: int, meiye: int) -> dict:
    """通用分页查询。"""
    ye = max(1, ye)
    meiye = max(1, min(100, meiye))
    zongshu = chaxun_yi(f'SELECT COUNT(*) AS n FROM {biaoming} {tiaojian}', tuple(canshu))
    jilu = chaxun_duo(
        f'SELECT * FROM {biaoming} {tiaojian} ORDER BY {paixu} '
        f'LIMIT ? OFFSET ?',
        tuple(canshu) + (meiye, (ye - 1) * meiye),
    )
    return {
        'items': jilu,
        'total': int(zongshu['n']) if zongshu else 0,
        'page': ye,
        'size': meiye,
    }


# ---------------------------------------------------------------- 用户
def chuangjian_yonghu(yonghuming: str, mima_hash: str, youxiang: str,
                      jiaose: str) -> int:
    return zhixing(
        f'INSERT INTO yonghu (yonghuming, mima_hash, youxiang, jiaose, chuangjian_shijian) '
        f'VALUES (?, ?, ?, ?, {XIANZAI})',
        (yonghuming, mima_hash, youxiang, jiaose),
    )


def yonghu_an_id(yonghu_id: int) -> dict | None:
    return chaxun_yi('SELECT * FROM yonghu WHERE id = ?', (yonghu_id,))


def yonghu_an_ming(yonghuming: str) -> dict | None:
    return chaxun_yi('SELECT * FROM yonghu WHERE yonghuming = ?', (yonghuming,))


def yonghu_liechu(ye: int = 1, meiye: int = 20, guanli: bool = False) -> dict:
    if guanli:
        tiaojian, canshu = '', []
    else:
        tiaojian, canshu = 'WHERE jiaose != ?', ['guanliyuan']
    jieguo = _fenyie(tiaojian, canshu, 'yonghu', 'id DESC', ye, meiye)
    for hang in jieguo['items']:
        hang.pop('mima_hash', None)
    return jieguo


def yonghu_gengxin_zhuangtai(yonghu_id: int, zhuangtai: str) -> None:
    zhixing('UPDATE yonghu SET zhuangtai = ? WHERE id = ?', (zhuangtai, yonghu_id))


def yonghu_tongji() -> dict:
    return chaxun_yi(
        'SELECT COUNT(*) AS zongshu, '
        "SUM(CASE WHEN jiaose = 'tigongfang' THEN 1 ELSE 0 END) AS tigongfang, "
        "SUM(CASE WHEN jiaose = 'shiyongfang' THEN 1 ELSE 0 END) AS shiyongfang, "
        "SUM(CASE WHEN zhuangtai = 'tingyong' THEN 1 ELSE 0 END) AS tingyong "
        'FROM yonghu',
    ) or {}


# ---------------------------------------------------------------- 数据集
def chuangjian_shujuji(tigongfang_id: int, shuju: dict) -> int:
    return zhixing(
        f'INSERT INTO shujuji (tigongfang_id, mingcheng, geshi, daxiao, yangben_shu, '
        f'ziduan, benzhi_lujing, tuomin_guize, zhuangtai, jiaoyan_jielun, chuangjian_shijian) '
        f'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, {XIANZAI})',
        (
            tigongfang_id,
            shuju['mingcheng'],
            shuju['geshi'],
            shuju['daxiao'],
            shuju['yangben_shu'],
            json.dumps(shuju.get('ziduan', []), ensure_ascii=False),
            shuju.get('benzhi_lujing', ''),
            shuju.get('tuomin_guize', ''),
            shuju.get('zhuangtai', 'yijiaoyan'),
            shuju.get('jiaoyan_jielun', ''),
        ),
    )


def shujuji_an_id(shujuji_id: int) -> dict | None:
    hang = chaxun_yi(
        'SELECT s.*, y.yonghuming AS tigongfang_ming '
        'FROM shujuji s JOIN yonghu y ON y.id = s.tigongfang_id WHERE s.id = ?',
        (shujuji_id,),
    )
    if hang:
        _jiedu_ziduan(hang)
    return hang


def shujuji_liechu(yonghu_id: int | None, bao_tingyong: bool,
                   ye: int = 1, meiye: int = 50) -> dict:
    tiaojian, canshu = [], []
    if yonghu_id is not None:
        tiaojian.append('s.tigongfang_id = ?')
        canshu.append(yonghu_id)
    if not bao_tingyong:
        tiaojian.append("s.zhuangtai != 'yitingyong'")
    where = ('WHERE ' + ' AND '.join(tiaojian)) if tiaojian else ''
    zong = chaxun_yi(f'SELECT COUNT(*) AS n FROM shujuji s {where}', tuple(canshu))
    jilu = chaxun_duo(
        'SELECT s.*, y.yonghuming AS tigongfang_ming '
        f'FROM shujuji s JOIN yonghu y ON y.id = s.tigongfang_id {where} '
        'ORDER BY s.id DESC LIMIT ? OFFSET ?',
        tuple(canshu) + (meiye, (max(1, ye) - 1) * meiye),
    )
    for hang in jilu:
        _jiedu_ziduan(hang)
    return {'items': jilu, 'total': int(zong['n']), 'page': ye, 'size': meiye}


def _jiedu_ziduan(hang: dict) -> None:
    try:
        hang['ziduan'] = json.loads(hang.get('ziduan') or '[]')
    except (json.JSONDecodeError, TypeError):
        hang['ziduan'] = []


def shujuji_gengxin_zhuangtai(shujuji_id: int, zhuangtai: str,
                              jielun: str = '') -> None:
    zhixing(
        'UPDATE shujuji SET zhuangtai = ?, jiaoyan_jielun = ? WHERE id = ?',
        (zhuangtai, jielun, shujuji_id),
    )


def shujuji_tongji(yonghu_id: int | None = None) -> dict:
    where, canshu = '', ()
    if yonghu_id is not None:
        where, canshu = 'WHERE tigongfang_id = ?', (yonghu_id,)
    return chaxun_yi(
        f'SELECT COUNT(*) AS zongshu, COALESCE(SUM(yangben_shu), 0) AS yangben_zong, '
        f"SUM(CASE WHEN zhuangtai = 'yijiaoyan' THEN 1 ELSE 0 END) AS keyong "
        f'FROM shujuji {where}', canshu,
    ) or {}


# ---------------------------------------------------------------- 训练任务
def chuangjian_renwu(chuangjianzhe_id: int, renwu: dict,
                     canjia: list[dict]) -> int:
    with lianjie() as lian:
        youbiao = lian.execute(
            f'INSERT INTO xunlian_renwu (chuangjianzhe_id, mingcheng, moxing_leixing, '
            f'lunshu, piliang_daxiao, xuexilv, yinsipi, jiancai_yuzhi, '
            f'yusuan_shangxian, yunxing_moshi, zhuangtai, chuangjian_shijian) '
            f'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, {XIANZAI})',
            (
                chuangjianzhe_id, renwu['mingcheng'], renwu['moxing_leixing'],
                renwu['lunshu'], renwu['piliang_daxiao'], renwu['xuexilv'],
                renwu['yinsipi'], renwu['jiancai_yuzhi'],
                renwu['yusuan_shangxian'], renwu['yunxing_moshi'], 'daichufa',
            ),
        )
        renwu_id = int(youbiao.lastrowid)
        for hang in canjia:
            lian.execute(
                'INSERT INTO renwu_canjiafang '
                '(renwu_id, yonghu_id, shujuji_id, yangben_shu) VALUES (?, ?, ?, ?)',
                (renwu_id, hang['yonghu_id'], hang['shujuji_id'], hang['yangben_shu']),
            )
        return renwu_id


def renwu_an_id(renwu_id: int) -> dict | None:
    return chaxun_yi(
        'SELECT r.*, y.yonghuming AS chuangjianzhe_ming '
        'FROM xunlian_renwu r JOIN yonghu y ON y.id = r.chuangjianzhe_id WHERE r.id = ?',
        (renwu_id,),
    )


def renwu_liechu(yonghu_id: int | None, jiaose: str,
                 zhuangtai: str = '', ye: int = 1, meiye: int = 20) -> dict:
    tiaojian, canshu = [], []
    if jiaose != 'guanliyuan':
        tiaojian.append(
            '(r.chuangjianzhe_id = ? OR EXISTS (SELECT 1 FROM renwu_canjiafang c '
            'WHERE c.renwu_id = r.id AND c.yonghu_id = ?))'
        )
        canshu.extend([yonghu_id, yonghu_id])
    if zhuangtai:
        tiaojian.append('r.zhuangtai = ?')
        canshu.append(zhuangtai)
    where = ('WHERE ' + ' AND '.join(tiaojian)) if tiaojian else ''
    zong = chaxun_yi(f'SELECT COUNT(*) AS n FROM xunlian_renwu r {where}', tuple(canshu))
    jilu = chaxun_duo(
        'SELECT r.*, y.yonghuming AS chuangjianzhe_ming, '
        '(SELECT COUNT(*) FROM renwu_canjiafang c WHERE c.renwu_id = r.id) AS canjia_shu, '
        '(SELECT COALESCE(SUM(c.yangben_shu), 0) FROM renwu_canjiafang c '
        ' WHERE c.renwu_id = r.id) AS yangben_zong '
        f'FROM xunlian_renwu r JOIN yonghu y ON y.id = r.chuangjianzhe_id {where} '
        'ORDER BY r.id DESC LIMIT ? OFFSET ?',
        tuple(canshu) + (meiye, (max(1, ye) - 1) * meiye),
    )
    return {'items': jilu, 'total': int(zong['n']), 'page': ye, 'size': meiye}


def renwu_gengxin_zhuangtai(renwu_id: int, zhuangtai: str,
                            cuowu: str | None = None) -> None:
    if zhuangtai == 'xunlianzhong':
        zhixing(
            f"UPDATE xunlian_renwu SET zhuangtai = ?, qidong_shijian = {XIANZAI}, "
            "cuowu_xiaoxi = '' WHERE id = ?", (zhuangtai, renwu_id),
        )
        return
    if zhuangtai in ('yiwancheng', 'yichang', 'yiquxiao'):
        zhixing(
            f'UPDATE xunlian_renwu SET zhuangtai = ?, jieshu_shijian = {XIANZAI}, '
            'cuowu_xiaoxi = COALESCE(?, cuowu_xiaoxi) WHERE id = ?',
            (zhuangtai, cuowu, renwu_id),
        )
        return
    zhixing('UPDATE xunlian_renwu SET zhuangtai = ? WHERE id = ?', (zhuangtai, renwu_id))


def renwu_gengxin_lunci(renwu_id: int, lunci: int) -> None:
    zhixing('UPDATE xunlian_renwu SET dangqian_lunci = ? WHERE id = ?', (lunci, renwu_id))


def renwu_tongji(yonghu_id: int | None = None, jiaose: str = 'guanliyuan') -> dict:
    tiaojian, canshu = '', ()
    if jiaose != 'guanliyuan':
        tiaojian = ('WHERE (r.chuangjianzhe_id = ? OR EXISTS (SELECT 1 FROM renwu_canjiafang c '
                    'WHERE c.renwu_id = r.id AND c.yonghu_id = ?))')
        canshu = (yonghu_id, yonghu_id)
    return chaxun_yi(
        f'SELECT COUNT(*) AS zongshu, '
        f"SUM(CASE WHEN r.zhuangtai = 'xunlianzhong' THEN 1 ELSE 0 END) AS jinxingzhong, "
        f"SUM(CASE WHEN r.zhuangtai = 'yiwancheng' THEN 1 ELSE 0 END) AS yiwancheng, "
        f"SUM(CASE WHEN r.zhuangtai = 'yichang' THEN 1 ELSE 0 END) AS yichang "
        f'FROM xunlian_renwu r {tiaojian}', canshu,
    ) or {}


# ---------------------------------------------------------------- 参与方
def canjiafang_an_renwu(renwu_id: int) -> list[dict]:
    return chaxun_duo(
        'SELECT c.*, y.yonghuming, s.mingcheng AS shujuji_ming, s.geshi, '
        's.zhuangtai AS shujuji_zhuangtai '
        'FROM renwu_canjiafang c '
        'JOIN yonghu y ON y.id = c.yonghu_id '
        'JOIN shujuji s ON s.id = c.shujuji_id '
        'WHERE c.renwu_id = ? ORDER BY c.id',
        (renwu_id,),
    )


def canjiafang_shuliang(renwu_id: int) -> int:
    hang = chaxun_yi('SELECT COUNT(*) AS n FROM renwu_canjiafang WHERE renwu_id = ?',
                     (renwu_id,))
    return int(hang['n']) if hang else 0


def canjiafang_gengxin_zhuangtai(renwu_id: int, zhuangtai: str,
                                 yonghu_id: int | None = None) -> None:
    if yonghu_id is None:
        zhixing('UPDATE renwu_canjiafang SET zhuangtai = ? WHERE renwu_id = ?',
                (zhuangtai, renwu_id))
    else:
        zhixing('UPDATE renwu_canjiafang SET zhuangtai = ? WHERE renwu_id = ? AND yonghu_id = ?',
                (zhuangtai, renwu_id, yonghu_id))


def canjiafang_panduan(renwu_id: int, yonghu_id: int) -> dict | None:
    return chaxun_yi(
        'SELECT * FROM renwu_canjiafang WHERE renwu_id = ? AND yonghu_id = ?',
        (renwu_id, yonghu_id),
    )


# ---------------------------------------------------------------- 轮次
def charu_lunci(renwu_id: int, lunci_hao: int, sunshi: float, zhunquelv: float,
                haoshi: float, canshu_wenjian: str, canjia_shu: int) -> int:
    return zhixing(
        f'INSERT INTO lunci_jilu (renwu_id, lunci_hao, sunshi, zhunquelv, haoshi, '
        f'canshu_wenjian, canjia_shu, chuangjian_shijian) '
        f'VALUES (?, ?, ?, ?, ?, ?, ?, {XIANZAI})',
        (renwu_id, lunci_hao, sunshi, zhunquelv, haoshi, canshu_wenjian, canjia_shu),
    )


def lunci_liechu(renwu_id: int) -> list[dict]:
    return chaxun_duo(
        'SELECT * FROM lunci_jilu WHERE renwu_id = ? ORDER BY lunci_hao',
        (renwu_id,),
    )


def lunci_zuixin(renwu_id: int) -> dict | None:
    return chaxun_yi(
        'SELECT * FROM lunci_jilu WHERE renwu_id = ? ORDER BY lunci_hao DESC LIMIT 1',
        (renwu_id,),
    )


# ---------------------------------------------------------------- 隐私预算
def charu_yusuan(renwu_id: int, lunci_hao: int, benlun_eps: float,
                 leiji_eps: float) -> int:
    return zhixing(
        f'INSERT INTO yinsi_yusuan (renwu_id, lunci_hao, benlun_eps, leiji_eps, jilu_shijian) '
        f'VALUES (?, ?, ?, ?, {XIANZAI})',
        (renwu_id, lunci_hao, benlun_eps, leiji_eps),
    )


def yusuan_leiji(renwu_id: int) -> float:
    hang = chaxun_yi(
        'SELECT COALESCE(MAX(leiji_eps), 0) AS n FROM yinsi_yusuan WHERE renwu_id = ?',
        (renwu_id,),
    )
    return float(hang['n']) if hang else 0.0


def yusuan_liechu(renwu_id: int) -> list[dict]:
    return chaxun_duo(
        'SELECT * FROM yinsi_yusuan WHERE renwu_id = ? ORDER BY lunci_hao',
        (renwu_id,),
    )


# ---------------------------------------------------------------- 客户端更新
def baocun_gengxin(renwu_id: int, lunci_hao: int, yonghu_id: int,
                   gengxin: list[float], yangben_shu: int, sunshi: float,
                   zhunquelv: float, haoshi: float) -> None:
    zhixing(
        f'INSERT INTO renwu_gengxin (renwu_id, lunci_hao, yonghu_id, gengxin, '
        f'yangben_shu, sunshi, zhunquelv, haoshi, tijiao_shijian) '
        f'VALUES (?, ?, ?, ?, ?, ?, ?, ?, {XIANZAI}) '
        'ON CONFLICT(renwu_id, lunci_hao, yonghu_id) DO UPDATE SET '
        'gengxin = excluded.gengxin, yangben_shu = excluded.yangben_shu, '
        'sunshi = excluded.sunshi, zhunquelv = excluded.zhunquelv, '
        'haoshi = excluded.haoshi, tijiao_shijian = excluded.tijiao_shijian',
        (renwu_id, lunci_hao, yonghu_id, json.dumps(gengxin),
         yangben_shu, sunshi, zhunquelv, haoshi),
    )


def gengxin_liechu(renwu_id: int, lunci_hao: int) -> list[dict]:
    jilu = chaxun_duo(
        'SELECT g.*, y.yonghuming FROM renwu_gengxin g '
        'JOIN yonghu y ON y.id = g.yonghu_id '
        'WHERE g.renwu_id = ? AND g.lunci_hao = ? ORDER BY g.id',
        (renwu_id, lunci_hao),
    )
    for hang in jilu:
        try:
            hang['gengxin'] = json.loads(hang['gengxin'])
        except (json.JSONDecodeError, TypeError):
            hang['gengxin'] = []
    return jilu


def gengxin_shuliang(renwu_id: int, lunci_hao: int) -> int:
    hang = chaxun_yi(
        'SELECT COUNT(*) AS n FROM renwu_gengxin WHERE renwu_id = ? AND lunci_hao = ?',
        (renwu_id, lunci_hao),
    )
    return int(hang['n']) if hang else 0


def gengxin_shifou_tijiao(renwu_id: int, lunci_hao: int, yonghu_id: int) -> bool:
    hang = chaxun_yi(
        'SELECT 1 AS ok FROM renwu_gengxin WHERE renwu_id = ? AND lunci_hao = ? '
        'AND yonghu_id = ?', (renwu_id, lunci_hao, yonghu_id),
    )
    return hang is not None


# ---------------------------------------------------------------- 日志
def xie_rizhi(caozuozhe_id: int | None, caozuo_leixing: str, duixiang_leixing: str,
              duixiang_id: int | None, jieguo: str, xiangqing: str = '',
              kehu_ip: str = '') -> int:
    return zhixing(
        f'INSERT INTO xitong_rizhi (caozuozhe_id, caozuo_leixing, duixiang_leixing, '
        f'duixiang_id, jieguo, xiangqing, kehu_ip, rizhi_shijian) '
        f'VALUES (?, ?, ?, ?, ?, ?, ?, {XIANZAI})',
        (caozuozhe_id, caozuo_leixing, duixiang_leixing, duixiang_id,
         jieguo, xiangqing[:500], kehu_ip),
    )


def rizhi_liechu(leixing: str = '', jieguo: str = '', yonghuming: str = '',
                 kaishi: str = '', jieshu: str = '', ye: int = 1,
                 meiye: int = 30) -> dict:
    # 前端只传日期（YYYY-MM-DD）时按整天补齐，避免结束日期漏掉当天记录
    if len(kaishi) == 10:
        kaishi += ' 00:00:00'
    if len(jieshu) == 10:
        jieshu += ' 23:59:59'
    tiaojian, canshu = [], []
    if leixing:
        tiaojian.append('z.caozuo_leixing = ?')
        canshu.append(leixing)
    if jieguo:
        tiaojian.append('z.jieguo = ?')
        canshu.append(jieguo)
    if yonghuming:
        tiaojian.append('y.yonghuming LIKE ?')
        canshu.append(f'%{yonghuming}%')
    if kaishi:
        tiaojian.append('z.rizhi_shijian >= ?')
        canshu.append(kaishi)
    if jieshu:
        tiaojian.append('z.rizhi_shijian <= ?')
        canshu.append(jieshu)
    where = ('WHERE ' + ' AND '.join(tiaojian)) if tiaojian else ''
    zong = chaxun_yi(
        f'SELECT COUNT(*) AS n FROM xitong_rizhi z LEFT JOIN yonghu y '
        f'ON y.id = z.caozuozhe_id {where}', tuple(canshu),
    )
    jilu = chaxun_duo(
        'SELECT z.*, y.yonghuming AS caozuozhe_ming FROM xitong_rizhi z '
        f'LEFT JOIN yonghu y ON y.id = z.caozuozhe_id {where} '
        'ORDER BY z.id DESC LIMIT ? OFFSET ?',
        tuple(canshu) + (meiye, (max(1, ye) - 1) * meiye),
    )
    return {'items': jilu, 'total': int(zong['n']), 'page': ye, 'size': meiye}


def rizhi_tongji() -> dict:
    return chaxun_yi(
        "SELECT COUNT(*) AS zongshu, "
        "SUM(CASE WHEN jieguo = 'shibai' THEN 1 ELSE 0 END) AS shibai, "
        "SUM(CASE WHEN date(rizhi_shijian) = date('now', 'localtime') "
        "THEN 1 ELSE 0 END) AS jintian FROM xitong_rizhi"
    ) or {}


def qingli_shibai_renwu() -> int:
    """服务重启时把卡在训练中的任务标记为异常。"""
    with lianjie() as lian:
        youbiao = lian.execute(
            f"UPDATE xunlian_renwu SET zhuangtai = 'yichang', "
            f"cuowu_xiaoxi = '服务重启，任务中断', jieshu_shijian = {XIANZAI} "
            "WHERE zhuangtai = 'xunlianzhong'"
        )
        lian.execute(
            "UPDATE renwu_canjiafang SET zhuangtai = 'diaoxian' "
            "WHERE renwu_id IN (SELECT id FROM xunlian_renwu WHERE zhuangtai = 'yichang')"
        )
        return int(youbiao.rowcount or 0)
