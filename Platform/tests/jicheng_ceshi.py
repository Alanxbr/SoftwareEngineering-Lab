"""集成测试：启动真实服务进程，按接口交互顺序验证完整业务链路。

用法（在 Platform 目录下）：
    python tests/jicheng_ceshi.py [--shuchu 结果文件.md]

脚本会使用临时数据目录和独立端口，不影响演示库。
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

JIEGEN = Path(__file__).resolve().parents[1]
DUANKOU = 8011
JICHU = f'http://127.0.0.1:{DUANKOU}'
Jieguo = []


def qingqiu(fangshi, lujing, shuju=None, lingpai=None):
    yaoshi = urllib.request.Request(JICHU + lujing, method=fangshi)
    yaoshi.add_header('Content-Type', 'application/json')
    if lingpai:
        yaoshi.add_header('Authorization', 'Bearer ' + lingpai)
    zhengwen = json.dumps(shuju).encode() if shuju is not None else None
    try:
        with urllib.request.urlopen(yaoshi, zhengwen, timeout=20) as xiangying:
            return xiangying.status, json.loads(xiangying.read().decode())
    except urllib.error.HTTPError as cuowu:
        return cuowu.code, json.loads(cuowu.read().decode())


def jilu(bianhao, changjing, yingdang, shiji, tongguo):
    Jieguo.append({
        'bianhao': bianhao, 'changjing': changjing,
        'yingdang': yingdang, 'shiji': shiji,
        'tongguo': '通过' if tongguo else '失败',
    })
    print(f'[{Jieguo[-1]["tongguo"]}] {bianhao} {changjing}：{shiji}')


def denglu(ming, mima):
    zhuangtai, bao = qingqiu('POST', '/yonghu/denglu',
                             {'yonghuming': ming, 'mima': mima})
    return bao.get('data', {}).get('token', '')


def deng_fuwu(qichang=40):
    for _ in range(qichang * 5):
        try:
            with urllib.request.urlopen(JICHU + '/xitong/jiankang', timeout=1):
                return True
        except Exception:
            time.sleep(0.2)
    return False


def deng_renwu(lingpai, renwu_id, zhuangtai=('yiwancheng', 'yichang'), shichang=60):
    jiezhi = time.time() + shichang
    while time.time() < jiezhi:
        _, bao = qingqiu('GET', f'/xunlian/{renwu_id}', lingpai=lingpai)
        if bao.get('data', {}).get('zhuangtai') in zhuangtai:
            return bao['data']
        time.sleep(0.3)
    return bao.get('data', {})


def zhu():
    shuju_mulu = Path(tempfile.mkdtemp(prefix='pingtai_jicheng_'))
    huanjing = dict(os.environ, PINGTAI_SHUJU=str(shuju_mulu),
                    PYTHONIOENCODING='utf-8')
    fuwu = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1',
         '--port', str(DUANKOU), '--log-level', 'warning'],
        cwd=str(JIEGEN), env=huanjing,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        if not deng_fuwu():
            print('服务未能启动')
            return 1

        # S1 健康检查
        zhuangtai, bao = qingqiu('GET', '/xitong/jiankang')
        jilu('S1', '健康检查', '200 且 zhuangtai=ok',
             f'{zhuangtai} {bao.get("data", {}).get("zhuangtai")}',
             zhuangtai == 200 and bao['data']['zhuangtai'] == 'ok')

        # S2 登录
        admin = denglu('admin', 'admin123')
        tigong = denglu('tigong1', '123456')
        shiyong = denglu('shiyong1', '123456')
        jilu('S2', '三角色登录', '均返回 token',
             ', '.join(bool(x) and '有令牌' or '无令牌'
                       for x in (admin, tigong, shiyong)),
             all((admin, tigong, shiyong)))

        # S3 未登录访问
        zhuangtai, bao = qingqiu('GET', '/xunlian')
        jilu('S3', '未登录访问训练列表', '401/4010',
             f'{zhuangtai}/{bao.get("code")}',
             zhuangtai == 401 and bao.get('code') == 4010)

        # S4 提供方登记数据集
        ming = '集成测试数据集_' + uuid.uuid4().hex[:6]
        zhuangtai, bao = qingqiu('POST', '/shuju', {
            'mingcheng': ming, 'geshi': 'csv', 'daxiao': 20_000_000,
            'yangben_shu': 12_000,
            'ziduan': [f'f{i}' for i in range(1, 9)] + ['label'],
        }, tigong)
        jilu('S4', '提供方登记 12000 条数据集', '200/code=0',
             f'{zhuangtai}/{bao.get("code")}',
             zhuangtai == 200 and bao.get('code') == 0)

        # S5 使用方越权登记
        zhuangtai, bao = qingqiu('POST', '/shuju', {
            'mingcheng': ming + '_x', 'geshi': 'csv', 'daxiao': 1024,
            'yangben_shu': 100, 'ziduan': ['label'],
        }, shiyong)
        jilu('S5', '使用方登记数据集被拒', '403/4030',
             f'{zhuangtai}/{bao.get("code")}',
             zhuangtai == 403 and bao.get('code') == 4030)

        # 取固定两个演示数据集：医疗影像（tigong1）与金融风控（tigong2）
        _, bao = qingqiu('GET', '/shuju', lingpai=shiyong)
        anming = {x['mingcheng']: x['id'] for x in bao['data']['items']}
        ids = [anming['医疗影像特征集'], anming['金融风控特征集']]

        # S6 建任务
        zhuangtai, bao = qingqiu('POST', '/xunlian', {
            'mingcheng': '集成测试_模拟模式', 'moxing_leixing': 'mlp_8_16_2',
            'lunshu': 4, 'piliang_daxiao': 16, 'xuexilv': 0.05,
            'yinsipi': 0.5, 'jiancai_yuzhi': 1.0, 'yusuan_shangxian': 3.0,
            'yunxing_moshi': 'moni',
            'canjia': [{'shujuji_id': ids[0]}, {'shujuji_id': ids[1]}],
        }, shiyong)
        moni_id = bao.get('data', {}).get('id')
        jilu('S6', '创建 4 轮模拟任务', '200 且返回任务号',
             f'{zhuangtai}/任务 {moni_id}',
             zhuangtai == 200 and moni_id)

        # S7 启动并等待完成
        zhuangtai, bao = qingqiu('POST', f'/xunlian/{moni_id}/qidong',
                                 {}, shiyong)
        renwu = deng_renwu(shiyong, moni_id)
        jilu('S7', '启动并等待 4 轮训练', '任务已完成',
             f'{zhuangtai}/{renwu.get("zhuangtai")}',
             zhuangtai == 200 and renwu.get('zhuangtai') == 'yiwancheng')

        # S8 曲线完整性
        _, bao = qingqiu('GET', f'/xunlian/{moni_id}/quxian', lingpai=shiyong)
        lunshu = len(bao.get('data', {}).get('rounds', []))
        jilu('S8', '曲线轮次与任务配置一致', '4 轮',
             f'{lunshu} 轮', lunshu == 4)

        # S9 隐私预算累计
        _, bao = qingqiu('GET', f'/xunlian/{moni_id}/yinsi', lingpai=shiyong)
        leiji = bao.get('data', {}).get('leiji_eps')
        jilu('S9', '隐私预算累计', '2.0（4 轮 × 0.5）',
             f'{leiji}', abs(float(leiji) - 2.0) < 1e-9)

        # S10 真实模式全链路
        zhuangtai, bao = qingqiu('POST', '/xunlian', {
            'mingcheng': '集成测试_真实模式', 'moxing_leixing': 'mlp_8_16_2',
            'lunshu': 1, 'piliang_daxiao': 16, 'xuexilv': 0.05,
            'yinsipi': 0.5, 'jiancai_yuzhi': 1.0, 'yusuan_shangxian': 2.0,
            'yunxing_moshi': 'zhenshi',
            'canjia': [{'shujuji_id': ids[0]}, {'shujuji_id': ids[1]}],
        }, shiyong)
        zhen_id = bao.get('data', {}).get('id')
        qingqiu('POST', f'/xunlian/{zhen_id}/qidong', {}, shiyong)
        tigong1 = denglu('tigong1', '123456')
        tigong2 = denglu('tigong2', '123456')
        shangbao = 0
        for _ in range(50):
            _, xiang = qingqiu('GET', f'/xunlian/{zhen_id}', lingpai=shiyong)
            if xiang['data'].get('dangqian_lunci', 0) >= 1:
                break
            time.sleep(0.2)
        for lingpai_tigong, yangben in ((tigong1, 12000), (tigong2, 8600)):
            _, zhuang = qingqiu('GET', f'/kehuduan/renwu/{zhen_id}',
                                lingpai=lingpai_tigong)
            weidu = len(zhuang['data']['canshu'])
            _, tijiao = qingqiu(
                'POST', f'/kehuduan/renwu/{zhen_id}/tijiao', {
                    'lunci_hao': zhuang['data']['dangqian_lunci'],
                    'gengxin': [0.01] * weidu,
                    'yangben_shu': yangben, 'sunshi': 0.5,
                    'zhunquelv': 0.7, 'haoshi': 0.1,
                }, lingpai_tigong)
            shangbao += 1 if tijiao.get('code') == 0 else 0
        renwu = deng_renwu(shiyong, zhen_id)
        jilu('S10', '真实模式两方提交更新', '两次提交成功且任务完成',
             f'成功提交 {shangbao} 次，状态 {renwu.get("zhuangtai")}',
             shangbao == 2 and renwu.get('zhuangtai') == 'yiwancheng')

        # S11 日志按当天结束日期筛选（回归缺陷 002）
        jintian = time.strftime('%Y-%m-%d')
        _, bao = qingqiu('GET', f'/guanli/rizhi?jieshu={jintian}',
                         lingpai=admin)
        zongshu = bao.get('data', {}).get('total', 0)
        jilu('S11', '日志结束日期=今天', '能查到当天记录',
             f'{zongshu} 条', zongshu > 0)

        # S12 备份创建与下载
        _, bao = qingqiu('POST', '/guanli/beifen', {}, admin)
        wenjian = bao.get('data', {}).get('wenjian', '')
        yaoshi = urllib.request.Request(
            JICHU + f'/guanli/beifen/{wenjian}',
            headers={'Authorization': 'Bearer ' + admin})
        with urllib.request.urlopen(yaoshi, timeout=20) as xiangying:
            daxiao = len(xiangying.read())
        jilu('S12', '创建并下载备份', '备份字节数 > 0',
             f'{wenjian} {daxiao} 字节', bool(wenjian) and daxiao > 0)

        # S13 任务不存在
        zhuangtai, bao = qingqiu('GET', '/xunlian/999999', lingpai=shiyong)
        jilu('S13', '查询不存在的任务', '404/4040',
             f'{zhuangtai}/{bao.get("code")}',
             zhuangtai == 404 and bao.get('code') == 4040)

        # S14 前端首页
        with urllib.request.urlopen(JICHU + '/', timeout=10) as xiangying:
            neirong = xiangying.read().decode('utf-8', 'ignore')
        jilu('S14', '访问前端首页', '返回 HTML',
             'HTML' if '<html' in neirong.lower() else '非 HTML',
             '<html' in neirong.lower())

        # S15 使用方访问管理接口
        zhuangtai, bao = qingqiu('GET', '/guanli/rizhi', lingpai=shiyong)
        jilu('S15', '使用方访问管理接口', '403/4030',
             f'{zhuangtai}/{bao.get("code")}',
             zhuangtai == 403 and bao.get('code') == 4030)

        tongguo = sum(1 for x in Jieguo if x['tongguo'] == '通过')
        print(f'\n合计 {len(Jieguo)} 项，通过 {tongguo} 项，失败 '
              f'{len(Jieguo) - tongguo} 项')
        return 0 if tongguo == len(Jieguo) else 1
    finally:
        fuwu.terminate()
        try:
            fuwu.wait(5)
        except subprocess.TimeoutExpired:
            fuwu.kill()
        import shutil
        shutil.rmtree(shuju_mulu, ignore_errors=True)


def xie_markdown(lujing):
    hang = ['| 编号 | 场景 | 预期 | 实际 | 结果 |',
            '| --- | --- | --- | --- | --- |']
    for x in Jieguo:
        hang.append(f'| {x["bianhao"]} | {x["changjing"]} | {x["yingdang"]} | '
                    f'{x["shiji"]} | {x["tongguo"]} |')
    Path(lujing).write_text('\n'.join(hang) + '\n', encoding='utf-8')


if __name__ == '__main__':
    jiexi = argparse.ArgumentParser()
    jiexi.add_argument('--shuchu', default='')
    canshu = jiexi.parse_args()
    zhuangtai = zhu()
    if canshu.shuchu:
        xie_markdown(canshu.shuchu)
        print('结果已写入：' + canshu.shuchu)
    sys.exit(zhuangtai)
