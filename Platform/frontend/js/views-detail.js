/* 页面：任务详情、参与方中心、管理页面、关于 */

const RenwuXiangqingShiTu = {
  data() {
    return {
      renwu: null, quxian: null, yinsi: null,
      jiazai: true, cuowu: '',
      zidong: true, dingshi: null,
      guanli_tan: false, guanli_yuanyin: '管理员操作', guanli_zhong: false,
      qidong_zhong: false,
    };
  },
  computed: {
    renwu_id() {
      const bufen = Pingtai.qu_canshu_lujing(Pingtai.zhuangtai.luxian);
      return Number(bufen[1]);
    },
    yonghu() { return Pingtai.zhuangtai.yonghu || {}; },
    shi_guanli() { return this.yonghu.jiaose === 'guanliyuan'; },
    neng_qidong() {
      return this.renwu && this.renwu.zhuangtai === 'daichufa' &&
        (this.shi_guanli || this.renwu.chuangjianzhe_id === this.yonghu.id);
    },
    sunshi_dian() {
      return ((this.quxian && this.quxian.rounds) || []).map((x) => ({ x: x.lunci, y: x.sunshi }));
    },
    zhunque_dian() {
      return ((this.quxian && this.quxian.rounds) || []).map((x) => ({ x: x.lunci, y: x.zhunquelv }));
    },
    yusuan() { return (this.renwu && this.renwu.yusuan) || {}; },
    yusuan_bu_zu() {
      const y = this.yusuan;
      return y.shengyu !== undefined && y.shengyu < y.meilun_eps;
    },
  },
  methods: {
    async jiazai_shuju(anjing = false) {
      if (!anjing) this.jiazai = true;
      try {
        const [renwu, quxian, yinsi] = await Promise.all([
          Pingtai.qingqiu('GET', '/xunlian/' + this.renwu_id),
          Pingtai.qingqiu('GET', '/xunlian/' + this.renwu_id + '/quxian'),
          Pingtai.qingqiu('GET', '/xunlian/' + this.renwu_id + '/yinsi'),
        ]);
        this.renwu = renwu;
        this.quxian = quxian;
        this.yinsi = yinsi;
        this.cuowu = '';
        this.guan_dingshi();
      } catch (e) {
        this.cuowu = e.message;
        this.guan_dingshi();
      } finally {
        this.jiazai = false;
      }
    },
    guan_dingshi() {
      if (this.dingshi) { clearInterval(this.dingshi); this.dingshi = null; }
      if (this.zidong && this.renwu && this.renwu.zhuangtai === 'xunlianzhong') {
        this.dingshi = setInterval(() => this.jiazai_shuju(true), 3000);
      }
    },
    qiehuan_zidong() {
      this.zidong = !this.zidong;
      this.guan_dingshi();
    },
    async qidong() {
      if (!confirm('启动训练后将在后台逐轮聚合，确定启动吗？')) return;
      this.qidong_zhong = true;
      try {
        const jieguo = await Pingtai.qingqiu('POST', '/xunlian/' + this.renwu_id + '/qidong');
        this.renwu = jieguo;
        Pingtai.tishi('训练已启动', 'good');
        await this.jiazai_shuju(true);
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.qidong_zhong = false;
      }
    },
    async shezhi_zhuangtai(mubiao) {
      this.guanli_zhong = true;
      try {
        await Pingtai.qingqiu('PATCH', '/guanli/renwu/' + this.renwu_id, {
          zhuangtai: mubiao,
          yuanyin: this.guanli_yuanyin || '管理员操作',
        });
        Pingtai.tishi(mubiao === 'yichang' ? '已标记为异常' : '任务已取消', 'good');
        this.guanli_tan = false;
        this.jiazai_shuju(true);
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.guanli_zhong = false;
      }
    },
    hui_qu() { Pingtai.tiaozhuan('/tasks'); },
    geshihua: Pingtai.geshihua_shijian,
    shuliang: Pingtai.shuliang,
    baifen: Pingtai.bili_zhi,
    wenjian_ming(lujing) {
      if (!lujing) return '—';
      return String(lujing).split(/[\\/]/).pop();
    },
    xiaoshu(zhi, wei) { return Number(zhi || 0).toFixed(wei); },
  },
  watch: {
    zidong() { this.guan_dingshi(); },
  },
  mounted() { this.jiazai_shuju(); },
  unmounted() { if (this.dingshi) clearInterval(this.dingshi); },
  template: `
  <div class="zhankai-zhuti">
    <div class="an-zu">
      <div>
        <button class="an xiao wenzi" @click="hui_qu">← 返回任务列表</button>
        <h2 style="font-size:21px;margin-top:10px">
          <span v-if="renwu">#{{ renwu.id }} {{ renwu.mingcheng }}</span>
          <span v-else>训练任务</span>
          <zhuangtai-biao v-if="renwu" :zhi="renwu.zhuangtai" leixing="renwu" style="margin-left:8px;vertical-align:3px"></zhuangtai-biao>
        </h2>
        <div class="wenben-ruo" style="margin-top:7px;font-size:12.5px" v-if="renwu">
          创建者 {{ renwu.chuangjianzhe_ming }} · {{ Pingtai.MOSHI_MING[renwu.yunxing_moshi] }} ·
          模型 {{ renwu.moxing_leixing }} · 创建于 {{ geshihua(renwu.chuangjian_shijian) }}
        </div>
      </div>
      <div class="an-zu" style="margin-left:auto" v-if="renwu">
        <label class="fuxuan" :class="{ xuan: zidong }" style="cursor:pointer">
          <input type="checkbox" :checked="zidong" @change="qiehuan_zidong">
          自动刷新
        </label>
        <button class="an" @click="jiazai_shuju(false)">刷新</button>
        <button v-if="neng_qidong" class="an zhuyi" @click="qidong" :disabled="qidong_zhong">
          {{ qidong_zhong ? '启动中…' : '启动训练' }}
        </button>
        <button v-if="shi_guanli && renwu.zhuangtai === 'xunlianzhong'"
                class="an weixian" @click="guanli_tan = true">强制终止</button>
        <button v-if="shi_guanli && renwu.zhuangtai === 'xunlianzhong'"
                class="an" @click="guanli_tan = true; guanli_yuanyin = '训练指标异常'">标记异常</button>
      </div>
    </div>

    <div v-if="cuowu" class="jian-tishi bad">{{ cuowu }}</div>
    <div v-if="renwu && renwu.zhuangtai === 'yichang'" class="jian-tishi bad">
      <b>任务异常：</b>{{ renwu.cuowu_xiaoxi || '训练过程中断' }}
    </div>

    <zhengzai-jiazai v-if="jiazai && !renwu"></zhengzai-jiazai>

    <template v-if="renwu">
      <div class="kapian">
        <div class="kapian-tou">
          <h3>训练概况</h3>
          <span class="fu">{{ renwu.dangqian_lunci }} / {{ renwu.lunshu }} 轮已完成</span>
          <div class="you"><span class="fu">进度 {{ baifen(renwu.jindu) }}</span></div>
        </div>
        <div class="kapian-shen">
          <jindu-tiao :zhi="renwu.jindu" :se="renwu.zhuangtai === 'yiwancheng' ? 'good' : (renwu.zhuangtai === 'yichang' ? 'bad' : '')"></jindu-tiao>
          <div class="yusuan-lie" style="grid-template-columns:repeat(4,1fr)">
            <div class="yusuan-xiang"><div class="jian">参与方</div><div class="zhi">{{ renwu.canjiafang.length }}</div></div>
            <div class="yusuan-xiang"><div class="jian">样本总量</div><div class="zhi">{{ shuliang(renwu.canjiafang.reduce((s, x) => s + x.yangben_shu, 0)) }}</div></div>
            <div class="yusuan-xiang"><div class="jian">当前损失</div><div class="zhi">{{ renwu.lunci.length ? xiaoshu(renwu.lunci[renwu.lunci.length - 1].sunshi, 4) : '—' }}</div></div>
            <div class="yusuan-xiang"><div class="jian">当前准确率</div><div class="zhi">{{ renwu.lunci.length ? baifen(renwu.lunci[renwu.lunci.length - 1].zhunquelv) : '—' }}</div></div>
          </div>
        </div>
      </div>

      <div class="liang-lan">
        <div class="kapian">
          <div class="kapian-tou">
            <h3>损失曲线</h3>
            <span class="fu">越低越好</span>
            <div class="you"><span class="fu" v-if="quxian && quxian.zuiyou">最优轮次 第 {{ quxian.zuiyou.lunci }} 轮</span></div>
          </div>
          <div class="kapian-shen">
            <zhe-xian-tu :shuju="sunshi_dian" yanseq="#2a78d6" yiming="损失"
                         :geshihua="(v) => Number(v).toFixed(4)"></zhe-xian-tu>
          </div>
        </div>
        <div class="kapian">
          <div class="kapian-tou">
            <h3>准确率曲线</h3>
            <span class="fu">越高越好</span>
            <div class="you"><span class="fu" v-if="quxian && quxian.zuiyou">最优 {{ baifen(quxian.zuiyou.zhunquelv) }}</span></div>
          </div>
          <div class="kapian-shen">
            <zhe-xian-tu :shuju="zhunque_dian" yanseq="#eb6834" yiming="准确率"
                         :zuixiao="0" :zuida="1" :geshihua="(v) => (Number(v) * 100).toFixed(1) + '%'"></zhe-xian-tu>
          </div>
        </div>
      </div>

      <div class="san-lan">
        <div class="kapian">
          <div class="kapian-tou">
            <h3>轮次记录</h3>
            <span class="fu">每轮聚合后落库</span>
          </div>
          <div class="biaoge-kuang">
            <table class="biaoge">
              <thead><tr>
                <th>轮次</th><th>损失</th><th>准确率</th><th>耗时</th>
                <th>参与方</th><th>参数文件</th><th>时间</th>
              </tr></thead>
              <tbody>
                <tr v-for="r in renwu.lunci.slice().reverse()" :key="r.lunci_hao">
                  <td class="tabular">
                    第 {{ r.lunci_hao }} 轮
                    <span v-if="quxian && quxian.zuiyou && quxian.zuiyou.lunci === r.lunci_hao"
                          class="zhuangtai good" style="margin-left:4px"><span class="dian"></span>最优</span>
                  </td>
                  <td class="tabular">{{ xiaoshu(r.sunshi, 4) }}</td>
                  <td class="tabular">{{ baifen(r.zhunquelv) }}</td>
                  <td class="tabular">{{ xiaoshu(r.haoshi, 2) }} s</td>
                  <td class="tabular">{{ r.canjia_shu }}</td>
                  <td class="mono" style="font-size:11.5px">{{ wenjian_ming(r.canshu_wenjian) }}</td>
                  <td class="wenben-ruo">{{ geshihua(r.chuangjian_shijian) }}</td>
                </tr>
                <tr v-if="!renwu.lunci.length">
                  <td colspan="7"><kong-zhuang ming="还没有完成任何轮次" fu="启动训练后每轮结束会生成一条记录"></kong-zhuang></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div style="display:flex;flex-direction:column;gap:16px">
          <div class="kapian">
            <div class="kapian-tou"><h3>隐私预算</h3><span class="fu">差分隐私</span></div>
            <div class="kapian-shen">
              <div class="yusuan-tou">
                <span class="da tabular">{{ yusuan.leiji_eps }}</span>
                <span class="xiao">/ {{ yusuan.shangxian }} ε 已使用</span>
              </div>
              <div style="margin-top:10px">
                <jindu-tiao :zhi="yusuan.shiyong_lv"
                            :se="yusuan.shiyong_lv >= 1 ? 'bad' : (yusuan.shiyong_lv > 0.7 ? 'warn' : '')"></jindu-tiao>
                <div class="fu" style="margin-top:5px">预算使用率 {{ baifen(yusuan.shiyong_lv) }}</div>
              </div>
              <div class="yusuan-lie">
                <div class="yusuan-xiang"><div class="jian">每轮 ε</div><div class="zhi">{{ yusuan.meilun_eps }}</div></div>
                <div class="yusuan-xiang"><div class="jian">剩余 ε</div><div class="zhi">{{ yusuan.shengyu }}</div></div>
                <div class="yusuan-xiang"><div class="jian">裁剪阈值 C</div><div class="zhi">{{ yusuan.jiancai_yuzhi }}</div></div>
              </div>
              <div v-if="yusuan_bu_zu" class="jian-tishi warn" style="margin-top:12px">
                剩余预算不足以支撑下一轮，训练将在预算耗尽时停止。
              </div>
              <div class="fenge" v-if="yinsi && yinsi.jilu && yinsi.jilu.length"></div>
              <div v-if="yinsi && yinsi.jilu && yinsi.jilu.length">
                <div class="fu" style="margin-bottom:6px">逐轮预算明细</div>
                <table class="biaoge">
                  <thead><tr><th>轮次</th><th>本轮 ε</th><th>累计 ε</th></tr></thead>
                  <tbody>
                    <tr v-for="j in yinsi.jilu.slice().reverse()" :key="j.id">
                      <td class="tabular">第 {{ j.lunci_hao }} 轮</td>
                      <td class="tabular">{{ j.benlun_eps }}</td>
                      <td class="tabular">{{ j.leiji_eps }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div class="kapian">
            <div class="kapian-tou"><h3>参与方</h3><span class="fu">{{ renwu.canjiafang.length }} 方</span></div>
            <div class="kapian-shen" style="padding-top:4px">
              <div v-for="c in renwu.canjiafang" :key="c.id" style="padding:10px 0;border-bottom:1px solid var(--biankuang-ruo)">
                <div class="an-zu">
                  <div>
                    <div style="font-size:13px;font-weight:600">{{ c.yonghuming }}</div>
                    <div class="fu" style="font-size:11.5px">{{ c.shujuji_ming }}</div>
                  </div>
                  <div style="margin-left:auto;text-align:right">
                    <zhuangtai-biao :zhi="c.zhuangtai" leixing="canjia"></zhuangtai-biao>
                    <div class="fu tabular" style="font-size:11.5px;margin-top:3px">{{ shuliang(c.yangben_shu) }} 样本</div>
                  </div>
                </div>
              </div>
              <div v-if="!renwu.canjiafang.length" class="wenben-ruo" style="padding:14px 0">没有参与方</div>
            </div>
          </div>
        </div>
      </div>

      <div class="kapian">
        <div class="kapian-tou"><h3>训练配置</h3></div>
        <div class="kapian-shen">
          <div class="xinxi-ge">
            <div class="xinxi-xiang"><div class="jian">模型</div><div class="zhi">{{ renwu.moxing_leixing }}</div></div>
            <div class="xinxi-xiang"><div class="jian">运行模式</div><div class="zhi">{{ Pingtai.MOSHI_MING[renwu.yunxing_moshi] }}</div></div>
            <div class="xinxi-xiang"><div class="jian">训练轮数</div><div class="zhi">{{ renwu.lunshu }}</div></div>
            <div class="xinxi-xiang"><div class="jian">批大小</div><div class="zhi">{{ renwu.piliang_daxiao }}</div></div>
            <div class="xinxi-xiang"><div class="jian">学习率</div><div class="zhi tabular">{{ renwu.xuexilv }}</div></div>
            <div class="xinxi-xiang"><div class="jian">每轮 ε</div><div class="zhi tabular">{{ renwu.yinsipi }}</div></div>
            <div class="xinxi-xiang"><div class="jian">裁剪阈值</div><div class="zhi tabular">{{ renwu.jiancai_yuzhi }}</div></div>
            <div class="xinxi-xiang"><div class="jian">预算上限</div><div class="zhi tabular">{{ renwu.yusuan_shangxian }}</div></div>
            <div class="xinxi-xiang"><div class="jian">创建时间</div><div class="zhi">{{ geshihua(renwu.chuangjian_shijian) }}</div></div>
            <div class="xinxi-xiang"><div class="jian">启动时间</div><div class="zhi">{{ geshihua(renwu.qidong_shijian) }}</div></div>
            <div class="xinxi-xiang"><div class="jian">结束时间</div><div class="zhi">{{ geshihua(renwu.jieshu_shijian) }}</div></div>
            <div class="xinxi-xiang"><div class="jian">任务编号</div><div class="zhi tabular">#{{ renwu.id }}</div></div>
          </div>
        </div>
      </div>
    </template>

    <tan-chuang v-if="guanli_tan" biaoti="管理员操作" @guanbi="guanli_tan = false">
      <div class="biaodan">
        <div class="jian-tishi warn">任务会立即停止聚合，正在训练的轮次不会写入结果。操作会记入系统日志。</div>
        <div class="ziduan">
          <label>操作原因</label>
          <input class="shuru" v-model.trim="guanli_yuanyin" maxlength="200" placeholder="例如：数据源异常、演示结束">
        </div>
      </div>
      <template #jiao>
        <button class="an" @click="guanli_tan = false">取消</button>
        <button class="an" @click="shezhi_zhuangtai('yichang')" :disabled="guanli_zhong">标记异常</button>
        <button class="an weixian" @click="shezhi_zhuangtai('yiquxiao')" :disabled="guanli_zhong">取消任务</button>
      </template>
    </tan-chuang>
  </div>`,
};

const KehuduanShiTu = {
  data() {
    return {
      renwu: [], xuanzhong: null, xiangqing: null, jiazai: true, jiazai_xiangqing: false,
      biaodan: { lunci_hao: 1, yangben_shu: 0, sunshi: 0, zhunquelv: 0, haoshi: 0, gengxin_text: '' },
      tijiao_zhong: false, cuowu: '',
    };
  },
  computed: {
    yonghu() { return Pingtai.zhuangtai.yonghu || {}; },
    gengxin_shuzi() {
      return this.biaodan.gengxin_text.split(/[\s,，;；]+/).filter(Boolean).map(Number);
    },
    gengxin_hefa() {
      const a = this.gengxin_shuzi;
      return a.length === (this.xiangqing ? this.xiangqing.canshu_weidu : -1) &&
        a.every((x) => Number.isFinite(x));
    },
    neng_tijiao() {
      const x = this.xiangqing;
      return x && x.zhuangtai === 'xunlianzhong' && !x.yijing_tijiao &&
        this.gengxin_hefa && Number(this.biaodan.yangben_shu) > 0;
    },
    canshu_yulan() {
      return ((this.xiangqing && this.xiangqing.canshu) || []).slice(0, 8);
    },
  },
  methods: {
    async jiazai_shuju() {
      this.jiazai = true;
      try {
        this.renwu = await Pingtai.qingqiu('GET', '/kehuduan/renwu');
        if (this.renwu.length && !this.xuanzhong) this.xuanze(this.renwu[0].id);
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.jiazai = false;
      }
    },
    async xuanze(id) {
      this.xuanzhong = id;
      this.jiazai_xiangqing = true;
      this.cuowu = '';
      try {
        const x = await Pingtai.qingqiu('GET', '/kehuduan/renwu/' + id);
        this.xiangqing = x;
        this.biaodan.lunci_hao = Math.max(1, x.dangqian_lunci);
        this.biaodan.yangben_shu = x.yangben_shu;
        this.biaodan.gengxin_text = '';
      } catch (e) {
        this.cuowu = e.message;
        this.xiangqing = null;
      } finally {
        this.jiazai_xiangqing = false;
      }
    },
    shengcheng() {
      const weidu = (this.xiangqing && this.xiangqing.canshu_weidu) || 178;
      const canshu = Array.from({ length: weidu }, () => {
        const zhi = (Math.random() * 0.2 - 0.1);
        return Number(zhi.toFixed(6));
      });
      this.biaodan.gengxin_text = canshu.join(', ');
    },
    async tijiao() {
      if (!this.gengxin_hefa) {
        Pingtai.tishi('更新向量维度必须为 ' + this.xiangqing.canshu_weidu, 'warn');
        return;
      }
      this.tijiao_zhong = true;
      try {
        await Pingtai.qingqiu('POST', '/kehuduan/renwu/' + this.xuanzhong + '/tijiao', {
          lunci_hao: Number(this.biaodan.lunci_hao),
          gengxin: this.gengxin_shuzi,
          yangben_shu: Number(this.biaodan.yangben_shu),
          sunshi: Number(this.biaodan.sunshi) || 0,
          zhunquelv: Number(this.biaodan.zhunquelv) || 0,
          haoshi: Number(this.biaodan.haoshi) || 0,
        });
        Pingtai.tishi('本地更新已提交，等待服务端聚合', 'good');
        this.xuanze(this.xuanzhong);
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.tijiao_zhong = false;
      }
    },
    qu_xiangqing(id) { Pingtai.tiaozhuan('/tasks/' + id); },
    baifen: Pingtai.bili_zhi,
    shuliang: Pingtai.shuliang,
  },
  mounted() { this.jiazai_shuju(); },
  template: `
  <div class="zhankai-zhuti">
    <div>
      <h2 style="font-size:21px">参与方中心</h2>
      <div class="wenben-ruo" style="margin-top:6px;font-size:12.5px">
        真实联邦模式下，参与方在这里领取当前轮全局参数，提交本地训练得到的加噪更新
      </div>
    </div>

    <div class="liang-lan">
      <div class="kapian">
        <div class="kapian-tou"><h3>我参与的任务</h3><span class="fu">最多 50 条</span></div>
        <div class="kapian-shen" style="padding:10px 18px">
          <div v-for="x in renwu" :key="x.id"
               style="padding:12px 12px;border-radius:10px;cursor:pointer;border:1px solid transparent"
               :style="xuanzhong === x.id ? { background: '#eaf2fd', borderColor: '#2a78d6' } : {}"
               @click="xuanze(x.id)">
            <div class="an-zu">
              <div>
                <div style="font-size:13.5px;font-weight:600">#{{ x.id }} {{ x.mingcheng }}</div>
                <div class="fu" style="font-size:11.5px;margin-top:3px">
                  {{ Pingtai.MOSHI_MING[x.yunxing_moshi] }} · 第 {{ x.dangqian_lunci }} / {{ x.lunshu }} 轮
                </div>
              </div>
              <div style="margin-left:auto"><zhuangtai-biao :zhi="x.canjia_zhuangtai" leixing="canjia"></zhuangtai-biao></div>
            </div>
          </div>
          <kong-zhuang v-if="!renwu.length && !jiazai" ming="你还没有参与任何训练任务"
                       fu="被数据使用方加入任务后，这里会显示当前轮次和全局参数"></kong-zhuang>
          <kong-zhuang v-if="jiazai && !renwu.length" ming="正在加载…"></kong-zhuang>
        </div>
      </div>

      <div class="kapian" v-if="xiangqing">
        <div class="kapian-tou">
          <h3>当前轮次与全局参数</h3>
          <div class="you">
            <button class="an xiao wenzi" @click="qu_xiangqing(xuanzhong)">任务详情 →</button>
          </div>
        </div>
        <div class="kapian-shen">
          <div class="xinxi-ge" style="border-top:0">
            <div class="xinxi-xiang" style="border-right:0"><div class="jian">任务状态</div>
              <div class="zhi"><zhuangtai-biao :zhi="xiangqing.zhuangtai" leixing="renwu"></zhuangtai-biao></div></div>
            <div class="xinxi-xiang"><div class="jian">当前轮次</div>
              <div class="zhi tabular">{{ xiangqing.dangqian_lunci }} / {{ xiangqing.zong_lunshu }}</div></div>
            <div class="xinxi-xiang" style="border-right:0"><div class="jian">本轮是否已提交</div>
              <div class="zhi">
                <span class="zhuangtai" :class="xiangqing.yijing_tijiao ? 'good' : 'warn'">
                  <span class="dian"></span>{{ xiangqing.yijing_tijiao ? '已提交' : '待提交' }}
                </span>
              </div></div>
            <div class="xinxi-xiang"><div class="jian">本地样本数</div><div class="zhi tabular">{{ shuliang(xiangqing.yangben_shu) }}</div></div>
            <div class="xinxi-xiang" style="border-right:0;border-bottom:0"><div class="jian">学习率 / 批大小</div>
              <div class="zhi tabular">{{ xiangqing.xuexilv }} / {{ xiangqing.piliang_daxiao }}</div></div>
            <div class="xinxi-xiang" style="border-bottom:0"><div class="jian">每轮 ε / 裁剪 C</div>
              <div class="zhi tabular">{{ xiangqing.yinsipi }} / {{ xiangqing.jiancai_yuzhi }}</div></div>
          </div>

          <div class="fenge"></div>
          <div class="ziduan">
            <label>全局模型参数（{{ xiangqing.canshu_weidu }} 维，预览前 8 维）</label>
            <div class="ji-kuang">
              <span class="ji mono" v-for="(v, i) in canshu_yulan" :key="i">{{ Number(v).toFixed(5) }}</span>
              <span class="ji">…</span>
            </div>
            <span class="shuoming">完整参数通过接口返回；本地训练时从该参数出发，按差分隐私要求裁剪并加噪后再提交。</span>
          </div>

          <div class="fenge"></div>
          <div class="biaodan">
            <div class="hang-3">
              <div class="ziduan">
                <label>轮次</label>
                <input class="shuru" type="number" v-model.number="biaodan.lunci_hao" readonly>
              </div>
              <div class="ziduan">
                <label>样本数 <span class="xing">*</span></label>
                <input class="shuru" type="number" min="1" v-model.number="biaodan.yangben_shu">
              </div>
              <div class="ziduan">
                <label>本地耗时（秒）</label>
                <input class="shuru" type="number" min="0" step="0.1" v-model.number="biaodan.haoshi">
              </div>
            </div>
            <div class="hang">
              <div class="ziduan">
                <label>本地损失</label>
                <input class="shuru" type="number" min="0" step="0.0001" v-model.number="biaodan.sunshi">
              </div>
              <div class="ziduan">
                <label>本地准确率（0-1）</label>
                <input class="shuru" type="number" min="0" max="1" step="0.01" v-model.number="biaodan.zhunquelv">
              </div>
            </div>
            <div class="ziduan">
              <label>模型更新向量 <span class="xing">*</span></label>
              <textarea class="duohang mono" v-model="biaodan.gengxin_text" rows="5"
                        placeholder="178 个浮点数，用逗号或空格分隔"></textarea>
              <span class="shuoming" :style="{ color: gengxin_hefa ? 'var(--chenggong)' : 'var(--jinggao)' }">
                已解析 {{ gengxin_shuzi.length }} / {{ xiangqing.canshu_weidu }} 维，服务端会按任务裁剪阈值再裁剪一次
              </span>
            </div>
            <div class="an-zu">
              <button class="an" @click="shengcheng">生成随机更新</button>
              <button class="an zhuyi" @click="tijiao" :disabled="!neng_tijiao || tijiao_zhong">
                {{ tijiao_zhong ? '提交中…' : '提交本地更新' }}
              </button>
            </div>
            <div v-if="xiangqing.zhuangtai !== 'xunlianzhong'" class="jian-tishi warn">
              任务当前不在训练中，无法提交更新。
            </div>
            <div v-else-if="xiangqing.yijing_tijiao" class="jian-tishi">
              本轮已提交。等待其他参与方，服务端聚合后轮次会推进。
            </div>
          </div>
        </div>
      </div>

      <div class="kapian" v-else>
        <div class="kapian-shen">
          <kong-zhuang :ming="jiazai_xiangqing ? '正在读取…' : (cuowu || '请选择左侧任务')" fu="任务处于真实联邦模式时才有待提交的更新"></kong-zhuang>
        </div>
      </div>
    </div>

    <div class="kapian">
      <div class="kapian-tou"><h3>真实联邦流程说明</h3></div>
      <div class="kapian-shen">
        <div class="xinxi-ge" style="border-top:0">
          <div class="xinxi-xiang" style="border-right:0"><div class="jian">第 1 步</div><div class="zhi">服务端下发当前轮全局参数</div></div>
          <div class="xinxi-xiang"><div class="jian">第 2 步</div><div class="zhi">参与方本地训练并做 L2 裁剪</div></div>
          <div class="xinxi-xiang"><div class="jian">第 3 步</div><div class="zhi">按 b = C / (ε√d) 加噪后提交</div></div>
          <div class="xinxi-xiang" style="border-right:0;border-bottom:0"><div class="jian">第 4 步</div><div class="zhi">服务端按样本数加权聚合并记账</div></div>
        </div>
      </div>
    </div>
  </div>`,
};

const YonghuGuanliShiTu = {
  data() {
    return { liebiao: [], zongshu: 0, ye: 1, meiye: 20, jiazai: true };
  },
  methods: {
    async jiazai_shuju() {
      this.jiazai = true;
      try {
        const jieguo = await Pingtai.qingqiu('GET', '/guanli/yonghu?ye=' + this.ye + '&meiye=' + this.meiye);
        this.liebiao = jieguo.items;
        this.zongshu = jieguo.total;
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.jiazai = false;
      }
    },
    async qiehuan(x) {
      const mubiao = x.zhuangtai === 'zhengchang' ? 'tingyong' : 'zhengchang';
      const dongzuo = mubiao === 'tingyong' ? '停用' : '恢复';
      if (!confirm('确定' + dongzuo + '账号「' + x.yonghuming + '」吗？')) return;
      try {
        await Pingtai.qingqiu('PATCH', '/guanli/yonghu/' + x.id, { zhuangtai: mubiao });
        Pingtai.tishi('账号已' + dongzuo, 'good');
        this.jiazai_shuju();
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      }
    },
    qu_ye(p) { this.ye = p; this.jiazai_shuju(); },
    geshihua: Pingtai.geshihua_shijian,
  },
  mounted() { this.jiazai_shuju(); },
  template: `
  <div class="zhankai-zhuti">
    <div>
      <h2 style="font-size:21px">用户管理</h2>
      <div class="wenben-ruo" style="margin-top:6px;font-size:12.5px">管理员可停用或恢复普通账号；管理员账号受保护，不能在此修改</div>
    </div>
    <div class="kapian">
      <div class="kapian-tou"><h3>账号列表</h3><span class="fu">共 {{ zongshu }} 个</span></div>
      <div class="biaoge-kuang">
        <table class="biaoge">
          <thead><tr>
            <th>用户名</th><th>邮箱</th><th>角色</th><th>状态</th><th>注册时间</th><th class="caozuo">操作</th>
          </tr></thead>
          <tbody>
            <tr v-for="x in liebiao" :key="x.id">
              <td>
                <div class="zhu">#{{ x.id }} {{ x.yonghuming }}</div>
                <div class="fu">ID {{ x.id }}</div>
              </td>
              <td>{{ x.youxiang }}</td>
              <td><span class="ji">{{ Pingtai.jiaose_ming(x.jiaose) }}</span></td>
              <td><zhuangtai-biao :zhi="x.zhuangtai" leixing="yonghu"></zhuangtai-biao></td>
              <td class="wenben-ruo">{{ geshihua(x.chuangjian_shijian) }}</td>
              <td class="caozuo">
                <button v-if="x.jiaose !== 'guanliyuan'" class="an xiao"
                        :class="{ weixian: x.zhuangtai === 'zhengchang' }" @click="qiehuan(x)">
                  {{ x.zhuangtai === 'zhengchang' ? '停用' : '恢复' }}
                </button>
                <span v-else class="wenben-ruo">受保护</span>
              </td>
            </tr>
            <tr v-if="!liebiao.length">
              <td colspan="6"><kong-zhuang :ming="jiazai ? '正在加载…' : '没有用户'"></kong-zhuang></td>
            </tr>
          </tbody>
        </table>
      </div>
      <fen-ye :zongshu="zongshu" :ye="ye" :meiye="meiye" @gengxin="qu_ye"></fen-ye>
    </div>
  </div>`,
};

const RizhiShiTu = {
  data() {
    return {
      liebiao: [], zongshu: 0, ye: 1, meiye: 30, jiazai: true,
      shaixuan: { leixing: '', jieguo: '', yonghuming: '', kaishi: '', jieshu: '' },
    };
  },
  methods: {
    async jiazai_shuju() {
      this.jiazai = true;
      const s = this.shaixuan;
      const canshu = [];
      if (s.leixing) canshu.push('leixing=' + encodeURIComponent(s.leixing));
      if (s.jieguo) canshu.push('jieguo=' + encodeURIComponent(s.jieguo));
      if (s.yonghuming) canshu.push('yonghuming=' + encodeURIComponent(s.yonghuming));
      if (s.kaishi) canshu.push('kaishi=' + encodeURIComponent(s.kaishi));
      if (s.jieshu) canshu.push('jieshu=' + encodeURIComponent(s.jieshu + ' 23:59:59'));
      canshu.push('ye=' + this.ye, 'meiye=' + this.meiye);
      try {
        const jieguo = await Pingtai.qingqiu('GET', '/guanli/rizhi?' + canshu.join('&'));
        this.liebiao = jieguo.items;
        this.zongshu = jieguo.total;
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.jiazai = false;
      }
    },
    chaxun() { this.ye = 1; this.jiazai_shuju(); },
    qu_ye(p) { this.ye = p; this.jiazai_shuju(); },
    chongzhi() {
      this.shaixuan = { leixing: '', jieguo: '', yonghuming: '', kaishi: '', jieshu: '' };
      this.chaxun();
    },
    geshihua: Pingtai.geshihua_shijian,
  },
  mounted() { this.jiazai_shuju(); },
  template: `
  <div class="zhankai-zhuti">
    <div>
      <h2 style="font-size:21px">系统日志</h2>
      <div class="wenben-ruo" style="margin-top:6px;font-size:12.5px">登录、数据登记、任务状态变更与管理员操作全部留痕</div>
    </div>

    <div class="kapian">
      <div class="kapian-shen">
        <div class="hang-3">
          <div class="ziduan">
            <label>操作类型</label>
            <input class="shuru" v-model.trim="shaixuan.leixing" placeholder="例如：用户登录、启动训练">
          </div>
          <div class="ziduan">
            <label>结果</label>
            <select class="xuanze" v-model="shaixuan.jieguo">
              <option value="">全部</option>
              <option value="chenggong">成功</option>
              <option value="shibai">失败</option>
              <option value="yuequan">越权</option>
            </select>
          </div>
          <div class="ziduan">
            <label>操作者用户名</label>
            <input class="shuru" v-model.trim="shaixuan.yonghuming" placeholder="模糊匹配">
          </div>
        </div>
        <div class="hang">
          <div class="ziduan">
            <label>开始日期</label>
            <input class="shuru" type="date" v-model="shaixuan.kaishi">
          </div>
          <div class="ziduan">
            <label>结束日期</label>
            <input class="shuru" type="date" v-model="shaixuan.jieshu">
          </div>
        </div>
        <div class="an-zu">
          <button class="an zhuyi" @click="chaxun">查询</button>
          <button class="an" @click="chongzhi">重置</button>
        </div>
      </div>
    </div>

    <div class="kapian">
      <div class="kapian-tou"><h3>日志记录</h3><span class="fu">共 {{ zongshu }} 条</span></div>
      <div class="biaoge-kuang">
        <table class="biaoge">
          <thead><tr>
            <th>时间</th><th>操作者</th><th>类型</th><th>对象</th><th>结果</th><th>详情</th><th>IP</th>
          </tr></thead>
          <tbody>
            <tr v-for="x in liebiao" :key="x.id">
              <td class="wenben-ruo" style="white-space:nowrap">{{ geshihua(x.rizhi_shijian) }}</td>
              <td>{{ x.caozuozhe_ming || '—' }}</td>
              <td>{{ x.caozuo_leixing }}</td>
              <td><span class="ji">{{ x.duixiang_leixing }}<template v-if="x.duixiang_id">#{{ x.duixiang_id }}</template></span></td>
              <td><zhuangtai-biao :zhi="x.jieguo" leixing="rizhi"></zhuangtai-biao></td>
              <td class="wenben-ruo" style="max-width:320px">{{ x.xiangqing }}</td>
              <td class="mono" style="font-size:11.5px">{{ x.kehu_ip }}</td>
            </tr>
            <tr v-if="!liebiao.length">
              <td colspan="7"><kong-zhuang :ming="jiazai ? '正在加载…' : '没有匹配的日志'"></kong-zhuang></td>
            </tr>
          </tbody>
        </table>
      </div>
      <fen-ye :zongshu="zongshu" :ye="ye" :meiye="meiye" @gengxin="qu_ye"></fen-ye>
    </div>
  </div>`,
};

const BeifenShiTu = {
  data() {
    return { liebiao: [], jiazai: true, chuangjian_zhong: false };
  },
  methods: {
    async jiazai_shuju() {
      this.jiazai = true;
      try {
        this.liebiao = await Pingtai.qingqiu('GET', '/guanli/beifen');
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.jiazai = false;
      }
    },
    async chuangjian() {
      this.chuangjian_zhong = true;
      try {
        const jieguo = await Pingtai.qingqiu('POST', '/guanli/beifen');
        Pingtai.tishi('已生成备份 ' + jieguo.wenjian, 'good');
        this.jiazai_shuju();
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.chuangjian_zhong = false;
      }
    },
    async xiazai(w) {
      try {
        const xiangying = await fetch('/guanli/beifen/' + encodeURIComponent(w.wenjian), {
          headers: { Authorization: 'Bearer ' + Pingtai.zhuangtai.token },
        });
        if (!xiangying.ok) throw new Error('下载失败（HTTP ' + xiangying.status + '）');
        const liu = await xiangying.blob();
        const a = document.createElement('a');
        a.href = URL.createObjectURL(liu);
        a.download = w.wenjian;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(a.href);
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      }
    },
    daxiao: Pingtai.geshihua_daxiao,
  },
  mounted() { this.jiazai_shuju(); },
  template: `
  <div class="zhankai-zhuti">
    <div class="an-zu">
      <div>
        <h2 style="font-size:21px">数据备份</h2>
        <div class="wenben-ruo" style="margin-top:6px;font-size:12.5px">
          使用 SQLite 在线备份 API，备份过程不阻塞读写；最多保留最近 7 份
        </div>
      </div>
      <div style="margin-left:auto">
        <button class="an zhuyi" @click="chuangjian" :disabled="chuangjian_zhong">
          {{ chuangjian_zhong ? '备份中…' : '立即备份' }}
        </button>
      </div>
    </div>

    <div class="kapian">
      <div class="kapian-tou"><h3>备份文件</h3><span class="fu">共 {{ liebiao.length }} 份</span></div>
      <div class="biaoge-kuang">
        <table class="biaoge">
          <thead><tr><th>文件名</th><th>大小</th><th class="caozuo">操作</th></tr></thead>
          <tbody>
            <tr v-for="w in liebiao" :key="w.wenjian">
              <td class="mono">{{ w.wenjian }}</td>
              <td class="tabular">{{ daxiao(w.daxiao) }}</td>
              <td class="caozuo"><button class="an xiao" @click="xiazai(w)">下载</button></td>
            </tr>
            <tr v-if="!liebiao.length">
              <td colspan="3"><kong-zhuang :ming="jiazai ? '正在加载…' : '还没有备份'" fu="点击右上角立即备份生成第一份"></kong-zhuang></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>`,
};

const GuanyuShiTu = {
  data() { return { xinxi: null, jiankang: null }; },
  methods: {
    async jiazai_shuju() {
      try {
        [this.xinxi, this.jiankang] = await Promise.all([
          Pingtai.qingqiu('GET', '/xitong/xinxi'),
          Pingtai.qingqiu('GET', '/xitong/jiankang'),
        ]);
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      }
    },
  },
  mounted() { this.jiazai_shuju(); },
  template: `
  <div class="zhankai-zhuti">
    <div class="kapian">
      <div class="kapian-shen" style="padding:28px">
        <div style="font-size:12px;letter-spacing:.14em;color:var(--zhuti);font-weight:700">SOFTWARE ENGINEERING LAB</div>
        <h2 style="font-size:24px;margin-top:8px">隐私计算数据共享平台</h2>
        <p style="max-width:720px;margin-top:12px;line-height:1.85;color:var(--ciwen)">
          面向多数据持有方的联邦学习平台：原始数据始终留在本地，各方只交换模型更新；服务端按样本数加权聚合，
          每轮更新先做 L2 裁剪再按拉普拉斯机制加噪，隐私预算逐轮累计，超限自动停止。
          课程项目覆盖需求分析、概要设计、详细设计、编码与测试六个阶段。
        </p>
        <div class="ji-kuang" style="margin-top:16px">
          <span class="ji">FastAPI</span><span class="ji">SQLite WAL</span><span class="ji">NumPy</span>
          <span class="ji">Vue 3</span><span class="ji">ECharts</span><span class="ji">JWT</span>
          <span class="ji">bcrypt</span><span class="ji">Laplace DP</span>
        </div>
      </div>
    </div>

    <div class="liang-lan">
      <div class="kapian">
        <div class="kapian-tou"><h3>平台信息</h3></div>
        <div class="kapian-shen" v-if="xinxi">
          <div class="xinxi-ge">
            <div class="xinxi-xiang"><div class="jian">名称</div><div class="zhi">{{ xinxi.mingcheng }}</div></div>
            <div class="xinxi-xiang"><div class="jian">版本</div><div class="zhi">{{ xinxi.banben }}</div></div>
            <div class="xinxi-xiang"><div class="jian">命题</div><div class="zhi">{{ xinxi.mingti }}</div></div>
            <div class="xinxi-xiang"><div class="jian">服务状态</div>
              <div class="zhi">
                <span v-if="jiankang" class="zhuangtai" :class="jiankang.zhuangtai === 'ok' ? 'good' : 'bad'">
                  <span class="dian"></span>{{ jiankang.zhuangtai === 'ok' ? '正常' : '异常' }}
                </span>
              </div>
            </div>
            <div class="xinxi-xiang" style="border-bottom:0"><div class="jian">数据库</div><div class="zhi mono">{{ xinxi.lujing.shujuku }}</div></div>
            <div class="xinxi-xiang" style="border-bottom:0"><div class="jian">模型目录</div><div class="zhi mono">{{ xinxi.lujing.canshu }}</div></div>
          </div>
        </div>
      </div>

      <div class="kapian">
        <div class="kapian-tou"><h3>模型与隐私</h3></div>
        <div class="kapian-shen" v-if="xinxi">
          <div class="xinxi-ge" style="border-top:0">
            <div class="xinxi-xiang" style="border-right:0"><div class="jian">模型</div><div class="zhi">{{ xinxi.moxing.mingcheng }}</div></div>
            <div class="xinxi-xiang"><div class="jian">网络结构</div><div class="zhi">{{ xinxi.moxing.shuru_weidu }}-{{ xinxi.moxing.yincang_weidu }}-{{ xinxi.moxing.shuchu_weidu }}</div></div>
            <div class="xinxi-xiang" style="border-right:0;border-bottom:0"><div class="jian">参数维度</div><div class="zhi tabular">{{ xinxi.moxing.canshu_weidu }}</div></div>
            <div class="xinxi-xiang" style="border-bottom:0"><div class="jian">隐私机制</div><div class="zhi">{{ xinxi.yinsi.jizhi }}</div></div>
            <div class="xinxi-xiang" style="border-right:0"><div class="jian">默认每轮 ε</div><div class="zhi tabular">{{ xinxi.yinsi.meilun_eps_default }}</div></div>
            <div class="xinxi-xiang"><div class="jian">默认裁剪阈值</div><div class="zhi tabular">{{ xinxi.yinsi.jiancai_yuzhi_default }}</div></div>
          </div>
        </div>
      </div>
    </div>

    <div class="kapian">
      <div class="kapian-tou"><h3>算法说明</h3><span class="fu">联邦平均 + 差分隐私</span></div>
      <div class="kapian-shen">
        <div class="liang-lan">
          <div>
            <div style="font-weight:600;font-size:13.5px">联邦平均聚合</div>
            <p style="color:var(--ciwen);line-height:1.8;font-size:13px;margin-top:8px">
              第 t 轮中，各参与方 k 用本地样本训练得到更新 w<sub>k</sub>，服务端按样本数 n<sub>k</sub> 加权：
            </p>
            <div class="jian-tishi mono" style="font-size:12.5px">w<sub>t+1</sub> = Σ (n<sub>k</sub> / n) · w<sub>k</sub></div>
          </div>
          <div>
            <div style="font-weight:600;font-size:13.5px">拉普拉斯机制</div>
            <p style="color:var(--ciwen);line-height:1.8;font-size:13px;margin-top:8px">
              每个更新先裁剪到 L2 范数不超过 C，再叠加尺度为 b 的拉普拉斯噪声，满足 ε-差分隐私：
            </p>
            <div class="jian-tishi mono" style="font-size:12.5px">b = C / (ε · √d)，d 为参数维度</div>
          </div>
        </div>
        <div class="fenge"></div>
        <div class="xinxi-ge" style="border-top:0">
          <div class="xinxi-xiang" style="border-right:0"><div class="jian">数据提供方</div><div class="zhi">登记数据集元数据，参与训练</div></div>
          <div class="xinxi-xiang"><div class="jian">数据使用方</div><div class="zhi">选择数据集，创建并启动训练</div></div>
          <div class="xinxi-xiang" style="border-right:0;border-bottom:0"><div class="jian">系统管理员</div><div class="zhi">用户、任务的审计与运维</div></div>
          <div class="xinxi-xiang" style="border-bottom:0"><div class="jian">课程信息</div><div class="zhi">软件工程实验 · 2024103365 许博儒</div></div>
        </div>
      </div>
    </div>
  </div>`,
};
