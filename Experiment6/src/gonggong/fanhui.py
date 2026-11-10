"""统一返回结构。

业务方法不抛未捕获异常，成功和失败都用 FanhuiJieguo 表达，
接口层根据 cuowu_ma 组装 HTTP 响应。
"""

from dataclasses import dataclass
from typing import Any


CUOWU_YUSUAN = 4001
CUOWU_SHUJUJI = 4002
CUOWU_CANJIAFANG = 4003
CUOWU_ZHUANGTAI = 4004
CUOWU_CANSHU = 4005
CUOWU_CHONGMING = 4006


@dataclass
class FanhuiJieguo:
    """业务方法的统一返回值。"""

    chenggong: bool
    shuju: Any = None
    cuowu_ma: int = 0
    xiaoxi: str = ''

    @classmethod
    def chenggong_fanhui(cls, shuju: Any = None, xiaoxi: str = '操作成功') -> 'FanhuiJieguo':
        """构造成功结果。"""
        return cls(True, shuju, 0, xiaoxi)

    @classmethod
    def shibai_fanhui(cls, cuowu_ma: int, xiaoxi: str) -> 'FanhuiJieguo':
        """构造失败结果。"""
        return cls(False, None, cuowu_ma, xiaoxi)
