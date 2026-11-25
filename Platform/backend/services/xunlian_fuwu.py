"""联邦训练任务：创建、启动、查询与结果读取。"""

import os

from backend import dao
from backend.db import YewuCuowu
from backend.deps import CUOWU_BU_CUNZAI, CUOWU_QUANXIAN
from backend.federated import xietiao
from backend.schemas import RenwuRuku
from backend.security import JIAOSE_GUANLIYUAN, JIAOSE_SHIYONGFANG
from backend.services import yinsi_fuwu

CUOWU_YUSUAN = 4001
CUOWU_CANJIAFANG = 4003
CUOWU_ZHUANGTAI = 4004
CUOWU_CANSHU = 4005


def _kejian(yonghu: dict, renwu: dict) -> None:
    """创建者、参与方和管理员可以查看任务。"""
    if yonghu['jiaose'] == JIAOSE_GUANLIYUAN:
        return
    if int(renwu['chuangjianzhe_id']) == int(yonghu['id']):
        return
    if dao.canjiafang_panduan(int(renwu['id']), int(yonghu['id'])):
        return
    raise YewuCuowu(CUOWU_QUANXIAN, '无权查看该训练任务', 403)


def _qu_renwu(renwu_id: int) -> dict:
    renwu = dao.renwu_an_id(renwu_id)
    if not renwu:
        raise YewuCuowu(CUOWU_BU_CUNZAI, '训练任务不存在', 404)
    return renwu


def chuangjian(yonghu: dict, shuru: RenwuRuku, ip: str = '') -> dict:
    """数据使用方创建联邦训练任务。"""
    if yonghu['jiaose'] not in (JIAOSE_SHIYONGFANG, JIAOSE_GUANLIYUAN):
        raise YewuCuowu(CUOWU_QUANXIAN, '仅数据使用方可创建训练任务', 403)
    canjia, tigongzhe = [], set()
    for xiang in shuru.canjia:
        shuju = dao.shujuji_an_id(xiang.shujuji_id)
        if not shuju:
            raise YewuCuowu(CUOWU_CANJIAFANG, f'数据集 {xiang.shujuji_id} 不存在')
        if shuju['zhuangtai'] != 'yijiaoyan':
            raise YewuCuowu(CUOWU_CANJIAFANG,
                            f'数据集「{shuju["mingcheng"]}」未通过校验或已停用')
        tigongfang = dao.yonghu_an_id(int(shuju['tigongfang_id']))
        if not tigongfang or tigongfang['zhuangtai'] != 'zhengchang':
            raise YewuCuowu(CUOWU_CANJIAFANG,
                            f'数据提供方「{shuju.get("tigongfang_ming", "")}」账号已停用')
        if shuju['tigongfang_id'] in tigongzhe:
            raise YewuCuowu(CUOWU_CANJIAFANG, '同一数据提供方只能加入一次')
        tigongzhe.add(shuju['tigongfang_id'])
        yangben = xiang.yangben_shu or int(shuju['yangben_shu'])
        if yangben > int(shuju['yangben_shu']):
            raise YewuCuowu(CUOWU_CANSHU,
                            f'数据集「{shuju["mingcheng"]}」最多 {shuju["yangben_shu"]} 条样本')
        canjia.append({
            'yonghu_id': int(shuju['tigongfang_id']),
            'shujuji_id': int(shuju['id']),
            'yangben_shu': int(yangben),
        })
    if len(canjia) < 1:
        raise YewuCuowu(CUOWU_CANJIAFANG, '至少需要一个参与方')
    if float(shuru.yinsipi) > float(shuru.yusuan_shangxian) + 1e-9:
        raise YewuCuowu(CUOWU_YUSUAN, '隐私预算上限不能小于单轮 ε')
    if float(shuru.lunshu) * float(shuru.yinsipi) > float(shuru.yusuan_shangxian) + 1e-9:
        raise YewuCuowu(CUOWU_CANSHU,
                        f'预算上限不足以覆盖 {shuru.lunshu} 轮，'
                        f'至少需要 {float(shuru.lunshu) * float(shuru.yinsipi):.2f}')
    renwu_id = dao.chuangjian_renwu(yonghu['id'], shuru.model_dump(), canjia)
    dao.xie_rizhi(yonghu['id'], '创建训练任务', 'xunlian_renwu', renwu_id,
                  'chenggong',
                  f'{shuru.mingcheng}，{len(canjia)} 个参与方，{shuru.lunshu} 轮', ip)
    return xiangqing(yonghu, renwu_id)


def liechu(yonghu: dict, zhuangtai: str, ye: int, meiye: int) -> dict:
    return dao.renwu_liechu(yonghu['id'], yonghu['jiaose'], zhuangtai, ye, meiye)


def xiangqing(yonghu: dict, renwu_id: int) -> dict:
    """任务详情：参与方、轮次与预算概览。"""
    renwu = _qu_renwu(renwu_id)
    _kejian(yonghu, renwu)
    canjia = dao.canjiafang_an_renwu(renwu_id)
    lunci = dao.lunci_liechu(renwu_id)
    for xiang in lunci:
        if xiang.get('canshu_wenjian'):
            xiang['canshu_wenjian'] = os.path.basename(xiang['canshu_wenjian'])
    leiji = dao.yusuan_leiji(renwu_id)
    renwu['canjiafang'] = canjia
    renwu['lunci'] = lunci
    renwu['yusuan'] = yinsi_fuwu.yusuan_zonglan(renwu, leiji)
    renwu['jindu'] = (
        round(min(1.0, len(lunci) / renwu['lunshu']), 4)
        if renwu['lunshu'] else 0.0
    )
    return renwu


def qidong(yonghu: dict, renwu_id: int, ip: str = '') -> dict:
    """校验后启动后台联邦训练。"""
    renwu = _qu_renwu(renwu_id)
    _kejian(yonghu, renwu)
    if (yonghu['jiaose'] != JIAOSE_GUANLIYUAN
            and int(renwu['chuangjianzhe_id']) != int(yonghu['id'])):
        raise YewuCuowu(CUOWU_QUANXIAN, '只有任务创建者可以启动训练', 403)
    if renwu['zhuangtai'] != 'daichufa':
        raise YewuCuowu(CUOWU_ZHUANGTAI, '任务已启动或已结束，不能重复启动', 409)
    canjia = dao.canjiafang_an_renwu(renwu_id)
    if not canjia:
        raise YewuCuowu(CUOWU_CANJIAFANG, '任务没有参与方')
    for xiang in canjia:
        if xiang['yonghu_zhuangtai'] != 'zhengchang':
            raise YewuCuowu(CUOWU_CANJIAFANG,
                            f'参与方「{xiang["yonghuming"]}」账号已停用')
        if xiang['shujuji_zhuangtai'] != 'yijiaoyan':
            raise YewuCuowu(CUOWU_CANJIAFANG,
                            f'数据集「{xiang["shujuji_ming"]}」已停用或未通过校验')
    if float(renwu['yinsipi']) > float(renwu['yusuan_shangxian']) + 1e-9:
        raise YewuCuowu(CUOWU_YUSUAN, '隐私预算上限不足')
    if (float(renwu['lunshu']) * float(renwu['yinsipi'])
            > float(renwu['yusuan_shangxian']) + 1e-9):
        raise YewuCuowu(CUOWU_YUSUAN, '预算上限不足以覆盖全部训练轮次')
    if xietiao.bingfa_shu() >= xietiao.ZUIDA_BINGFA:
        raise YewuCuowu(CUOWU_CANSHU,
                        f'并发训练任务已达上限（{xietiao.ZUIDA_BINGFA} 个），请稍后再试')
    if not dao.renwu_tiaojian_zhuangtai(renwu_id, 'daichufa', 'xunlianzhong'):
        raise YewuCuowu(CUOWU_ZHUANGTAI, '任务已被其他请求启动', 409)
    if not xietiao.qidong(renwu_id):
        dao.renwu_tiaojian_zhuangtai(renwu_id, 'xunlianzhong', 'daichufa')
        raise YewuCuowu(CUOWU_CANSHU, '训练线程启动失败，请稍后重试', 409)
    dao.xie_rizhi(yonghu['id'], '启动训练', 'xunlian_renwu', renwu_id,
                  'chenggong',
                  f'{renwu["mingcheng"]}，模式：{renwu["yunxing_moshi"]}', ip)
    return xiangqing(yonghu, renwu_id)


def quxian(yonghu: dict, renwu_id: int) -> dict:
    """损失/准确率曲线，允许轮次缺失。"""
    renwu = _qu_renwu(renwu_id)
    _kejian(yonghu, renwu)
    lunci = dao.lunci_liechu(renwu_id)
    zuiyou = None
    if lunci:
        zuiyou = max(lunci, key=lambda x: float(x['zhunquelv']))
    return {
        'renwu_id': renwu_id,
        'lunshu': renwu['lunshu'],
        'qiyong': True,
        'rounds': [
            {
                'lunci': x['lunci_hao'],
                'sunshi': x['sunshi'],
                'zhunquelv': x['zhunquelv'],
                'haoshi': x['haoshi'],
                'canjia_shu': x['canjia_shu'],
                'shijian': x['chuangjian_shijian'],
            }
            for x in lunci
        ],
        'zuiyou': {
            'lunci': zuiyou['lunci_hao'],
            'zhunquelv': zuiyou['zhunquelv'],
            'sunshi': zuiyou['sunshi'],
        } if zuiyou else None,
    }


def yinsi(yonghu: dict, renwu_id: int) -> dict:
    """隐私预算使用情况。"""
    renwu = _qu_renwu(renwu_id)
    _kejian(yonghu, renwu)
    leiji = dao.yusuan_leiji(renwu_id)
    zonglan = yinsi_fuwu.yusuan_zonglan(renwu, leiji)
    zonglan['renwu_id'] = renwu_id
    zonglan['mingcheng'] = renwu['mingcheng']
    zonglan['jilu'] = dao.yusuan_liechu(renwu_id)
    return zonglan
