"""系统信息接口。"""

from fastapi import APIRouter

from backend import xiangying
from backend.services import xitong_fuwu

router = APIRouter(prefix='/xitong', tags=['系统'])


@router.get('/jiankang')
def jiankang():
    """健康检查。"""
    return xiangying.chenggong(xitong_fuwu.jiankang())


@router.get('/xinxi')
def xinxi():
    """平台与模型信息。"""
    return xiangying.chenggong(xitong_fuwu.xinxi())
