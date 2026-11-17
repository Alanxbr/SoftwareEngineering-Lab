"""轻量级 numpy MLP：前向、反向传播与参数序列化。"""

import numpy as np

SHURU_WEIDU = 8
YINCANG_WEIDU = 16
SHUCHU_WEIDU = 2


class MlpMoxing:
    """8-16-2 全连接网络，二分类。"""

    def __init__(self, zhongzi: int = 42,
                 shuru_weidu: int = SHURU_WEIDU,
                 yincang_weidu: int = YINCANG_WEIDU,
                 shuchu_weidu: int = SHUCHU_WEIDU):
        self.shuru_weidu = shuru_weidu
        self.yincang_weidu = yincang_weidu
        self.shuchu_weidu = shuchu_weidu
        suijishu = np.random.default_rng(zhongzi)
        self.W1 = suijishu.normal(0.0, np.sqrt(2.0 / shuru_weidu),
                                  (shuru_weidu, yincang_weidu))
        self.b1 = np.zeros(yincang_weidu)
        self.W2 = suijishu.normal(0.0, np.sqrt(2.0 / yincang_weidu),
                                  (yincang_weidu, shuchu_weidu))
        self.b2 = np.zeros(shuchu_weidu)

    @property
    def weidu(self) -> int:
        return (self.shuru_weidu * self.yincang_weidu + self.yincang_weidu
                + self.yincang_weidu * self.shuchu_weidu + self.shuchu_weidu)

    def qu_canshu(self) -> np.ndarray:
        """把各层参数摊平成一维向量。"""
        return np.concatenate([
            self.W1.ravel(), self.b1.ravel(), self.W2.ravel(), self.b2.ravel(),
        ])

    def she_canshu(self, canshu) -> None:
        """从一维向量恢复各层参数。"""
        xiangliang = np.asarray(canshu, dtype=float)
        if xiangliang.size != self.weidu:
            raise ValueError(f'参数维度应为 {self.weidu}，实际为 {xiangliang.size}')
        weizhi = 0
        changdu = self.shuru_weidu * self.yincang_weidu
        self.W1 = xiangliang[weizhi:weizhi + changdu].reshape(
            self.shuru_weidu, self.yincang_weidu)
        weizhi += changdu
        self.b1 = xiangliang[weizhi:weizhi + self.yincang_weidu].copy()
        weizhi += self.yincang_weidu
        changdu = self.yincang_weidu * self.shuchu_weidu
        self.W2 = xiangliang[weizhi:weizhi + changdu].reshape(
            self.yincang_weidu, self.shuchu_weidu)
        weizhi += changdu
        self.b2 = xiangliang[weizhi:weizhi + self.shuchu_weidu].copy()

    def _qianxiang(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        z1 = X @ self.W1 + self.b1
        a1 = np.maximum(z1, 0.0)
        z2 = a1 @ self.W2 + self.b2
        z2 = z2 - z2.max(axis=1, keepdims=True)
        jingyan = np.exp(z2)
        gailv = jingyan / jingyan.sum(axis=1, keepdims=True)
        return z1, a1, gailv

    def yuce(self, X: np.ndarray) -> np.ndarray:
        return self._qianxiang(np.asarray(X, dtype=float))[2]

    def sunshi(self, X: np.ndarray, y: np.ndarray) -> float:
        gailv = self.yuce(X)
        zhengque = gailv[np.arange(len(y)), np.asarray(y, dtype=int)]
        return float(-np.mean(np.log(np.clip(zhengque, 1e-12, 1.0))))

    def zhunquelv(self, X: np.ndarray, y: np.ndarray) -> float:
        yuce = np.argmax(self.yuce(X), axis=1)
        return float(np.mean(yuce == np.asarray(y, dtype=int)))

    def xunlian_yilun(self, X: np.ndarray, y: np.ndarray, xuexilv: float,
                      piliang: int, suijishu: np.random.Generator) -> float:
        """一轮小批量 SGD，返回平均交叉熵损失。"""
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        suoyin = suijishu.permutation(len(X))
        zong_sunshi = 0.0
        piliang_shu = 0
        for qi in range(0, len(X), piliang):
            xuan = suoyin[qi:qi + piliang]
            xb, yb = X[xuan], y[xuan]
            z1, a1, gailv = self._qianxiang(xb)
            zhengque = gailv[np.arange(len(yb)), yb]
            zong_sunshi += float(-np.sum(np.log(np.clip(zhengque, 1e-12, 1.0))))
            piliang_shu += len(yb)
            d2 = gailv.copy()
            d2[np.arange(len(yb)), yb] -= 1.0
            d2 /= len(yb)
            dW2 = a1.T @ d2
            db2 = d2.sum(axis=0)
            da1 = d2 @ self.W2.T
            dz1 = da1 * (z1 > 0)
            dW1 = xb.T @ dz1
            db1 = dz1.sum(axis=0)
            self.W1 -= xuexilv * dW1
            self.b1 -= xuexilv * db1
            self.W2 -= xuexilv * dW2
            self.b2 -= xuexilv * db2
        return zong_sunshi / max(1, piliang_shu)
