"""真实模式参与方接口。"""

from fastapi import APIRouter, Depends

from backend import xiangying
from backend.deps import dangqian_yonghu
from backend.schemas import KehuduanGengxinRuku
from backend.services import kehuduan_fuwu

router = APIRouter(prefix='/kehuduan', tags=['参与方'])


@router.get('/renwu')
def renwu_liechu(yonghu: dict = Depends(dangqian_yonghu)):
    """我参与的训练任务。"""
    return xiangying.chenggong(kehuduan_fuwu.renwu_liechu(yonghu))


@router.get('/renwu/{renwu_id}')
def zhuangtai(renwu_id: int, yonghu: dict = Depends(dangqian_yonghu)):
    """当前轮次与应使用的全局模型参数。"""
    return xiangying.chenggong(kehuduan_fuwu.zhuangtai(yonghu, renwu_id))


@router.post('/renwu/{renwu_id}/tijiao')
def tijiao(renwu_id: int, shuru: KehuduanGengxinRuku,
           yonghu: dict = Depends(dangqian_yonghu)):
    """提交本地加噪更新。"""
    return xiangying.chenggong(
        kehuduan_fuwu.tijiao(yonghu, renwu_id, shuru), '更新已提交')
