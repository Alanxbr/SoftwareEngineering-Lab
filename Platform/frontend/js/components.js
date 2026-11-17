/* 通用组件：状态徽标、弹窗、分页、空状态、折线图、数字卡、进度条 */

const ZhuangtaiBiao = {
  props: { zhi: String, leixing: { type: String, default: 'renwu' } },
  computed: {
    xinxi() { return Pingtai.qu_zhuangtai(this.leixing, this.zhi); },
  },
  template: `
    <span class="zhuangtai" :class="xinxi.c">
      <span class="dian"></span>{{ xinxi.t }}
    </span>`,
};

const TanChuang = {
  props: {
    biaoti: { type: String, default: '' },
    kuan: { type: Boolean, default: false },
  },
  emits: ['guanbi'],
  mounted() {
    this._anjian = (e) => { if (e.key === 'Escape') this.$emit('guanbi'); };
    window.addEventListener('keydown', this._anjian);
    document.body.style.overflow = 'hidden';
  },
  unmounted() {
    window.removeEventListener('keydown', this._anjian);
    document.body.style.overflow = '';
  },
  template: `
    <teleport to="body">
      <div class="zhezhao" @click.self="$emit('guanbi')">
        <div class="tanchuang" :class="{ kuan: kuan }" role="dialog">
          <div class="tanchuang-tou">
            <h3>{{ biaoti }}</h3>
            <button class="guan" @click="$emit('guanbi')" aria-label="关闭">×</button>
          </div>
          <div class="tanchuang-shen"><slot></slot></div>
          <div class="tanchuang-jiao" v-if="$slots.jiao"><slot name="jiao"></slot></div>
        </div>
      </div>
    </teleport>`,
};

const FenYe = {
  props: {
    zongshu: { type: Number, default: 0 },
    ye: { type: Number, default: 1 },
    meiye: { type: Number, default: 20 },
  },
  emits: ['gengxin'],
  computed: {
    zongye() { return Math.max(1, Math.ceil(this.zongshu / this.meiye)); },
  },
  template: `
    <div class="fenye" v-if="zongshu > 0">
      <span class="xinxi">共 {{ zongshu }} 条 · 第 {{ ye }} / {{ zongye }} 页</span>
      <button class="an xiao" :disabled="ye <= 1" @click="$emit('gengxin', ye - 1)">上一页</button>
      <button class="an xiao" :disabled="ye >= zongye" @click="$emit('gengxin', ye + 1)">下一页</button>
    </div>`,
};

const KongZhuang = {
  props: {
    ming: { type: String, default: '暂无数据' },
    fu: { type: String, default: '' },
    tubiao: { type: String, default: '📭' },
  },
  template: `
    <div class="kong">
      <div class="tubiao">{{ tubiao }}</div>
      <div class="ming">{{ ming }}</div>
      <div class="fu" v-if="fu">{{ fu }}</div>
      <slot></slot>
    </div>`,
};

const ShuziKa = {
  props: {
    biaoti: String,
    zhi: [String, Number],
    fu: String,
    tubiao: { type: String, default: '📊' },
    se: { type: String, default: '' },
  },
  template: `
    <div class="shuzi-ka" :class="se">
      <div class="tubiao">{{ tubiao }}</div>
      <div class="tou">{{ biaoti }}</div>
      <div class="zhi">{{ zhi }}</div>
      <div class="fu" v-if="fu">{{ fu }}</div>
    </div>`,
};

const JinduTiao = {
  props: {
    zhi: { type: Number, default: 0 },
    se: { type: String, default: '' },
  },
  computed: {
    baifen() { return Math.max(0, Math.min(100, Number(this.zhi) * 100)); },
  },
  template: `
    <div class="jindu" :class="se">
      <span :style="{ width: baifen + '%' }"></span>
    </div>`,
};

const ZhexianTu = {
  props: {
    shuju: { type: Array, default: () => [] },
    yanseq: { type: String, default: '#2a78d6' },
    yiming: { type: String, default: '' },
    geshihua: { type: Function, default: (v) => v },
    zuixiao: { type: Number, default: null },
    zuida: { type: Number, default: null },
  },
  template: `<div ref="rongqi" class="tubiao-kuang"></div>`,
  mounted() {
    this.tubiao = echarts.init(this.$refs.rongqi, null, { renderer: 'canvas' });
    this._gaibian = () => { this.tubiao && this.tubiao.resize(); };
    window.addEventListener('resize', this._gaibian);
    if (window.ResizeObserver) {
      this._guancha = new ResizeObserver(this._gaibian);
      this._guancha.observe(this.$refs.rongqi);
    }
    this.gengxin();
  },
  unmounted() {
    window.removeEventListener('resize', this._gaibian);
    if (this._guancha) this._guancha.disconnect();
    if (this.tubiao) { this.tubiao.dispose(); this.tubiao = null; }
  },
  watch: {
    shuju: { deep: true, handler() { this.gengxin(); } },
  },
  methods: {
    gengxin() {
      if (!this.tubiao) return;
      if (!this.shuju.length) {
        this.tubiao.clear();
        this.tubiao.setOption({
          title: {
            text: '暂无轮次数据',
            left: 'center',
            top: 'middle',
            textStyle: { color: '#898781', fontSize: 12, fontWeight: 'normal' },
          },
        });
        return;
      }
      const leibie = this.shuju.map((x) => '第 ' + x.x + ' 轮');
      const shuzhi = this.shuju.map((x) => Number(x.y));
      const yzhou = {
        type: 'value',
        name: this.yiming,
        nameTextStyle: { color: '#898781', fontSize: 11 },
        min: this.zuixiao,
        max: this.zuida,
        axisLabel: {
          color: '#898781',
          fontSize: 11,
          formatter: (v) => this.geshihua(v),
        },
        splitLine: { lineStyle: { color: '#eeece6', width: 1 } },
        axisLine: { show: false },
        axisTick: { show: false },
      };
      this.tubiao.setOption({
        grid: { left: 54, right: 18, top: 26, bottom: 34 },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'line', lineStyle: { color: '#c3c2b7' } },
          backgroundColor: '#ffffff',
          borderColor: 'rgba(11,11,11,.12)',
          textStyle: { color: '#0b0b0b', fontSize: 12 },
          formatter: (xiang) => {
            const dian = xiang[0];
            return leibie[dian.dataIndex] + '<br/>' +
              this.yiming + '：<b>' + this.geshihua(dian.value) + '</b>';
          },
        },
        xAxis: {
          type: 'category',
          data: leibie,
          boundaryGap: false,
          axisLabel: { color: '#898781', fontSize: 11 },
          axisLine: { lineStyle: { color: '#c3c2b7' } },
          axisTick: { show: false },
        },
        yAxis: yzhou,
        series: [{
          type: 'line',
          data: shuzhi,
          smooth: false,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { width: 2, color: this.yanseq },
          itemStyle: { color: this.yanseq, borderColor: '#ffffff', borderWidth: 2 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: this.yanseq + '2e' },
              { offset: 1, color: this.yanseq + '00' },
            ]),
          },
          emphasis: { scale: 1.3 },
        }],
      }, true);
    },
  },
};

const ZhengzaiJiazai = {
  template: `
    <div class="kong">
      <div class="tubiao">⏳</div>
      <div class="fu">正在加载…</div>
    </div>`,
};

const QuanjuZujian = {
  install(app) {
    app.component('zhuangtai-biao', ZhuangtaiBiao);
    app.component('tan-chuang', TanChuang);
    app.component('fen-ye', FenYe);
    app.component('kong-zhuang', KongZhuang);
    app.component('shuzi-ka', ShuziKa);
    app.component('jindu-tiao', JinduTiao);
    app.component('zhe-xian-tu', ZhexianTu);
    app.component('zhengzai-jiazai', ZhengzaiJiazai);
  },
};
