"""本地数据：合成数据、划分与 CSV 读取。"""

import tempfile
import unittest
from pathlib import Path

import numpy as np

from backend.federated import shuju


class ShujuTest(unittest.TestCase):
    def test_shengcheng_xingzhuang_yu_biaoqian(self):
        X, y = shuju.shengcheng(100, 12)
        self.assertEqual(X.shape, (100, 8))
        self.assertEqual(y.shape, (100,))
        self.assertTrue(set(np.unique(y)).issubset({0, 1}))

    def test_zhongzi_xiangtong_jieguo_xiangtong(self):
        X1, y1 = shuju.shengcheng(50, 99)
        X2, y2 = shuju.shengcheng(50, 99)
        np.testing.assert_array_equal(X1, X2)
        np.testing.assert_array_equal(y1, y2)

    def test_chaiFen_an_8_bi_2(self):
        X, y = shuju.shengcheng(100, 3)
        Xxun, yxun, Xce, yce = shuju.chaiFen(X, y)
        self.assertEqual(len(Xxun), 80)
        self.assertEqual(len(Xce), 20)

    def test_jiazai_csv_du_qu_yu_buqi(self):
        with tempfile.TemporaryDirectory() as mulu:
            lujing = Path(mulu) / 'a.csv'
            lujing.write_text(
                '1,2,3,0\n4,5,6,1\n7,8,9,0\n', encoding='utf-8')
            X, y = shuju.jiazai_csv(lujing)
            self.assertEqual(X.shape, (3, 8))
            self.assertEqual(list(y), [0, 1, 0])
            self.assertEqual(float(X[0, 0]), 1.0)

    def test_jiazai_csv_wenjian_bucunzai(self):
        with self.assertRaises(FileNotFoundError):
            shuju.jiazai_csv('D:/not_exists/x.csv')

    def test_jiazai_csv_kong_wenjian(self):
        with tempfile.TemporaryDirectory() as mulu:
            lujing = Path(mulu) / 'kong.csv'
            lujing.write_text('a,b,c\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                shuju.jiazai_csv(lujing)


if __name__ == '__main__':
    unittest.main()
