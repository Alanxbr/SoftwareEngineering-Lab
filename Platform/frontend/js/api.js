/* 全局状态、HTTP 请求、路由与格式化工具 */

const Pingtai = (() => {
  const TOKEN_JIAN = 'pingtai_token';
  const YONGHU_JIAN = 'pingtai_yonghu';

  const zhuangtai = Vue.reactive({
    token: localStorage.getItem(TOKEN_JIAN) || '',
    yonghu: JSON.parse(localStorage.getItem(YONGHU_JIAN) || 'null'),
    luxian: '/dashboard',
    canshu: {},
    tishi_liebiao: [],
  });

  let tishi_bianhao = 0;

  function tishi(neirong, leixing = 'info', shichang = 3600) {
    const id = ++tishi_bianhao;
    zhuangtai.tishi_liebiao.push({ id, neirong, leixing });
    setTimeout(() => {
      const weizhi = zhuangtai.tishi_liebiao.findIndex((x) => x.id === id);
      if (weizhi >= 0) zhuangtai.tishi_liebiao.splice(weizhi, 1);
    }, shichang);
  }

  class PingtaiCuowu extends Error {
    constructor(daima, xiaoxi, http) {
      super(xiaoxi || '请求失败');
      this.daima = daima;
      this.http = http;
    }
  }

  async function qingqiu(fangshi, lujing, shuju) {
    const tou = { 'Content-Type': 'application/json' };
    if (zhuangtai.token) tou.Authorization = 'Bearer ' + zhuangtai.token;
    let xiangying;
    try {
      xiangying = await fetch(lujing, {
        method: fangshi,
        headers: tou,
        body: shuju === undefined ? undefined : JSON.stringify(shuju),
      });
    } catch (e) {
      throw new PingtaiCuowu(-1, '无法连接后端服务，请确认服务已启动', 0);
    }
    let bao = null;
    try {
      bao = await xiangying.json();
    } catch (e) {
      throw new PingtaiCuowu(-1, '服务返回了非 JSON 内容（HTTP ' + xiangying.status + '）', xiangying.status);
    }
    if (xiangying.status === 401) {
      tuichu(false);
      throw new PingtaiCuowu(bao.code, bao.message || '登录已过期', 401);
    }
    if (!xiangying.ok || bao.code !== 0) {
      throw new PingtaiCuowu(bao.code, bao.message || '请求失败', xiangying.status);
    }
    return bao.data;
  }

  function cunchu_denglu(shuju) {
    zhuangtai.token = shuju.token;
    zhuangtai.yonghu = shuju.user;
    localStorage.setItem(TOKEN_JIAN, shuju.token);
    localStorage.setItem(YONGHU_JIAN, JSON.stringify(shuju.user));
  }

  function tuichu(tiaozhuan = true) {
    zhuangtai.token = '';
    zhuangtai.yonghu = null;
    localStorage.removeItem(TOKEN_JIAN);
    localStorage.removeItem(YONGHU_JIAN);
    if (tiaozhuan) tiaozhuan_luxian('/login');
  }

  // ------------------------------------------------ 路由
  zhuangtai.luxian = jiexi_lujing();

  function jiexi_lujing() {
    const yuan = (location.hash || '').replace(/^#/, '');
    if (!yuan) return '/dashboard';
    return yuan.split('?')[0];
  }

  function tiaozhuan_luxian(lujing) {
    if (location.hash !== '#' + lujing) {
      location.hash = lujing;
    } else {
      zhuangtai.luxian = lujing.split('?')[0];
    }
  }

  window.addEventListener('hashchange', () => {
    zhuangtai.luxian = jiexi_lujing();
    zhuangtai.canshu = {};
  });

  // ------------------------------------------------ 映射与格式化
  const JIAOSE_MING = {
    tigongfang: '数据提供方',
    shiyongfang: '数据使用方',
    guanliyuan: '系统管理员',
  };

  const ZHUANGTAI_MING = {
    renwu: {
      daichufa: { t: '待启动', c: 'warn' },
      xunlianzhong: { t: '训练中', c: 'info' },
      yiwancheng: { t: '已完成', c: 'good' },
      yichang: { t: '异常', c: 'bad' },
      yiquxiao: { t: '已取消', c: 'mute' },
    },
    shujuji: {
      daijiaoyan: { t: '待校验', c: 'warn' },
      yijiaoyan: { t: '可用', c: 'good' },
      yitingyong: { t: '已停用', c: 'mute' },
    },
    canjia: {
      daixunlian: { t: '待训练', c: 'mute' },
      xunlianzhong: { t: '训练中', c: 'info' },
      yiwancheng: { t: '已完成', c: 'good' },
      diaoxian: { t: '掉线', c: 'bad' },
    },
    yonghu: {
      zhengchang: { t: '正常', c: 'good' },
      tingyong: { t: '已停用', c: 'mute' },
    },
    rizhi: {
      chenggong: { t: '成功', c: 'good' },
      shibai: { t: '失败', c: 'bad' },
      yuequan: { t: '越权', c: 'warn' },
    },
  };

  const MOSHI_MING = { moni: '模拟训练', zhenshi: '真实联邦' };
  const GESHI_MING = { csv: 'CSV', json: 'JSON', parquet: 'Parquet', npy: 'NumPy' };

  function qu_zhuangtai(leixing, zhi) {
    const biao = ZHUANGTAI_MING[leixing] || {};
    return biao[zhi] || { t: zhi || '未知', c: 'mute' };
  }

  function jiaose_ming(zhi) {
    return JIAOSE_MING[zhi] || zhi || '未知角色';
  }

  function geshihua_shijian(zhi) {
    if (!zhi) return '—';
    return String(zhi).replace('T', ' ').slice(0, 19);
  }

  function geshihua_daxiao(zhi) {
    const n = Number(zhi) || 0;
    if (n >= 1024 ** 3) return (n / 1024 ** 3).toFixed(2) + ' GB';
    if (n >= 1024 ** 2) return (n / 1024 ** 2).toFixed(2) + ' MB';
    if (n >= 1024) return (n / 1024).toFixed(1) + ' KB';
    return n + ' B';
  }

  function bili_zhi(zhi, wei = 1) {
    return (Number(zhi || 0) * 100).toFixed(wei) + '%';
  }

  function shuliang(zhi) {
    return Number(zhi || 0).toLocaleString('zh-CN');
  }

  function qu_canshu_lujing(lujing) {
    const bufen = lujing.split('/').filter(Boolean);
    return bufen;
  }

  return {
    zhuangtai,
    tishi,
    qingqiu,
    cunchu_denglu,
    tuichu,
    tiaozhuan: tiaozhuan_luxian,
    qu_zhuangtai,
    jiaose_ming,
    JIAOSE_MING,
    ZHUANGTAI_MING,
    MOSHI_MING,
    GESHI_MING,
    geshihua_shijian,
    geshihua_daxiao,
    bili_zhi,
    shuliang,
    qu_canshu_lujing,
    PingtaiCuowu,
  };
})();
