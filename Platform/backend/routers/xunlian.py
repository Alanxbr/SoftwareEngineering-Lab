"""联邦训练任务接口。"""

from fastapi import APIRouter, Depends, Query, Request

from backend import xiangying
from backend.deps import dangqian_yonghu, kehu_ip
from backend.schemas import RenwuRuku
from backend.services import xunlian_fuwu

router = APIRouter(prefix='/xunlian', tags=['联邦训练'])


@router.post('')
def chuangjian(shuru: RenwuRuku, request: Request,
               yonghu: dict = Depends(dangqian_yonghu)):
    """数据使用方创建联邦训练任务。"""
    return xiangying.chenggong(
        xunlian_fuwu.chuangjian(yonghu, shuru, kehu_ip(request)), '任务创建成功')


@router.get('')
def liechu(zhuangtai: str = '', ye: int = Query(1, ge=1),
           meiye: int = Query(20, ge=1, le=100),
           yonghu: dict = Depends(dangqian_yonghu)):
    return xiangying.chenggong(xunlian_fuwu.liechu(yonghu, zhuangtai, ye, meiye))


@router.get('/{renwu_id}')
def xiangqing(renwu_id: int, yonghu: dict = Depends(dangqian_yonghu)):
    return xiangying.chenggong(xunlian_fuwu.xiangqing(yonghu, renwu_id))


@router.post('/{renwu_id}/qidong')
def qidong(renwu_id: int, request: Request,
           yonghu: dict = Depends(dangqian_yonghu)):
    """启动联邦训练（后台线程）。"""
    return xiangying.chenggong(
        xunlian_fuwu.qidong(yonghu, renwu_id, kehu_ip(request)), '训练已启动')


@router.get('/{renwu_id}/quxian')
def quxian(renwu_id: int, yonghu: dict = Depends(dangqian_yonghu)):
    """损失与准确率曲线。"""
    return xiangying.chenggong(xunlian_fuwu.quxian(yonghu, renwu_id))


@router.get('/{renwu_id}/yinsi')
def yinsi(renwu_id: int, yonghu: dict = Depends(dangqian_yonghu)):
    """隐私预算使用情况。"""
    return xiangying.chenggong(xunlian_fuwu.yinsi(yonghu, renwu_id))
