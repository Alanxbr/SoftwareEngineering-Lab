"""系统管理：概览、账号、任务、日志与备份。"""

import unittest
from datetime import date

from backend import dao
from backend.db import YewuCuowu
from backend.schemas import CanjiafangRuku, RenwuRuku
from backend.services import guanli_fuwu, xunlian_fuwu


def _yonghu(ming):
    return dao.yonghu_an_ming(ming)


def _shujuji(mingcheng):
    for xiang in dao.shujuji_liechu(None, True, 1, 100)['items']:
        if xiang['mingcheng'] == mingcheng:
            return xiang['id']
    raise AssertionError(mingcheng)


def _jian_renwu(ming='管理测试任务'):
    return xunlian_fuwu.chuangjian(_yonghu('shiyong1'), RenwuRuku(
        mingcheng=ming, moxing_leixing='mlp_8_16_2', lunshu=2,
        piliang_daxiao=16, xuexilv=0.05, yinsipi=0.5, jiancai_yuzhi=1.0,
        yusuan_shangxian=2.0, yunxing_moshi='moni',
        canjia=[CanjiafangRuku(shujuji_id=_shujuji('医疗影像特征集')),
                CanjiafangRuku(shujuji_id=_shujuji('金融风控特征集'))]))


class ZonglanTest(unittest.TestCase):
    def test_sanzhong_jiaose_gezi_zonglan(self):
        guanli = guanli_fuwu.zonglan(_yonghu('admin'))
        self.assertEqual(guanli['jiaose'], 'guanliyuan')
        self.assertIn('rizhi', guanli)
        tigong = guanli_fuwu.zonglan(_yonghu('tigong1'))
        self.assertEqual(tigong['jiaose'], 'tigongfang')
        shiyong = guanli_fuwu.zonglan(_yonghu('shiyong1'))
        self.assertEqual(shiyong['jiaose'], 'shiyongfang')


class QuanxianTest(unittest.TestCase):
    def test_feiguanliyuan_jujue(self):
        shiyong = _yonghu('shiyong1')
        dongzuo = [
            lambda: guanli_fuwu.yonghu_liechu(shiyong, 1, 20),
            lambda: guanli_fuwu.renwu_liechu(shiyong, '', 1, 20),
            lambda: guanli_fuwu.rizhi(shiyong, '', '', '', '', '', 1, 20),
            lambda: guanli_fuwu.beifen_liechu(shiyong),
        ]
        for dongzuo_xiang in dongzuo:
            with self.assertRaises(YewuCuowu) as qingjing:
                dongzuo_xiang()
            self.assertEqual(qingjing.exception.cuowu_ma, 4030)


class RenwuGuanliTest(unittest.TestCase):
    def test_guanliyuan_quxiao_daichufa_renwu(self):
        renwu = _jian_renwu()
        jieguo = guanli_fuwu.renwu_gengxin(
            _yonghu('admin'), renwu['id'], 'yiquxiao', '测试取消')
        self.assertEqual(jieguo['zhuangtai'], 'yiquxiao')

    def test_yijieshu_renwu_buneng_zaigai(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            guanli_fuwu.renwu_gengxin(
                _yonghu('admin'), 1, 'yichang', '重复操作')
        self.assertEqual(qingjing.exception.cuowu_ma, 4004)

    def test_renwu_bucunzai_pao_4040(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            guanli_fuwu.renwu_gengxin(
                _yonghu('admin'), 999_999, 'yiquxiao', '不存在')
        self.assertEqual(qingjing.exception.cuowu_ma, 4040)


class BeifenTest(unittest.TestCase):
    def test_chuangjian_liechu_yu_lujing_jiaoyan(self):
        guanli = _yonghu('admin')
        xinjian = guanli_fuwu.beifen(guanli)
        self.assertGreater(xinjian['daxiao'], 0)
        liebiao = guanli_fuwu.beifen_liechu(guanli)
        self.assertIn(xinjian['wenjian'], [x['wenjian'] for x in liebiao])
        lujing = guanli_fuwu.beifen_lujing(guanli, xinjian['wenjian'])
        self.assertTrue(lujing.exists())

    def test_mulu_chuanyue_pao_4040(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            guanli_fuwu.beifen_lujing(_yonghu('admin'), '../pingtai.db')
        self.assertEqual(qingjing.exception.cuowu_ma, 4040)


class RizhiTest(unittest.TestCase):
    def test_an_leixing_guolv(self):
        jieguo = guanli_fuwu.rizhi(_yonghu('admin'), '用户登录', '', '', '', '',
                                   1, 50)
        self.assertGreaterEqual(jieguo['total'], 1)
        self.assertTrue(all(x['caozuo_leixing'] == '用户登录'
                            for x in jieguo['items']))

    def test_jieshu_riqi_baohan_dangtian(self):
        jintian = date.today().isoformat()
        jieguo = guanli_fuwu.rizhi(_yonghu('admin'), '', '', '', '', jintian,
                                   1, 50)
        self.assertGreaterEqual(jieguo['total'], 1)


if __name__ == '__main__':
    unittest.main()
