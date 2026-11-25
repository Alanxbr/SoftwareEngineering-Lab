"""FastAPI 应用入口：路由挂载、异常处理与启动初始化。

启动命令（在 Platform 目录下）：
    python main.py
或
    python -m uvicorn main:app --host 127.0.0.1 --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend import dao, db, seed, xiangying
from backend.config import QIANDUAN_MULU, chushihua_mulu
from backend.db import YewuCuowu
from backend.routers import (
    gongzuotai,
    guanli,
    kehuduan,
    shuju,
    xitong,
    xunlian,
    yonghu,
)

rizhi = logging.getLogger('pingtai')

# 前端开发服务器（Vue）常用端口；前端未部署时不影响接口调用
CORS_LAIYUAN = ['http://localhost:5173', 'http://127.0.0.1:5173']


@asynccontextmanager
async def shengming_zhouqi(app: FastAPI):
    """启动时建表、写演示数据，并把上次中断的训练标记为异常。"""
    chushihua_mulu()
    db.chushi_hua()
    seed.chushihua_shuju()
    zhongduan = dao.qingli_shibai_renwu()
    if zhongduan:
        rizhi.warning('已把 %s 个中断的训练任务标记为异常', zhongduan)
    rizhi.info('隐私计算数据共享平台启动完成')
    yield
    rizhi.info('平台已停止')


app = FastAPI(
    title='隐私计算数据共享平台',
    description='联邦学习 + 差分隐私的课程实验平台',
    version='1.0.0',
    lifespan=shengming_zhouqi,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_LAIYUAN,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(YewuCuowu)
async def yewu_yichang(request: Request, cuowu: YewuCuowu) -> JSONResponse:
    """业务异常统一转换成 {code, message, data}。"""
    return JSONResponse(
        status_code=cuowu.http_zhuangtai,
        content=xiangying.shibai(cuowu.cuowu_ma, cuowu.xiaoxi),
    )


@app.exception_handler(RequestValidationError)
async def canshu_yichang(request: Request,
                         cuowu: RequestValidationError) -> JSONResponse:
    """Pydantic 校验失败按平台错误码 4005 返回，不暴露 422 原始结构。"""
    xiang = []
    for cuo in cuowu.errors()[:3]:
        weizhi = '.'.join(str(x) for x in cuo.get('loc', []) if x != 'body')
        xiaoxi = cuo.get('msg', '参数不合法')
        xiang.append(f'{weizhi}: {xiaoxi}' if weizhi else xiaoxi)
    return JSONResponse(
        status_code=400,
        content=xiangying.shibai(4005, '；'.join(xiang) or '请求参数不合法'),
    )


@app.exception_handler(Exception)
async def weizhi_yichang(request: Request, cuowu: Exception) -> JSONResponse:
    """未预期异常统一返回 500 信封，细节只写服务端日志。"""
    rizhi.exception('未处理异常：%s %s', request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=xiangying.shibai(5000, '服务器内部错误'),
    )


for lu in (yonghu.router, shuju.router, xunlian.router, kehuduan.router,
           gongzuotai.router, xitong.router, guanli.router):
    app.include_router(lu)


@app.get('/')
def shouye():
    """有前端时返回单页入口，否则返回平台信息。"""
    shouye_wenjian = QIANDUAN_MULU / 'index.html'
    if shouye_wenjian.exists():
        return FileResponse(str(shouye_wenjian))
    return xiangying.chenggong({
        'mingcheng': '隐私计算数据共享平台',
        'banben': '1.0.0',
        'wendang': '/docs',
        'shoukong': '/xunlian',
    })


# 前端产物存在时挂载为静态站点；接口路由先注册，优先级更高
if QIANDUAN_MULU.exists():
    app.mount('/', StaticFiles(directory=str(QIANDUAN_MULU), html=True),
              name='qianduan')


if __name__ == '__main__':
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')
