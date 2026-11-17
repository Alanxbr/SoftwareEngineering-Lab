"""FastAPI 依赖：身份认证、角色校验和客户端地址。"""

from fastapi import Depends, Header, Request

from backend import dao
from backend.db import YewuCuowu
from backend.security import jiexi_token

CUOWU_RENZHENG = 4010
CUOWU_QUANXIAN = 4030
CUOWU_BU_CUNZAI = 4040


def kehu_ip(request: Request) -> str:
    """优先取反向代理转发地址。"""
    zhuanfa = request.headers.get('x-forwarded-for', '')
    if zhuanfa:
        return zhuanfa.split(',')[0].strip()
    return request.client.host if request.client else ''


def dangqian_yonghu(authorization: str | None = Header(default=None)) -> dict:
    """解析 Bearer Token 并加载用户。"""
    if not authorization or not authorization.startswith('Bearer '):
        raise YewuCuowu(CUOWU_RENZHENG, '未登录或登录已过期', 401)
    token = authorization[7:].strip()
    try:
        zaizhi = jiexi_token(token)
        yonghu_id = int(zaizhi.get('sub', 0))
    except Exception:
        raise YewuCuowu(CUOWU_RENZHENG, '登录凭证无效', 401)
    yonghu = dao.yonghu_an_id(yonghu_id)
    if not yonghu:
        raise YewuCuowu(CUOWU_RENZHENG, '用户不存在', 401)
    if yonghu['zhuangtai'] != 'zhengchang':
        raise YewuCuowu(CUOWU_QUANXIAN, '账号已被停用', 403)
    return yonghu


def yaoqiu_jiaose(*jiaose: str):
    """生成角色校验依赖，管理员始终放行。"""
    def jiancha(yonghu: dict = Depends(dangqian_yonghu)) -> dict:
        if yonghu['jiaose'] != 'guanliyuan' and yonghu['jiaose'] not in jiaose:
            raise YewuCuowu(CUOWU_QUANXIAN, '当前角色无权执行该操作', 403)
        return yonghu
    return jiancha


def gongkai_yonghu(yonghu: dict) -> dict:
    """去掉密码哈希。"""
    jieguo = dict(yonghu)
    jieguo.pop('mima_hash', None)
    return jieguo
