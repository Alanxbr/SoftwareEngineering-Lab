"""用户认证与账号管理接口。"""

from fastapi import APIRouter, Depends, Query, Request

from backend import xiangying
from backend.deps import dangqian_yonghu, gongkai_yonghu, kehu_ip
from backend.schemas import DengluRuku, GuanliYonghuRuku, ZhuceRuku
from backend.services import yonghu_fuwu
from backend.services.guanli_fuwu import yonghu_gengxin, yonghu_liechu

router = APIRouter(prefix='/yonghu', tags=['用户'])


@router.post('/zhuce')
def zhuce(shuru: ZhuceRuku, request: Request):
    """注册数据提供方或数据使用方账号。"""
    jieguo = yonghu_fuwu.zhuce(shuru, kehu_ip(request))
    return xiangying.chenggong(jieguo, '注册成功')


@router.post('/denglu')
def denglu(shuru: DengluRuku, request: Request):
    """登录并获取访问令牌。"""
    return xiangying.chenggong(yonghu_fuwu.denglu(shuru, kehu_ip(request)), '登录成功')


@router.get('/wo')
def wo(yonghu: dict = Depends(dangqian_yonghu)):
    """当前登录用户信息。"""
    return xiangying.chenggong(gongkai_yonghu(yonghu))


@router.get('')
def liechu(ye: int = Query(1, ge=1), meiye: int = Query(20, ge=1, le=100),
           yonghu: dict = Depends(dangqian_yonghu)):
    """管理员分页查看用户。"""
    return xiangying.chenggong(yonghu_liechu(yonghu, ye, meiye))


@router.patch('/{yonghu_id}/zhuangtai')
def gengxin_zhuangtai(yonghu_id: int, shuru: GuanliYonghuRuku, request: Request,
                      yonghu: dict = Depends(dangqian_yonghu)):
    """管理员启用或停用账号。"""
    jieguo = yonghu_gengxin(yonghu, yonghu_id, shuru.zhuangtai, kehu_ip(request))
    return xiangying.chenggong(jieguo, '账号状态已更新')
