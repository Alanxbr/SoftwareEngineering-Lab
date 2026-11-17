"""工作台概览接口。"""

from fastapi import APIRouter, Depends

from backend import xiangying
from backend.deps import dangqian_yonghu
from backend.services import guanli_fuwu

router = APIRouter(tags=['工作台'])


@router.get('/zonglan')
def zonglan(yonghu: dict = Depends(dangqian_yonghu)):
    """按角色返回工作台统计。"""
    return xiangying.chenggong(guanli_fuwu.zonglan(yonghu))
