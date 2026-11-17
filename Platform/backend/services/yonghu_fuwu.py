"""用户注册、登录与账号管理。"""

from backend import dao
from backend.db import YewuCuowu
from backend.deps import CUOWU_QUANXIAN
from backend.schemas import DengluRuku, ZhuceRuku
from backend.security import (
    chuangjian_token,
    jiayi_mima,
    jiancha_mima_qiangdu,
    yanzheng_mima,
)

CUOWU_CHONGMING = 4006
CUOWU_CANSHU = 4005


def zhuce(shuru: ZhuceRuku, ip: str = '') -> dict:
    """注册数据提供方或数据使用方。"""
    wenti = jiancha_mima_qiangdu(shuru.mima)
    if wenti:
        raise YewuCuowu(CUOWU_CANSHU, wenti)
    if dao.yonghu_an_ming(shuru.yonghuming):
        dao.xie_rizhi(None, '用户注册', 'yonghu', None, 'shibai',
                      f'用户名重复：{shuru.yonghuming}', ip)
        raise YewuCuowu(CUOWU_CHONGMING, '用户名已被占用', 409)
    yonghu_id = dao.chuangjian_yonghu(
        shuru.yonghuming, jiayi_mima(shuru.mima), shuru.youxiang, shuru.jiaose,
    )
    dao.xie_rizhi(yonghu_id, '用户注册', 'yonghu', yonghu_id, 'chenggong',
                  f'角色：{shuru.jiaose}', ip)
    return {'id': yonghu_id, 'yonghuming': shuru.yonghuming,
            'youxiang': shuru.youxiang, 'jiaose': shuru.jiaose,
            'zhuangtai': 'zhengchang'}


def denglu(shuru: DengluRuku, ip: str = '') -> dict:
    """校验用户名密码并签发 JWT。"""
    yonghu = dao.yonghu_an_ming(shuru.yonghuming)
    if not yonghu or not yanzheng_mima(shuru.mima, yonghu['mima_hash']):
        dao.xie_rizhi(yonghu['id'] if yonghu else None, '用户登录', 'yonghu',
                      yonghu['id'] if yonghu else None, 'shibai',
                      f'登录失败：{shuru.yonghuming}', ip)
        raise YewuCuowu(4010, '用户名或密码错误', 401)
    if yonghu['zhuangtai'] != 'zhengchang':
        dao.xie_rizhi(yonghu['id'], '用户登录', 'yonghu', yonghu['id'],
                      'yuequan', '账号已停用', ip)
        raise YewuCuowu(CUOWU_QUANXIAN, '账号已被停用，请联系管理员', 403)
    token = chuangjian_token(yonghu)
    dao.xie_rizhi(yonghu['id'], '用户登录', 'yonghu', yonghu['id'],
                  'chenggong', f'角色：{yonghu["jiaose"]}', ip)
    yonghu.pop('mima_hash', None)
    return {'token': token, 'user': yonghu}


def liechu(yonghu: dict, ye: int, meiye: int) -> dict:
    """管理员分页查看用户。"""
    if yonghu['jiaose'] != 'guanliyuan':
        raise YewuCuowu(CUOWU_QUANXIAN, '仅管理员可查看用户列表', 403)
    return dao.yonghu_liechu(ye, meiye, guanli=True)


def gengxin_zhuangtai(caozuozhe: dict, yonghu_id: int, zhuangtai: str,
                      ip: str = '') -> dict:
    """启用或停用账号，管理员账号保护。"""
    if caozuozhe['jiaose'] != 'guanliyuan':
        raise YewuCuowu(CUOWU_QUANXIAN, '仅管理员可操作账号', 403)
    mubiao = dao.yonghu_an_id(yonghu_id)
    if not mubiao:
        raise YewuCuowu(4040, '用户不存在', 404)
    if mubiao['jiaose'] == 'guanliyuan':
        raise YewuCuowu(CUOWU_QUANXIAN, '不能停用管理员账号', 403)
    if mubiao['id'] == caozuozhe['id']:
        raise YewuCuowu(CUOWU_QUANXIAN, '不能修改自己的账号状态', 403)
    dao.yonghu_gengxin_zhuangtai(yonghu_id, zhuangtai)
    dao.xie_rizhi(caozuozhe['id'], '账号状态变更', 'yonghu', yonghu_id,
                  'chenggong', f'{mubiao["yonghuming"]} -> {zhuangtai}', ip)
    mubiao['zhuangtai'] = zhuangtai
    mubiao.pop('mima_hash', None)
    return mubiao
