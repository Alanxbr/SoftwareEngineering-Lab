"""请求与响应数据模型。"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ZhuceRuku(BaseModel):
    yonghuming: str = Field(min_length=3, max_length=32)
    mima: str = Field(min_length=6, max_length=64)
    youxiang: str = Field(min_length=5, max_length=120)
    jiaose: Literal['tigongfang', 'shiyongfang'] = 'shiyongfang'

    @field_validator('yonghuming')
    @classmethod
    def jiancha_yonghuming(cls, zhi: str) -> str:
        if not all(c.isalnum() or c in '_-' for c in zhi):
            raise ValueError('用户名只能包含字母、数字、下划线和短横线')
        return zhi

    @field_validator('youxiang')
    @classmethod
    def jiancha_youxiang(cls, zhi: str) -> str:
        if '@' not in zhi or '.' not in zhi.split('@')[-1]:
            raise ValueError('邮箱格式不正确')
        return zhi


class DengluRuku(BaseModel):
    yonghuming: str
    mima: str


class ShujujiRuku(BaseModel):
    mingcheng: str = Field(min_length=2, max_length=64)
    geshi: Literal['csv', 'json', 'parquet', 'npy'] = 'csv'
    daxiao: int = Field(gt=0, le=10 * 1024 * 1024 * 1024)
    yangben_shu: int = Field(gt=0, le=100_000_000)
    ziduan: list[str] = Field(default_factory=list)
    benzhi_lujing: str = Field(default='', max_length=300)
    tuomin_guize: str = Field(default='', max_length=300)

    @field_validator('ziduan')
    @classmethod
    def jiancha_ziduan(cls, zhi: list[str]) -> list[str]:
        jieguo = [x.strip() for x in zhi if x.strip()]
        if len(jieguo) != len(set(jieguo)):
            raise ValueError('字段名不能重复')
        return jieguo


class ShujuZhuangtaiRuku(BaseModel):
    zhuangtai: Literal['yijiaoyan', 'yitingyong']


class ShujuJiaoyanRuku(BaseModel):
    ziduan: list[str] = Field(default_factory=list)
    yangben_shu: int = Field(gt=0)
    geshi: str = 'csv'
    biaozhun_ziduan: list[str] = Field(default_factory=list)


class CanjiafangRuku(BaseModel):
    shujuji_id: int
    yangben_shu: int | None = Field(default=None, gt=0)


class RenwuRuku(BaseModel):
    mingcheng: str = Field(min_length=2, max_length=64)
    moxing_leixing: Literal['mlp_8_16_2'] = 'mlp_8_16_2'
    lunshu: int = Field(ge=1, le=50)
    piliang_daxiao: int = Field(ge=4, le=1024, default=16)
    xuexilv: float = Field(gt=0, le=1, default=0.05)
    yinsipi: float = Field(gt=0, le=10, default=0.5)
    jiancai_yuzhi: float = Field(gt=0, le=100, default=1.0)
    yusuan_shangxian: float = Field(gt=0, le=100, default=5.0)
    yunxing_moshi: Literal['moni', 'zhenshi'] = 'moni'
    canjia: list[CanjiafangRuku] = Field(min_length=1)

    @field_validator('canjia')
    @classmethod
    def jiancha_canjia(cls, zhi: list[CanjiafangRuku]) -> list[CanjiafangRuku]:
        if len({x.shujuji_id for x in zhi}) != len(zhi):
            raise ValueError('同一数据集不能重复加入任务')
        return zhi


class GuanliYonghuRuku(BaseModel):
    zhuangtai: Literal['zhengchang', 'tingyong']


class GuanliRenwuRuku(BaseModel):
    zhuangtai: Literal['yiquxiao', 'yichang']
    yuanyin: str = Field(default='管理员操作', max_length=200)


class KehuduanGengxinRuku(BaseModel):
    lunci_hao: int = Field(gt=0)
    gengxin: list[float] = Field(min_length=1)
    yangben_shu: int = Field(gt=0)
    sunshi: float = Field(ge=0, default=0)
    zhunquelv: float = Field(ge=0, le=1, default=0)
    haoshi: float = Field(ge=0, default=0)
