"""单元测试包：启动前把数据目录切到临时目录，避免污染演示库。"""

import atexit
import os
import shutil
import tempfile
from pathlib import Path

_MULU = Path(tempfile.mkdtemp(prefix='pingtai_danxiang_'))
os.environ['PINGTAI_SHUJU'] = str(_MULU)
atexit.register(shutil.rmtree, _MULU, ignore_errors=True)

from backend import db, seed  # noqa: E402

db.chushi_hua()
seed.chushihua_shuju()
