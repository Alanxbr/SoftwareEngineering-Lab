"""系统管理接口（管理员）。"""

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse

from backend import xiangying
from backend.deps import dangqian_yonghu, kehu_ip
from backend.schemas import GuanliRenwuRuku, GuanliYonghuRuku
from backend.services import guanli_fuwu

router = APIRouter(prefix='/guanli', tags=['系统管理'])


@router.get('/yonghu')
def yonghu_liechu(ye: int = Query(1, ge=1), meiye: int = Query(20, ge=1, le=100),
                  yonghu: dict = Depends(dangqian_yonghu)):
    return xiangying.chenggong(guanli_fuwu.yonghu_liechu(yonghu, ye, meiye))


@router.patch('/yonghu/{yonghu_id}')
def yonghu_gengxin(yonghu_id: int, shuru: GuanliYonghuRuku, request: Request,
                   yonghu: dict = Depends(dangqian_yonghu)):
    jieguo = guanli_fuwu.yonghu_gengxin(
        yonghu, yonghu_id, shuru.zhuangtai, kehu_ip(request))
    return xiangying.chenggong(jieguo, '账号状态已更新')


@router.get('/renwu')
def renwu_liechu(zhuangtai: str = '', ye: int = Query(1, ge=1),
                 meiye: int = Query(20, ge=1, le=100),
                 yonghu: dict = Depends(dangqian_yonghu)):
    return xiangying.chenggong(guanli_fuwu.renwu_liechu(yonghu, zhuangtai, ye, meiye))


@router.get('/renwu/{renwu_id}')
def renwu_xiangqing(renwu_id: int, yonghu: dict = Depends(dangqian_yonghu)):
    guanli_fuwu._yaoqiu_guanli(yonghu)
    return xiangying.chenggong(guanli_fuwu.xiangqing_guanli(renwu_id))


@router.patch('/renwu/{renwu_id}')
def renwu_gengxin(renwu_id: int, shuru: GuanliRenwuRuku, request: Request,
                  yonghu: dict = Depends(dangqian_yonghu)):
    jieguo = guanli_fuwu.renwu_gengxin(
        yonghu, renwu_id, shuru.zhuangtai, shuru.yuanyin, kehu_ip(request))
    return xiangying.chenggong(jieguo, '任务状态已更新')


@router.get('/rizhi')
def rizhi(leixing: str = '', jieguo: str = '', yonghuming: str = '',
          kaishi: str = '', jieshu: str = '', ye: int = Query(1, ge=1),
          meiye: int = Query(20, ge=1, le=100),
          yonghu: dict = Depends(dangqian_yonghu)):
    return xiangying.chenggong(guanli_fuwu.rizhi(
        yonghu, leixing, jieguo, yonghuming, kaishi, jieshu, ye, meiye))


@router.post('/beifen')
def beifen(request: Request, yonghu: dict = Depends(dangqian_yonghu)):
    """立即备份数据库。"""
    return xiangying.chenggong(
        guanli_fuwu.beifen(yonghu, kehu_ip(request)), '备份完成')


@router.get('/beifen')
def beifen_liechu(yonghu: dict = Depends(dangqian_yonghu)):
    return xiangying.chenggong(guanli_fuwu.beifen_liechu(yonghu))


@router.get('/beifen/{wenjian}')
def beifen_xiazai(wenjian: str, yonghu: dict = Depends(dangqian_yonghu)):
    """下载备份文件。"""
    lujing = guanli_fuwu.beifen_lujing(yonghu, wenjian)
    return FileResponse(str(lujing), filename=lujing.name,
                        media_type='application/octet-stream')
