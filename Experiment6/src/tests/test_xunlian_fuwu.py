"""联邦训练模块的单元测试。"""

import math
import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from zhuangpei import Zhuangpei  # noqa: E402


class XunlianFuwuTest(unittest.TestCase):
    """覆盖聚合、裁剪、预算和状态流转。"""

    def setUp(self) -> None:
        self.linshi = tempfile.TemporaryDirectory()
        mulu = Path(self.linshi.name)
        self.zhuangpei = Zhuangpei(str(mulu / 'test.db'), str(mulu / 'canshu'))
        self.tigong_yi = self.zhuangpei.yonghu_dao.charru(
            'tigong_yi', 'hash', 'a@example.com', 'tigongfang'
        )
        self.tigong_er = self.zhuangpei.yonghu_dao.charru(
            'tigong_er', 'hash', 'b@example.com', 'tigongfang'
        )
        self.shiyong = self.zhuangpei.yonghu_dao.charru(
            'shiyong', 'hash', 'c@example.com', 'shiyongfang'
        )
        self.shuju_yi = self.zhuangpei.shuju_fuwu.dengji_shujuji(
            self.tigong_yi, 'yiliao_yangben', 'csv', 102400, 800
        ).shuju['shujuji_id']
        self.shuju_er = self.zhuangpei.shuju_fuwu.dengji_shujuji(
            self.tigong_er, 'jinrong_yangben', 'csv', 51200, 200
        ).shuju['shujuji_id']

    def tearDown(self) -> None:
        self.zhuangpei.guanbi()
        self.linshi.cleanup()

    def _chuangjian_renwu(self, **xiugai):
        canshu = {
            'chuangjianzhe_id': self.shiyong,
            'mingcheng': 'xinpian_fenlei',
            'canjia_list': [
                {'yonghu_id': self.tigong_yi, 'shujuji_id': self.shuju_yi,
                 'yangben_shu': 800},
                {'yonghu_id': self.tigong_er, 'shujuji_id': self.shuju_er,
                 'yangben_shu': 200},
            ],
            'lunshu': 3,
            'piliang_daxiao': 32,
            'xuexilv': 0.01,
            'yinsipi': 0.5,
            'jiancai_yuzhi': 1.0,
            'yusuan_shangxian': 2.0,
        }
        canshu.update(xiugai)
        return self.zhuangpei.xunlian_fuwu.chuangjian_renwu(**canshu)

    def _canjia_gengxin(self) -> list[dict]:
        return [
            {'yonghu_id': self.tigong_yi, 'gengxin': [0.2, -0.4, 0.1, 0.3],
             'sunshi': 0.8, 'zhunquelv': 0.7, 'haoshi': 1.0},
            {'yonghu_id': self.tigong_er, 'gengxin': [-0.1, 0.2, 0.5, -0.2],
             'sunshi': 0.6, 'zhunquelv': 0.8, 'haoshi': 0.8},
        ]

    def test_jiaquan_juhe(self) -> None:
        renwu_id = self._chuangjian_renwu().shuju['renwu_id']
        jieguo = self.zhuangpei.xunlian_fuwu.juhe_canshu(renwu_id, [
            {'gengxin': [2.0, 4.0], 'yangben_shu': 1},
            {'gengxin': [4.0, 0.0], 'yangben_shu': 3},
        ])
        self.assertEqual(jieguo, [3.5, 1.0])

    def test_jiancai_baozheng_fanzhi(self) -> None:
        jiancai = self.zhuangpei.yinsi_fuwu.jiancai_gengxin([3.0, 4.0], 1.0)
        self.assertAlmostEqual(math.sqrt(sum(x * x for x in jiancai)), 1.0)

    def test_jiazao_ke_chongfu(self) -> None:
        yi = self.zhuangpei.yinsi_fuwu.jiazao_gengxin([0.6, 0.8], 0.5, 1.0, random.Random(7))
        er = self.zhuangpei.yinsi_fuwu.jiazao_gengxin([0.6, 0.8], 0.5, 1.0, random.Random(7))
        self.assertEqual(yi, er)
        self.assertNotEqual(yi, [0.6, 0.8])

    def test_yusuan_buzu_shibai(self) -> None:
        renwu_id = self._chuangjian_renwu(lunshu=2, yusuan_shangxian=0.5).shuju['renwu_id']
        self.assertTrue(self.zhuangpei.xunlian_fuwu.qidong_xunlian(renwu_id).chenggong)
        self.assertTrue(
            self.zhuangpei.xunlian_fuwu.zhixing_lunci(renwu_id, self._canjia_gengxin()).chenggong
        )
        jieguo = self.zhuangpei.xunlian_fuwu.zhixing_lunci(renwu_id, self._canjia_gengxin())
        self.assertFalse(jieguo.chenggong)
        self.assertEqual(jieguo.cuowu_ma, 4001)

    def test_shujuji_tingyong_hou_qidong_shibai(self) -> None:
        renwu_id = self._chuangjian_renwu().shuju['renwu_id']
        self.zhuangpei.shuju_fuwu.tingyong_shujuji(self.shuju_er)
        jieguo = self.zhuangpei.xunlian_fuwu.qidong_xunlian(renwu_id)
        self.assertFalse(jieguo.chenggong)
        self.assertEqual(jieguo.cuowu_ma, 4002)

    def test_wanzheng_yilun(self) -> None:
        renwu_id = self._chuangjian_renwu(lunshu=1).shuju['renwu_id']
        self.zhuangpei.xunlian_fuwu.qidong_xunlian(renwu_id)
        jieguo = self.zhuangpei.xunlian_fuwu.zhixing_lunci(
            renwu_id, self._canjia_gengxin(), random.Random(3)
        )
        self.assertTrue(jieguo.chenggong)
        self.assertEqual(jieguo.shuju['zhuangtai'], 'yiwancheng')
        self.assertAlmostEqual(jieguo.shuju['shengyu_yusuan'], 1.5)
        self.assertTrue(
            (self.zhuangpei.xunlian_fuwu.canshu_mulu / str(renwu_id) / 'lunci_1.json').is_file()
        )
        zhuangtai = self.zhuangpei.xunlian_fuwu.chaxun_zhuangtai(renwu_id)
        self.assertEqual(zhuangtai.shuju['yiwancheng_lunshu'], 1)

    def test_chongfu_shujuji_mingcheng(self) -> None:
        jieguo = self.zhuangpei.shuju_fuwu.dengji_shujuji(
            self.tigong_yi, 'yiliao_yangben', 'csv', 1024, 10
        )
        self.assertFalse(jieguo.chenggong)
        self.assertEqual(jieguo.cuowu_ma, 4006)

    def test_canjiafang_gengxin_bu_wanzheng(self) -> None:
        renwu_id = self._chuangjian_renwu().shuju['renwu_id']
        self.zhuangpei.xunlian_fuwu.qidong_xunlian(renwu_id)
        jieguo = self.zhuangpei.xunlian_fuwu.zhixing_lunci(
            renwu_id, self._canjia_gengxin()[:1]
        )
        self.assertFalse(jieguo.chenggong)
        self.assertEqual(jieguo.cuowu_ma, 4003)


if __name__ == '__main__':
    unittest.main()
