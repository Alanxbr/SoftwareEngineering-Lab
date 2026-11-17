"""密码哈希、JWT 与角色权限常量。"""

import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from backend.config import TOKEN_XIAOSHI, qu_miyao

SUANFA = 'HS256'
JIAOSE_TIGONGFANG = 'tigongfang'
JIAOSE_SHIYONGFANG = 'shiyongfang'
JIAOSE_GUANLIYUAN = 'guanliyuan'
HEFA_JIAOSE = (JIAOSE_TIGONGFANG, JIAOSE_SHIYONGFANG, JIAOSE_GUANLIYUAN)


def _yuchuli_mima(mima: str) -> bytes:
    """先做 SHA-256 再交给 bcrypt，规避 bcrypt 72 字节上限。"""
    zhaiyao = hashlib.sha256(mima.encode('utf-8')).digest()
    return base64.b64encode(zhaiyao)


def jiayi_mima(mima: str) -> str:
    """生成密码哈希。"""
    return bcrypt.hashpw(_yuchuli_mima(mima), bcrypt.gensalt()).decode('utf-8')


def yanzheng_mima(mima: str, mima_hash: str) -> bool:
    """校验明文密码。"""
    try:
        return bcrypt.checkpw(_yuchuli_mima(mima), mima_hash.encode('utf-8'))
    except (ValueError, TypeError):
        return False


def chuangjian_token(yonghu: dict) -> str:
    """签发 JWT。"""
    xianzai = datetime.now(timezone.utc)
    zaizhi = {
        'sub': str(yonghu['id']),
        'yonghuming': yonghu['yonghuming'],
        'jiaose': yonghu['jiaose'],
        'iat': xianzai,
        'exp': xianzai + timedelta(hours=TOKEN_XIAOSHI),
    }
    return jwt.encode(zaizhi, qu_miyao(), algorithm=SUANFA)


def jiexi_token(token: str) -> dict[str, Any]:
    """解析 JWT，失败时抛出 jwt 异常。"""
    return jwt.decode(token, qu_miyao(), algorithms=[SUANFA])


def jiancha_mima_qiangdu(mima: str) -> str | None:
    """返回密码问题描述；合格时返回 None。"""
    if len(mima) < 6:
        return '密码长度不能少于 6 位'
    if len(mima) > 64:
        return '密码长度不能超过 64 位'
    if mima.strip() != mima:
        return '密码首尾不能包含空白字符'
    return None
