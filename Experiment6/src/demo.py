"""演示联邦训练模块：从登记数据集到完成三轮训练。"""

import random
import tempfile
from pathlib import Path

from zhuangpei import Zhuangpei


def zhunbei(zhuangpei: Zhuangpei) -> tuple:
    """登记用户和数据集，返回任务需要的编号。"""
    tigong_yi = zhuangpei.yonghu_dao.charru(
        'tigong_yi', 'hash', 'a@example.com', 'tigongfang'
    )
    tigong_er = zhuangpei.yonghu_dao.charru(
        'tigong_er', 'hash', 'b@example.com', 'tigongfang'
    )
    shiyong = zhuangpei.yonghu_dao.charru(
        'shiyong', 'hash', 'c@example.com', 'shiyongfang'
    )
    yi = zhuangpei.shuju_fuwu.dengji_shujuji(tigong_yi, 'yiliao_yangben', 'csv', 102400, 800)
    er = zhuangpei.shuju_fuwu.dengji_shujuji(tigong_er, 'jinrong_yangben', 'csv', 51200, 200)
    print('登记数据集：', yi.xiaoxi, er.xiaoxi)
    return tigong_yi, tigong_er, shiyong, yi.shuju['shujuji_id'], er.shuju['shujuji_id']


def jianli_renwu(zhuangpei: Zhuangpei, shiyong: int, canjia_list: list) -> int:
    """创建并启动训练任务。"""
    chuangjian = zhuangpei.xunlian_fuwu.chuangjian_renwu(
        shiyong, 'xinpian_fenlei', canjia_list, lunshu=3, piliang_daxiao=32,
        xuexilv=0.01, yinsipi=0.5, jiancai_yuzhi=1.0, yusuan_shangxian=2.0,
    )
    print('创建任务：', chuangjian.xiaoxi)
    renwu_id = chuangjian.shuju['renwu_id']
    print('启动任务：', zhuangpei.xunlian_fuwu.qidong_xunlian(renwu_id).xiaoxi)
    return renwu_id


def zhixing(zhuangpei: Zhuangpei, renwu_id: int, canjia: list) -> None:
    """执行三轮训练并打印每轮结果。"""
    quanju = [0.0, 0.0, 0.0, 0.0]
    for lunci in range(1, 4):
        suijishu = random.Random(100 + lunci)
        gengxin_list = []
        for yonghu_id, yangben_shu in canjia:
            gengxin = [x + suijishu.uniform(-0.6, 0.6) for x in quanju]
            gengxin_list.append({
                'yonghu_id': yonghu_id, 'gengxin': gengxin,
                'sunshi': 0.9 / lunci, 'zhunquelv': 0.60 + 0.1 * lunci, 'haoshi': 1.2,
            })
        jieguo = zhuangpei.xunlian_fuwu.zhixing_lunci(renwu_id, gengxin_list, suijishu)
        if not jieguo.chenggong:
            print('训练失败：', jieguo.cuowu_ma, jieguo.xiaoxi)
            return
        quanju = jieguo.shuju['quanju_canshu']
        print(
            '第 %d 轮：损失 %.4f，准确率 %.2f，累计 ε %.1f，剩余预算 %.1f'
            % (lunci, jieguo.shuju['sunshi'], jieguo.shuju['zhunquelv'],
               jieguo.shuju['leiji_eps'], jieguo.shuju['shengyu_yusuan'])
        )


def main() -> None:
    with tempfile.TemporaryDirectory() as linshi:
        mulu = Path(linshi)
        zhuangpei = Zhuangpei(str(mulu / 'pingtai.db'), str(mulu / 'canshu'))
        try:
            tigong_yi, tigong_er, shiyong, shuju_yi, shuju_er = zhunbei(zhuangpei)
            canjia_list = [
                {'yonghu_id': tigong_yi, 'shujuji_id': shuju_yi, 'yangben_shu': 800},
                {'yonghu_id': tigong_er, 'shujuji_id': shuju_er, 'yangben_shu': 200},
            ]
            renwu_id = jianli_renwu(zhuangpei, shiyong, canjia_list)
            zhixing(zhuangpei, renwu_id, [(tigong_yi, 800), (tigong_er, 200)])
            zhuangtai = zhuangpei.xunlian_fuwu.chaxun_zhuangtai(renwu_id)
            print('任务最终状态：', zhuangtai.shuju['zhuangtai'])
            print('已完成轮次：', zhuangtai.shuju['yiwancheng_lunshu'])
            print('参数文件：', sorted(
                p.name for p in (mulu / 'canshu' / str(renwu_id)).iterdir()
            ))
        finally:
            zhuangpei.guanbi()


if __name__ == '__main__':
    main()
