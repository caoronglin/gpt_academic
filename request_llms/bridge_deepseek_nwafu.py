"""
西北农林科技大学DeepSeek平台专用适配器
专为https://deepseek.nwafu.edu.cn/系统定制，实现无缝CAS认证登录
支持__Secure-Login-State-cas Cookie自动获取、验证与更新
"""

import hashlib
import json
import os
import pickle
import re
import time
import traceback
from pathlib import Path

import requests
from loguru import logger

from toolbox import (ChatBotWithCookies, clip_history, encode_image, get_conf,
                     have_any_recent_upload_image_files, is_any_api_key,
                     is_the_upload_folder, log_chat, read_one_api_model_name,
                     select_api_key, trimmed_format_exc, update_ui, what_keys)

proxies, WHEN_TO_USE_PROXY, TIMEOUT_SECONDS, MAX_RETRY = get_conf(
    "proxies", "WHEN_TO_USE_PROXY", "TIMEOUT_SECONDS", "MAX_RETRY"
)

# DeepSeek平台API地址
DEEPSEEK_NWAFU_API_BASE = "https://deepseek.nwafu.edu.cn/api"
# Cookie缓存文件路径
COOKIE_CACHE_FILE = Path("cache/deepseek_nwafu_cookies.pkl")


# Cookie管理类 - 增强版
class DeepSeekCookieManager:
    def __init__(self):
        self.cookies = {}
        self.last_login_time = 0
        self.login_interval = 7200  # 2小时重新登录
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )

        # 确保缓存目录存在
        COOKIE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

        # 尝试从缓存加载Cookie
        self._load_cookies_from_cache()

    def get_cookies(self):
        """获取当前有效的cookies，自动验证和更新"""
        current_time = time.time()

        # 检查Cookie是否过期或需要验证
        if (
            not self.cookies
            or current_time - self.last_login_time > self.login_interval
        ):
            logger.info("Cookie已过期或需要更新，开始重新登录")
            return self._login_with_retry()

        # 验证Cookie是否仍然有效
        if not self._validate_cookies():
            logger.warning("Cookie验证失败，重新登录")
            return self._login_with_retry()

        logger.debug("使用缓存的Cookie")
        return self.cookies

    def _login_with_retry(self, max_retries=3):
        """带重试机制的登录"""
        for attempt in range(max_retries):
            try:
                if self.login():
                    return self.cookies
            except Exception as e:
                logger.error(f"登录尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒后重试

        # 所有重试都失败，尝试匿名访问
        logger.error("所有登录尝试均失败，尝试匿名访问")
        self._try_anonymous_access()
        return self.cookies

    def _validate_cookies(self):
        """验证Cookie是否仍然有效"""
        try:
            test_url = f"{DEEPSEEK_NWAFU_API_BASE}/models"
            response = self.session.get(test_url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Cookie验证失败: {str(e)}")
            return False

    def _save_cookies_to_cache(self):
        """保存Cookie到缓存文件"""
        try:
            cookie_data = {
                "cookies": self.cookies,
                "last_login_time": self.last_login_time,
                "checksum": self._generate_cookie_checksum(),
            }
            with open(COOKIE_CACHE_FILE, "wb") as f:
                pickle.dump(cookie_data, f)
            logger.debug("Cookie已保存到缓存")
        except Exception as e:
            logger.warning(f"保存Cookie缓存失败: {str(e)}")

    def _load_cookies_from_cache(self):
        """从缓存文件加载Cookie"""
        try:
            if COOKIE_CACHE_FILE.exists():
                with open(COOKIE_CACHE_FILE, "rb") as f:
                    cookie_data = pickle.load(f)

                # 验证缓存数据的完整性
                if self._validate_cookie_data(cookie_data):
                    self.cookies = cookie_data["cookies"]
                    self.last_login_time = cookie_data["last_login_time"]

                    # 更新session的cookies
                    self.session.cookies.update(self.cookies)
                    logger.info("从缓存成功加载Cookie")
                    return True
        except Exception as e:
            logger.debug(f"加载Cookie缓存失败: {str(e)}")
        return False

    def _generate_cookie_checksum(self):
        """生成Cookie数据的校验和"""
        cookie_str = json.dumps(self.cookies, sort_keys=True) + str(
            self.last_login_time
        )
        return hashlib.md5(cookie_str.encode()).hexdigest()

    def _validate_cookie_data(self, cookie_data):
        """验证缓存Cookie数据的有效性"""
        if not isinstance(cookie_data, dict):
            return False

        required_keys = {"cookies", "last_login_time", "checksum"}
        if not required_keys.issubset(cookie_data.keys()):
            return False

        # 检查是否过期
        if time.time() - cookie_data["last_login_time"] > self.login_interval:
            return False

        # 验证校验和
        expected_checksum = hashlib.md5(
            (
                json.dumps(cookie_data["cookies"], sort_keys=True)
                + str(cookie_data["last_login_time"])
            ).encode()
        ).hexdigest()

        return cookie_data["checksum"] == expected_checksum

    def login(self):
        """模拟CAS登录获取__Secure-Login-State-cas cookie"""
        try:
            # 从环境变量或配置获取登录信息
            username = os.getenv("DEEPSEEK_NWAFU_USERNAME", "")
            password = os.getenv("DEEPSEEK_NWAFU_PASSWORD", "")

            if not username or not password:
                logger.warning("未配置DeepSeek平台登录信息，将尝试匿名访问")
                # 尝试匿名访问，可能无法获取完整功能
                self._try_anonymous_access()
                return False

            # CAS登录流程（优化版）
            # 1. 获取登录页面，获取lt和execution参数
            cas_login_url = f"{DEEPSEEK_NWAFU_API_BASE}/cas/login"

            # 获取登录页面
            response = self.session.get(cas_login_url, timeout=TIMEOUT_SECONDS)

            # 解析登录表单中的隐藏字段
            lt_match = re.search(r'name="lt" value="([^"]+)"', response.text)
            execution_match = re.search(
                r'name="execution" value="([^"]+)"', response.text
            )

            if not lt_match or not execution_match:
                logger.warning("无法解析CAS登录表单，尝试简化登录")
                return self._simplified_login(username, password)

            lt_value = lt_match.group(1)
            execution_value = execution_match.group(1)

            # 2. 提交登录表单
            login_data = {
                "username": username,
                "password": password,
                "lt": lt_value,
                "execution": execution_value,
                "_eventId": "submit",
            }

            response = self.session.post(
                cas_login_url,
                data=login_data,
                timeout=TIMEOUT_SECONDS,
                allow_redirects=True,
            )

            # 3. 检查登录是否成功
            if (
                response.status_code in [200, 302]
                and "__Secure-Login-State-cas" in self.session.cookies
            ):
                self.cookies = self.session.cookies.get_dict()
                self.last_login_time = time.time()

                # 保存Cookie到缓存
                self._save_cookies_to_cache()

                logger.info("DeepSeek平台CAS登录成功")
                logger.debug(f"获取到的cookies: {list(self.cookies.keys())}")
                return True
            else:
                logger.error(f"DeepSeek平台CAS登录失败: {response.status_code}")
                # 尝试简化登录
                return self._simplified_login(username, password)

        except Exception as e:
            logger.error(f"DeepSeek平台登录异常: {str(e)}")
            # 尝试简化登录
            return self._simplified_login(username, password)

    def _simplified_login(self, username, password):
        """简化登录方式，直接调用API登录"""
        try:
            login_url = f"{DEEPSEEK_NWAFU_API_BASE}/auth/login"
            login_data = {"username": username, "password": password}

            response = self.session.post(
                login_url, json=login_data, timeout=TIMEOUT_SECONDS
            )

            if response.status_code == 200:
                self.cookies = self.session.cookies.get_dict()
                self.last_login_time = time.time()

                # 保存Cookie到缓存
                self._save_cookies_to_cache()

                logger.info("DeepSeek平台简化登录成功")
                return True
            else:
                logger.error(f"DeepSeek平台简化登录失败: {response.status_code}")
                return self._try_anonymous_access()

        except Exception as e:
            logger.error(f"简化登录异常: {str(e)}")
            return self._try_anonymous_access()

    def _try_anonymous_access(self):
        """尝试匿名访问"""
        try:
            # 尝试访问API端点，获取可能的匿名cookie
            test_url = f"{DEEPSEEK_NWAFU_API_BASE}/models"
            response = self.session.get(test_url, timeout=TIMEOUT_SECONDS)

            if response.status_code == 200:
                self.cookies = self.session.cookies.get_dict()
                self.last_login_time = time.time()

                # 保存Cookie到缓存
                self._save_cookies_to_cache()

                logger.info("DeepSeek平台匿名访问成功")
                return True
            else:
                logger.warning("DeepSeek平台匿名访问失败，将使用空cookie")
                self.cookies = {}
                return False

        except Exception as e:
            logger.error(f"匿名访问异常: {str(e)}")
            self.cookies = {}
            return False


# 全局cookie管理器
cookie_manager = DeepSeekCookieManager()


def get_full_error(chunk, stream_response):
    """获取完整的错误信息"""
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk


def generate_payload(
    inputs,
    llm_kwargs,
    history,
    system_prompt="",
    image_base64_array=None,
    has_multimodal_capacity=False,
    stream=True,
):
    """生成DeepSeek API请求的payload"""

    # 构建消息列表
    messages = []

    # 添加系统提示
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # 添加历史对话
    for i in range(0, len(history) - 1, 2):
        if i + 1 < len(history):
            messages.append({"role": "user", "content": history[i]})
            messages.append({"role": "assistant", "content": history[i + 1]})

    # 添加当前输入
    if has_multimodal_capacity and image_base64_array:
        # 多模态处理
        content_parts = [{"type": "text", "text": inputs}]
        for base64_image in image_base64_array:
            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }
            )
        messages.append({"role": "user", "content": content_parts})
    else:
        messages.append({"role": "user", "content": inputs})

    # 构建请求参数
    payload = {
        "model": llm_kwargs.get("llm_model", "deepseek-chat"),
        "messages": messages,
        "temperature": llm_kwargs.get("temperature", 0.7),
        "top_p": llm_kwargs.get("top_p", 0.95),
        "max_tokens": llm_kwargs.get("max_tokens", 4096),
        "stream": stream,
    }

    # 添加headers
    headers = {"Content-Type": "application/json", "User-Agent": "GPT-Academic/1.0"}

    # 添加认证信息
    api_key = llm_kwargs.get("api_key", "")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    return headers, payload


def predict_no_ui_long_connection(
    inputs: str,
    llm_kwargs: dict,
    history: list = [],
    sys_prompt: str = "",
    observe_window: list = None,
    console_silence: bool = False,
):
    """
    发送至DeepSeek平台，等待回复，一次性完成，不显示中间过程
    增强错误处理和Cookie自动更新机制
    """

    watch_dog_patience = 5  # 看门狗的耐心

    headers, payload = generate_payload(
        inputs, llm_kwargs, history, system_prompt=sys_prompt, stream=False
    )

    # 获取cookies（带自动更新机制）
    cookies = cookie_manager.get_cookies()

    retry = 0
    max_auth_retries = 2  # 认证重试次数

    while retry <= max_auth_retries:
        try:
            response = requests.post(
                f"{DEEPSEEK_NWAFU_API_BASE}/chat/completions",
                headers=headers,
                cookies=cookies,
                json=payload,
                stream=False,
                timeout=TIMEOUT_SECONDS,
            )

            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            elif response.status_code in [401, 403]:
                # 认证失败，尝试重新获取Cookie
                logger.warning(f"认证失败 (HTTP {response.status_code})，尝试重新登录")
                if retry < max_auth_retries:
                    # 强制清除缓存并重新登录
                    cookie_manager.cookies = {}
                    cookie_manager.last_login_time = 0
                    cookies = cookie_manager.get_cookies()
                    retry += 1
                    continue
                else:
                    error_msg = f"DeepSeek平台认证失败，请检查登录配置: {response.status_code} - {response.text}"
                    raise RuntimeError(error_msg)
            else:
                error_msg = (
                    f"DeepSeek平台请求失败: {response.status_code} - {response.text}"
                )
                raise RuntimeError(error_msg)

        except requests.exceptions.ReadTimeout as e:
            retry += 1
            traceback.print_exc()
            if retry > MAX_RETRY:
                raise TimeoutError
            if MAX_RETRY != 0:
                logger.error(f"请求超时，正在重试 ({retry}/{MAX_RETRY}) ……")

    # 所有重试都失败
    error_msg = "DeepSeek平台请求失败，所有重试尝试均未成功"
    raise RuntimeError(error_msg)


def predict(
    inputs: str,
    llm_kwargs: dict,
    plugin_kwargs: dict,
    chatbot: ChatBotWithCookies,
    history: list = [],
    system_prompt: str = "",
    stream: bool = True,
    additional_fn: str = None,
):
    """
    发送至DeepSeek平台，流式获取输出
    增强错误处理和Cookie自动更新机制
    """

    if is_any_api_key(inputs):
        chatbot._cookies["api_key"] = inputs
        chatbot.append(("输入已识别为DeepSeek的api_key", what_keys(inputs)))
        yield from update_ui(chatbot=chatbot, history=history, msg="api_key已导入")
        return
    elif not is_any_api_key(chatbot._cookies.get("api_key", "")):
        chatbot.append(
            (
                inputs,
                "缺少api_key。\n\n1. 临时解决方案：直接在输入区键入api_key，然后回车提交。\n\n2. 长效解决方案：在config.py中配置。",
            )
        )
        yield from update_ui(chatbot=chatbot, history=history, msg="缺少api_key")
        return

    user_input = inputs
    if additional_fn is not None:
        from core_functional import handle_core_functionality

        inputs, history = handle_core_functionality(
            additional_fn, inputs, history, chatbot
        )

    # 多模态支持
    has_multimodal_capacity = False  # DeepSeek平台暂不支持多模态
    if has_multimodal_capacity:
        has_recent_image_upload, image_paths = have_any_recent_upload_image_files(
            chatbot, pop=True
        )
    else:
        has_recent_image_upload, image_paths = False, []

    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history, msg="等待响应")

    # 获取cookies（带自动更新机制）
    cookies = cookie_manager.get_cookies()

    try:
        headers, payload = generate_payload(
            inputs,
            llm_kwargs,
            history,
            system_prompt,
            image_base64_array=None,
            has_multimodal_capacity=has_multimodal_capacity,
            stream=stream,
        )
    except RuntimeError as e:
        chatbot[-1] = (
            inputs,
            f"您提供的api-key不满足要求，不包含任何可用于{llm_kwargs['llm_model']}的api-key。您可能选择了错误的模型或请求源。",
        )
        yield from update_ui(chatbot=chatbot, history=history, msg="api-key不满足要求")
        return

    # 加入历史
    history.extend([inputs, ""])

    retry = 0
    max_auth_retries = 2  # 认证重试次数
    previous_ui_reflesh_time = 0
    ui_reflesh_min_interval = 0.0

    while retry <= max_auth_retries:
        try:
            response = requests.post(
                f"{DEEPSEEK_NWAFU_API_BASE}/chat/completions",
                headers=headers,
                cookies=cookies,
                json=payload,
                stream=stream,
                timeout=TIMEOUT_SECONDS,
            )

            # 检查响应状态
            if response.status_code == 200:
                break
            elif response.status_code in [401, 403]:
                # 认证失败，尝试重新获取Cookie
                logger.warning(f"认证失败 (HTTP {response.status_code})，尝试重新登录")
                if retry < max_auth_retries:
                    # 强制清除缓存并重新登录
                    cookie_manager.cookies = {}
                    cookie_manager.last_login_time = 0
                    cookies = cookie_manager.get_cookies()
                    retry += 1
                    continue
                else:
                    error_msg = f"DeepSeek平台认证失败，请检查登录配置: {response.status_code} - {response.text}"
                    chatbot[-1] = (inputs, error_msg)
                    yield from update_ui(
                        chatbot=chatbot, history=history, msg="认证失败"
                    )
                    return
            else:
                error_msg = (
                    f"DeepSeek平台请求失败: {response.status_code} - {response.text}"
                )
                chatbot[-1] = (inputs, error_msg)
                yield from update_ui(chatbot=chatbot, history=history, msg="请求失败")
                return

        except requests.exceptions.ReadTimeout as e:
            retry += 1
            traceback.print_exc()
            if retry > MAX_RETRY:
                chatbot[-1] = (inputs, "DeepSeek平台请求超时，请检查网络连接")
                yield from update_ui(chatbot=chatbot, history=history, msg="请求超时")
                return
            if MAX_RETRY != 0:
                logger.error(f"请求超时，正在重试 ({retry}/{MAX_RETRY}) ……")

    # 所有重试都失败
    if retry > max_auth_retries:
        chatbot[-1] = (inputs, "DeepSeek平台请求失败，所有重试尝试均未成功")
        yield from update_ui(chatbot=chatbot, history=history, msg="请求失败")
        return

    if not stream:
        # 非流式响应处理
        if response.status_code == 200:
            result = response.json()
            gpt_replying_buffer = result["choices"][0]["message"]["content"]
            history[-1] = gpt_replying_buffer
            chatbot[-1] = (history[-2], history[-1])
            yield from update_ui(chatbot=chatbot, history=history, msg="完成")
        else:
            error_msg = (
                f"DeepSeek平台请求失败: {response.status_code} - {response.text}"
            )
            chatbot[-1] = (inputs, error_msg)
            yield from update_ui(chatbot=chatbot, history=history, msg="请求失败")
        return

    # 流式响应处理
    if stream:
        reach_termination = False
        gpt_replying_buffer = ""
        is_head_of_the_stream = True
        stream_response = response.iter_lines()

        while True:
            try:
                chunk = next(stream_response)
            except StopIteration:
                if len(gpt_replying_buffer.strip()) > 0:
                    yield from update_ui(
                        chatbot=chatbot, history=history, msg="流式响应结束"
                    )
                    if not reach_termination:
                        reach_termination = True
                        log_chat(
                            llm_model=llm_kwargs["llm_model"],
                            input_str=inputs,
                            output_str=gpt_replying_buffer,
                        )
                    break
                else:
                    chatbot[-1] = (inputs, "接口返回了空响应")
                    yield from update_ui(chatbot=chatbot, history=history, msg="空响应")
                    return

            if chunk:
                try:
                    chunk_decoded = chunk.decode()

                    if chunk_decoded.startswith("data: "):
                        data_str = chunk_decoded[6:]
                        if data_str == "[DONE]":
                            reach_termination = True
                            log_chat(
                                llm_model=llm_kwargs["llm_model"],
                                input_str=inputs,
                                output_str=gpt_replying_buffer,
                            )
                            break

                        try:
                            data_json = json.loads(data_str)
                            if "choices" in data_json and len(data_json["choices"]) > 0:
                                delta = data_json["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content = delta["content"]
                                    gpt_replying_buffer += content
                                    history[-1] = gpt_replying_buffer
                                    chatbot[-1] = (history[-2], history[-1])

                                    if (
                                        time.time() - previous_ui_reflesh_time
                                        > ui_reflesh_min_interval
                                    ):
                                        yield from update_ui(
                                            chatbot=chatbot,
                                            history=history,
                                            msg="流式响应中",
                                        )
                                        previous_ui_reflesh_time = time.time()
                        except json.JSONDecodeError:
                            continue
                except Exception as e:
                    yield from update_ui(
                        chatbot=chatbot, history=history, msg="数据解析错误"
                    )
                    continue


# 导出预测函数
def get_predict_fns():
    return predict_no_ui_long_connection, predict
