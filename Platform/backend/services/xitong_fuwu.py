"""系统健康检查与平台信息。"""

import logging
from datetime import datetime

from backend import dao
from backend.config import CANSHU_MULU, SHUJUKU_LUJING
from backend.federated.moxing import MlpMoxing

BANBEN = '1.0.0'
rizhi = logging.getLogger('pingtai')


def jiankang() -> dict:
    """数据库与模型自检。"""
    try:
        hang = dao.chaxun_yi('SELECT COUNT(*) AS n FROM yonghu')
        yonghu_shu = int(hang['n']) if hang else 0
        shujuku = 'zhengchang'
    except Exception as cuowu:
        rizhi.exception('健康检查数据库访问失败')
        yonghu_shu = 0
        shujuku = 'yichang'
    moxing = MlpMoxing()
    return {
        'zhuangtai': 'ok' if shujuku == 'zhengchang' else 'error',
        'shijian': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'shujuku': shujuku,
        'yonghu_shu': yonghu_shu,
        'moxing': 'mlp_8_16_2',
        'canshu_weidu': moxing.weidu,
        'banben': BANBEN,
    }


def xinxi() -> dict:
    return {
        'mingcheng': '隐私计算数据共享平台',
        'banben': BANBEN,
        'mingti': '联邦学习 + 差分隐私',
        'moxing': {
            'mingcheng': 'mlp_8_16_2',
            'shuru_weidu': 8,
            'yincang_weidu': 16,
            'shuchu_weidu': 2,
            'canshu_weidu': MlpMoxing().weidu,
        },
        'yinsi': {
            'jizhi': 'Laplace',
            'meilun_eps_default': 0.5,
            'jiancai_yuzhi_default': 1.0,
        },
        'juese': [
            {'zhi': 'tigongfang', 'mingcheng': '数据提供方'},
            {'zhi': 'shiyongfang', 'mingcheng': '数据使用方'},
            {'zhi': 'guanliyuan', 'mingcheng': '系统管理员'},
        ],
        # 只暴露逻辑名称，不返回绝对路径
        'lujing': {
            'shujuku': SHUJUKU_LUJING.name,
            'canshu': CANSHU_MULU.name,
        },
    }
