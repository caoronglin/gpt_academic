# -*- coding: utf-8 -*-
"""
PyInstaller hook for pydub and its audio dependencies
"""

import os
import sys

from PyInstaller.utils.hooks import collect_data_files, copy_metadata

# 收集pydub的数据文件
datas = collect_data_files("pydub")

# 添加必要的元数据
datas += copy_metadata("pydub")

# 对于Python 3.14，audioop可能不可用，需要特殊处理
hiddenimports = ["pydub", "pydub.audio_segment", "pydub.utils"]

# 尝试不同的audioop模块名称
if sys.version_info < (3, 14):
    hiddenimports.extend(["audioop", "pyaudioop"])
    if sys.version_info >= (3, 10):
        hiddenimports.append("_audioop")
else:
    # Python 3.14+ 可能需要替代方案或手动实现
    # 添加空模块占位符以避免导入错误
    hiddenimports.extend(["audioop", "pyaudioop", "_audioop"])
