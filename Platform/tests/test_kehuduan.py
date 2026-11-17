"""参与方中心：领取全局参数、提交更新与轮次推进。"""

import time
import unittest

from backend import dao
from backend.db import YewuCuowu
from backend.schemas import CanjiafangRuku, KehuduanGengxinRuku, RenwuRuku
from backend.services import kehuduan_fuwu, xunlian_fuwu

WEIDU = 178


def _yonghu(ming):
    return dao.yonghu_an_ming(ming)


def _shujuji(mingcheng):
    for xiang in dao.shujuji_liechu(None, True, 1, 100)['items']:
        if xiang['mingcheng'] == mingcheng:
            return xiang['id']
    raise AssertionError(mingcheng)


class ZhenshiMoshiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renwu = xunlian_fuwu.chuangjian(_yonghu('shiyong1'), RenwuRuku(
            mingcheng='真实模式联调任务', moxing_leixing='mlp_8_16_2', lunshu=1,
            piliang_daxiao=16, xuexilv=0.05, yinsipi=0.5, jiancai_yuzhi=1.0,
            yusuan_shangxian=2.0, yunxing_moshi='zhenshi',
            canjia=[CanjiafangRuku(shujuji_id=_shujuji('医疗影像特征集')),
                    CanjiafangRuku(shujuji_id=_shujuji('金融风控特征集'))]))
        xunlian_fuwu.qidong(_yonghu('shiyong1'), cls.renwu['id'])
        cls.renwu_id = cls.renwu['id']

    def _deng_lunci(self, huan=60):
        for _ in range(huan):
            renwu = dao.renwu_an_id(self.renwu_id)
            if int(renwu['dangqian_lunci']) >= 1:
                return renwu
            time.sleep(0.1)
        raise AssertionError('协调器未进入第 1 轮')

    def test_01_lingqu_quanju_canshu(self):
        renwu = self._deng_lunci()
        zhuangtai = kehuduan_fuwu.zhuangtai(_yonghu('tigong1'), self.renwu_id)
        self.assertEqual(zhuangtai['dangqian_lunci'], 1)
        self.assertEqual(len(zhuangtai['canshu']), WEIDU)
        self.assertFalse(zhuangtai['yijing_tijiao'])
        self.assertEqual(zhuangtai['zhuangtai'], renwu['zhuangtai'])

    def test_02_weidu_cuowu_pao_4005(self):
        self._deng_lunci()
        with self.assertRaises(YewuCuowu) as qingjing:
            kehuduan_fuwu.tijiao(_yonghu('tigong1'), self.renwu_id,
                                 KehuduanGengxinRuku(
                                     lunci_hao=1, gengxin=[0.1] * 10,
                                     yangben_shu=100))
        self.assertEqual(qingjing.exception.cuowu_ma, 4005)

    def test_03_feicanshi_pao_4030(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            kehuduan_fuwu.tijiao(_yonghu('shiyong2'), self.renwu_id,
                                 KehuduanGengxinRuku(
                                     lunci_hao=1, gengxin=[0.0] * WEIDU,
                                     yangben_shu=100))
        self.assertEqual(qingjing.exception.cuowu_ma, 4030)

    def test_04_shuangfang_tijiao_hou_wan_cheng(self):
        self._deng_lunci()
        for ming, yangben in (('tigong1', 12000), ('tigong2', 8600)):
            kehuduan_fuwu.tijiao(_yonghu(ming), self.renwu_id,
                                 KehuduanGengxinRuku(
                                     lunci_hao=1, gengxin=[0.01] * WEIDU,
                                     yangben_shu=yangben, sunshi=0.5,
                                     zhunquelv=0.7, haoshi=0.1))
        for _ in range(100):
            renwu = dao.renwu_an_id(self.renwu_id)
            if renwu['zhuangtai'] == 'yiwancheng':
                break
            time.sleep(0.1)
        self.assertEqual(renwu['zhuangtai'], 'yiwancheng')
        self.assertEqual(len(dao.lunci_liechu(self.renwu_id)), 1)

    def test_05_yijieshu_hou_tijiao_pao_4004(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            kehuduan_fuwu.tijiao(_yonghu('tigong1'), 1,
                                 KehuduanGengxinRuku(
                                     lunci_hao=1, gengxin=[0.0] * WEIDU,
                                     yangben_shu=100))
        self.assertEqual(qingjing.exception.cuowu_ma, 4004)

    def test_06_renwu_bucunzai_pao_4040(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            kehuduan_fuwu.zhuangtai(_yonghu('tigong1'), 999_999)
        self.assertEqual(qingjing.exception.cuowu_ma, 4040)


if __name__ == '__main__':
    unittest.main()
