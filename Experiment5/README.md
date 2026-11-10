# 实验5：系统详细设计

## 实验目的

掌握详细设计方法，基于实验4的概要设计完成核心模块的类设计、关键业务时序设计和数据库 E-R 设计，并检查设计是否满足第三范式。

## 项目选题

隐私计算数据共享平台（联邦学习 + 差分隐私）。

## 设计结果

- **类图**：4 张，覆盖 6 个核心模块
  - 用户管理与系统管理（`Yonghu` 抽象类 + 3 个角色子类 + `XitongRizhi`）
  - 数据管理、联邦训练与隐私保护（`Shujuji`、`XunlianRenwu`、`CanjiaFang`、`LunciJilu`、`YinsiPeizhi`、`YinsiYusuan`）
  - 业务服务层（`FuwuJichu` + 6 个服务类）
  - 数据访问层（`DaoJichu` + 6 个 DAO + `Shujuku`）
- **时序图**：2 张
  - 联邦训练任务执行（创建、预算检查、逐轮训练、聚合、预算记录、结果查询）
  - 数据集登记与格式校验（本地校验、登记、查重、可选脱敏）
- **数据库**：7 张表，全部给出主键、外键、唯一约束、CHECK 约束和索引，并做 1NF/2NF/3NF 分析
  - yonghu、shujuji、xunlian_renwu、renwu_canjiafang、lunci_jilu、yinsi_yusuan、xitong_rizhi

## 交付物

| 文件 | 说明 |
| --- | --- |
| `实验5-系统详细设计-实验内容.md` | 实验内容正文：类设计、时序流程、数据库设计、范式分析和需求追踪 |
| `uml/leitu_1_yonghu.puml` | 用户管理与系统管理模块类图源文件 |
| `uml/leitu_2_shuju_xunlian.puml` | 数据管理、联邦训练与隐私保护模块类图源文件 |
| `uml/leitu_3_fuwu.puml` | 业务服务层类图源文件 |
| `uml/leitu_4_dao.puml` | 数据访问层类图源文件 |
| `uml/shixu_1_lianhe_xunlian.puml` | 联邦训练任务执行时序图源文件 |
| `uml/shixu_2_shuju_dengji.puml` | 数据集登记与格式校验时序图源文件 |
| `uml/er_tu.dot` | E-R 图源文件 |
| `uml/*.png`、`uml/*.svg` | 各图的位图和矢量图 |

## 建模工具

- PlantUML 1.2024.7（类图、时序图），渲染命令：`java -jar plantuml.jar -charset UTF-8 -tpng xxx.puml`
- Graphviz 16.1.0（E-R 图），渲染命令：`dot -Tpng er_tu.dot -o er_tu.png`

## 设计原则

1. 类名、方法名沿用拼音命名规范，与实验4的模块内部接口一一对应；
2. 属性私有、方法公开，公共行为（权限判断、日志、SQL 执行）放在抽象基类，不在子类重复实现；
3. 关系按生命周期确定：任务与轮次、预算为组合，任务与参与方为聚合；
4. 数据库满足第三范式，可推导的数据不落库；
5. 原始训练数据不落库、不出本地，数据库中只保存元信息、任务状态、指标和参数文件路径。
