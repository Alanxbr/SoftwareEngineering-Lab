"""数据集接口。"""

from fastapi import APIRouter, Depends, Query, Request

from backend import xiangying
from backend.deps import dangqian_yonghu, kehu_ip
from backend.schemas import ShujuJiaoyanRuku, ShujuZhuangtaiRuku, ShujujiRuku
from backend.services import shuju_fuwu

router = APIRouter(prefix='/shuju', tags=['数据集'])


@router.post('/jiaoyan')
def jiaoyan(shuru: ShujuJiaoyanRuku, yonghu: dict = Depends(dangqian_yonghu)):
    """预检数据集格式，不落库。"""
    return xiangying.chenggong(shuju_fuwu.jiaoyan(shuru))


@router.post('')
def dengji(shuru: ShujujiRuku, request: Request,
           yonghu: dict = Depends(dangqian_yonghu)):
    """登记数据集元数据。"""
    return xiangying.chenggong(shuju_fuwu.dengji(yonghu, shuru, kehu_ip(request)),
                               '数据集登记成功')


@router.get('')
def liechu(ye: int = Query(1, ge=1), meiye: int = Query(50, ge=1, le=100),
           yonghu: dict = Depends(dangqian_yonghu)):
    """按当前角色返回可见数据集。"""
    return xiangying.chenggong(shuju_fuwu.liechu(yonghu, ye, meiye))


@router.get('/{shujuji_id}')
def qu(shujuji_id: int, yonghu: dict = Depends(dangqian_yonghu)):
    return xiangying.chenggong(shuju_fuwu.qu(yonghu, shujuji_id))


@router.patch('/{shujuji_id}/zhuangtai')
def gengxin_zhuangtai(shujuji_id: int, shuru: ShujuZhuangtaiRuku, request: Request,
                      yonghu: dict = Depends(dangqian_yonghu)):
    """停用或恢复数据集。"""
    jieguo = shuju_fuwu.gengxin_zhuangtai(
        yonghu, shujuji_id, shuru.zhuangtai, kehu_ip(request))
    return xiangying.chenggong(jieguo, '数据集状态已更新')
