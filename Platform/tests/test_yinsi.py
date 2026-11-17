"""差分隐私服务：裁剪、加噪与预算检查。"""

import math
import random
import unittest

from backend.db import YewuCuowu
from backend.services import yinsi_fuwu


class JiancaiTest(unittest.TestCase):
    def test_fanshu_weichao_shibao_liu(self):
        xiangliang = [0.3, 0.4]
        self.assertEqual(yinsi_fuwu.jiancai(xiangliang, 1.0), xiangliang)

    def test_fanshu_chaoxian_beisuodao_yuzhi(self):
        jieguo = yinsi_fuwu.jiancai([3.0, 4.0], 1.0)
        self.assertAlmostEqual(math.dist(jieguo, [0, 0]), 1.0, places=9)
        self.assertAlmostEqual(jieguo[0], 0.6, places=9)
        self.assertAlmostEqual(jieguo[1], 0.8, places=9)

    def test_ling_xiangliang_baochi_bubian(self):
        self.assertEqual(yinsi_fuwu.jiancai([0.0, 0.0, 0.0], 1.0),
                         [0.0, 0.0, 0.0])

    def test_fu_shu_fanshu_yi_yang(self):
        jieguo = yinsi_fuwu.jiancai([-3.0, 0.0], 2.0)
        self.assertAlmostEqual(abs(jieguo[0]), 2.0, places=9)


class JiazaoTest(unittest.TestCase):
    def test_weidu_bubian(self):
        jieguo = yinsi_fuwu.jiazao([0.1] * 8, 0.5, 1.0,
                                   random.Random(7))
        self.assertEqual(len(jieguo), 8)
        self.assertNotEqual(jieguo, [0.1] * 8)

    def test_gaowei_zaosheng_an_weidu_jun_tan(self):
        jieguo = yinsi_fuwu.jiagong_gaowei([0.0] * 178, 0.5, 1.0,
                                           random.Random(3))
        self.assertEqual(len(jieguo), 178)
        self.assertLess(max(abs(x) for x in jieguo), 2.0)

    def test_yinsipi_buhefa_pao_yewu_cuowu(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            yinsi_fuwu.jiazao([0.1], 0.0, 1.0)
        self.assertEqual(qingjing.exception.cuowu_ma, 4005)


class YusuanTest(unittest.TestCase):
    def test_leiji_weichao_shangxian(self):
        self.assertAlmostEqual(
            yinsi_fuwu.jiancha_yusuan(1.0, 0.5, 5.0), 1.5)

    def test_ganghao_da_shangxian_yunxu(self):
        self.assertAlmostEqual(
            yinsi_fuwu.jiancha_yusuan(4.5, 0.5, 5.0), 5.0)

    def test_chaochu_shangxian_pao_4001(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            yinsi_fuwu.jiancha_yusuan(4.8, 0.5, 5.0)
        self.assertEqual(qingjing.exception.cuowu_ma, 4001)

    def test_zonglan_shengyu_yu_shiyonglv(self):
        zonglan = yinsi_fuwu.yusuan_zonglan(
            {'yusuan_shangxian': 5.0, 'yinsipi': 0.5, 'jiancai_yuzhi': 1.0},
            2.0)
        self.assertAlmostEqual(zonglan['shengyu'], 3.0)
        self.assertAlmostEqual(zonglan['shiyong_lv'], 0.4)
        self.assertEqual(zonglan['ke_xunlian_lunshu'], 10)

    def test_ke_xunlian_lunshu_xiangxia_quzheng(self):
        self.assertEqual(yinsi_fuwu.ke_xunlian_lunshu(5.0, 0.5), 10)
        self.assertEqual(yinsi_fuwu.ke_xunlian_lunshu(2.5, 0.5), 5)
        self.assertEqual(yinsi_fuwu.ke_xunlian_lunshu(2.4, 0.5), 4)

    def test_ke_xunlian_lunshu_eps_buhefa_pao_4005(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            yinsi_fuwu.ke_xunlian_lunshu(5.0, 0.0)
        self.assertEqual(qingjing.exception.cuowu_ma, 4005)


if __name__ == '__main__':
    unittest.main()
