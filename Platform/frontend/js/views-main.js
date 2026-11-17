/* 页面：登录、工作台、数据集、训练任务列表 */

const DengluShiTu = {
  emits: ['chenggong'],
  data() {
    return {
      moban: 'denglu',
      denglu: { yonghuming: '', mima: '' },
      zhuce: { yonghuming: '', mima: '', youxiang: '', jiaose: 'shiyongfang' },
      jiazai: false,
      cuowu: '',
      shili: [
        { juese: '管理员', zhanghao: 'admin', mima: 'admin123' },
        { juese: '提供方', zhanghao: 'tigong1', mima: '123456' },
        { juese: '使用方', zhanghao: 'shiyong1', mima: '123456' },
      ],
    };
  },
  methods: {
    tian(zhanghao, mima) {
      this.denglu.yonghuming = zhanghao;
      this.denglu.mima = mima;
      this.moban = 'denglu';
    },
    async tijiao_denglu() {
      this.cuowu = '';
      if (!this.denglu.yonghuming || !this.denglu.mima) {
        this.cuowu = '请输入用户名和密码';
        return;
      }
      this.jiazai = true;
      try {
        const jieguo = await Pingtai.qingqiu('POST', '/yonghu/denglu', this.denglu);
        Pingtai.cunchu_denglu(jieguo);
        Pingtai.tishi('欢迎回来，' + jieguo.user.yonghuming, 'good');
        this.$emit('chenggong');
      } catch (e) {
        this.cuowu = e.message;
      } finally {
        this.jiazai = false;
      }
    },
    async tijiao_zhuce() {
      this.cuowu = '';
      this.jiazai = true;
      try {
        await Pingtai.qingqiu('POST', '/yonghu/zhuce', this.zhuce);
        Pingtai.tishi('注册成功，请登录', 'good');
        this.denglu.yonghuming = this.zhuce.yonghuming;
        this.denglu.mima = '';
        this.moban = 'denglu';
      } catch (e) {
        this.cuowu = e.message;
      } finally {
        this.jiazai = false;
      }
    },
  },
  template: `
  <div class="denglu-ye">
    <div class="denglu-zuo">
      <div class="denglu-pinpai">
        <div class="pinpai-tubiao">🛡</div>
        <span>隐私计算数据共享平台</span>
      </div>
      <div class="denglu-biaoyu">
        <h1>数据不出域，<br>模型联合训。</h1>
        <p>面向多数据持有方的联邦学习平台。原始数据留在本地，各方只上传经 L2 裁剪与拉普拉斯加噪的模型更新，服务端按样本数加权聚合，全程记录隐私预算。</p>
        <div class="denglu-tes">
          <div class="denglu-tese">
            <div class="dian">🔒</div>
            <div><b>数据可用不可见</b><span>只交换模型更新，不传输原始样本；平台仅登记数据集元数据。</span></div>
          </div>
          <div class="denglu-tese">
            <div class="dian">🧮</div>
            <div><b>差分隐私可度量</b><span>每轮消耗固定 ε，累计预算超限自动拦截，预算使用全程可查。</span></div>
          </div>
          <div class="denglu-tese">
            <div class="dian">🔁</div>
            <div><b>联邦聚合可追溯</b><span>轮次指标、参与方状态、全局参数文件逐轮落库，异常自动标记。</span></div>
          </div>
        </div>
      </div>
      <div class="denglu-dibu">暨南大学网络空间安全学院 · 软件工程实验 · 2024103365 许博儒</div>
    </div>

    <div class="denglu-you">
      <div class="denglu-ka">
        <h2>{{ moban === 'denglu' ? '登录平台' : '创建账号' }}</h2>
        <div class="fu">{{ moban === 'denglu' ? '使用课程演示账号或自己注册的账号进入' : '数据提供方登记数据集，数据使用方发起训练' }}</div>

        <div class="denglu-qiehuan">
          <button :class="{ huoyue: moban === 'denglu' }" @click="moban = 'denglu'">登录</button>
          <button :class="{ huoyue: moban === 'zhuce' }" @click="moban = 'zhuce'">注册</button>
        </div>

        <div v-if="cuowu" class="jian-tishi bad" style="margin-bottom:14px">{{ cuowu }}</div>

        <form v-if="moban === 'denglu'" class="biaodan" @submit.prevent="tijiao_denglu">
          <div class="ziduan">
            <label>用户名</label>
            <input class="shuru" v-model.trim="denglu.yonghuming" placeholder="请输入用户名" autocomplete="username">
          </div>
          <div class="ziduan">
            <label>密码</label>
            <input class="shuru" type="password" v-model="denglu.mima" placeholder="请输入密码" autocomplete="current-password">
          </div>
          <button class="an zhuyi quan" type="submit" :disabled="jiazai">{{ jiazai ? '登录中…' : '登录' }}</button>
        </form>

        <form v-else class="biaodan" @submit.prevent="tijiao_zhuce">
          <div class="ziduan">
            <label>用户名 <span class="xing">*</span></label>
            <input class="shuru" v-model.trim="zhuce.yonghuming" placeholder="3-32 位字母、数字、下划线">
          </div>
          <div class="hang">
            <div class="ziduan">
              <label>密码 <span class="xing">*</span></label>
              <input class="shuru" type="password" v-model="zhuce.mima" placeholder="6-64 位">
            </div>
            <div class="ziduan">
              <label>角色</label>
              <select class="xuanze" v-model="zhuce.jiaose">
                <option value="shiyongfang">数据使用方</option>
                <option value="tigongfang">数据提供方</option>
              </select>
            </div>
          </div>
          <div class="ziduan">
            <label>邮箱 <span class="xing">*</span></label>
            <input class="shuru" v-model.trim="zhuce.youxiang" placeholder="name@example.com">
          </div>
          <button class="an zhuyi quan" type="submit" :disabled="jiazai">{{ jiazai ? '提交中…' : '注册' }}</button>
        </form>

        <div class="zhanghao-kuai">
          <div class="tou">课程演示账号（点击填入）</div>
          <div class="lie">
            <button v-for="x in shili" :key="x.zhanghao" class="zhanghao"
                    @click="tian(x.zhanghao, x.mima)">
              {{ x.juese }} · {{ x.zhanghao }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>`,
};

const GongzuoTaiShiTu = {
  data() {
    return { zonglan: null, jiankang: null, xinxi: null, jiazai: true };
  },
  computed: {
    yonghu() { return Pingtai.zhuangtai.yonghu || {}; },
    jiaose() { return this.yonghu.jiaose; },
    kaPian() {
      const zl = this.zonglan || {};
      const sj = zl.shujuji || {};
      const rw = zl.renwu || {};
      if (this.jiaose === 'guanliyuan') {
        const yh = zl.yonghu || {};
        const rz = zl.rizhi || {};
        return [
          { biaoti: '平台用户', zhi: Pingtai.shuliang(yh.zongshu), fu: '提供方 ' + (yh.tigongfang || 0) + ' · 使用方 ' + (yh.shiyongfang || 0), tubiao: '👥' },
          { biaoti: '数据集', zhi: Pingtai.shuliang(sj.zongshu), fu: '可用 ' + (sj.keyong || 0) + ' 个 · 样本 ' + Pingtai.shuliang(sj.yangben_zong), tubiao: '🗂' },
          { biaoti: '训练任务', zhi: Pingtai.shuliang(rw.zongshu), fu: '进行中 ' + (rw.jinxingzhong || 0) + ' · 异常 ' + (rw.yichang || 0), tubiao: '🔁', se: rw.yichang ? 'warn' : '' },
          { biaoti: '今日操作', zhi: Pingtai.shuliang(rz.jintian), fu: '累计 ' + Pingtai.shuliang(rz.zongshu) + ' 条 · 失败 ' + (rz.shibai || 0), tubiao: '📋' },
        ];
      }
      if (this.jiaose === 'tigongfang') {
        return [
          { biaoti: '我的数据集', zhi: Pingtai.shuliang(sj.zongshu), fu: '可用 ' + (sj.keyong || 0) + ' 个', tubiao: '🗂' },
          { biaoti: '样本总量', zhi: Pingtai.shuliang(sj.yangben_zong), fu: '本地样本，不出域', tubiao: '🧾' },
          { biaoti: '相关任务', zhi: Pingtai.shuliang(rw.zongshu), fu: '进行中 ' + (rw.jinxingzhong || 0) + ' 个', tubiao: '🔁' },
          { biaoti: '已完成任务', zhi: Pingtai.shuliang(rw.yiwancheng), fu: '异常 ' + (rw.yichang || 0) + ' 个', tubiao: '✅', se: 'good' },
        ];
      }
      return [
        { biaoti: '我的训练任务', zhi: Pingtai.shuliang(rw.zongshu), fu: '进行中 ' + (rw.jinxingzhong || 0) + ' · 已完成 ' + (rw.yiwancheng || 0), tubiao: '🔁' },
        { biaoti: '可用数据集', zhi: Pingtai.shuliang(sj.keyong), fu: '共 ' + (sj.zongshu || 0) + ' 个，样本 ' + Pingtai.shuliang(sj.yangben_zong), tubiao: '🗂' },
        { biaoti: '已完成任务', zhi: Pingtai.shuliang(rw.yiwancheng), fu: '异常 ' + (rw.yichang || 0) + ' 个', tubiao: '✅', se: 'good' },
        { biaoti: '平台模型', zhi: this.xinxi ? this.xinxi.moxing.canshu_weidu : '—', fu: this.xinxi ? this.xinxi.moxing.mingcheng + ' · 参数维度' : '', tubiao: '🧠' },
      ];
    },
  },
  methods: {
    async jiazai_shuju() {
      this.jiazai = true;
      try {
        const [zonglan, jiankang, xinxi] = await Promise.all([
          Pingtai.qingqiu('GET', '/zonglan'),
          Pingtai.qingqiu('GET', '/xitong/jiankang'),
          Pingtai.qingqiu('GET', '/xitong/xinxi'),
        ]);
        this.zonglan = zonglan;
        this.jiankang = jiankang;
        this.xinxi = xinxi;
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.jiazai = false;
      }
    },
    qu_renwu(id) { Pingtai.tiaozhuan('/tasks/' + id); },
    qu_dengji() { Pingtai.tiaozhuan('/datasets'); },
    qu_xinjian() { Pingtai.tiaozhuan('/tasks'); },
    geshihua: Pingtai.geshihua_shijian,
    daxiao: Pingtai.geshihua_daxiao,
  },
  mounted() { this.jiazai_shuju(); },
  template: `
  <div class="zhankai-zhuti">
    <div>
      <h2 style="font-size:21px">你好，{{ yonghu.yonghuming }}</h2>
      <div class="wenben-ruo" style="margin-top:6px;font-size:12.5px">
        {{ jiaose === 'guanliyuan' ? '系统管理员视角：可管理用户、任务、日志与备份' :
           jiaose === 'tigongfang' ? '数据提供方视角：登记数据集，参与联邦训练' :
           '数据使用方视角：选择数据集发起联邦训练任务' }}
      </div>
    </div>

    <div class="tongji-ge">
      <shuzi-ka v-for="(k, i) in kaPian" :key="i" :biaoti="k.biaoti" :zhi="k.zhi"
                :fu="k.fu" :tubiao="k.tubiao" :se="k.se || ''"></shuzi-ka>
    </div>

    <div class="san-lan">
      <div class="kapian">
        <div class="kapian-tou">
          <h3>最近训练任务</h3>
          <span class="fu">按创建时间倒序</span>
          <div class="you">
            <button class="an xiao wenzi" @click="qu_xinjian">全部任务 →</button>
          </div>
        </div>
        <div class="biaoge-kuang">
          <table class="biaoge">
            <thead><tr>
              <th>任务</th><th>状态</th><th style="width:150px">进度</th>
              <th>参与方</th><th>创建时间</th><th class="caozuo">操作</th>
            </tr></thead>
            <tbody>
              <tr v-for="r in (zonglan && zonglan.zuijin_renwu) || []" :key="r.id">
                <td>
                  <div class="zhu">#{{ r.id }} {{ r.mingcheng }}</div>
                  <div class="fu">{{ r.chuangjianzhe_ming }} · {{ Pingtai.MOSHI_MING[r.yunxing_moshi] }}</div>
                </td>
                <td><zhuangtai-biao :zhi="r.zhuangtai" leixing="renwu"></zhuangtai-biao></td>
                <td>
                  <jindu-tiao :zhi="r.lunshu ? r.dangqian_lunci / r.lunshu : 0"
                              :se="r.zhuangtai === 'yiwancheng' ? 'good' : (r.zhuangtai === 'yichang' ? 'bad' : '')"></jindu-tiao>
                  <div class="fu tabular">{{ r.dangqian_lunci }} / {{ r.lunshu }} 轮</div>
                </td>
                <td class="tabular">{{ r.canjia_shu }} 方 · {{ Pingtai.shuliang(r.yangben_zong) }} 样本</td>
                <td class="wenben-ruo">{{ geshihua(r.chuangjian_shijian) }}</td>
                <td class="caozuo"><button class="an xiao wenzi" @click="qu_renwu(r.id)">查看</button></td>
              </tr>
              <tr v-if="!zonglan || !zonglan.zuijin_renwu || !zonglan.zuijin_renwu.length">
                <td colspan="6"><kong-zhuang ming="还没有训练任务" fu="数据使用方可以创建第一个联邦训练任务"></kong-zhuang></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div style="display:flex;flex-direction:column;gap:16px">
        <div class="kapian">
          <div class="kapian-tou"><h3>快捷操作</h3></div>
          <div class="kapian-shen">
            <div class="an-zu" style="flex-direction:column;align-items:stretch">
              <button v-if="jiaose !== 'tigongfang'" class="an zhuyi" @click="qu_xinjian">➕ 新建训练任务</button>
              <button v-if="jiaose !== 'shiyongfang'" class="an" @click="qu_dengji">🗂 登记数据集</button>
              <button class="an" @click="qu_xinjian">🔁 查看训练任务</button>
            </div>
          </div>
        </div>

        <div class="kapian">
          <div class="kapian-tou"><h3>平台状态</h3></div>
          <div class="kapian-shen">
            <div class="xinxi-ge" style="border-top:0">
              <div class="xinxi-xiang" style="border-right:0">
                <div class="jian">服务状态</div>
                <div class="zhi">
                  <span v-if="jiankang" class="zhuangtai" :class="jiankang.zhuangtai === 'ok' ? 'good' : 'bad'">
                    <span class="dian"></span>{{ jiankang.zhuangtai === 'ok' ? '运行正常' : '异常' }}
                  </span>
                  <span v-else class="wenben-ruo">—</span>
                </div>
              </div>
              <div class="xinxi-xiang">
                <div class="jian">数据库</div>
                <div class="zhi">{{ jiankang ? jiankang.shujuku : '—' }}</div>
              </div>
              <div class="xinxi-xiang" style="border-right:0">
                <div class="jian">注册用户</div>
                <div class="zhi tabular">{{ jiankang ? jiankang.yonghu_shu : '—' }}</div>
              </div>
              <div class="xinxi-xiang">
                <div class="jian">模型</div>
                <div class="zhi">{{ xinxi ? xinxi.moxing.mingcheng : '—' }}</div>
              </div>
              <div class="xinxi-xiang" style="border-right:0;border-bottom:0">
                <div class="jian">参数维度</div>
                <div class="zhi tabular">{{ xinxi ? xinxi.moxing.canshu_weidu : '—' }}</div>
              </div>
              <div class="xinxi-xiang" style="border-bottom:0">
                <div class="jian">默认 ε / 裁剪</div>
                <div class="zhi tabular">{{ xinxi ? xinxi.yinsi.meilun_eps_default + ' / ' + xinxi.yinsi.jiancai_yuzhi_default : '—' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>`,
};

const ShujuJiShiTu = {
  data() {
    return {
      liebiao: [], zongshu: 0, ye: 1, meiye: 50, jiazai: true,
      guanJian: '', zhuangtai_shai: '',
      tanchuang: false, xiangqing: null,
      biaodan: this.kong_biaodan(),
      yujian_jieguo: null, tijiao_zhong: false,
    };
  },
  computed: {
    yonghu() { return Pingtai.zhuangtai.yonghu || {}; },
    neng_dengji() { return this.yonghu.jiaose === 'tigongfang' || this.yonghu.jiaose === 'guanliyuan'; },
    guolv_hou() {
      const jian = this.guanJian.trim().toLowerCase();
      return this.liebiao.filter((x) => {
        const ming = (x.mingcheng + ' ' + (x.tigongfang_ming || '')).toLowerCase();
        if (jian && !ming.includes(jian)) return false;
        if (this.zhuangtai_shai && x.zhuangtai !== this.zhuangtai_shai) return false;
        return true;
      });
    },
  },
  methods: {
    kong_biaodan() {
      return {
        mingcheng: '', geshi: 'csv', yangben_shu: 1000, daxiao_mb: 10,
        ziduan_text: 'feature_1, feature_2, feature_3, label',
        tuomin_guize: '', benzhi_lujing: '',
      };
    },
    async jiazai_shuju() {
      this.jiazai = true;
      try {
        const jieguo = await Pingtai.qingqiu('GET', '/shuju?meiye=100');
        this.liebiao = jieguo.items;
        this.zongshu = jieguo.total;
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.jiazai = false;
      }
    },
    dakai_dengji() {
      this.biaodan = this.kong_biaodan();
      this.yujian_jieguo = null;
      this.tanchuang = true;
    },
    ziduan_liebiao() {
      return this.biaodan.ziduan_text.split(/[,，、\s]+/).map((x) => x.trim()).filter(Boolean);
    },
    async yujian() {
      this.tijiao_zhong = true;
      this.yujian_jieguo = null;
      try {
        this.yujian_jieguo = await Pingtai.qingqiu('POST', '/shuju/jiaoyan', {
          ziduan: this.ziduan_liebiao(),
          yangben_shu: Number(this.biaodan.yangben_shu) || 0,
          geshi: this.biaodan.geshi,
        });
      } catch (e) {
        this.yujian_jieguo = { tongguo: false, jielun: e.message };
      } finally {
        this.tijiao_zhong = false;
      }
    },
    async tijiao_dengji() {
      this.tijiao_zhong = true;
      try {
        await Pingtai.qingqiu('POST', '/shuju', {
          mingcheng: this.biaodan.mingcheng,
          geshi: this.biaodan.geshi,
          daxiao: Math.round(Number(this.biaodan.daxiao_mb) * 1024 * 1024),
          yangben_shu: Number(this.biaodan.yangben_shu),
          ziduan: this.ziduan_liebiao(),
          tuomin_guize: this.biaodan.tuomin_guize,
          benzhi_lujing: this.biaodan.benzhi_lujing,
        });
        Pingtai.tishi('数据集登记成功', 'good');
        this.tanchuang = false;
        this.jiazai_shuju();
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.tijiao_zhong = false;
      }
    },
    dakai_xiangqing(x) { this.xiangqing = x; },
    async qiehuan(x) {
      const mubiao = x.zhuangtai === 'yijiaoyan' ? 'yitingyong' : 'yijiaoyan';
      const dongzuo = mubiao === 'yitingyong' ? '停用' : '恢复';
      if (!confirm('确定' + dongzuo + '数据集「' + x.mingcheng + '」吗？')) return;
      try {
        await Pingtai.qingqiu('PATCH', '/shuju/' + x.id + '/zhuangtai', { zhuangtai: mubiao });
        Pingtai.tishi('已' + dongzuo, 'good');
        this.jiazai_shuju();
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      }
    },
    geshihua: Pingtai.geshihua_shijian,
    daxiao: Pingtai.geshihua_daxiao,
    shuliang: Pingtai.shuliang,
  },
  mounted() { this.jiazai_shuju(); },
  template: `
  <div class="zhankai-zhuti">
    <div class="an-zu">
      <div>
        <h2 style="font-size:21px">数据集</h2>
        <div class="wenben-ruo" style="margin-top:6px;font-size:12.5px">
          平台只保存元数据与校验结论，原始文件保留在数据提供方本地
        </div>
      </div>
      <div style="margin-left:auto">
        <button v-if="neng_dengji" class="an zhuyi" @click="dakai_dengji">＋ 登记数据集</button>
      </div>
    </div>

    <div class="kapian">
      <div class="kapian-tou">
        <h3>数据集列表</h3>
        <span class="fu">共 {{ zongshu }} 个</span>
        <div class="you">
          <input class="shuru" style="width:210px;padding:6px 10px" v-model="guanJian"
                 placeholder="搜索名称或提供方">
          <div class="biaoqian-zu">
            <button class="biaoqian" :class="{ huoyue: !zhuangtai_shai }" @click="zhuangtai_shai = ''">全部</button>
            <button class="biaoqian" :class="{ huoyue: zhuangtai_shai === 'yijiaoyan' }" @click="zhuangtai_shai = 'yijiaoyan'">可用</button>
            <button class="biaoqian" :class="{ huoyue: zhuangtai_shai === 'yitingyong' }" @click="zhuangtai_shai = 'yitingyong'">已停用</button>
          </div>
        </div>
      </div>
      <div class="biaoge-kuang">
        <table class="biaoge">
          <thead><tr>
            <th>数据集</th><th>格式</th><th>样本数</th><th>大小</th>
            <th>提供方</th><th>状态</th><th>登记时间</th><th class="caozuo">操作</th>
          </tr></thead>
          <tbody>
            <tr v-for="x in guolv_hou" :key="x.id">
              <td>
                <div class="zhu">#{{ x.id }} {{ x.mingcheng }}</div>
                <div class="fu">{{ (x.ziduan || []).length }} 个字段 · {{ (x.ziduan || []).slice(0, 3).join('、') }}{{ (x.ziduan || []).length > 3 ? ' …' : '' }}</div>
              </td>
              <td><span class="ji">{{ Pingtai.GESHI_MING[x.geshi] || x.geshi }}</span></td>
              <td class="tabular">{{ shuliang(x.yangben_shu) }}</td>
              <td class="tabular">{{ daxiao(x.daxiao) }}</td>
              <td>{{ x.tigongfang_ming }}</td>
              <td><zhuangtai-biao :zhi="x.zhuangtai" leixing="shujuji"></zhuangtai-biao></td>
              <td class="wenben-ruo">{{ geshihua(x.chuangjian_shijian) }}</td>
              <td class="caozuo">
                <button class="an xiao wenzi" @click="dakai_xiangqing(x)">详情</button>
                <button v-if="neng_dengji && (yonghu.jiaose === 'guanliyuan' || x.tigongfang_id === yonghu.id)"
                        class="an xiao" :class="{ weixian: x.zhuangtai === 'yijiaoyan' }"
                        @click="qiehuan(x)">{{ x.zhuangtai === 'yijiaoyan' ? '停用' : '恢复' }}</button>
              </td>
            </tr>
            <tr v-if="!guolv_hou.length">
              <td colspan="8">
                <kong-zhuang :ming="jiazai ? '正在加载…' : '没有匹配的数据集'" fu="数据提供方可以登记新的数据集"></kong-zhuang>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <tan-chuang v-if="tanchuang" biaoti="登记数据集" kuan @guanbi="tanchuang = false">
      <div class="biaodan">
        <div class="hang">
          <div class="ziduan">
            <label>数据集名称 <span class="xing">*</span></label>
            <input class="shuru" v-model.trim="biaodan.mingcheng" placeholder="例如：医疗影像特征集">
          </div>
          <div class="ziduan">
            <label>数据格式</label>
            <select class="xuanze" v-model="biaodan.geshi">
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
              <option value="parquet">Parquet</option>
              <option value="npy">NumPy（.npy）</option>
            </select>
          </div>
        </div>
        <div class="hang-3">
          <div class="ziduan">
            <label>样本数 <span class="xing">*</span></label>
            <input class="shuru" type="number" min="1" v-model.number="biaodan.yangben_shu">
          </div>
          <div class="ziduan">
            <label>文件大小（MB） <span class="xing">*</span></label>
            <input class="shuru" type="number" min="0.01" step="0.01" v-model.number="biaodan.daxiao_mb">
          </div>
          <div class="ziduan">
            <label>原始文件路径</label>
            <input class="shuru" v-model.trim="biaodan.benzhi_lujing" placeholder="D:/data/xxx.csv">
            <span class="shuoming">只做记录，平台不会读取文件</span>
          </div>
        </div>
        <div class="ziduan">
          <label>字段列表 <span class="xing">*</span></label>
          <input class="shuru" v-model="biaodan.ziduan_text" placeholder="用逗号分隔，例如 feature_1, feature_2, label">
          <span class="shuoming">当前 {{ ziduan_liebiao().length }} 个字段；字段名只能包含字母、数字和下划线</span>
        </div>
        <div class="ziduan">
          <label>脱敏规则</label>
          <textarea class="duohang" v-model="biaodan.tuomin_guize"
                    placeholder="例如：patient_id -> SHA256；姓名 -> 掩码"></textarea>
          <span class="shuoming">说明本地数据在出域前如何脱敏，仅做登记</span>
        </div>
        <div v-if="yujian_jieguo" class="jian-tishi" :class="{ bad: !yujian_jieguo.tongguo }">
          <b>{{ yujian_jieguo.tongguo ? '预检通过：' : '预检未通过：' }}</b>{{ yujian_jieguo.jielun }}
        </div>
      </div>
      <template #jiao>
        <button class="an" @click="yujian" :disabled="tijiao_zhong">格式预检</button>
        <button class="an" @click="tanchuang = false">取消</button>
        <button class="an zhuyi" @click="tijiao_dengji" :disabled="tijiao_zhong">
          {{ tijiao_zhong ? '提交中…' : '登记' }}
        </button>
      </template>
    </tan-chuang>

    <tan-chuang v-if="xiangqing" :biaoti="'数据集 #' + xiangqing.id + ' · ' + xiangqing.mingcheng" kuan
                @guanbi="xiangqing = null">
      <div class="xinxi-ge">
        <div class="xinxi-xiang"><div class="jian">数据提供方</div><div class="zhi">{{ xiangqing.tigongfang_ming }}</div></div>
        <div class="xinxi-xiang"><div class="jian">格式</div><div class="zhi">{{ Pingtai.GESHI_MING[xiangqing.geshi] || xiangqing.geshi }}</div></div>
        <div class="xinxi-xiang"><div class="jian">样本数</div><div class="zhi tabular">{{ shuliang(xiangqing.yangben_shu) }}</div></div>
        <div class="xinxi-xiang"><div class="jian">大小</div><div class="zhi tabular">{{ daxiao(xiangqing.daxiao) }}</div></div>
        <div class="xinxi-xiang"><div class="jian">状态</div><div class="zhi"><zhuangtai-biao :zhi="xiangqing.zhuangtai" leixing="shujuji"></zhuangtai-biao></div></div>
        <div class="xinxi-xiang"><div class="jian">登记时间</div><div class="zhi">{{ geshihua(xiangqing.chuangjian_shijian) }}</div></div>
        <div class="xinxi-xiang" style="grid-column: span 2"><div class="jian">原始文件路径</div><div class="zhi mono">{{ xiangqing.benzhi_lujing || '—' }}</div></div>
        <div class="xinxi-xiang" style="grid-column: span 2"><div class="jian">脱敏规则</div><div class="zhi">{{ xiangqing.tuomin_guize || '—' }}</div></div>
      </div>
      <div class="fenge"></div>
      <div class="ziduan">
        <label>字段（{{ (xiangqing.ziduan || []).length }} 个）</label>
        <div class="ji-kuang">
          <span class="ji" v-for="z in xiangqing.ziduan" :key="z">{{ z }}</span>
          <span v-if="!(xiangqing.ziduan || []).length" class="wenben-ruo">未登记字段</span>
        </div>
      </div>
      <div class="fenge"></div>
      <div class="ziduan">
        <label>格式校验结论</label>
        <div class="jian-tishi">{{ xiangqing.jiaoyan_jielun || '—' }}</div>
      </div>
    </tan-chuang>
  </div>`,
};

const XunlianRenwuShiTu = {
  data() {
    return {
      liebiao: [], zongshu: 0, ye: 1, meiye: 20, jiazai: true,
      zhuangtai_shai: '',
      tanchuang: false, shujuji: [], tijiao_zhong: false,
      biaodan: this.kong_biaodan(),
    };
  },
  computed: {
    yonghu() { return Pingtai.zhuangtai.yonghu || {}; },
    neng_chuangjian() { return this.yonghu.jiaose === 'shiyongfang' || this.yonghu.jiaose === 'guanliyuan'; },
    keyong_shujuji() {
      return this.shujuji.filter((x) => x.zhuangtai === 'yijiaoyan' &&
        (this.yonghu.jiaose === 'guanliyuan' || x.tigongfang_id === this.yonghu.id ? true : true));
    },
    xuanze_shuliang() {
      return Object.values(this.biaodan.canjia).filter((x) => x.xuan).length;
    },
    zong_yangben() {
      return Object.keys(this.biaodan.canjia)
        .filter((k) => this.biaodan.canjia[k].xuan)
        .reduce((he, k) => he + (Number(this.biaodan.canjia[k].yangben_shu) || 0), 0);
    },
    ke_xunlian_lunshu() {
      const eps = Number(this.biaodan.yinsipi) || 0;
      const shangxian = Number(this.biaodan.yusuan_shangxian) || 0;
      return eps > 0 ? Math.floor(shangxian / eps + 1e-9) : 0;
    },
  },
  methods: {
    kong_biaodan() {
      return {
        mingcheng: '', yunxing_moshi: 'moni', lunshu: 5, piliang_daxiao: 16,
        xuexilv: 0.05, yinsipi: 0.5, jiancai_yuzhi: 1.0, yusuan_shangxian: 2.5,
        canjia: {},
      };
    },
    async jiazai_shuju() {
      this.jiazai = true;
      try {
        const lujing = '/xunlian?ye=' + this.ye + '&meiye=' + this.meiye +
          (this.zhuangtai_shai ? '&zhuangtai=' + this.zhuangtai_shai : '');
        const jieguo = await Pingtai.qingqiu('GET', lujing);
        this.liebiao = jieguo.items;
        this.zongshu = jieguo.total;
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.jiazai = false;
      }
    },
    shaixuan(zhi) {
      this.zhuangtai_shai = zhi;
      this.ye = 1;
      this.jiazai_shuju();
    },
    async dakai_chuangjian() {
      this.biaodan = this.kong_biaodan();
      try {
        const jieguo = await Pingtai.qingqiu('GET', '/shuju?meiye=100');
        this.shujuji = jieguo.items;
        const canjia = {};
        jieguo.items.filter((x) => x.zhuangtai === 'yijiaoyan').forEach((x) => {
          canjia[x.id] = { xuan: false, yangben_shu: x.yangben_shu };
        });
        this.biaodan.canjia = canjia;
        this.tanchuang = true;
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      }
    },
    async tijiao() {
      const xuanzhong = Object.keys(this.biaodan.canjia)
        .filter((k) => this.biaodan.canjia[k].xuan)
        .map((k) => ({
          shujuji_id: Number(k),
          yangben_shu: Number(this.biaodan.canjia[k].yangben_shu) || undefined,
        }));
      if (!xuanzhong.length) {
        Pingtai.tishi('请至少选择一个参与方数据集', 'warn');
        return;
      }
      this.tijiao_zhong = true;
      try {
        const jieguo = await Pingtai.qingqiu('POST', '/xunlian', {
          mingcheng: this.biaodan.mingcheng,
          moxing_leixing: 'mlp_8_16_2',
          lunshu: Number(this.biaodan.lunshu),
          piliang_daxiao: Number(this.biaodan.piliang_daxiao),
          xuexilv: Number(this.biaodan.xuexilv),
          yinsipi: Number(this.biaodan.yinsipi),
          jiancai_yuzhi: Number(this.biaodan.jiancai_yuzhi),
          yusuan_shangxian: Number(this.biaodan.yusuan_shangxian),
          yunxing_moshi: this.biaodan.yunxing_moshi,
          canjia: xuanzhong,
        });
        Pingtai.tishi('任务创建成功', 'good');
        this.tanchuang = false;
        Pingtai.tiaozhuan('/tasks/' + jieguo.id);
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      } finally {
        this.tijiao_zhong = false;
      }
    },
    async qidong(x) {
      if (!confirm('启动任务「' + x.mingcheng + '」？启动后训练在后台进行。')) return;
      try {
        await Pingtai.qingqiu('POST', '/xunlian/' + x.id + '/qidong');
        Pingtai.tishi('训练已启动', 'good');
        this.jiazai_shuju();
      } catch (e) {
        Pingtai.tishi(e.message, 'bad');
      }
    },
    kan(x) { Pingtai.tiaozhuan('/tasks/' + x.id); },
    qu_ye(p) { this.ye = p; this.jiazai_shuju(); },
    geshihua: Pingtai.geshihua_shijian,
    shuliang: Pingtai.shuliang,
    bili: Pingtai.bili_zhi,
  },
  mounted() { this.jiazai_shuju(); },
  template: `
  <div class="zhankai-zhuti">
    <div class="an-zu">
      <div>
        <h2 style="font-size:21px">训练任务</h2>
        <div class="wenben-ruo" style="margin-top:6px;font-size:12.5px">
          联邦训练在后台线程执行，逐轮聚合加噪更新并记录隐私预算
        </div>
      </div>
      <div style="margin-left:auto">
        <button v-if="neng_chuangjian" class="an zhuyi" @click="dakai_chuangjian">＋ 新建任务</button>
      </div>
    </div>

    <div class="kapian">
      <div class="kapian-tou">
        <div class="biaoqian-zu">
          <button class="biaoqian" :class="{ huoyue: !zhuangtai_shai }" @click="shaixuan('')">全部</button>
          <button class="biaoqian" :class="{ huoyue: zhuangtai_shai === 'daichufa' }" @click="shaixuan('daichufa')">待启动</button>
          <button class="biaoqian" :class="{ huoyue: zhuangtai_shai === 'xunlianzhong' }" @click="shaixuan('xunlianzhong')">训练中</button>
          <button class="biaoqian" :class="{ huoyue: zhuangtai_shai === 'yiwancheng' }" @click="shaixuan('yiwancheng')">已完成</button>
          <button class="biaoqian" :class="{ huoyue: zhuangtai_shai === 'yichang' }" @click="shaixuan('yichang')">异常</button>
        </div>
        <div class="you"><span class="fu">共 {{ zongshu }} 个任务</span></div>
      </div>
      <div class="biaoge-kuang">
        <table class="biaoge">
          <thead><tr>
            <th>任务</th><th>状态</th><th style="width:140px">进度</th><th>轮次</th>
            <th>参与方</th><th>创建者</th><th>创建时间</th><th class="caozuo">操作</th>
          </tr></thead>
          <tbody>
            <tr v-for="x in liebiao" :key="x.id">
              <td>
                <div class="zhu">#{{ x.id }} {{ x.mingcheng }}</div>
                <div class="fu">{{ Pingtai.MOSHI_MING[x.yunxing_moshi] }} · ε {{ x.yinsipi }}/轮 · 预算 {{ x.yusuan_shangxian }}</div>
              </td>
              <td><zhuangtai-biao :zhi="x.zhuangtai" leixing="renwu"></zhuangtai-biao></td>
              <td>
                <jindu-tiao :zhi="x.lunshu ? x.dangqian_lunci / x.lunshu : 0"
                            :se="x.zhuangtai === 'yiwancheng' ? 'good' : (x.zhuangtai === 'yichang' ? 'bad' : '')"></jindu-tiao>
                <div class="fu tabular">{{ x.dangqian_lunci }} / {{ x.lunshu }} 轮</div>
              </td>
              <td class="tabular">{{ x.lunshu }}</td>
              <td class="tabular">{{ x.canjia_shu }} 方<br><span class="fu">{{ shuliang(x.yangben_zong) }} 样本</span></td>
              <td>{{ x.chuangjianzhe_ming }}</td>
              <td class="wenben-ruo">{{ geshihua(x.chuangjian_shijian) }}</td>
              <td class="caozuo">
                <button class="an xiao wenzi" @click="kan(x)">详情</button>
                <button v-if="x.zhuangtai === 'daichufa' && (yonghu.jiaose === 'guanliyuan' || x.chuangjianzhe_id === yonghu.id)"
                        class="an xiao" @click="qidong(x)">启动</button>
              </td>
            </tr>
            <tr v-if="!liebiao.length">
              <td colspan="8">
                <kong-zhuang :ming="jiazai ? '正在加载…' : '没有训练任务'"
                             :fu="neng_chuangjian ? '点击右上角新建任务，选择数据集后即可启动联邦训练' : '你参与的任务会显示在这里'"></kong-zhuang>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <fen-ye :zongshu="zongshu" :ye="ye" :meiye="meiye" @gengxin="qu_ye"></fen-ye>
    </div>

    <tan-chuang v-if="tanchuang" biaoti="新建联邦训练任务" kuan @guanbi="tanchuang = false">
      <div class="biaodan">
        <div class="hang">
          <div class="ziduan">
            <label>任务名称 <span class="xing">*</span></label>
            <input class="shuru" v-model.trim="biaodan.mingcheng" placeholder="例如：跨机构信用评估模型">
          </div>
          <div class="ziduan">
            <label>运行模式</label>
            <select class="xuanze" v-model="biaodan.yunxing_moshi">
              <option value="moni">模拟训练（服务端模拟各参与方）</option>
              <option value="zhenshi">真实联邦（参与方通过接口提交更新）</option>
            </select>
          </div>
        </div>
        <div class="jian-tishi">
          模型固定为 <b>mlp_8_16_2</b>（8-16-2 全连接网络，178 维参数）。模拟模式适合课程演示，
          真实模式需要参与方在「参与方中心」领取全局参数并提交本地更新。
        </div>

        <div class="fenge"></div>
        <div class="hang-3">
          <div class="ziduan">
            <label>训练轮数</label>
            <input class="shuru" type="number" min="1" max="50" v-model.number="biaodan.lunshu">
          </div>
          <div class="ziduan">
            <label>批大小</label>
            <input class="shuru" type="number" min="4" max="1024" v-model.number="biaodan.piliang_daxiao">
          </div>
          <div class="ziduan">
            <label>学习率</label>
            <input class="shuru" type="number" min="0.0001" max="1" step="0.01" v-model.number="biaodan.xuexilv">
          </div>
        </div>

        <div class="fenge"></div>
        <div class="hang-3">
          <div class="ziduan">
            <label>每轮 ε（隐私预算）</label>
            <input class="shuru" type="number" min="0.01" step="0.1" v-model.number="biaodan.yinsipi">
          </div>
          <div class="ziduan">
            <label>L2 裁剪阈值 C</label>
            <input class="shuru" type="number" min="0.1" step="0.1" v-model.number="biaodan.jiancai_yuzhi">
          </div>
          <div class="ziduan">
            <label>预算上限</label>
            <input class="shuru" type="number" min="0.1" step="0.1" v-model.number="biaodan.yusuan_shangxian">
          </div>
        </div>
        <div class="jian-tishi" :class="{ warn: ke_xunlian_lunshu < biaodan.lunshu }">
          当前预算最多可训练 <b>{{ ke_xunlian_lunshu }}</b> 轮（上限 {{ biaodan.yusuan_shangxian }} ÷ 每轮 {{ biaodan.yinsipi }}）。
          <span v-if="ke_xunlian_lunshu < biaodan.lunshu">训练会在预算耗尽的那一轮前停止，建议调低轮数或提高预算上限。</span>
        </div>

        <div class="fenge"></div>
        <div class="ziduan">
          <label>参与方数据集 <span class="xing">*</span>（已选 {{ xuanze_shuliang }} 个，样本合计 {{ shuliang(zong_yangben) }}）</label>
          <div style="display:flex;flex-direction:column;gap:8px">
            <label v-for="s in keyong_shujuji" :key="s.id" class="fuxuan" :class="{ xuan: biaodan.canjia[s.id] && biaodan.canjia[s.id].xuan }">
              <input type="checkbox" v-model="biaodan.canjia[s.id].xuan">
              <span style="flex:1">
                <b>{{ s.mingcheng }}</b>
                <span class="wenben-ruo"> · {{ s.tigongfang_ming }} · {{ Pingtai.GESHI_MING[s.geshi] }}</span>
              </span>
              <span class="wenben-ruo">样本</span>
              <input class="shuru" style="width:110px;padding:5px 8px" type="number" min="1" :max="s.yangben_shu"
                     v-model.number="biaodan.canjia[s.id].yangben_shu" :disabled="!biaodan.canjia[s.id].xuan">
            </label>
            <div v-if="!keyong_shujuji.length" class="wenben-ruo">没有可用数据集，请先由数据提供方登记并通过校验。</div>
          </div>
          <span class="shuoming">同一提供方只能加入一次；样本数用于加权聚合，可不填，默认取数据集登记值。</span>
        </div>
      </div>
      <template #jiao>
        <button class="an" @click="tanchuang = false">取消</button>
        <button class="an zhuyi" @click="tijiao" :disabled="tijiao_zhong">{{ tijiao_zhong ? '创建中…' : '创建任务' }}</button>
      </template>
    </tan-chuang>
  </div>`,
};
