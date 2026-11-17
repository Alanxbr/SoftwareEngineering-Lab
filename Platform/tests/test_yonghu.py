"""用户服务：注册、登录、停用与管理员操作。"""

import unittest
import uuid

from pydantic import ValidationError

from backend import dao
from backend.db import YewuCuowu
from backend.schemas import DengluRuku, ZhuceRuku
from backend.services import yonghu_fuwu


def _ming(prefix='ceshi'):
    return prefix + uuid.uuid4().hex[:6]


def _zhanghao(ming, jiaose='shiyongfang', mima='123456'):
    return ZhuceRuku(yonghuming=ming, mima=mima,
                     youxiang=f'{ming}@example.com', jiaose=jiaose)


def _guanliyuan():
    return dao.yonghu_an_ming('admin')


class ZhuceDengluTest(unittest.TestCase):
    def test_zhuce_hou_keyi_denglu(self):
        ming = _ming()
        jieguo = yonghu_fuwu.zhuce(_zhanghao(ming))
        self.assertEqual(jieguo['yonghuming'], ming)
        self.assertEqual(jieguo['zhuangtai'], 'zhengchang')
        denglu = yonghu_fuwu.denglu(DengluRuku(yonghuming=ming, mima='123456'))
        self.assertTrue(denglu['token'])
        self.assertNotIn('mima_hash', denglu['user'])

    def test_yonghuming_chongfu_pao_4006(self):
        ming = _ming()
        yonghu_fuwu.zhuce(_zhanghao(ming))
        with self.assertRaises(YewuCuowu) as qingjing:
            yonghu_fuwu.zhuce(_zhanghao(ming))
        self.assertEqual(qingjing.exception.cuowu_ma, 4006)
        self.assertEqual(qingjing.exception.http_zhuangtai, 409)

    def test_mima_tai_duan_bei_schema_jujue(self):
        with self.assertRaises(ValidationError):
            _zhanghao(_ming(), mima='123')

    def test_mima_shouwei_kongge_pao_4005(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            yonghu_fuwu.zhuce(_zhanghao(_ming(), mima=' 123456'))
        self.assertEqual(qingjing.exception.cuowu_ma, 4005)

    def test_mima_cuowu_pao_4010(self):
        ming = _ming()
        yonghu_fuwu.zhuce(_zhanghao(ming))
        with self.assertRaises(YewuCuowu) as qingjing:
            yonghu_fuwu.denglu(DengluRuku(yonghuming=ming, mima='654321'))
        self.assertEqual(qingjing.exception.cuowu_ma, 4010)
        self.assertEqual(qingjing.exception.http_zhuangtai, 401)

    def test_yonghu_bucunzai_pao_4010(self):
        with self.assertRaises(YewuCuowu) as qingjing:
            yonghu_fuwu.denglu(DengluRuku(yonghuming=_ming('wu'), mima='123456'))
        self.assertEqual(qingjing.exception.cuowu_ma, 4010)

    def test_tingyong_zhanghao_buneng_denglu(self):
        ming = _ming()
        yonghu_fuwu.zhuce(_zhanghao(ming))
        zhanghao = dao.yonghu_an_ming(ming)
        yonghu_fuwu.gengxin_zhuangtai(_guanliyuan(), zhanghao['id'], 'tingyong')
        with self.assertRaises(YewuCuowu) as qingjing:
            yonghu_fuwu.denglu(DengluRuku(yonghuming=ming, mima='123456'))
        self.assertEqual(qingjing.exception.cuowu_ma, 4030)


class GuanliTest(unittest.TestCase):
    def test_feiguanliyuan_liechu_pao_4030(self):
        ming = _ming()
        yonghu_fuwu.zhuce(_zhanghao(ming))
        with self.assertRaises(YewuCuowu) as qingjing:
            yonghu_fuwu.liechu(dao.yonghu_an_ming(ming), 1, 20)
        self.assertEqual(qingjing.exception.cuowu_ma, 4030)

    def test_buneng_tingyong_guanliyuan(self):
        guanli = _guanliyuan()
        with self.assertRaises(YewuCuowu) as qingjing:
            yonghu_fuwu.gengxin_zhuangtai(guanli, guanli['id'], 'tingyong')
        self.assertEqual(qingjing.exception.cuowu_ma, 4030)

    def test_tingyong_hou_keyi_huifu(self):
        ming = _ming()
        yonghu_fuwu.zhuce(_zhanghao(ming))
        zhanghao = dao.yonghu_an_ming(ming)
        guanli = _guanliyuan()
        yonghu_fuwu.gengxin_zhuangtai(guanli, zhanghao['id'], 'tingyong')
        jieguo = yonghu_fuwu.gengxin_zhuangtai(guanli, zhanghao['id'], 'zhengchang')
        self.assertEqual(jieguo['zhuangtai'], 'zhengchang')


if __name__ == '__main__':
    unittest.main()
