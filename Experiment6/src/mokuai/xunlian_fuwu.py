"""联邦训练模块：任务创建、逐轮训练、参数聚合与状态查询。"""

import json
import random
from pathlib import Path

from cunchu.dao import CanjiaFangDao, LunciDao, RenwuDao
from gonggong.fanhui import (
    CUOWU_CANJIAFANG,
    CUOWU_CANSHU,
    CUOWU_SHUJUJI,
    CUOWU_YUSUAN,
    CUOWU_ZHUANGTAI,
    FanhuiJieguo,
)
from mokuai.shuju_fuwu import ShujuFuwu
from mokuai.yinsi_fuwu import YinsiFuwu


class XunlianFuwu:
    """联邦训练核心服务。"""

    def __init__(self, renwu_dao: RenwuDao, canjia_dao: CanjiaFangDao,
                 lunci_dao: LunciDao, shuju_fuwu: ShujuFuwu,
                 yinsi_fuwu: YinsiFuwu, canshu_mulu: str):
        self.renwu_dao = renwu_dao
        self.canjia_dao = canjia_dao
        self.lunci_dao = lunci_dao
        self.shuju_fuwu = shuju_fuwu
        self.yinsi_fuwu = yinsi_fuwu
        self.canshu_mulu = Path(canshu_mulu)

    def chuangjian_renwu(self, chuangjianzhe_id: int, mingcheng: str,
                         canjia_list: list[dict], lunshu: int,
                         piliang_daxiao: int, xuexilv: float, yinsipi: float,
                         jiancai_yuzhi: float,
                         yusuan_shangxian: float) -> FanhuiJieguo:
        """创建训练任务，并校验参与方数据集可用。"""
        jiancha = self._jiancha_renwu_canshu(
            mingcheng, canjia_list, lunshu, piliang_daxiao, xuexilv,
            yinsipi, jiancai_yuzhi, yusuan_shangxian,
        )
        if jiancha is not None:
            return jiancha
        for canjia in canjia_list:
            shujuji = self.shuju_fuwu.chaxun_shujuji(canjia['shujuji_id'])
            if not shujuji.chenggong:
                return FanhuiJieguo.shibai_fanhui(CUOWU_SHUJUJI, '参与方数据集不存在')
            if shujuji.shuju['zhuangtai'] != 'yijiaoyan':
                return FanhuiJieguo.shibai_fanhui(
                    CUOWU_SHUJUJI,
                    '数据集 %s 不可用' % shujuji.shuju['mingcheng'],
                )
        renwu_id = self.renwu_dao.charru(
            chuangjianzhe_id, mingcheng, lunshu, piliang_daxiao, xuexilv,
            yinsipi, jiancai_yuzhi, yusuan_shangxian,
        )
        for canjia in canjia_list:
            self.canjia_dao.charru(
                renwu_id, canjia['yonghu_id'], canjia['shujuji_id'],
                canjia['yangben_shu'],
            )
        return FanhuiJieguo.chenggong_fanhui({'renwu_id': renwu_id}, '任务创建成功')

    def qidong_xunlian(self, renwu_id: int) -> FanhuiJieguo:
        """启动任务：检查状态、参与方、数据集和预算。"""
        renwu = self.renwu_dao.chaxun_an_id(renwu_id)
        if renwu is None:
            return FanhuiJieguo.shibai_fanhui(CUOWU_ZHUANGTAI, '任务不存在')
        if renwu['zhuangtai'] != 'daichufa':
            return FanhuiJieguo.shibai_fanhui(CUOWU_ZHUANGTAI, '只有待启动任务可以启动')
        canjiafang = self.canjia_dao.chaxun_an_renwu(renwu_id)
        if not canjiafang:
            return FanhuiJieguo.shibai_fanhui(CUOWU_CANJIAFANG, '任务没有参与方')
        for canjia in canjiafang:
            shujuji = self.shuju_fuwu.chaxun_shujuji(canjia['shujuji_id'])
            if not shujuji.chenggong or shujuji.shuju['zhuangtai'] != 'yijiaoyan':
                return FanhuiJieguo.shibai_fanhui(CUOWU_SHUJUJI, '参与方数据集不可用')
        if not self.yinsi_fuwu.jiancha_yusuan(renwu_id, float(renwu['yinsipi'])):
            return FanhuiJieguo.shibai_fanhui(
                CUOWU_YUSUAN, '隐私预算不足，无法启动训练'
            )
        self.renwu_dao.gengxin_zhuangtai(renwu_id, 'xunlianzhong')
        for canjia in canjiafang:
            self.canjia_dao.gengxin_zhuangtai(renwu_id, canjia['yonghu_id'], 'xunlianzhong')
        return FanhuiJieguo.chenggong_fanhui(
            {'renwu_id': renwu_id, 'zhuangtai': 'xunlianzhong'},
            '训练已启动',
        )

    def zhixing_lunci(self, renwu_id: int, canjia_gengxin: list[dict],
                      suijishu: random.Random | None = None) -> FanhuiJieguo:
        """执行一轮：本地更新加噪、加权聚合、记录预算和指标。"""
        renwu = self.renwu_dao.chaxun_an_id(renwu_id)
        jiancha = self._jiancha_lunci(renwu_id, renwu, canjia_gengxin)
        if jiancha is not None:
            return jiancha
        lunci_hao = len(self.lunci_dao.chaxun_an_renwu(renwu_id)) + 1
        canjiafang = self.canjia_dao.chaxun_an_renwu(renwu_id)
        gengxin_map = {x['yonghu_id']: x for x in canjia_gengxin}
        yinsipi = float(renwu['yinsipi'])
        suijishu = suijishu or random.Random()
        jiaguan_list = self._jiaguan_benlun(canjiafang, gengxin_map, renwu, suijishu)
        quanju_canshu = self.juhe_canshu(renwu_id, jiaguan_list)
        sunshi, zhunquelv, haoshi = self._jihe_zhibiao(canjiafang, gengxin_map)
        canshu_wenjian = self._baocun_canshu(renwu_id, lunci_hao, quanju_canshu)
        yusuan = self.yinsi_fuwu.jilu_yusuan(renwu_id, lunci_hao, yinsipi)
        if not yusuan.chenggong:
            return yusuan
        self.lunci_dao.charru(
            renwu_id, lunci_hao, sunshi, zhunquelv, haoshi, canshu_wenjian
        )
        zhuangtai = self._jieshu_lunci(renwu, lunci_hao, canjiafang)
        return FanhuiJieguo.chenggong_fanhui(
            {
                'renwu_id': renwu_id,
                'lunci_hao': lunci_hao,
                'quanju_canshu': quanju_canshu,
                'sunshi': sunshi,
                'zhunquelv': zhunquelv,
                'haoshi': haoshi,
                'canshu_wenjian': canshu_wenjian,
                'leiji_eps': yusuan.shuju['leiji_eps'],
                'shengyu_yusuan': yusuan.shuju['shengyu_yusuan'],
                'zhuangtai': zhuangtai,
            },
            '第 %d 轮训练完成' % lunci_hao,
        )

    def _jiancha_lunci(self, renwu_id: int, renwu: dict | None,
                       canjia_gengxin: list[dict]) -> FanhuiJieguo | None:
        """执行一轮前的状态、参与方和预算检查。"""
        if renwu is None:
            return FanhuiJieguo.shibai_fanhui(CUOWU_ZHUANGTAI, '任务不存在')
        if renwu['zhuangtai'] != 'xunlianzhong':
            return FanhuiJieguo.shibai_fanhui(CUOWU_ZHUANGTAI, '任务不在训练状态')
        lunci_hao = len(self.lunci_dao.chaxun_an_renwu(renwu_id)) + 1
        if lunci_hao > int(renwu['lunshu']):
            return FanhuiJieguo.shibai_fanhui(CUOWU_ZHUANGTAI, '任务轮次已全部完成')
        canjiafang = self.canjia_dao.chaxun_an_renwu(renwu_id)
        gengxin_set = {x['yonghu_id'] for x in canjia_gengxin}
        if gengxin_set != {x['yonghu_id'] for x in canjiafang}:
            return FanhuiJieguo.shibai_fanhui(CUOWU_CANJIAFANG, '参与方更新不完整')
        if not self.yinsi_fuwu.jiancha_yusuan(renwu_id, float(renwu['yinsipi'])):
            return FanhuiJieguo.shibai_fanhui(CUOWU_YUSUAN, '隐私预算不足，训练停止')
        return None

    def _jiaguan_benlun(self, canjiafang: list[dict], gengxin_map: dict,
                        renwu: dict, suijishu: random.Random) -> list[dict]:
        """对本轮每个参与方的更新先裁剪再加噪。"""
        yinsipi = float(renwu['yinsipi'])
        jiancai_yuzhi = float(renwu['jiancai_yuzhi'])
        jieguo = []
        for canjia in canjiafang:
            gengxin = gengxin_map[canjia['yonghu_id']]['gengxin']
            jieguo.append({
                'gengxin': self.yinsi_fuwu.jiazao_gengxin(
                    gengxin, yinsipi, jiancai_yuzhi, suijishu
                ),
                'yangben_shu': int(canjia['yangben_shu']),
            })
        return jieguo

    @staticmethod
    def _jihe_zhibiao(canjiafang: list[dict], gengxin_map: dict) -> tuple:
        """按样本数加权汇总损失和准确率，耗时取最大值。"""
        zong_yangben = sum(int(c['yangben_shu']) for c in canjiafang)
        sunshi = sum(
            gengxin_map[c['yonghu_id']].get('sunshi', 0.0) * c['yangben_shu']
            for c in canjiafang
        ) / zong_yangben
        zhunquelv = sum(
            gengxin_map[c['yonghu_id']].get('zhunquelv', 0.0) * c['yangben_shu']
            for c in canjiafang
        ) / zong_yangben
        haoshi = max(
            gengxin_map[c['yonghu_id']].get('haoshi', 0.0) for c in canjiafang
        )
        return sunshi, zhunquelv, haoshi

    def _jieshu_lunci(self, renwu: dict, lunci_hao: int,
                      canjiafang: list[dict]) -> str:
        """更新任务和参与方状态，返回本轮结束后的任务状态。"""
        zhuangtai = 'yiwancheng' if lunci_hao == int(renwu['lunshu']) else 'xunlianzhong'
        if zhuangtai == 'yiwancheng':
            self.renwu_dao.gengxin_zhuangtai(renwu['id'], 'yiwancheng')
        for canjia in canjiafang:
            self.canjia_dao.gengxin_zhuangtai(
                renwu['id'], canjia['yonghu_id'], zhuangtai,
            )
        return zhuangtai

    def juhe_canshu(self, renwu_id: int,
                    gengxin_list: list[dict]) -> list[float]:
        """按样本数加权平均各参与方的模型更新。"""
        if self.renwu_dao.chaxun_an_id(renwu_id) is None:
            raise ValueError('任务不存在')
        if not gengxin_list:
            raise ValueError('没有可以聚合的更新')
        weidu = len(gengxin_list[0]['gengxin'])
        for xiang in gengxin_list:
            if len(xiang['gengxin']) != weidu or xiang['yangben_shu'] <= 0:
                raise ValueError('参与方更新维度或样本数不合法')
        zong_yangben = sum(x['yangben_shu'] for x in gengxin_list)
        jieguo = []
        for i in range(weidu):
            jiaquan_he = sum(
                x['gengxin'][i] * x['yangben_shu'] for x in gengxin_list
            )
            jieguo.append(jiaquan_he / zong_yangben)
        return jieguo

    def chaxun_zhuangtai(self, renwu_id: int) -> FanhuiJieguo:
        """查询任务状态、轮次指标和隐私预算使用情况。"""
        renwu = self.renwu_dao.chaxun_an_id(renwu_id)
        if renwu is None:
            return FanhuiJieguo.shibai_fanhui(CUOWU_ZHUANGTAI, '任务不存在')
        lunci = self.lunci_dao.chaxun_an_renwu(renwu_id)
        leiji = self.yinsi_fuwu.chaxun_leiji(renwu_id)
        return FanhuiJieguo.chenggong_fanhui({
            'renwu_id': renwu_id,
            'mingcheng': renwu['mingcheng'],
            'zhuangtai': renwu['zhuangtai'],
            'zong_lunshu': renwu['lunshu'],
            'yiwancheng_lunshu': len(lunci),
            'lunci': lunci,
            'leiji_eps': leiji,
            'shengyu_yusuan': float(renwu['yusuan_shangxian']) - leiji,
        })

    def _jiancha_renwu_canshu(self, mingcheng: str, canjia_list: list[dict],
                              lunshu: int, piliang_daxiao: int, xuexilv: float,
                              yinsipi: float, jiancai_yuzhi: float,
                              yusuan_shangxian: float) -> FanhuiJieguo | None:
        """创建任务前的参数校验。"""
        if not mingcheng.strip():
            return FanhuiJieguo.shibai_fanhui(CUOWU_CANSHU, '任务名称不能为空')
        if lunshu <= 0 or piliang_daxiao <= 0 or xuexilv <= 0:
            return FanhuiJieguo.shibai_fanhui(
                CUOWU_CANSHU, '轮数、批大小和学习率必须为正数'
            )
        if yinsipi <= 0 or jiancai_yuzhi <= 0 or yusuan_shangxian <= 0:
            return FanhuiJieguo.shibai_fanhui(CUOWU_CANSHU, '隐私参数必须为正数')
        if not canjia_list:
            return FanhuiJieguo.shibai_fanhui(CUOWU_CANJIAFANG, '至少需要一个参与方')
        yonghu_set = set()
        for canjia in canjia_list:
            if not {'yonghu_id', 'shujuji_id', 'yangben_shu'} <= set(canjia):
                return FanhuiJieguo.shibai_fanhui(CUOWU_CANSHU, '参与方字段不完整')
            if canjia['yangben_shu'] <= 0:
                return FanhuiJieguo.shibai_fanhui(CUOWU_CANSHU, '参与方样本数必须为正数')
            if canjia['yonghu_id'] in yonghu_set:
                return FanhuiJieguo.shibai_fanhui(CUOWU_CANJIAFANG, '同一参与方不能重复')
            yonghu_set.add(canjia['yonghu_id'])
        return None

    def _baocun_canshu(self, renwu_id: int, lunci_hao: int,
                       canshu: list[float]) -> str:
        """把全局参数写入文件，数据库只保存相对路径。"""
        mulu = self.canshu_mulu / str(renwu_id)
        mulu.mkdir(parents=True, exist_ok=True)
        lujing = mulu / ('lunci_%d.json' % lunci_hao)
        lujing.write_text(json.dumps(canshu, ensure_ascii=False), encoding='utf-8')
        return '%d/lunci_%d.json' % (renwu_id, lunci_hao)
