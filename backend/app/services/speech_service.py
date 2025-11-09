
import json
import base64
import hashlib
import time
import hmac
import asyncio
import websockets
import logging
from typing import Dict, Any, Optional

from ..core.config import settings

# 设置日志
logger = logging.getLogger(__name__)

class SpeechService:
    """科大讯飞语音识别服务"""

    @staticmethod
    def generate_auth_url():
        """生成科大讯飞API鉴权URL"""
        url = "wss://iat-api.xfyun.cn/v2/iat"
        host = "iat-api.xfyun.cn"
        path = "/v2/iat"

        # 生成RFC1123格式的日期
        date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())

        # 拼接字符串
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        
        # 使用hmac-sha256进行加密
        signature_sha = hmac.new(
            settings.XUNFEI_API_SECRET.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        signature = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = f'api_key="{settings.XUNFEI_API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        # 将请求的鉴权参数组合为字符串
        v = {
            "authorization": authorization,
            "date": date,
            "host": host
        }
        
        # 拼接鉴权URL
        from urllib.parse import quote
        url = f"{url}?{ '&'.join([f'{k}={quote(v[k])}' for k in v])}"
        return url

    @staticmethod
    async def speech_to_text(audio_data: bytes) -> Dict[str, Any]:
        """
        将音频数据转换为文本
        :param audio_data: 音频数据，支持webm和WAV格式
        :return: 包含识别结果的字典
        """
        if not all([settings.XUNFEI_APP_ID, settings.XUNFEI_API_KEY, settings.XUNFEI_API_SECRET]):
            logger.error("科大讯飞API配置不完整")
            return {
                "success": False,
                "error": "科大讯飞API配置不完整，请检查环境变量XUNFEI_APP_ID、XUNFEI_API_KEY和XUNFEI_API_SECRET"
            }

        try:
            # 获取鉴权URL
            auth_url = SpeechService.generate_auth_url()
            logger.info(f"连接到科大讯飞API: {auth_url[:50]}...")

            # 科大讯飞API不需要单独发送参数，参数将包含在第一帧中
            logger.info("准备连接到科大讯飞WebSocket服务器...")

            # 将音频数据转换为base64
            audio_base64 = str(base64.b64encode(audio_data), "utf8")
            logger.info(f"音频数据大小: {len(audio_data)} bytes")
            logger.info(f"音频数据Base64编码长度: {len(audio_base64)}")

            # 连接WebSocket
            try:
                logger.info(f"正在连接到科大讯飞WebSocket服务器...")
                async with websockets.connect(
                    auth_url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10
                ) as websocket:
                    logger.info("成功连接到科大讯飞WebSocket服务器")

                    # 发送音频数据
                    # 科大讯飞API要求使用特定的数据格式
                    # 第一帧需要包含common和business参数
                    # 第一帧需要包含common和business参数
                    frame_size = 1280  # 每一帧的音频大小
                    intervel = 0.04  # 发送音频间隔(单位:s)
                    status = 0  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

                    # 按帧发送音频数据
                    pos = 0
                    while pos < len(audio_data):
                        # 读取当前帧数据
                        end_pos = min(pos + frame_size, len(audio_data))
                        chunk = audio_data[pos:end_pos]
                        chunk_base64 = str(base64.b64encode(chunk), "utf-8")

                        # 判断是否是最后一帧
                        if end_pos >= len(audio_data):
                            status = 2  # 最后一帧
                        elif pos == 0:
                            status = 0  # 第一帧
                        else:
                            status = 1  # 中间帧

                        # 构建数据帧
                        if status == 0:
                            # 第一帧需要包含common和business参数
                            data = {
                                "common": {
                                    "app_id": settings.XUNFEI_APP_ID
                                },
                                "business": {
                                    "language": "zh_cn",
                                    "domain": "iat",
                                    "accent": "mandarin",
                                    "vad_eos": 5000,
                                    "dwa": "wpgs"
                                },
                                "data": {
                                    "status": status,
                                    "format": "audio/L16;rate=16000",
                                    "audio": chunk_base64,
                                    "encoding": "raw"
                                }
                            }
                        else:
                            # 中间帧和最后一帧只需要data参数
                            data = {
                                "data": {
                                    "status": status,
                                    "format": "audio/L16;rate=16000",
                                    "audio": chunk_base64,
                                    "encoding": "raw"
                                }
                            }

                        logger.info(f"发送音频数据，位置: {pos}-{end_pos}，状态: {status}")
                        await websocket.send(json.dumps(data))

                        # 更新位置
                        pos = end_pos

                        # 模拟音频采样间隔
                        if status != 2:  # 最后一帧不需要等待
                            await asyncio.sleep(intervel)

                    


                    logger.info("已发送所有音频数据到科大讯飞API")

                    # 接收结果
                    result_text = ""
                    error_code = None
                    error_message = None

                    while True:
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=15)
                            result = json.loads(message)
                            logger.info(f"收到科大讯飞API响应: {json.dumps(result, indent=2)}")

                            # 检查是否有错误
                            if "code" in result and result["code"] != 0:
                                error_code = result["code"]
                                error_message = result.get("message", "未知错误")
                                logger.error(f"科大讯飞API错误: {error_code} - {error_message}")
                                break

                            # 检查是否是结果消息
                            if "data" in result and "result" in result["data"]:
                                # 解析结果
                                ws = result["data"]["result"]["ws"]
                                for ws_item in ws:
                                    for cw in ws_item["cw"]:
                                        result_text += cw["w"]
                                logger.info(f"收到部分识别结果: {result_text}")

                            # 检查是否结束
                            if "data" in result and "status" in result["data"] and result["data"]["status"] == 2:
                                logger.info("语音识别完成")
                                break

                        except asyncio.TimeoutError:
                            logger.warning("等待识别结果超时")
                            break

                    if error_code:
                        return {
                            "success": False,
                            "error": f"科大讯飞API错误 ({error_code}): {error_message}"
                        }

                    return {
                        "success": True,
                        "text": result_text,
                        "status": "completed"
                    }

            except websockets.exceptions.InvalidStatusCode as e:
                logger.error(f"WebSocket连接错误: {e}")
                return {
                    "success": False,
                    "error": f"无法连接到科大讯飞API: {e.status_code} - {e.headers.get('error', '未知错误')}"
                }
            except websockets.exceptions.ConnectionClosed as e:
                logger.error(f"WebSocket连接意外关闭: {e}")
                return {
                    "success": False,
                    "error": f"与科大讯飞API的连接意外关闭: {e.code} - {e.reason}"
                }

        except Exception as e:
            logger.error(f"语音识别过程中发生错误: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"语音识别失败: {str(e)}"
            }
