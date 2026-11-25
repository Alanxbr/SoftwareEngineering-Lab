"""系统信息接口。"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend import xiangying
from backend.services import xitong_fuwu

router = APIRouter(prefix='/xitong', tags=['系统'])


@router.get('/jiankang')
def jiankang():
    """健康检查；数据库不可用时返回 503，便于监控摘除实例。"""
    jieguo = xitong_fuwu.jiankang()
    if jieguo.get('zhuangtai') != 'ok':
        return JSONResponse(status_code=503,
                            content=xiangying.shibai(5000, '数据库不可用'))
    return xiangying.chenggong(jieguo)


@router.get('/xinxi')
def xinxi():
    """平台与模型信息。"""
    return xiangying.chenggong(xitong_fuwu.xinxi())
