"""平台配置：路径、JWT 密钥和运行参数。"""

import os
import secrets
from pathlib import Path

JIEGEN = Path(__file__).resolve().parents[1]
SHUJU_MULU = Path(os.environ.get('PINGTAI_SHUJU', JIEGEN / 'data'))
BEIFEN_MULU = SHUJU_MULU / 'beifen'
CANSHU_MULU = SHUJU_MULU / 'canshu'
SHUJUKU_LUJING = SHUJU_MULU / 'pingtai.db'
QIANDUAN_MULU = JIEGEN / 'frontend'
MIYAO_LUJING = SHUJU_MULU / 'jwt.key'

TOKEN_XIAOSHI = 12
FEDENG_CHAOSHI = int(os.environ.get('PINGTAI_FEDENG_CHAOSHI', '180'))
BEIFEN_BAOLIU = 7


def chushihua_mulu() -> None:
    """确保运行目录存在。"""
    for mulu in (SHUJU_MULU, BEIFEN_MULU, CANSHU_MULU):
        mulu.mkdir(parents=True, exist_ok=True)


def qu_miyao() -> str:
    """读取或生成 JWT 签名密钥。"""
    chushihua_mulu()
    if MIYAO_LUJING.exists():
        return MIYAO_LUJING.read_text(encoding='utf-8').strip()
    miyao = secrets.token_urlsafe(48)
    MIYAO_LUJING.write_text(miyao, encoding='utf-8')
    return miyao
