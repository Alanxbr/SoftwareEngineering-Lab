# 隐私计算数据共享平台

《软件工程实验》课程项目：面向多数据持有方的**联邦学习 + 差分隐私**数据共享平台。
数据不出本地，各方只上传加噪后的模型更新，服务端按样本数加权聚合成全局模型。

本目录是平台的可运行实现：FastAPI 后端 + Vue 3 单页前端，对应实验4、实验5的架构设计与详细设计。

## 一、技术栈

| 项目 | 选型 |
| --- | --- |
| Web 框架 | FastAPI + Uvicorn |
| 数据库 | SQLite（单文件，WAL 模式） |
| 模型 | NumPy 实现的 8-16-2 全连接网络（二分类，178 维参数） |
| 隐私保护 | L2 裁剪 + 拉普拉斯机制 |
| 认证 | JWT（HS256）+ bcrypt 密码哈希 |
| 前端 | Vue 3.5（全局构建，无需 Node 打包）+ ECharts 5.6，依赖已放在 `frontend/vendor/` |

## 二、目录结构

```text
Platform/
├── main.py                 FastAPI 入口：路由挂载、异常处理、启动初始化
├── requirements.txt
├── backend/
│   ├── config.py           路径、JWT 密钥、超时与保留期配置
│   ├── db.py               SQLite 连接、7 张表建表、业务异常
│   ├── dao.py              全部 SQL 集中在这里
│   ├── schemas.py          Pydantic 请求模型与字段校验
│   ├── security.py         bcrypt 哈希与 JWT 签发解析
│   ├── deps.py             登录态、角色校验、客户端 IP
│   ├── xiangying.py        统一响应结构 {code, message, data}
│   ├── seed.py             首次启动写入演示账号、数据集与训练任务（带版本升级）
│   ├── routers/            HTTP 接口层（7 个路由模块，31 个接口）
│   ├── services/           业务层（用户、数据、训练、隐私、管理、系统）
│   └── federated/          联邦训练：模型、数据合成、本地模拟、协调器
├── frontend/               单页前端（由 FastAPI 直接托管）
│   ├── index.html
│   ├── css/app.css         设计变量与全部样式（类名沿用拼音命名）
│   ├── js/api.js           全局状态、fetch 封装、哈希路由、格式化
│   ├── js/components.js    状态徽标、弹窗、分页、数字卡、折线图等通用组件
│   ├── js/views-main.js    登录、工作台、数据集、训练任务列表
│   ├── js/views-detail.js  任务详情、参与方中心、用户/日志/备份管理、关于
│   ├── js/app.js           根组件：侧边栏、顶栏、路由表与权限守卫
│   └── vendor/             Vue、ECharts 本地副本（不依赖外网）
└── data/                   运行后生成：pingtai.db、参数文件、备份
```

## 三、快速开始

```bash
cd Platform
pip install -r requirements.txt

# 启动服务（默认 127.0.0.1:8000）
python main.py
```

启动时会自动建表、写入演示数据，并把上次异常中断的训练任务标记为异常。

- 平台界面：<http://127.0.0.1:8000/>（`frontend/` 存在时由 FastAPI 直接托管单页应用）
- 接口文档：<http://127.0.0.1:8000/docs>

若把 `frontend/` 目录移走，`/` 会退化为返回平台信息的 JSON，接口本身不受影响。

演示账号（首次启动自动创建）：

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| admin | admin123 | 系统管理员 |
| tigong1 / tigong2 / tigong3 | 123456 | 数据提供方 |
| shiyong1 / shiyong2 | 123456 | 数据使用方 |

演示数据规模（`seed.py`，版本 2）：

- 6 个数据集，合计 **57,000 条样本**：医疗影像 12,000、金融风控 8,600、制造质检 15,000、
  零售消费 6,400、交通流量 9,800、教育测评 5,200；
- 5 个训练任务，覆盖全部状态：已完成 1 个（5 轮曲线 + 隐私预算记录）、待启动 2 个、
  已取消 1 个、异常 1 个；
- 12 条操作日志，含成功与失败的登录记录。

演示数据版本记录在数据库 `PRAGMA user_version`。旧版本演示库在启动时会先用 SQLite
备份接口另存到 `data/beifen/pingtai_yanshi_v1_*.db`，再清空重建，不需要手工删库。

修改数据目录（测试时避免污染正式库）：

```bash
PINGTAI_SHUJU=D:/tmp/pingtai_data python main.py
```

## 四、前端页面

前端是无需构建的 Vue 3 单页应用：全局构建版 Vue 与 ECharts 放在 `frontend/vendor/`，
浏览器直接加载 `js/*.js`，FastAPI 用 `StaticFiles` 把整个目录挂到 `/`。改完代码刷新即可，不需要 Node。

| 路由 | 页面 | 可见角色 | 主要内容 |
| --- | --- | --- | --- |
| `#/login` | 登录/注册 | 未登录 | 登录注册切换、演示账号一键填充、注册时选角色 |
| `#/dashboard` | 工作台 | 全部 | 4 张统计卡、最近任务、快捷入口、平台健康状态 |
| `#/datasets` | 数据集 | 全部 | 检索与状态筛选、登记（先做格式预检）、详情、停用/恢复 |
| `#/tasks` | 训练任务 | 全部 | 状态分页列表、新建任务（基本/训练/隐私/参与方四段式表单）、启动 |
| `#/tasks/:id` | 任务详情 | 全部 | 进度与指标、损失与准确率两张独立曲线、轮次表、隐私预算、参与方、管理员强制终止 |
| `#/client` | 参与方中心 | 提供方、使用方 | 参与任务列表、领取全局参数（178 维预览）、提交本地更新 |
| `#/admin/users` | 用户管理 | 管理员 | 账号列表、角色与状态、启用/停用 |
| `#/admin/logs` | 系统日志 | 管理员 | 按类型/结果/用户/时间过滤、分页 |
| `#/admin/backups` | 数据备份 | 管理员 | 创建备份、备份列表、授权下载 |
| `#/about` | 关于平台 | 全部 | 技术栈、模型结构、隐私机制、角色说明 |

实现要点：

- 路由是哈希路由，全局状态集中在 `Pingtai`（`js/api.js`）：令牌存 `localStorage`，
  `qingqiu()` 自动带 `Authorization`、拆 `{code, message, data}` 信封，收到 401 时清空登录态并回登录页。
- 侧边栏由 `app.js` 的 `CaidanXiang` 按角色过滤；`dangqian` 计算属性把路径解析成组件，
  `jiancha_quanxian()` 负责未登录跳转和越权拦截。
- 损失和准确率是两张独立图表，不共用坐标轴；任务进行中每 3 秒轮询任务、曲线与隐私预算。
- 视图使用 Options API，通用件（弹窗、分页、状态徽标、数字卡、折线图）在 `js/components.js`。

## 五、接口概览

| 模块 | 方法与路径 | 说明 |
| --- | --- | --- |
| 用户 | `POST /yonghu/zhuce`、`POST /yonghu/denglu`、`GET /yonghu/wo` | 注册、登录、当前用户 |
| 用户 | `GET /yonghu`、`PATCH /yonghu/{id}/zhuangtai` | 管理员查看/停用账号 |
| 数据 | `POST /shuju/jiaoyan`、`POST /shuju`、`GET /shuju`、`GET /shuju/{id}` | 格式预检、登记、列表、详情 |
| 数据 | `PATCH /shuju/{id}/zhuangtai` | 停用/恢复数据集 |
| 训练 | `POST /xunlian`、`GET /xunlian`、`GET /xunlian/{id}` | 创建、列表、详情 |
| 训练 | `POST /xunlian/{id}/qidong` | 启动后台联邦训练 |
| 训练 | `GET /xunlian/{id}/quxian`、`GET /xunlian/{id}/yinsi` | 损失/准确率曲线、隐私预算 |
| 参与方 | `GET /kehuduan/renwu`、`GET /kehuduan/renwu/{id}`、`POST /kehuduan/renwu/{id}/tijiao` | 真实模式下领取全局参数并提交本地更新 |
| 工作台 | `GET /zonglan` | 按角色返回统计 |
| 系统 | `GET /xitong/jiankang`、`GET /xitong/xinxi` | 健康检查、平台信息 |
| 管理 | `/guanli/yonghu`、`/guanli/renwu`、`/guanli/rizhi`、`/guanli/beifen` | 用户/任务/日志/备份 |

统一响应格式：

```json
{"code": 0, "message": "操作成功", "data": {}}
```

## 六、错误码

| 错误码 | 含义 |
| --- | --- |
| 4001 | 隐私预算不足 |
| 4002 | 数据集不存在或不可用 |
| 4003 | 参与方缺失、重复或掉线 |
| 4004 | 任务状态不允许当前操作 |
| 4005 | 参数不合法 |
| 4006 | 数据集名称重复 |
| 4010 | 未登录或凭证无效 |
| 4030 | 当前角色无权执行该操作 |
| 4040 | 资源不存在 |

业务异常由 `main.py` 的异常处理器统一转换；Pydantic 校验失败也返回 4005，
前端不需要处理 422 的原始结构。前端把 `message` 直接作为提示条内容，
并按 `code` 区分提示样式（预算不足、角色越权等显示警告色）。

## 七、联邦训练流程

1. 数据提供方登记数据集（只登记元数据，原始数据留在本地）。
2. 数据使用方创建任务，选择参与方数据集、轮数、ε、裁剪阈值、预算上限。
3. 启动后协调器按轮执行：
   - 检查累计 ε 是否超过预算上限（超限则任务异常停止）；
   - `moni` 模式：服务端为每个参与方模拟一轮本地 SGD（单方单轮最多使用 20,000 条样本，
     可用 `PINGTAI_YANGBEN_SHANGXIAN` 调低）；
     `zhenshi` 模式：等待参与方通过 `/kehuduan` 接口提交更新；
   - 对更新做 L2 裁剪并加入拉普拉斯噪声，噪声尺度 `b = C / (ε·√d)`；
   - 按服务端记录的样本数加权聚合，样本数不采用客户端上传值；
   - 在固定合成基准集上评估，保存全局参数文件，写入预算与轮次记录。
4. 最后一轮结束把任务置为已完成；预算不足、参与方掉线、服务重启都会让任务进入异常状态。

隐私参数默认：裁剪阈值 `C = 1.0`，每轮 `ε = 0.5`，预算上限按任务配置。

## 八、编码与提交约定

- 命名、注释、格式规范与实验6 一致：类名大驼峰拼音，函数/变量小写下划线拼音，常量全大写。
- SQL 只写在 `backend/dao.py`；业务层不拼接 SQL，不直接返回 `None` 表示失败。
- 提交信息格式 `类型(范围): 说明`，类型取 `feat`、`fix`、`docs`、`test`、`chore`。
- 不提交 `__pycache__`、`data/`、`*.db` 和参数文件（见仓库根目录 `.gitignore`）。
