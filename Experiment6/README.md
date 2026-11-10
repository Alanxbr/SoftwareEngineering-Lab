# 实验6 隐私计算数据共享平台：核心模块代码

本目录是《软件工程实验》实验6的交付物，按实验5的详细设计实现**联邦训练模块**，
并通过公开接口调用数据管理模块和隐私保护模块，演示模块化开发与编码规范。

## 一、实现范围

| 模块 | 实现内容 | 说明 |
| --- | --- | --- |
| 联邦训练 FT | 任务创建、启动校验、逐轮训练、加权聚合、状态查询 | 本次核心模块 |
| 数据管理 DM | 数据集登记、查询、停用 | 供训练模块调用 |
| 隐私保护 PP | L2 裁剪、拉普拉斯加噪、预算检查与记录 | 纯函数式接口 |
| 公共组件 | 统一返回结构、操作日志 | 被各模块复用 |
| 数据访问 | SQLite 连接、7 张表建表、各表 DAO | SQL 只出现在这一层 |

接口层（FastAPI 路由）和前端不在本次代码范围内，实验6按模板要求聚焦一个模块的核心代码。

## 二、目录结构

```text
Experiment6/
├── README.md
├── 实验6-编码规范与模块化编程-实验内容.md
├── uml/
│   ├── mokuai_yilai_tu.dot
│   ├── mokuai_yilai_tu.png
│   └── mokuai_yilai_tu.svg
└── src/
    ├── demo.py                 演示入口
    ├── zhuangpei.py            依赖装配
    ├── gonggong/
    │   ├── fanhui.py           统一返回结构
    │   └── rizhi.py            日志组件
    ├── cunchu/
    │   ├── shujuku.py          SQLite 连接与建表
    │   └── dao.py              各表 DAO
    ├── mokuai/
    │   ├── shuju_fuwu.py       数据管理模块
    │   ├── yinsi_fuwu.py       隐私保护模块
    │   └── xunlian_fuwu.py     联邦训练模块（核心）
    └── tests/
        └── test_xunlian_fuwu.py
```

## 三、运行环境与步骤

- Python 3.10 及以上（使用了 `list[float]`、`X | None` 类型写法）。
- 仅使用标准库：`sqlite3`、`json`、`math`、`random`、`unittest`，不需要安装第三方包。

```bash
cd Experiment6/src

# 运行演示：登记数据集 → 创建任务 → 启动 → 训练 3 轮 → 查询状态
python demo.py

# 运行单元测试（8 个用例）
python -m unittest discover -s tests -v
```

演示程序和测试都使用系统临时目录，不会在仓库里留下数据库或参数文件。

## 四、核心模块说明

### 4.1 训练流程

1. `XunlianFuwu.chuangjian_renwu` 校验任务参数和参与方数据集，写入任务与参与方表。
2. `XunlianFuwu.qidong_xunlian` 再次检查数据集、参与方和隐私预算，把任务置为训练中。
3. `XunlianFuwu.zhixing_lunci` 对每个参与方的更新调用 `YinsiFuwu.jiazao_gengxin`
   裁剪加噪，再调用 `juhe_canshu` 按样本数加权平均。
4. 每轮结束写入预算记录和轮次记录，全局参数按“任务编号/轮次”保存为 JSON 文件。
5. `XunlianFuwu.chaxun_zhuangtai` 返回任务状态、每轮指标和预算使用情况。

### 4.2 模块间接口

| 调用方 | 被调用方 | 接口 | 说明 |
| --- | --- | --- | --- |
| XunlianFuwu | ShujuFuwu | `chaxun_shujuji` | 校验参与方数据集存在且已校验 |
| XunlianFuwu | YinsiFuwu | `jiancha_yusuan` | 启动前和每轮前检查预算 |
| XunlianFuwu | YinsiFuwu | `jiazao_gengxin` | 裁剪加噪 |
| XunlianFuwu | YinsiFuwu | `jilu_yusuan` | 写入本轮消耗并返回剩余额度 |

模块之间只通过公开方法通信，不访问对方的 DAO，不共享全局变量。

### 4.3 错误码

| 错误码 | 含义 |
| --- | --- |
| 4001 | 隐私预算不足 |
| 4002 | 数据集不存在或不可用 |
| 4003 | 参与方缺失、重复或掉线 |
| 4004 | 任务状态不允许当前操作 |
| 4005 | 参数不合法 |
| 4006 | 数据集名称重复 |

## 五、编码规范摘要

完整规范见 `实验6-编码规范与模块化编程-实验内容.md` 第 3.1 节，要点如下：

- 类名用大驼峰拼音，函数和变量用小写下划线拼音，常量全大写。
- 文件、类、公开方法写中文文档字符串；行内注释只解释“为什么”。
- 4 空格缩进，单行不超过 100 个字符，函数不超过 50 行。
- 公开接口标注类型；业务失败返回 `FanhuiJieguo`，不抛未捕获异常。
- SQL 只写在 `cunchu/dao.py`，业务层不拼接 SQL。

## 六、Git 约定

- 分支：`master` 保存可交付版本，`dev` 日常集成，功能在 `feature/xxx` 上开发。
- 提交信息格式：`类型(范围): 说明`，类型取 `feat`、`fix`、`docs`、`test`、`chore`。
- 一次提交只做一件事；不提交 `__pycache__`、`.db` 文件和训练参数文件。
