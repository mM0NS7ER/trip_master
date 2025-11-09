
import os
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...services.speech_service import SpeechService

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    将语音转换为文本
    """
    try:
        # 检查文件类型
        if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
            logger.error(f"无效的文件类型: {audio_file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="上传的文件不是有效的音频文件"
            )

        # 读取上传的音频文件
        audio_bytes = await audio_file.read()

        # 检查文件大小
        if len(audio_bytes) == 0:
            logger.error("音频文件为空")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音频文件为空"
            )

        # 检查文件大小限制 (10MB)
        if len(audio_bytes) > 10 * 1024 * 1024:
            logger.error(f"音频文件过大: {len(audio_bytes)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音频文件过大，请上传小于10MB的文件"
            )

        logger.info(f"用户 {current_user.id} 上传了音频文件，大小: {len(audio_bytes)} bytes, 类型: {audio_file.content_type}")

        # 如果是webm格式，可能需要转换为WAV格式
        # 这里我们直接传递给SpeechService，让服务处理转换
        result = await SpeechService.speech_to_text(audio_bytes)

        if not result["success"]:
            logger.error(f"语音识别失败: {result.get('error', '未知错误')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "语音识别失败")
            )

        logger.info(f"语音识别成功: {result.get('text', '')[:50]}...")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音识别处理过程中发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音识别失败: {str(e)}"
        )
