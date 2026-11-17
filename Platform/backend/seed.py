"""首次启动时写入演示账号、数据集、训练任务与操作日志。

演示数据版本：1 = 早期精简版，2 = 千条样本起步的完整版。
数据库里的 PRAGMA user_version 低于当前版本时，会自动备份旧库后重建演示数据。
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from backend import dao, db
from backend.config import BEIFEN_MULU, SHUJUKU_LUJING
from backend.security import jiayi_mima

YANSHI_BANBEN = 2

ZHANGHAO = [
    ('admin', 'admin123', 'admin@example.com', 'guanliyuan'),
    ('tigong1', '123456', 'tigong1@example.com', 'tigongfang'),
    ('tigong2', '123456', 'tigong2@example.com', 'tigongfang'),
    ('tigong3', '123456', 'tigong3@example.com', 'tigongfang'),
    ('shiyong1', '123456', 'shiyong1@example.com', 'shiyongfang'),
    ('shiyong2', '123456', 'shiyong2@example.com', 'shiyongfang'),
]

# 名称、格式、字节数、样本数、字段、路径、脱敏规则、校验结论
SHUJIJI = {
    'yiliao': ('医疗影像特征集', 'csv', 58_720_256, 12_000,
               ['age', 'bmi', 'blood_pressure', 'cholesterol', 'glucose',
                'heart_rate', 'smoke', 'family_history', 'label'],
               'D:/data/yiliao_yingxiang.csv',
               'patient_id -> SHA256；姓名/身份证 -> 掩码；就诊时间 -> 泛化为季度',
               '格式 CSV 可解析，9 个字段定义完整，12,000 条样本元数据有效'),
    'jinrong': ('金融风控特征集', 'csv', 41_943_040, 8_600,
                ['income', 'debt_ratio', 'credit_score', 'loan_amount',
                 'employment_years', 'late_payments', 'balance', 'age', 'label'],
                'D:/data/jinrong_fengkong.csv',
                '身份证号 -> 哈希；手机号/银行卡 -> 掩码；收入 -> 分箱',
                '格式 CSV 可解析，9 个字段定义完整，8,600 条样本元数据有效'),
    'zhizao': ('制造质检特征集', 'csv', 73_400_320, 15_000,
               ['temperature', 'pressure', 'vibration', 'rotation_speed',
                'tool_wear', 'torque', 'humidity', 'machine_age', 'label'],
               'D:/data/zhizao_zhijian.csv',
               '设备编号 -> 哈希；工位信息 -> 泛化为车间；批次号 -> 截断',
               '格式 CSV 可解析，9 个字段定义完整，15,000 条样本元数据有效'),
    'lingshou': ('零售消费行为特征集', 'csv', 31_457_280, 6_400,
                 ['age', 'gender', 'income_level', 'visit_freq',
                  'avg_order', 'discount_rate', 'category_depth', 'loyalty_years', 'label'],
                 'D:/data/lingshou_xiaofei.csv',
                 '会员卡号 -> SHA256；姓名/手机号 -> 掩码；订单号 -> 脱敏',
                 '格式 CSV 可解析，9 个字段定义完整，6,400 条样本元数据有效'),
    'jiaotong': ('交通流量特征集', 'csv', 47_185_920, 9_800,
                 ['flow', 'speed', 'occupancy', 'hour', 'weekday',
                  'weather', 'temperature', 'accident_flag', 'label'],
                 'D:/data/jiaotong_liuliang.csv',
                 '车牌号 -> SHA256；卡口编号 -> 泛化为路段；时间 -> 保留小时',
                 '格式 CSV 可解析，9 个字段定义完整，9,800 条样本元数据有效'),
    'jiaoyu': ('教育测评特征集', 'csv', 25_165_824, 5_200,
               ['attendance', 'homework_score', 'quiz_avg', 'study_hours',
                'parent_edu', 'class_size', 'extra_lessons', 'sleep_hours', 'label'],
               'D:/data/jiaoyu_ceping.csv',
               '学号 -> SHA256；姓名 -> 掩码；班级 -> 泛化为年级',
               '格式 CSV 可解析，9 个字段定义完整，5,200 条样本元数据有效'),
}

SHUJIJI_GUISHU = {
    'yiliao': 'tigong1', 'jinrong': 'tigong2', 'zhizao': 'tigong3',
    'lingshou': 'tigong1', 'jiaotong': 'tigong3', 'jiaoyu': 'tigong2',
}


def chushihua_shuju() -> None:
    """按演示数据版本初始化；旧版本先备份再重建。"""
    banben = db.qu_banben()
    if dao.yonghu_an_ming('admin'):
        if banben >= YANSHI_BANBEN:
            return
        _beifen_jiu_ku()
        _qingkong()
    _xieru_yanshi()
    db.she_banben(YANSHI_BANBEN)


def _beifen_jiu_ku() -> Path:
    """用 SQLite 备份接口把旧库另存一份，再清空重建。"""
    BEIFEN_MULU.mkdir(parents=True, exist_ok=True)
    mubiao = BEIFEN_MULU / f'pingtai_yanshi_v1_{datetime.now():%Y%m%d_%H%M%S}.db'
    with sqlite3.connect(str(SHUJUKU_LUJING)) as yuan, \
            sqlite3.connect(str(mubiao)) as mu:
        yuan.backup(mu)
    return mubiao


def _qingkong() -> None:
    with db.lianjie() as lian:
        for biao in ('xitong_rizhi', 'renwu_gengxin', 'yinsi_yusuan', 'lunci_jilu',
                     'renwu_canjiafang', 'xunlian_renwu', 'shujuji', 'yonghu'):
            lian.execute(f'DELETE FROM {biao}')
        lian.execute('DELETE FROM sqlite_sequence')


def _xieru_yanshi() -> None:
    zhanghao = {}
    for ming, mima, youxiang, jiaose in ZHANGHAO:
        zhanghao[ming] = dao.chuangjian_yonghu(
            ming, jiayi_mima(mima), youxiang, jiaose)

    shuju = {}
    for jian, (mingcheng, geshi, daxiao, yangben, ziduan, lujing,
               tuomin, jielun) in SHUJIJI.items():
        shuju[jian] = dao.chuangjian_shujuji(zhanghao[SHUJIJI_GUISHU[jian]], {
            'mingcheng': mingcheng,
            'geshi': geshi,
            'daxiao': daxiao,
            'yangben_shu': yangben,
            'ziduan': ziduan,
            'benzhi_lujing': lujing,
            'tuomin_guize': tuomin,
            'zhuangtai': 'yijiaoyan',
            'jiaoyan_jielun': jielun,
        })

    def canjia(*jian_list):
        return [
            {'yonghu_id': zhanghao[SHUJIJI_GUISHU[j]], 'shujuji_id': shuju[j],
             'yangben_shu': SHUJIJI[j][3]}
            for j in jian_list
        ]

    # 任务 1：已完成，5 轮曲线体现"差分隐私带来的收敛延迟"
    yiwancheng = dao.chuangjian_renwu(zhanghao['shiyong1'], {
        'mingcheng': '医疗与金融联合诊断模型',
        'moxing_leixing': 'mlp_8_16_2', 'lunshu': 5, 'piliang_daxiao': 16,
        'xuexilv': 0.05, 'yinsipi': 0.5, 'jiancai_yuzhi': 1.0,
        'yusuan_shangxian': 3.0, 'yunxing_moshi': 'moni',
    }, canjia('yiliao', 'jinrong'))
    dao.renwu_gengxin_zhuangtai(yiwancheng, 'xunlianzhong')
    for lun, (sunshi, zhunquelv) in enumerate(
            [(3.490555, 0.4713), (1.673903, 0.4963), (0.530830, 0.7550),
             (0.210241, 0.9187), (0.105112, 0.9700)], 1):
        dao.renwu_gengxin_lunci(yiwancheng, lun)
        dao.charu_lunci(yiwancheng, lun, sunshi, zhunquelv, 0.02,
                        f'renwu_{yiwancheng}_lunci_{lun}.json', 2)
        dao.charu_yusuan(yiwancheng, lun, 0.5, 0.5 * lun)
    dao.renwu_gengxin_zhuangtai(yiwancheng, 'yiwancheng')
    dao.canjiafang_gengxin_zhuangtai(yiwancheng, 'yiwancheng')

    # 任务 2、3：待启动
    dai1 = dao.chuangjian_renwu(zhanghao['shiyong2'], {
        'mingcheng': '制造业质量联合预测',
        'moxing_leixing': 'mlp_8_16_2', 'lunshu': 6, 'piliang_daxiao': 16,
        'xuexilv': 0.05, 'yinsipi': 0.5, 'jiancai_yuzhi': 1.0,
        'yusuan_shangxian': 5.0, 'yunxing_moshi': 'moni',
    }, canjia('zhizao', 'jinrong'))

    dai2 = dao.chuangjian_renwu(zhanghao['shiyong1'], {
        'mingcheng': '跨机构信用评估模型',
        'moxing_leixing': 'mlp_8_16_2', 'lunshu': 5, 'piliang_daxiao': 16,
        'xuexilv': 0.05, 'yinsipi': 0.4, 'jiancai_yuzhi': 1.0,
        'yusuan_shangxian': 4.0, 'yunxing_moshi': 'zhenshi',
    }, canjia('yiliao', 'jiaoyu'))

    # 任务 4：已取消
    yiquxiao = dao.chuangjian_renwu(zhanghao['shiyong2'], {
        'mingcheng': '零售用户画像联合建模',
        'moxing_leixing': 'mlp_8_16_2', 'lunshu': 5, 'piliang_daxiao': 16,
        'xuexilv': 0.05, 'yinsipi': 0.5, 'jiancai_yuzhi': 1.0,
        'yusuan_shangxian': 2.5, 'yunxing_moshi': 'moni',
    }, canjia('lingshou', 'jiaotong'))
    dao.renwu_gengxin_zhuangtai(yiquxiao, 'yiquxiao', '管理员取消：数据集口径调整')

    # 任务 5：异常中断
    yichang = dao.chuangjian_renwu(zhanghao['shiyong1'], {
        'mingcheng': '教育效果联合评估',
        'moxing_leixing': 'mlp_8_16_2', 'lunshu': 6, 'piliang_daxiao': 16,
        'xuexilv': 0.05, 'yinsipi': 0.5, 'jiancai_yuzhi': 1.0,
        'yusuan_shangxian': 3.0, 'yunxing_moshi': 'moni',
    }, canjia('jiaoyu', 'jiaotong'))
    dao.renwu_gengxin_zhuangtai(yichang, 'yichang', '服务重启，任务中断')
    dao.canjiafang_gengxin_zhuangtai(yichang, 'diaoxian')

    # 演示日志
    dao.xie_rizhi(None, '系统初始化', 'xitong', None, 'chenggong',
                  '已创建 6 个账号、6 个数据集（合计 57,000 条样本）和 5 个训练任务',
                  '127.0.0.1')
    dao.xie_rizhi(zhanghao['admin'], '用户登录', 'yonghu', zhanghao['admin'],
                  'chenggong', '角色：guanliyuan', '127.0.0.1')
    dao.xie_rizhi(zhanghao['shiyong1'], '创建训练任务', 'xunlian_renwu',
                  yiwancheng, 'chenggong', '医疗与金融联合诊断模型，2 个参与方，5 轮',
                  '127.0.0.1')
    dao.xie_rizhi(zhanghao['shiyong1'], '启动训练', 'xunlian_renwu',
                  yiwancheng, 'chenggong', '医疗与金融联合诊断模型，模式：moni',
                  '127.0.0.1')
    dao.xie_rizhi(None, '训练完成', 'xunlian_renwu', yiwancheng, 'chenggong',
                  '共 5 轮，累计 ε 2.50', '127.0.0.1')
    for rid, ming, zhe in ((dai1, '制造业质量联合预测', 'shiyong2'),
                           (dai2, '跨机构信用评估模型', 'shiyong1'),
                           (yiquxiao, '零售用户画像联合建模', 'shiyong2'),
                           (yichang, '教育效果联合评估', 'shiyong1')):
        dao.xie_rizhi(zhanghao[zhe], '创建训练任务', 'xunlian_renwu', rid,
                      'chenggong', f'{ming}，2 个参与方', '127.0.0.1')
    dao.xie_rizhi(zhanghao['admin'], '取消训练任务', 'xunlian_renwu', yiquxiao,
                  'chenggong', '管理员取消：数据集口径调整', '127.0.0.1')
    dao.xie_rizhi(zhanghao['tigong1'], '用户登录', 'yonghu', zhanghao['tigong1'],
                  'shibai', '登录失败：密码错误', '127.0.0.1')
    dao.xie_rizhi(zhanghao['tigong1'], '用户登录', 'yonghu', zhanghao['tigong1'],
                  'chenggong', '角色：tigongfang', '127.0.0.1')
