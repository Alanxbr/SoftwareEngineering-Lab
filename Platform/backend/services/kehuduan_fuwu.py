"""真实模式参与方接口：读取轮次模型并提交本地更新。"""

import math

from backend import dao
from backend.db import YewuCuowu
from backend.deps import CUOWU_QUANXIAN
from backend.federated import xietiao
from backend.federated.moxing import MlpMoxing
from backend.schemas import KehuduanGengxinRuku
from backend.services import yinsi_fuwu

CUOWU_CANJIAFANG = 4003
CUOWU_ZHUANGTAI = 4004
CUOWU_CANSHU = 4005


def _canjia(yonghu: dict, renwu_id: int) -> dict:
    renwu = dao.renwu_an_id(renwu_id)
    if not renwu:
        raise YewuCuowu(4040, '训练任务不存在', 404)
    canjia = dao.canjiafang_panduan(renwu_id, yonghu['id'])
    if not canjia:
        raise YewuCuowu(CUOWU_QUANXIAN, '当前用户不是该任务的参与方', 403)
    return {'renwu': renwu, 'canjia': canjia}


def renwu_liechu(yonghu: dict) -> list[dict]:
    """当前用户参与的任务。"""
    return dao.chaxun_duo(
        'SELECT r.id, r.mingcheng, r.zhuangtai, r.dangqian_lunci, r.lunshu, '
        'r.yinsipi, r.yunxing_moshi, c.zhuangtai AS canjia_zhuangtai '
        'FROM renwu_canjiafang c JOIN xunlian_renwu r ON r.id = c.renwu_id '
        'WHERE c.yonghu_id = ? ORDER BY r.id DESC LIMIT 50',
        (yonghu['id'],),
    )


def zhuangtai(yonghu: dict, renwu_id: int) -> dict:
    """返回当前轮次、应使用的全局参数和本地配置。"""
    xiang = _canjia(yonghu, renwu_id)
    renwu, canjia = xiang['renwu'], xiang['canjia']
    lunci = max(1, int(renwu['dangqian_lunci']))
    moxing = MlpMoxing()
    return {
        'renwu_id': renwu_id,
        'mingcheng': renwu['mingcheng'],
        'zhuangtai': renwu['zhuangtai'],
        'dangqian_lunci': int(renwu['dangqian_lunci']),
        'zong_lunshu': int(renwu['lunshu']),
        'canshu': xietiao.dangqian_canshu(renwu_id, lunci),
        'canshu_weidu': moxing.weidu,
        'xuexilv': float(renwu['xuexilv']),
        'piliang_daxiao': int(renwu['piliang_daxiao']),
        'yinsipi': float(renwu['yinsipi']),
        'jiancai_yuzhi': float(renwu['jiancai_yuzhi']),
        'yangben_shu': int(canjia['yangben_shu']),
        'yijing_tijiao': (
            int(renwu['dangqian_lunci']) > 0
            and dao.gengxin_shifou_tijiao(renwu_id, int(renwu['dangqian_lunci']),
                                          yonghu['id'])
        ),
    }


def tijiao(yonghu: dict, renwu_id: int, shuru: KehuduanGengxinRuku) -> dict:
    """接收参与方提交的加噪模型更新。"""
    xiang = _canjia(yonghu, renwu_id)
    renwu = xiang['renwu']
    if renwu['zhuangtai'] != 'xunlianzhong':
        raise YewuCuowu(CUOWU_ZHUANGTAI, '任务当前不在训练中', 409)
    if int(shuru.lunci_hao) != int(renwu['dangqian_lunci']):
        raise YewuCuowu(CUOWU_ZHUANGTAI, '轮次已变化，请重新获取全局模型', 409)
    moxing = MlpMoxing()
    if len(shuru.gengxin) != moxing.weidu:
        raise YewuCuowu(CUOWU_CANSHU,
                        f'模型更新维度应为 {moxing.weidu}，实际 {len(shuru.gengxin)}')
    if not all(math.isfinite(x) for x in shuru.gengxin):
        raise YewuCuowu(CUOWU_CANSHU, '模型更新包含非法数值')
    # 客户端不可信：服务端统一裁剪并按本轮 ε 加噪，不能依赖客户端自报的加噪结果
    gengxin = yinsi_fuwu.jiagong(
        shuru.gengxin, float(renwu['yinsipi']), float(renwu['jiancai_yuzhi']),
    )
    dao.baocun_gengxin(
        renwu_id, int(shuru.lunci_hao), yonghu['id'], gengxin,
        int(shuru.yangben_shu), float(shuru.sunshi), float(shuru.zhunquelv),
        float(shuru.haoshi),
    )
    dao.canjiafang_gengxin_zhuangtai(renwu_id, 'xunlianzhong', yonghu['id'])
    return {'renwu_id': renwu_id, 'lunci_hao': shuru.lunci_hao,
            'zhuangtai': 'yijieshou'}
