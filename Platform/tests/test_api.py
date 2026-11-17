"""接口层：统一响应、鉴权、校验与权限分支。"""

import unittest
import uuid

from fastapi.testclient import TestClient

from main import app


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kehu = TestClient(app)
        cls.kehu.__enter__()
        cls.tokens = {}
        for ming, mima in (('admin', 'admin123'), ('tigong1', '123456'),
                           ('shiyong1', '123456')):
            bao = cls.kehu.post('/yonghu/denglu',
                                json={'yonghuming': ming, 'mima': mima}).json()
            cls.tokens[ming] = bao['data']['token']

    @classmethod
    def tearDownClass(cls):
        cls.kehu.__exit__(None, None, None)

    def _tou(self, ming):
        return {'Authorization': 'Bearer ' + self.tokens[ming]}

    def test_jiankang_yu_wendang(self):
        jiankang = self.kehu.get('/xitong/jiankang').json()
        self.assertEqual(jiankang['code'], 0)
        self.assertEqual(jiankang['data']['zhuangtai'], 'ok')
        self.assertEqual(self.kehu.get('/docs').status_code, 200)
        self.assertEqual(self.kehu.get('/openapi.json').status_code, 200)

    def test_shouye_fanhui_qian_duan(self):
        xiangying = self.kehu.get('/')
        self.assertEqual(xiangying.status_code, 200)
        self.assertIn('text/html', xiangying.headers['content-type'])
        self.assertIn('隐私计算', xiangying.text)

    def test_denglu_cuowu_mima_pao_401(self):
        xiangying = self.kehu.post('/yonghu/denglu',
                                   json={'yonghuming': 'admin', 'mima': 'cuowu'})
        self.assertEqual(xiangying.status_code, 401)
        self.assertEqual(xiangying.json()['code'], 4010)

    def test_weidenglu_fangwen_pao_401(self):
        xiangying = self.kehu.get('/xunlian')
        self.assertEqual(xiangying.status_code, 401)
        self.assertEqual(xiangying.json()['code'], 4010)

    def test_token_wuxiao_pao_401(self):
        xiangying = self.kehu.get('/xunlian',
                                  headers={'Authorization': 'Bearer abc.def.ghi'})
        self.assertEqual(xiangying.status_code, 401)

    def test_zhuce_ziduan_hefa_xing_pao_4005(self):
        xiangying = self.kehu.post('/yonghu/zhuce', json={
            'yonghuming': 'ab', 'mima': '123456',
            'youxiang': 'bad-email', 'jiaose': 'shiyongfang'})
        self.assertEqual(xiangying.status_code, 400)
        self.assertEqual(xiangying.json()['code'], 4005)

    def test_shujuji_liebiao_dai_fenye(self):
        bao = self.kehu.get('/shuju', headers=self._tou('shiyong1')).json()
        self.assertEqual(bao['code'], 0)
        self.assertIn('items', bao['data'])
        self.assertGreaterEqual(bao['data']['total'], 6)

    def test_tigongfang_dengji_shiyongfang_bei_jujue(self):
        ming = 'api_shuju_' + uuid.uuid4().hex[:6]
        tiguan = self.kehu.post('/shuju', headers=self._tou('tigong1'), json={
            'mingcheng': ming, 'geshi': 'csv', 'daxiao': 2048,
            'yangben_shu': 3000, 'ziduan': [f'f{i}' for i in range(1, 9)] + ['label']})
        self.assertEqual(tiguan.status_code, 200)
        xiangying = self.kehu.post('/shuju', headers=self._tou('shiyong1'), json={
            'mingcheng': ming + '_x', 'geshi': 'csv', 'daxiao': 2048,
            'yangben_shu': 100, 'ziduan': ['label']})
        self.assertEqual(xiangying.status_code, 403)
        self.assertEqual(xiangying.json()['code'], 4030)

    def test_jian_renwu_canshu_buhefa_pao_4005(self):
        xiangying = self.kehu.post('/xunlian', headers=self._tou('shiyong1'), json={
            'mingcheng': '接口测试', 'lunshu': 0, 'canjia': []})
        self.assertEqual(xiangying.status_code, 400)
        self.assertEqual(xiangying.json()['code'], 4005)

    def test_jian_renwu_bing_qidong_liucheng(self):
        shuju = self.kehu.get('/shuju', headers=self._tou('shiyong1')).json()
        ids = [x['id'] for x in shuju['data']['items'][:2]]
        bao = self.kehu.post('/xunlian', headers=self._tou('shiyong1'), json={
            'mingcheng': '接口层联调任务', 'moxing_leixing': 'mlp_8_16_2',
            'lunshu': 2, 'piliang_daxiao': 16, 'xuexilv': 0.05,
            'yinsipi': 0.5, 'jiancai_yuzhi': 1.0, 'yusuan_shangxian': 2.0,
            'yunxing_moshi': 'moni',
            'canjia': [{'shujuji_id': ids[0]}, {'shujuji_id': ids[1]}]}).json()
        self.assertEqual(bao['code'], 0)
        renwu_id = bao['data']['id']
        qidong = self.kehu.post(f'/xunlian/{renwu_id}/qidong',
                                headers=self._tou('shiyong1')).json()
        self.assertEqual(qidong['code'], 0)
        xiangqing = self.kehu.get(f'/xunlian/{renwu_id}',
                                  headers=self._tou('shiyong1')).json()
        self.assertIn(xiangqing['data']['zhuangtai'],
                      ('xunlianzhong', 'yiwancheng'))

    def test_guanli_jiekou_jiaose_kongzhi(self):
        ju = self.kehu.get('/guanli/rizhi', headers=self._tou('shiyong1'))
        self.assertEqual(ju.status_code, 403)
        tong = self.kehu.get('/guanli/rizhi', headers=self._tou('admin'))
        self.assertEqual(tong.status_code, 200)
        self.assertGreaterEqual(tong.json()['data']['total'], 12)

    def test_renwu_bucunzai_pao_404(self):
        xiangying = self.kehu.get('/xunlian/999999',
                                  headers=self._tou('shiyong1'))
        self.assertEqual(xiangying.status_code, 404)
        self.assertEqual(xiangying.json()['code'], 4040)


if __name__ == '__main__':
    unittest.main()
