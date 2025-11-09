
import json
import base64
import hashlib
import time
import hmac
import asyncio
import websockets
import logging
from typing import Dict, Any, Optional
import io
import wave
import struct
import numpy as np

from ..core.config import settings

# 设置日志
logger = logging.getLogger(__name__)

class SpeechService:
    """科大讯飞语音识别服务 - 改进版"""

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
    def convert_to_pcm(audio_data: bytes, input_format: str = "webm") -> bytes:
        """
        将音频数据转换为PCM格式
        :param audio_data: 原始音频数据
        :param input_format: 输入格式，支持webm和wav
        :return: PCM格式的音频数据
        """
        try:
            import librosa
            import soundfile as sf
            import tempfile
            import os
            
            # 如果已经是PCM格式，直接返回
            if input_format == "pcm":
                return audio_data
                
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav' if input_format == "wav" else '.webm', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # 使用librosa加载音频
                # 确保采样率为16kHz，单声道
                y, sr = librosa.load(temp_file_path, sr=16000, mono=True)
                
                # 创建另一个临时文件用于保存PCM数据
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as pcm_file:
                    pcm_file_path = pcm_file.name
                
                # 保存为WAV格式（PCM编码）
                sf.write(pcm_file_path, y, sr, format='WAV', subtype='PCM_16')
                
                # 读取PCM数据
                with open(pcm_file_path, 'rb') as f:
                    # 跳过WAV文件头（44字节）
                    f.seek(44)
                    pcm_data = f.read()
                
                # 删除临时文件
                os.unlink(temp_file_path)
                os.unlink(pcm_file_path)
                
                return pcm_data
                
            except Exception as e:
                logger.error(f"使用librosa处理音频失败: {str(e)}", exc_info=True)
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                raise
            
        except ImportError as e:
            logger.warning(f"音频处理库未安装，使用简化处理: {str(e)}")
            return SpeechService._simple_convert_to_pcm(audio_data, input_format)
        except Exception as e:
            logger.error(f"音频格式转换失败: {str(e)}", exc_info=True)
            # 如果是WebM格式，尝试使用ffmpeg直接转换
            if input_format == "webm":
                try:
                    logger.info("尝试使用ffmpeg直接转换WebM格式")
                    return SpeechService._convert_webm_with_ffmpeg(audio_data)
                except Exception as ffmpeg_e:
                    logger.error(f"使用ffmpeg转换WebM失败: {str(ffmpeg_e)}", exc_info=True)
            # 转换失败时返回原始数据，让API尝试处理
            return audio_data
        except Exception as e:
            logger.error(f"音频格式转换失败: {str(e)}")
            # 转换失败时返回原始数据，让API尝试处理
            return audio_data
    
    @staticmethod
    def _simple_convert_to_pcm(audio_data: bytes, input_format: str = "webm") -> bytes:
        """
        简化的音频格式转换方法，不依赖外部库
        :param audio_data: 原始音频数据
        :param input_format: 输入格式，支持webm和wav
        :return: PCM格式的音频数据
        """
        try:
            # 如果已经是PCM格式，直接返回
            if input_format == "pcm":
                return audio_data
                
            # 如果是WAV格式，提取PCM数据
            if input_format == "wav":
                try:
                    # 使用io.BytesIO将字节数据转换为文件对象
                    wav_file = io.BytesIO(audio_data)
                    with wave.open(wav_file, 'rb') as wav:
                        # 获取音频参数
                        n_channels = wav.getnchannels()
                        sampwidth = wav.getsampwidth()
                        framerate = wav.getframerate()
                        n_frames = wav.getnframes()
                        
                        # 读取音频数据
                        audio_data = wav.readframes(n_frames)
                        
                        # 如果不是单声道，转换为单声道
                        if n_channels > 1:
                            # 将多声道转换为单声道
                            audio_data = np.frombuffer(audio_data, dtype=np.int16)
                            audio_data = audio_data.reshape(-1, n_channels)
                            audio_data = np.mean(audio_data, axis=1).astype(np.int16)
                            audio_data = audio_data.tobytes()
                        
                        # 如果采样率不是16kHz，进行重采样
                        if framerate != 16000:
                            # 这里简化处理，实际应用中应使用专业的重采样算法
                            logger.warning(f"音频采样率为{framerate}Hz，不是期望的16000Hz，可能影响识别效果")
                        
                        return audio_data
                except Exception as e:
                    logger.error(f"处理WAV格式音频失败: {str(e)}")
                    raise
            
            # 如果是WebM格式，需要特殊处理
            # 这里简化处理，实际项目中应使用ffmpeg或其他库进行转换
            logger.warning("WebM格式音频可能无法正确处理，建议使用WAV格式")
            return audio_data
            
        except Exception as e:
            logger.error(f"音频格式转换失败: {str(e)}")
            # 转换失败时返回原始数据，让API尝试处理
            return audio_data

    @staticmethod
    async def speech_to_text(audio_data: bytes, content_type: str = "audio/webm") -> Dict[str, Any]:
        """
        将音频数据转换为文本
        :param audio_data: 音频数据，支持webm和WAV格式
        :param content_type: 音频内容类型
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

            # 将音频数据转换为PCM格式
            input_format = "webm"
            if content_type == "audio/wav":
                input_format = "wav"
            elif content_type == "audio/x-wav":
                input_format = "wav"
            elif content_type == "audio/webm":
                input_format = "webm"

            try:
                # 尝试将音频转换为PCM格式
                pcm_audio_data = SpeechService.convert_to_pcm(audio_data, input_format)
                logger.info(f"音频格式转换完成，原始大小: {len(audio_data)} bytes，转换后大小: {len(pcm_audio_data)} bytes")
            except Exception as e:
                logger.error(f"音频格式转换失败，使用原始数据: {str(e)}")
                pcm_audio_data = audio_data

            # 将音频数据转换为base64
            audio_base64 = str(base64.b64encode(pcm_audio_data), "utf8")
            logger.info(f"音频数据大小: {len(pcm_audio_data)} bytes")
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
                    frame_size = 1280  # 每一帧的音频大小
                    intervel = 0.04  # 发送音频间隔(单位:s)
                    status = 0  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

                    # 按帧发送音频数据
                    pos = 0
                    while pos < len(pcm_audio_data):
                        # 读取当前帧数据
                        end_pos = min(pos + frame_size, len(pcm_audio_data))
                        chunk = pcm_audio_data[pos:end_pos]
                        chunk_base64 = str(base64.b64encode(chunk), "utf-8")

                        # 判断是否是最后一帧
                        if end_pos >= len(pcm_audio_data):
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
                    # 记录已处理的结果片段，避免重复
                    processed_segments = set()

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
                                # 检查pgs字段，科大讯飞API返回的不同pgs值表示不同类型的更新
                                pgs = result["data"]["result"].get("pgs", "")

                                # pgs为"apd"表示追加结果，"rpl"表示替换结果
                                if pgs == "rpl":
                                    # 替换模式，清空之前的结果
                                    result_text = ""
                                    processed_segments.clear()

                                # 解析结果
                                ws = result["data"]["result"]["ws"]
                                segment_text = ""

                                for ws_item in ws:
                                    for cw in ws_item["cw"]:
                                        segment_text += cw["w"]

                                # 创建一个唯一标识符，用于避免重复处理相同片段
                                segment_id = f"{ws_item.get('bg', 0)}_{ws_item.get('ed', 0)}_{segment_text}"

                                # 只有当片段未被处理过时，才添加到结果中
                                if segment_id not in processed_segments:
                                    processed_segments.add(segment_id)

                                    # 如果是追加模式，直接添加到结果
                                    if pgs == "apd":
                                        result_text += segment_text
                                    # 如果是替换模式或无pgs标识，替换整个结果
                                    else:
                                        result_text = segment_text

                                logger.info(f"收到部分识别结果 (pgs={pgs}): {result_text}")

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
    
    @staticmethod
    def _convert_webm_with_ffmpeg(audio_data: bytes) -> bytes:
        """
        使用ffmpeg将WebM格式音频转换为PCM格式
        :param audio_data: WebM格式的音频数据
        :return: PCM格式的音频数据
        """
        try:
            import ffmpeg
            import tempfile
            import os
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_file:
                webm_file.write(audio_data)
                webm_file_path = webm_file.name
            
            # 创建输出临时文件
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                wav_file_path = wav_file.name
            
            try:
                # 使用ffmpeg进行转换
                # 设置采样率为16kHz，单声道，PCM 16位编码
                (
                    ffmpeg
                    .input(webm_file_path)
                    .output(wav_file_path, acodec='pcm_s16le', ac=1, ar='16k')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                
                # 读取转换后的PCM数据
                with open(wav_file_path, 'rb') as f:
                    # 跳过WAV文件头（44字节）
                    f.seek(44)
                    pcm_data = f.read()
                
                # 删除临时文件
                os.unlink(webm_file_path)
                os.unlink(wav_file_path)
                
                return pcm_data
                
            except ffmpeg.Error as e:
                logger.error(f"ffmpeg转换错误: {e.stderr.decode('utf-8')}")
                # 删除临时文件
                if os.path.exists(webm_file_path):
                    os.unlink(webm_file_path)
                if os.path.exists(wav_file_path):
                    os.unlink(wav_file_path)
                raise
            except Exception as e:
                logger.error(f"使用ffmpeg转换时发生错误: {str(e)}", exc_info=True)
                # 删除临时文件
                if os.path.exists(webm_file_path):
                    os.unlink(webm_file_path)
                if os.path.exists(wav_file_path):
                    os.unlink(wav_file_path)
                raise
                
        except ImportError as e:
            logger.error(f"ffmpeg-python库未安装: {str(e)}")
            raise
