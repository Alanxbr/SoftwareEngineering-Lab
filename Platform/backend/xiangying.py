"""统一 JSON 响应构造。"""

from typing import Any


def chenggong(shuju: Any = None, xiaoxi: str = '操作成功') -> dict:
    return {'code': 0, 'message': xiaoxi, 'data': shuju}


def shibai(cuowu_ma: int, xiaoxi: str) -> dict:
    return {'code': cuowu_ma, 'message': xiaoxi, 'data': None}
