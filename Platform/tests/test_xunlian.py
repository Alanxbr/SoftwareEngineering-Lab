"""训练服务：建任务校验、启动权限、曲线与隐私预算。"""

import unittest

from backend import dao
from backend.db import YewuCuowu
from backend.schemas import CanjiafangRuku, RenwuRuku
from backend.services import xunlian_fuwu


def _yonghu(ming):
    return dao.yonghu_an_ming(ming)


def _shujuji_id(mingcheng):
    for xiang in dao.shujuji_liechu(None, True, 1, 100)['items']:
        if xiang['mingcheng'] == mingcheng:
            return xiang['id']
    raise AssertionError(f'演示数据缺少数据集：{mingcheng}')


def _renwu(**gaidong):
    jichu = dict(
        mingcheng='单元测试任务', moxing_leixing='mlp_8_16_2', lunshu=2,
        piliang_daxiao=16, xuexilv=0.05, yinsipi=0.5, jiancai_yuzhi=1.0,
        yusuan_shangxian=3.0, yunxing_moshi='moni',
        canjia=[CanjiafangRuku(shujuji_id=_shujuji_id('医疗影像特征集')),
                CanjiafangRuku(shujuji_id=_shujuji_id('金融风控特征集'))],
    )
    jichu.update(gaidong)
    return RenwuRuku(**jichu)


class ChuangjianTest(unittest.TestCase):
    def test_zhengchang_chuangjian(self):
        jieguo = xunlian_fuwu.chuangjian(_yonghu('shiyong1'), _renwu())
        self.assertEqual(jieguo['zhuangtai'], 'daichufa')
        self.assertEqual(len(jieguo['canjiafang']), 2)
        yangben = sorted(x['yangben_shu'] for x in jieguo['canjiafang'])
        self.assertEqual(yangben, [8600, 12000])

    def test_tigongfang_chuangjian_pao_4030(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.chuangjian(_yonghu('tigong1'), _renwu())
        self.assertEqual(qingjing.exception.cuowu_ma, 4030)

    def test_tongyi_tigongfang_liangci_pao_4003(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.chuangjian(_yonghu('shiyong1'), _renwu(
                canjia=[CanjiafangRuku(shujuji_id=_shujuji_id('医疗影像特征集')),
                        CanjiafangRuku(shujuji_id=_shujuji_id('零售消费行为特征集'))]))
        self.assertEqual(qingjing.exception.cuowu_ma, 4003)

    def test_yangben_shu_chaochu_pao_4005(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.chuangjian(_yonghu('shiyong1'), _renwu(
                canjia=[CanjiafangRuku(shujuji_id=_shujuji_id('医疗影像特征集'),
                                       yangben_shu=999_999)]))
        self.assertEqual(qingjing.exception.cuowu_ma, 4005)

    def test_yusuan_xiaoyu_danlun_eps_pao_4001(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.chuangjian(_yonghu('shiyong1'), _renwu(
                yinsipi=0.5, yusuan_shangxian=0.3))
        self.assertEqual(qingjing.exception.cuowu_ma, 4001)

    def test_shujuji_bucunzai_pao_4003(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.chuangjian(_yonghu('shiyong1'), _renwu(
                canjia=[CanjiafangRuku(shujuji_id=999_999)]))
        self.assertEqual(qingjing.exception.cuowu_ma, 4003)


class QidongTest(unittest.TestCase):
    def test_qidong_bucunzai_pao_4040(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.qidong(_yonghu('shiyong1'), 999_999)
        self.assertEqual(qingjing.exception.cuowu_ma, 4040)

    def test_feichuangjianzhe_qidong_pao_4030(self):
        renwu = xunlian_fuwu.chuangjian(_yonghu('shiyong1'), _renwu())
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.qidong(_yonghu('shiyong2'), renwu['id'])
        self.assertEqual(qingjing.exception.cuowu_ma, 4030)

    def test_yijieshu_renwu_chongfu_qidong_pao_4004(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.qidong(_yonghu('shiyong1'), 1)
        self.assertEqual(qingjing.exception.cuowu_ma, 4004)
        self.assertEqual(qingjing.exception.http_zhuangtai, 409)


class ChaxunTest(unittest.TestCase):
    def test_yanshi_renwu_you_5_lun_quxian(self):
        quxian = xunlian_fuwu.quxian(_yonghu('shiyong1'), 1)
        self.assertEqual(len(quxian['rounds']), 5)
        zhunquelv = [x['zhunquelv'] for x in quxian['rounds']]
        self.assertEqual(zhunquelv, sorted(zhunquelv))

    def test_quxian_bucunzai_pao_4040(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.quxian(_yonghu('shiyong1'), 999_999)
        self.assertEqual(qingjing.exception.cuowu_ma, 4040)

    def test_wuguan_yonghu_chakan_pao_4030(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            xunlian_fuwu.xiangqing(_yonghu('shiyong2'), 1)
        self.assertEqual(qingjing.exception.cuowu_ma, 4030)

    def test_yinsi_yusuan_dengyu_2_dian_5(self):
        yinsi = xunlian_fuwu.yinsi(_yonghu('shiyong1'), 1)
        self.assertAlmostEqual(yinsi['leiji_eps'], 2.5)
        self.assertAlmostEqual(yinsi['shengyu'], 0.5)


if __name__ == '__main__':
    unittest.main()
