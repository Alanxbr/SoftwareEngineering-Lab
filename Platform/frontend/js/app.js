/* 根应用：侧边栏、顶栏、哈希路由、登录保护 */

const CaidanXiang = [
  {
    fen: '工作区',
    xiang: [
      { lujing: '/dashboard', ming: '工作台', tubiao: '📊', zujian: GongzuoTaiShiTu },
      { lujing: '/tasks', ming: '训练任务', tubiao: '🔁', zujian: XunlianRenwuShiTu },
      { lujing: '/datasets', ming: '数据集', tubiao: '🗂', zujian: ShujuJiShiTu },
    ],
  },
  {
    fen: '协作',
    xiang: [
      { lujing: '/client', ming: '参与方中心', tubiao: '🤝', zujian: KehuduanShiTu, jiaose: ['tigongfang', 'shiyongfang'] },
    ],
  },
  {
    fen: '系统管理',
    xiang: [
      { lujing: '/admin/users', ming: '用户管理', tubiao: '👥', zujian: YonghuGuanliShiTu, jiaose: ['guanliyuan'] },
      { lujing: '/admin/logs', ming: '系统日志', tubiao: '📋', zujian: RizhiShiTu, jiaose: ['guanliyuan'] },
      { lujing: '/admin/backups', ming: '数据备份', tubiao: '💾', zujian: BeifenShiTu, jiaose: ['guanliyuan'] },
    ],
  },
  {
    fen: '其他',
    xiang: [
      { lujing: '/about', ming: '关于平台', tubiao: 'ℹ️', zujian: GuanyuShiTu },
    ],
  },
];

const App = {
  components: { DengluShiTu },
  data() {
    return { jiazai_yonghu: false };
  },
  computed: {
    zhuangtai() { return Pingtai.zhuangtai; },
    yonghu() { return Pingtai.zhuangtai.yonghu || {}; },
    jiaose() { return this.yonghu.jiaose || ''; },
    lujing() { return Pingtai.zhuangtai.luxian; },
    caidan() {
      return CaidanXiang
        .map((fen) => ({ fen: fen.fen, xiang: fen.xiang.filter((x) => !x.jiaose || x.jiaose.includes(this.jiaose)) }))
        .filter((fen) => fen.xiang.length);
    },
    dangqian() {
      const l = this.lujing;
      if (/^\/tasks\/\d+$/.test(l)) {
        return { biaoti: '任务详情', zujian: RenwuXiangqingShiTu, jiaose: null };
      }
      const xiang = CaidanXiang.flatMap((f) => f.xiang).find((x) => x.lujing === l);
      if (xiang && (!xiang.jiaose || xiang.jiaose.includes(this.jiaose))) {
        return { biaoti: xiang.ming, zujian: xiang.zujian, jiaose: xiang.jiaose };
      }
      return { biaoti: '工作台', zujian: GongzuoTaiShiTu, jiaose: null };
    },
    touxiang() {
      return (this.yonghu.yonghuming || '?').slice(0, 1).toUpperCase();
    },
  },
  methods: {
    denglu_chenggong() {
      this.jiazai_yonghu = false;
      Pingtai.tiaozhuan('/dashboard');
    },
    tiaozhuan(lujing) {
      Pingtai.tiaozhuan(lujing);
    },
    tuichu() {
      if (!confirm('确定退出登录吗？')) return;
      Pingtai.tuichu();
      Pingtai.tishi('已退出登录');
    },
    jiancha_quanxian() {
      if (!Pingtai.zhuangtai.token) {
        if (this.lujing !== '/login') Pingtai.tiaozhuan('/login');
        return;
      }
      if (this.lujing === '/login') {
        Pingtai.tiaozhuan('/dashboard');
        return;
      }
      const xiang = CaidanXiang.flatMap((f) => f.xiang).find((x) => x.lujing === this.lujing);
      if (xiang && xiang.jiaose && !xiang.jiaose.includes(this.jiaose)) {
        Pingtai.tishi('当前角色无权访问该页面', 'warn');
        Pingtai.tiaozhuan('/dashboard');
      }
    },
    async shuaxin_yonghu() {
      if (!Pingtai.zhuangtai.token) return;
      try {
        const yonghu = await Pingtai.qingqiu('GET', '/yonghu/wo');
        Pingtai.zhuangtai.yonghu = yonghu;
        localStorage.setItem('pingtai_yonghu', JSON.stringify(yonghu));
      } catch (e) {
        /* 令牌失效时由 qingqiu 统一跳转登录 */
      }
    },
    tishi_tubiao(leixing) {
      return { good: '✅', warn: '⚠️', bad: '⛔' }[leixing] || 'ℹ️';
    },
    tishi_liebiao_chang() {
      /* 占位，保证模板中读取响应式列表 */
      return Pingtai.zhuangtai.tishi_liebiao;
    },
  },
  watch: {
    lujing() { this.jiancha_quanxian(); },
  },
  mounted() {
    this.shuaxin_yonghu();
    this.jiancha_quanxian();
  },
  template: `
  <denglu-shi-tu v-if="!zhuangtai.token" @chenggong="denglu_chenggong"></denglu-shi-tu>

  <div v-else class="zhuangpei">
    <aside class="cebian">
      <div class="pinpai">
        <div class="pinpai-tubiao">🛡</div>
        <div>
          <div class="pinpai-ming">隐私计算平台</div>
          <div class="pinpai-fu">数据共享 · 联邦学习</div>
        </div>
      </div>

      <nav class="daohang">
        <template v-for="fen in caidan" :key="fen.fen">
          <div class="daohang-fen">{{ fen.fen }}</div>
          <button v-for="x in fen.xiang" :key="x.lujing" class="daohang-xiang"
                  :class="{ huoyue: lujing === x.lujing || (x.lujing === '/tasks' && lujing.startsWith('/tasks/')) }"
                  @click="tiaozhuan(x.lujing)">
            <span class="tubiao">{{ x.tubiao }}</span>
            <span class="ming">{{ x.ming }}</span>
          </button>
        </template>
      </nav>

      <div class="cebian-dibu">
        <div class="cebian-tishi">
          联邦学习 · 差分隐私<br>
          <b>SQLite WAL</b> · 本地部署 v1.0.0
        </div>
      </div>
    </aside>

    <div class="zhuti">
      <header class="dinglan">
        <div class="dinglan-biaoti">{{ dangqian.biaoti }}</div>
        <div class="dinglan-cengci" v-if="lujing === '/dashboard'">平台总览</div>

        <div class="dinglan-you">
          <button class="an xiao wenzi" @click="$root.tiaozhuan('/about')">关于</button>
          <div class="yonghu-ka">
            <div class="yonghu-tou">{{ touxiang }}</div>
            <div>
              <div class="yonghu-ming">{{ yonghu.yonghuming }}</div>
              <div class="yonghu-jiao">{{ Pingtai.jiaose_ming(yonghu.jiaose) }}</div>
            </div>
          </div>
          <button class="an xiao" @click="tuichu">退出</button>
        </div>
      </header>

      <main class="neirong">
        <component :is="dangqian.zujian" :key="lujing"></component>
      </main>
    </div>
  </div>

  <div class="tishi-kuang">
    <div v-for="t in tishi_liebiao_chang()" :key="t.id" class="tishi" :class="t.leixing">
      <span>{{ tishi_tubiao(t.leixing) }}</span>
      <span class="neirong">{{ t.neirong }}</span>
    </div>
  </div>`,
};

const app = Vue.createApp(App);
app.config.globalProperties.Pingtai = Pingtai;
app.use(QuanjuZujian);
app.mount('#app');

window.Pingtai = Pingtai;
