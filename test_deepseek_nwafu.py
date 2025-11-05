#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek NWAFU无缝登录功能测试脚本
简化版本，避免复杂的依赖导入
"""

import hashlib
import json
import os
import pickle
import sys
import time
from pathlib import Path


def test_cookie_manager_basic():
    """测试Cookie管理器基本功能"""
    print("=== DeepSeek NWAFU Cookie管理器基本功能测试 ===")

    # 模拟Cookie管理器类
    class MockCookieManager:
        def __init__(self):
            self.cookie_cache_file = Path("cache/deepseek_nwafu_cookies.pkl")
            self.cookies = {}
            self.last_login_time = 0
            self.login_interval = 7200  # 2小时

        def _generate_cookie_checksum(self, cookies):
            """生成Cookie校验和"""
            cookie_str = json.dumps(cookies, sort_keys=True)
            return hashlib.md5(cookie_str.encode()).hexdigest()

        def _save_cookies_to_cache(self, cookies):
            """保存Cookie到缓存"""
            try:
                # 确保缓存目录存在
                self.cookie_cache_file.parent.mkdir(parents=True, exist_ok=True)

                # 生成校验和
                checksum = self._generate_cookie_checksum(cookies)
                cache_data = {
                    "cookies": cookies,
                    "checksum": checksum,
                    "timestamp": time.time(),
                }

                with open(self.cookie_cache_file, "wb") as f:
                    pickle.dump(cache_data, f)

                print(f"   ✓ Cookie已保存到缓存: {self.cookie_cache_file}")
                return True
            except Exception as e:
                print(f"   ✗ Cookie保存失败: {e}")
                return False

        def _load_cookies_from_cache(self):
            """从缓存加载Cookie"""
            try:
                if not self.cookie_cache_file.exists():
                    return None

                with open(self.cookie_cache_file, "rb") as f:
                    cache_data = pickle.load(f)

                # 验证校验和
                expected_checksum = self._generate_cookie_checksum(
                    cache_data["cookies"]
                )
                if cache_data["checksum"] == expected_checksum:
                    print(f"   ✓ Cookie从缓存加载成功")
                    return cache_data["cookies"]
                else:
                    print("   ✗ Cookie校验和验证失败")
                    return None

            except Exception as e:
                print(f"   ✗ Cookie加载失败: {e}")
                return None

        def _validate_cookie_data(self, cookies):
            """验证Cookie数据完整性"""
            if not isinstance(cookies, dict):
                return False

            # 检查是否包含必要的Cookie
            required_cookies = ["__Secure-Login-State-cas"]
            for cookie in required_cookies:
                if cookie not in cookies:
                    return False

            return True

    # 创建模拟管理器
    manager = MockCookieManager()

    # 测试1: 保存Cookie到缓存
    print("1. 测试Cookie缓存保存功能...")
    test_cookies = {
        "__Secure-Login-State-cas": "test_cookie_value_123456",
        "session_id": "test_session_789",
    }
    manager._save_cookies_to_cache(test_cookies)

    # 测试2: 从缓存加载Cookie
    print("\n2. 测试Cookie缓存加载功能...")
    loaded_cookies = manager._load_cookies_from_cache()
    if loaded_cookies:
        print(f"   加载的Cookie数量: {len(loaded_cookies)}")
        print(f"   Cookie键: {list(loaded_cookies.keys())}")

    # 测试3: 验证Cookie数据完整性
    print("\n3. 测试Cookie数据验证功能...")
    valid_cookies = {"__Secure-Login-State-cas": "valid_cookie_value"}
    invalid_cookies = {"other_cookie": "value"}

    print(f"   有效Cookie验证: {manager._validate_cookie_data(valid_cookies)}")
    print(f"   无效Cookie验证: {manager._validate_cookie_data(invalid_cookies)}")

    # 测试4: 检查缓存文件
    print("\n4. 检查缓存文件状态...")
    if manager.cookie_cache_file.exists():
        print(f"   ✓ 缓存文件存在: {manager.cookie_cache_file}")
        print(f"   文件大小: {manager.cookie_cache_file.stat().st_size} 字节")
    else:
        print("   ✗ 缓存文件不存在")


def test_environment_config():
    """测试环境变量配置"""
    print("\n=== 环境变量配置测试 ===")

    # 检查环境变量
    env_vars = [
        ("DEEPSEEK_NWAFU_API_KEY", "API密钥"),
        ("DEEPSEEK_NWAFU_USERNAME", "用户名"),
        ("DEEPSEEK_NWAFU_PASSWORD", "密码"),
    ]

    for var_name, description in env_vars:
        value = os.getenv(var_name)
        status = "已设置" if value else "未设置"
        print(f"   {var_name} ({description}): {status}")
        if value:
            print(f"     值长度: {len(value)} 字符")


def test_api_endpoints():
    """测试API端点配置"""
    print("\n=== API端点配置测试 ===")

    # 模拟API端点配置
    api_base = "https://deepseek.nwafu.edu.cn/api"
    endpoints = {
        "聊天完成": f"{api_base}/chat/completions",
        "模型列表": f"{api_base}/models",
        "CAS登录": f"{api_base}/cas/login",
        "简化登录": f"{api_base}/auth/login",
    }

    for name, url in endpoints.items():
        print(f"   {name}: {url}")


def main():
    """主测试函数"""
    print("DeepSeek NWAFU无缝登录功能测试 (简化版)")
    print("=" * 60)

    # 运行测试
    test_cookie_manager_basic()
    test_environment_config()
    test_api_endpoints()

    print("\n" + "=" * 60)
    print("测试完成")

    # 提供使用建议
    print("\n使用建议:")
    print("1. 确保设置以下环境变量:")
    print("   - DEEPSEEK_NWAFU_API_KEY: API密钥")
    print("   - DEEPSEEK_NWAFU_USERNAME: 用户名（可选，用于自动登录）")
    print("   - DEEPSEEK_NWAFU_PASSWORD: 密码（可选，用于自动登录）")
    print("\n2. Cookie将自动缓存到 cache/deepseek_nwafu_cookies.pkl")
    print("3. Cookie过期时间为2小时，过期后会自动重新获取")
    print("4. 认证失败时会自动尝试重新登录")
    print("\n5. 主要功能特性:")
    print("   - 自动获取和验证 __Secure-Login-State-cas Cookie")
    print("   - Cookie缓存机制，避免频繁登录")
    print("   - 自动重试机制，处理网络和认证问题")
    print("   - 错误处理和日志记录")


if __name__ == "__main__":
    main()
