"""NumPy MLP：参数序列化、前向传播与单轮训练。"""

import unittest

import numpy as np

from backend.federated import shuju
from backend.federated.moxing import MlpMoxing


class MoxingTest(unittest.TestCase):
    def setUp(self):
        self.moxing = MlpMoxing(zhongzi=42)

    def test_canshu_weidu_178(self):
        self.assertEqual(self.moxing.weidu, 178)
        self.assertEqual(len(self.moxing.qu_canshu()), 178)

    def test_canshu_qu_she_wangfan_yizhi(self):
        suijishu = np.random.default_rng(1)
        canshu = suijishu.normal(0, 0.5, self.moxing.weidu)
        self.moxing.she_canshu(canshu)
        np.testing.assert_allclose(self.moxing.qu_canshu(), canshu)

    def test_weidu_budui_pao_value_error(self):
        with self.assertRaises(ValueError):
            self.moxing.she_canshu([0.0] * 10)

    def test_qianxiang_gailv_hewei_yi(self):
        X, _ = shuju.shengcheng(32, 5)
        gailv = self.moxing.yuce(X)
        self.assertEqual(gailv.shape, (32, 2))
        np.testing.assert_allclose(gailv.sum(axis=1), np.ones(32), atol=1e-9)

    def test_sunshi_yu_zhunquelv_qujian(self):
        X, y = shuju.shengcheng(64, 6)
        self.assertGreaterEqual(self.moxing.sunshi(X, y), 0.0)
        self.assertGreaterEqual(self.moxing.zhunquelv(X, y), 0.0)
        self.assertLessEqual(self.moxing.zhunquelv(X, y), 1.0)

    def test_xunlian_yilun_jiejiang_sunshi(self):
        X, y = shuju.shengcheng(256, 8)
        Xxun, yxun, Xce, yce = shuju.chaiFen(X, y)
        qian = self.moxing.sunshi(Xce, yce)
        for _ in range(5):
            self.moxing.xunlian_yilun(Xxun, yxun, 0.1, 16,
                                      np.random.default_rng(9))
        hou = self.moxing.sunshi(Xce, yce)
        self.assertLess(hou, qian)


if __name__ == '__main__':
    unittest.main()
