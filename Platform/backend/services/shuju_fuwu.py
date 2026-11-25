"""数据集元数据登记、格式校验与停用管理。"""

import sqlite3

from backend import dao
from backend.db import YewuCuowu
from backend.deps import CUOWU_BU_CUNZAI, CUOWU_QUANXIAN
from backend.schemas import ShujuJiaoyanRuku, ShujujiRuku
from backend.security import JIAOSE_GUANLIYUAN, JIAOSE_TIGONGFANG

CUOWU_CANSHU = 4005
CUOWU_CHONGMING = 4006
CUOWU_ZHUANGTAI = 4004
ZHICHI_GESHI = ('csv', 'json', 'parquet', 'npy')


def _jiancha_ziduan(ziduan: list[str], biaozhun: list[str] | None = None) -> list[str]:
    wenti = []
    if not ziduan:
        wenti.append('字段清单不能为空')
    if len(ziduan) > 200:
        wenti.append('字段数量不能超过 200')
    for zi in ziduan:
        if len(zi) > 40:
            wenti.append(f'字段名过长：{zi[:20]}...')
        if not all(c.isalnum() or c == '_' for c in zi):
            wenti.append(f'字段名只能包含字母、数字和下划线：{zi}')
    if biaozhun:
        queshao = [x for x in biaozhun if x not in ziduan]
        if queshao:
            wenti.append('缺少必需字段：' + '、'.join(queshao))
    return wenti


def jiaoyan(shuru: ShujuJiaoyanRuku) -> dict:
    """执行格式校验并给出结论。"""
    wenti = []
    if shuru.geshi not in ZHICHI_GESHI:
        wenti.append(f'不支持的格式：{shuru.geshi}')
    if shuru.yangben_shu <= 0:
        wenti.append('样本数必须大于 0')
    wenti.extend(_jiancha_ziduan(shuru.ziduan, shuru.biaozhun_ziduan))
    if wenti:
        return {'tongguo': False, 'wenti': wenti, 'jielun': '；'.join(wenti)}
    jielun = (
        f'格式 {shuru.geshi.upper()} 可解析，{len(shuru.ziduan)} 个字段类型定义完整，'
        f'{shuru.yangben_shu} 条样本元数据有效'
    )
    return {'tongguo': True, 'wenti': [], 'jielun': jielun}


def dengji(yonghu: dict, shuru: ShujujiRuku, ip: str = '') -> dict:
    """登记数据集，仅保存元数据，不上传原始数据。"""
    if yonghu['jiaose'] not in (JIAOSE_TIGONGFANG, JIAOSE_GUANLIYUAN):
        raise YewuCuowu(CUOWU_QUANXIAN, '仅数据提供方可登记数据集', 403)
    jieguo = jiaoyan(ShujuJiaoyanRuku(
        ziduan=shuru.ziduan,
        yangben_shu=shuru.yangben_shu,
        geshi=shuru.geshi,
    ))
    if not jieguo['tongguo']:
        raise YewuCuowu(CUOWU_CANSHU, jieguo['jielun'])
    shuju = shuru.model_dump()
    shuju['zhuangtai'] = 'yijiaoyan'
    shuju['jiaoyan_jielun'] = jieguo['jielun']
    try:
        shujuji_id = dao.chuangjian_shujuji(yonghu['id'], shuju)
    except sqlite3.IntegrityError:
        raise YewuCuowu(CUOWU_CHONGMING, '同名数据集已存在', 409)
    dao.xie_rizhi(yonghu['id'], '登记数据集', 'shujuji', shujuji_id,
                  'chenggong', f'{shuru.mingcheng}（{shuru.yangben_shu} 条）', ip)
    return dao.shujuji_an_id(shujuji_id)


def _gongkai(shuju: dict) -> dict:
    """非所有者只返回公开元数据，隐藏本地路径和脱敏规则。"""
    gongkai = dict(shuju)
    gongkai.pop('benzhi_lujing', None)
    gongkai.pop('tuomin_guize', None)
    return gongkai


def liechu(yonghu: dict, ye: int = 1, meiye: int = 50) -> dict:
    """按角色返回可见数据集。"""
    if yonghu['jiaose'] == JIAOSE_GUANLIYUAN:
        return dao.shujuji_liechu(None, bao_tingyong=True, ye=ye, meiye=meiye)
    if yonghu['jiaose'] == JIAOSE_TIGONGFANG:
        return dao.shujuji_liechu(yonghu['id'], bao_tingyong=True, ye=ye, meiye=meiye)
    jieguo = dao.shujuji_liechu(None, bao_tingyong=False, ye=ye, meiye=meiye)
    jieguo['items'] = [_gongkai(x) for x in jieguo['items']]
    return jieguo


def qu(yonghu: dict, shujuji_id: int) -> dict:
    """读取数据集并做权限判断。"""
    shuju = dao.shujuji_an_id(shujuji_id)
    if not shuju:
        raise YewuCuowu(CUOWU_BU_CUNZAI, '数据集不存在', 404)
    if yonghu['jiaose'] == JIAOSE_GUANLIYUAN:
        return shuju
    if shuju['tigongfang_id'] == yonghu['id']:
        return shuju
    if shuju['zhuangtai'] == 'yijiaoyan':
        return _gongkai(shuju)
    raise YewuCuowu(CUOWU_QUANXIAN, '无权查看该数据集', 403)


def gengxin_zhuangtai(yonghu: dict, shujuji_id: int, zhuangtai: str,
                      ip: str = '') -> dict:
    """停用或恢复数据集。"""
    if zhuangtai not in ('yijiaoyan', 'yitingyong'):
        raise YewuCuowu(CUOWU_CANSHU, '状态只能为 yijiaoyan 或 yitingyong')
    shuju = dao.shujuji_an_id(shujuji_id)
    if not shuju:
        raise YewuCuowu(CUOWU_BU_CUNZAI, '数据集不存在', 404)
    if yonghu['jiaose'] != JIAOSE_GUANLIYUAN and shuju['tigongfang_id'] != yonghu['id']:
        raise YewuCuowu(CUOWU_QUANXIAN, '只能管理自己的数据集', 403)
    if zhuangtai == 'yitingyong':
        zhengzai = dao.chaxun_yi(
            "SELECT 1 AS ok FROM renwu_canjiafang c JOIN xunlian_renwu r "
            "ON r.id = c.renwu_id WHERE c.shujuji_id = ? AND r.zhuangtai = 'xunlianzhong'",
            (shujuji_id,),
        )
        if zhengzai:
            raise YewuCuowu(CUOWU_ZHUANGTAI, '数据集正在被训练任务使用，暂不能停用', 409)
    dao.shujuji_gengxin_zhuangtai(shujuji_id, zhuangtai, shuju['jiaoyan_jielun'])
    dao.xie_rizhi(yonghu['id'], '数据集状态变更', 'shujuji', shujuji_id,
                  'chenggong', f'{shuju["mingcheng"]} -> {zhuangtai}', ip)
    return dao.shujuji_an_id(shujuji_id)
