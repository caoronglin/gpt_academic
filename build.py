#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT Academic 构建脚本
支持Windows和macOS平台的打包
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def create_pyinstaller_spec():
    """创建PyInstaller spec文件"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.getcwd())

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('requirements.txt', '.'),
        ('request_llms', 'request_llms'),
        ('crazy_functions', 'crazy_functions'),
        ('shared_utils', 'shared_utils'),
        ('themes', 'themes'),
        ('docs', 'docs'),
        ('tests', 'tests'),
    ],
    hiddenimports=[
        'config',
        'request_llms.bridge_all',
        'request_llms.bridge_qwen',
        'request_llms.bridge_qwen_local',
        'request_llms.com_qwenapi',
        'gradio',
        'fastapi',
        'uvicorn',
        'markdown',
        'requests',
        'numpy',
        'pandas',
        'matplotlib',
        'plotly',
        'altair',
        'spacy',
        'transformers',
        'torch',
        'dashscope',
        'langchain',
        'llama_index',
        'openai',
        'tiktoken',
        'beautifulsoup4',
        'selenium',
        'pyautogui',
        'pyperclip',
        'pygetwindow',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'tkinter',
        'threading',
        'multiprocessing',
        'concurrent.futures',
        'asyncio',
        'aiofiles',
        'aiohttp',
        'websockets',
        'json',
        're',
        'os',
        'sys',
        'time',
        'datetime',
        'logging',
        'hashlib',
        'base64',
        'urllib',
        'urllib.parse',
        'urllib.request',
        'ssl',
        'socket',
        'email',
        'smtplib',
        'zipfile',
        'tarfile',
        'gzip',
        'bz2',
        'lzma',
        'csv',
        'xml',
        'html',
        'http',
        'ftplib',
        'telnetlib',
        'poplib',
        'imaplib',
        'nntplib',
        'socketserver',
        'xmlrpc',
        'webbrowser',
        'cgi',
        'cgitb',
        'wsgiref',
        'pydoc',
        'doctest',
        'unittest',
        'test',
        'pdb',
        'profile',
        'cProfile',
        'hotshot',
        'timeit',
        'trace',
        'tracemalloc',
        'linecache',
        'pickle',
        'shelve',
        'copy',
        'pprint',
        'reprlib',
        'enum',
        'types',
        'collections',
        'collections.abc',
        'heapq',
        'bisect',
        'array',
        'weakref',
        'copyreg',
        'operator',
        'functools',
        'itertools',
        'toolz',
        'toolz.itertoolz',
        'toolz.functoolz',
        'toolz.dicttoolz',
        'audioop',
        'pyaudioop',
        'pydub',
        'pydub.audio_segment',
        'pydub.utils',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GPT_Academic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    with open("gpt_academic.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    print("✅ PyInstaller spec文件创建成功")


def build_windows():
    """构建Windows版本"""
    print("🚀 开始构建Windows版本...")

    # 检查PyInstaller是否可用
    try:
        import PyInstaller

        print("✅ PyInstaller已安装")
    except ImportError:
        print("❌ PyInstaller未安装，请运行: pip install pyinstaller")
        sys.exit(1)

    # 创建spec文件
    create_pyinstaller_spec()

    # 执行PyInstaller构建
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "gpt_academic.spec",
        "--clean",
        "--noconfirm"
    ]

    try:
        subprocess.run(cmd, check=True)
        print("✅ Windows版本构建成功")

        # 清理临时文件
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("gpt_academic.spec"):
            os.remove("gpt_academic.spec")

    except subprocess.CalledProcessError as e:
        print(f"❌ Windows构建失败: {e}")
        sys.exit(1)


def build_macos():
    """构建macOS版本"""
    print("🚀 开始构建macOS版本...")

    # 检查PyInstaller是否可用
    try:
        import PyInstaller

        print("✅ PyInstaller已安装")
    except ImportError:
        print("❌ PyInstaller未安装，请运行: pip install pyinstaller")
        sys.exit(1)

    # 创建spec文件
    create_pyinstaller_spec()

    # 执行PyInstaller构建
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "gpt_academic.spec",
        "--clean",
        "--noconfirm",
    ]

    try:
        subprocess.run(cmd, check=True)
        print("✅ macOS版本构建成功")

        # 创建macOS应用包
        create_macos_app()

        # 清理临时文件
        if os.path.exists("build"):
            shutil.rmtree("build")
        if os.path.exists("gpt_academic.spec"):
            os.remove("gpt_academic.spec")

    except subprocess.CalledProcessError as e:
        print(f"❌ macOS构建失败: {e}")
        sys.exit(1)


def create_macos_app():
    """创建macOS应用包"""
    print("📦 创建macOS应用包...")

    app_dir = Path("GPT Academic.app")
    contents_dir = app_dir / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"

    # 创建目录结构
    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)

    # 复制可执行文件
    shutil.copy("dist/GPT_Academic", str(macos_dir / "GPT_Academic"))

    # 设置执行权限
    os.chmod(str(macos_dir / "GPT_Academic"), 0o755)

    # 创建Info.plist
    info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>GPT_Academic</string>
    <key>CFBundleIdentifier</key>
    <string>com.gptacademic.app</string>
    <key>CFBundleName</key>
    <string>GPT Academic</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024 GPT Academic. All rights reserved.</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>"""

    with open(str(contents_dir / "Info.plist"), "w") as f:
        f.write(info_plist)

    print("✅ macOS应用包创建成功")


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 GPT Academic 构建工具")
    print("=" * 60)

    current_platform = platform.system().lower()

    if current_platform == "windows":
        build_windows()
    elif current_platform == "darwin":
        build_macos()
    else:
        print("❌ 不支持的操作系统: {}".format(platform.system()))
        print("💡 支持的平台: Windows, macOS")
        sys.exit(1)

    print("\n🎉 构建完成！")
    print("📁 输出目录: dist/")
    if current_platform == "darwin":
        print("🍎 macOS应用包: GPT Academic.app")


if __name__ == "__main__":
    main()
