"""数据集服务：格式校验、登记、停用与可见范围。"""

import unittest
import uuid

from backend import dao
from backend.db import YewuCuowu
from backend.schemas import ShujuJiaoyanRuku, ShujujiRuku
from backend.services import shuju_fuwu

_ZIDUAN = [f'f{i}' for i in range(1, 9)] + ['label']


def _ming():
    return 'ceshi_shuju_' + uuid.uuid4().hex[:6]


def _tigong(ming='tigong1'):
    return dao.yonghu_an_ming(ming)


class JiaoyanTest(unittest.TestCase):
    def test_hefa_ziduan_tongguo(self):
        jieguo = shuju_fuwu.jiaoyan(ShujuJiaoyanRuku(
            ziduan=_ZIDUAN, yangben_shu=5000, geshi='csv'))
        self.assertTrue(jieguo['tongguo'])

    def test_queshao_biaozhun_ziduan_bu_tongguo(self):
        jieguo = shuju_fuwu.jiaoyan(ShujuJiaoyanRuku(
            ziduan=[f'f{i}' for i in range(1, 9)], yangben_shu=5000,
            geshi='csv', biaozhun_ziduan=['label']))
        self.assertFalse(jieguo['tongguo'])
        self.assertIn('label', jieguo['jielun'])

    def test_ziduan_kong_bu_tongguo(self):
        jieguo = shuju_fuwu.jiaoyan(ShujuJiaoyanRuku(
            ziduan=[], yangben_shu=10, geshi='csv'))
        self.assertFalse(jieguo['tongguo'])

    def test_ziduan_han_feifa_zifu_bu_tongguo(self):
        jieguo = shuju_fuwu.jiaoyan(ShujuJiaoyanRuku(
            ziduan=['a b', 'c-d'], yangben_shu=10, geshi='csv'))
        self.assertFalse(jieguo['tongguo'])


class DengjiTest(unittest.TestCase):
    def test_tigongfang_dengji_chenggong(self):
        ming = _ming()
        jieguo = shuju_fuwu.dengji(_tigong(), ShujujiRuku(
            mingcheng=ming, geshi='csv', daxiao=1_000_000,
            yangben_shu=5000, ziduan=_ZIDUAN))
        self.assertEqual(jieguo['zhuangtai'], 'yijiaoyan')
        self.assertIn('yijiaoyan', jieguo['zhuangtai'])
        self.assertIn('5000', jieguo['jiaoyan_jielun'])

    def test_shiyongfang_dengji_pao_4030(self):
        shiyong = dao.yonghu_an_ming('shiyong1')
        with self.assertRaises(YewuCuowu) as qingjing:
            shuju_fuwu.dengji(shiyong, ShujujiRuku(
                mingcheng=_ming(), geshi='csv', daxiao=1000,
                yangben_shu=100, ziduan=_ZIDUAN))
        self.assertEqual(qingjing.exception.cuowu_ma, 4030)

    def test_tongming_shujuji_pao_4006(self):
        ming = _ming()
        shuru = ShujujiRuku(mingcheng=ming, geshi='csv', daxiao=1000,
                            yangben_shu=100, ziduan=_ZIDUAN)
        shuju_fuwu.dengji(_tigong(), shuru)
        with self.assertRaises(YewuCuowu) as qingjing:
            shuju_fuwu.dengji(_tigong(), shuru)
        self.assertEqual(qingjing.exception.cuowu_ma, 4006)


class ZhuangtaiTest(unittest.TestCase):
    def setUp(self):
        self.shuju = shuju_fuwu.dengji(_tigong(), ShujujiRuku(
            mingcheng=_ming(), geshi='csv', daxiao=1000,
            yangben_shu=100, ziduan=_ZIDUAN))

    def test_bieren_buneng_tingyong(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            shuju_fuwu.gengxin_zhuangtai(
                _tigong('tigong2'), self.shuju['id'], 'yitingyong')
        self.assertEqual(qingjing.exception.cuowu_ma, 4030)

    def test_tingyong_hou_shiyongfang_kan_budao(self):
        shuju_fuwu.gengxin_zhuangtai(
            _tigong(), self.shuju['id'], 'yitingyong')
        liebiao = shuju_fuwu.liechu(dao.yonghu_an_ming('shiyong1'))
        bianhao = [x['id'] for x in liebiao['items']]
        self.assertNotIn(self.shuju['id'], bianhao)

    def test_huifu_hou_chongxin_keyong(self):
        shuju_fuwu.gengxin_zhuangtai(
            _tigong(), self.shuju['id'], 'yitingyong')
        jieguo = shuju_fuwu.gengxin_zhuangtai(
            _tigong(), self.shuju['id'], 'yijiaoyan')
        self.assertEqual(jieguo['zhuangtai'], 'yijiaoyan')

    def test_feifa_zhuangtai_pao_4005(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            shuju_fuwu.gengxin_zhuangtai(
                _tigong(), self.shuju['id'], 'suibian')
        self.assertEqual(qingjing.exception.cuowu_ma, 4005)

    def test_shiyongfang_kan_budao_benzhi_lujing(self):
        jieguo = shuju_fuwu.qu(
            dao.yonghu_an_ming('shiyong1'), self.shuju['id'])
        self.assertNotIn('benzhi_lujing', jieguo)
        self.assertNotIn('tuomin_guize', jieguo)
        ziji = shuju_fuwu.qu(_tigong(), self.shuju['id'])
        self.assertIn('benzhi_lujing', ziji)


if __name__ == '__main__':
    unittest.main()
