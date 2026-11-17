"""联邦训练协调器：轮次调度、加权聚合、指标评估与落盘。"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from backend import dao
from backend.config import CANSHU_MULU, FEDENG_CHAOSHI
from backend.federated import shuju
from backend.federated.moni import moni_xunlian
from backend.federated.moxing import MlpMoxing
from backend.services import yinsi_fuwu

_ZIDONG = threading.Lock()
_YUNXING: set[int] = set()
PINGGU_ZHONGZI = 2024103365
CHUSHI_ZHONGZI = 8800


def chushi_canshu(renwu_id: int) -> list[float]:
    """任务初始全局参数（由任务编号确定）。"""
    moxing = MlpMoxing(zhongzi=CHUSHI_ZHONGZI + renwu_id)
    return moxing.qu_canshu().tolist()


def qidong(renwu_id: int) -> None:
    """启动后台训练线程。"""
    with _ZIDONG:
        if renwu_id in _YUNXING:
            return
        _YUNXING.add(renwu_id)
    xiancheng = threading.Thread(
        target=_yunxing_baohu, args=(renwu_id,),
        name=f'xunlian-{renwu_id}', daemon=True,
    )
    xiancheng.start()


def _yunxing_baohu(renwu_id: int) -> None:
    try:
        _yunxing(renwu_id)
    except Exception as cuowu:  # 后台线程必须兜底，避免任务永久卡住
        _shibai(renwu_id, f'训练线程异常：{str(cuowu)[:180]}')
    finally:
        with _ZIDONG:
            _YUNXING.discard(renwu_id)


def _yunxing(renwu_id: int) -> None:
    renwu = dao.renwu_an_id(renwu_id)
    if not renwu:
        return
    canjia = dao.canjiafang_an_renwu(renwu_id)
    if not canjia:
        _shibai(renwu_id, '没有可用的参与方')
        return
    cans = chushi_canshu(renwu_id)
    try:
        for lunci in range(1, int(renwu['lunshu']) + 1):
            dangqian = dao.renwu_an_id(renwu_id)
            if not dangqian or dangqian['zhuangtai'] != 'xunlianzhong':
                _rizhi(renwu_id, '训练终止', '任务状态已变化，协调器退出')
                return
            leiji = dao.yusuan_leiji(renwu_id)
            yinsi_fuwu.jiancha_yusuan(leiji, float(renwu['yinsipi']),
                                      float(renwu['yusuan_shangxian']))
            dao.renwu_gengxin_lunci(renwu_id, lunci)
            canjia = dao.canjiafang_an_renwu(renwu_id)
            dao.canjiafang_gengxin_zhuangtai(renwu_id, 'xunlianzhong')
            kaishi = time.time()
            _zhixing_benlun(renwu, lunci, cans, canjia)
            gengxin = dao.gengxin_liechu(renwu_id, lunci)
            if len(gengxin) < len(canjia):
                queshi = [c['yonghuming'] for c in canjia
                          if c['yonghu_id'] not in {g['yonghu_id'] for g in gengxin}]
                dao.canjiafang_gengxin_zhuangtai(renwu_id, 'diaoxian')
                _shibai(renwu_id, f'第 {lunci} 轮缺少参与方更新：{"、".join(queshi)}')
                return
            cans = _juhe(cans, gengxin, canjia, float(renwu['jiancai_yuzhi']))
            sunshi, zhunquelv = _pinggu(cans)
            haoshi = round(time.time() - kaishi, 3)
            wenjian = _baocun_canshu(renwu_id, lunci, cans)
            dao.charu_lunci(renwu_id, lunci, sunshi, zhunquelv, haoshi,
                            wenjian, len(gengxin))
            leiji_xin = yinsi_fuwu.jiancha_yusuan(
                leiji, float(renwu['yinsipi']), float(renwu['yusuan_shangxian']))
            dao.charu_yusuan(renwu_id, lunci, float(renwu['yinsipi']), leiji_xin)
            dao.canjiafang_gengxin_zhuangtai(renwu_id, 'yiwancheng')
            _rizhi(renwu_id, '轮次完成',
                   f'第 {lunci} 轮，损失 {sunshi:.4f}，准确率 {zhunquelv:.4f}，'
                   f'耗时 {haoshi:.2f}s')
            time.sleep(0.2)
    except Exception as cuowu:
        from backend.db import YewuCuowu
        if isinstance(cuowu, YewuCuowu):
            _shibai(renwu_id, cuowu.xiaoxi)
        else:
            _shibai(renwu_id, f'训练失败：{str(cuowu)[:180]}')
        return
    dao.renwu_gengxin_zhuangtai(renwu_id, 'yiwancheng')
    _rizhi(renwu_id, '训练完成',
           f'共 {renwu["lunshu"]} 轮，累计 ε {dao.yusuan_leiji(renwu_id):.2f}')


def _zhixing_benlun(renwu: dict, lunci: int, cans: list[float],
                    canjia: list[dict]) -> None:
    """模拟模式直接产生更新，真实模式等待客户端提交。"""
    if renwu['yunxing_moshi'] == 'moni':
        for canyifang in canjia:
            zhongzi = int(canyifang['shujuji_id']) * 1000 + int(canyifang['yonghu_id'])
            jieguo = moni_xunlian(
                cans, int(canyifang['yangben_shu']), zhongzi,
                float(renwu['xuexilv']), int(renwu['piliang_daxiao']),
                float(renwu['yinsipi']), float(renwu['jiancai_yuzhi']),
            )
            dao.baocun_gengxin(
                int(renwu['id']), lunci, int(canyifang['yonghu_id']),
                jieguo['gengxin'], int(canyifang['yangben_shu']),
                jieguo['sunshi'], jieguo['zhunquelv'], jieguo['haoshi'],
            )
        return
    jiezhi = time.time() + FEDENG_CHAOSHI
    while time.time() < jiezhi:
        dangqian = dao.renwu_an_id(int(renwu['id']))
        if not dangqian or dangqian['zhuangtai'] != 'xunlianzhong':
            return
        if dao.gengxin_shuliang(int(renwu['id']), lunci) >= len(canjia):
            return
        time.sleep(1.0)


def _juhe(cans: list[float], gengxin: list[dict],
          canjia: list[dict], jiancai_yuzhi: float) -> list[float]:
    """按服务端记录的样本数加权聚合模型更新。"""
    quanzhong = {int(c['yonghu_id']): int(c['yangben_shu']) for c in canjia}
    zong_yangben = sum(quanzhong.get(int(g['yonghu_id']), 0) for g in gengxin)
    if zong_yangben <= 0:
        raise ValueError('参与方样本数无效')
    weidu = len(cans)
    leiji = np.zeros(weidu, dtype=float)
    for g in gengxin:
        xiangliang = np.asarray(g['gengxin'], dtype=float)
        if xiangliang.size != weidu:
            raise ValueError(
                f'参与方 {g.get("yonghuming", g["yonghu_id"])} 的更新维度为 '
                f'{xiangliang.size}，应为 {weidu}')
        # 服务端按任务自己的裁剪阈值再裁剪一次，防止客户端跳过或篡改阈值
        xiangliang = np.asarray(
            yinsi_fuwu.jiancai(xiangliang.tolist(), jiancai_yuzhi), dtype=float)
        leiji += xiangliang * quanzhong.get(int(g['yonghu_id']), 0)
    jieguo = np.asarray(cans, dtype=float) + leiji / zong_yangben
    return jieguo.tolist()


def _pinggu(cans: list[float]) -> tuple[float, float]:
    """在固定合成基准集上评估全局模型。"""
    X, y = shuju.shengcheng(800, PINGGU_ZHONGZI)
    moxing = MlpMoxing(zhongzi=PINGGU_ZHONGZI)
    moxing.she_canshu(cans)
    return round(moxing.sunshi(X, y), 6), round(moxing.zhunquelv(X, y), 6)


def _baocun_canshu(renwu_id: int, lunci: int, cans: list[float]) -> str:
    CANSHU_MULU.mkdir(parents=True, exist_ok=True)
    lujing = CANSHU_MULU / f'renwu_{renwu_id}_lunci_{lunci}.json'
    linshi = lujing.with_suffix('.tmp')
    neirong = {
        'renwu_id': renwu_id,
        'lunci': lunci,
        'weidu': len(cans),
        'canshu': cans,
        'shijian': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    linshi.write_text(json.dumps(neirong, ensure_ascii=False), encoding='utf-8')
    linshi.replace(lujing)
    return str(lujing)


def duqu_canshu(lujing: str) -> list[float]:
    """读取某轮全局参数文件。"""
    try:
        neirong = json.loads(Path(lujing).read_text(encoding='utf-8'))
        return [float(x) for x in neirong.get('canshu', [])]
    except (OSError, ValueError, json.JSONDecodeError):
        return []


def dangqian_canshu(renwu_id: int, lunci: int) -> list[float]:
    """返回第 lunci 轮开始时客户端应使用的全局参数。"""
    if lunci <= 1:
        return chushi_canshu(renwu_id)
    zuixin = dao.lunci_zuixin(renwu_id)
    if zuixin and int(zuixin['lunci_hao']) < lunci:
        return duqu_canshu(zuixin['canshu_wenjian'])
    if zuixin and int(zuixin['lunci_hao']) == lunci:
        return duqu_canshu(zuixin['canshu_wenjian'])
    return chushi_canshu(renwu_id)


def _shibai(renwu_id: int, yuanyin: str) -> None:
    renwu = dao.renwu_an_id(renwu_id)
    if not renwu or renwu['zhuangtai'] in ('yiwancheng', 'yiquxiao'):
        return
    dao.renwu_gengxin_zhuangtai(renwu_id, 'yichang', yuanyin)
    dao.canjiafang_gengxin_zhuangtai(renwu_id, 'diaoxian')
    _rizhi(renwu_id, '训练异常', yuanyin)


def _rizhi(renwu_id: int, dongzuo: str, xiangqing: str) -> None:
    renwu = dao.renwu_an_id(renwu_id)
    mingcheng = renwu['mingcheng'] if renwu else str(renwu_id)
    dao.xie_rizhi(None, dongzuo, 'xunlian_renwu', renwu_id, 'chenggong',
                  f'{mingcheng}：{xiangqing}')
