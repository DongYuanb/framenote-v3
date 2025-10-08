"""
视频预览和缩略图生成服务
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
from PIL import Image
import base64
import io

logger = logging.getLogger(__name__)

class VideoPreviewService:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
    
    def generate_thumbnail(self, video_path: str, output_path: str, 
                          time_offset: float = 1.0, width: int = 320, height: int = 240) -> bool:
        """生成视频缩略图"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-ss", str(time_offset),
                "-vframes", "1",
                "-vf", f"scale={width}:{height}",
                "-y",  # 覆盖输出文件
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info(f"缩略图生成成功: {output_path}")
                return True
            else:
                logger.error(f"缩略图生成失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("缩略图生成超时")
            return False
        except Exception as e:
            logger.error(f"缩略图生成异常: {e}")
            return False
    
    def generate_multiple_thumbnails(self, video_path: str, output_dir: str, 
                                   count: int = 6, width: int = 160, height: int = 120) -> List[str]:
        """生成多个缩略图（时间轴预览）"""
        try:
            # 获取视频时长
            duration = self.get_video_duration(video_path)
            if duration <= 0:
                return []
            
            # 计算时间间隔
            interval = duration / (count + 1)
            
            thumbnails = []
            for i in range(1, count + 1):
                time_offset = interval * i
                output_path = os.path.join(output_dir, f"thumb_{i:02d}.jpg")
                
                if self.generate_thumbnail(video_path, output_path, time_offset, width, height):
                    thumbnails.append(output_path)
            
            return thumbnails
            
        except Exception as e:
            logger.error(f"批量缩略图生成失败: {e}")
            return []
    
    def get_video_duration(self, video_path: str) -> float:
        """获取视频时长（秒）"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-f", "null",
                "-"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                # 从stderr中解析时长
                for line in result.stderr.split('\n'):
                    if 'Duration:' in line:
                        duration_str = line.split('Duration:')[1].split(',')[0].strip()
                        return self._parse_duration(duration_str)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"获取视频时长失败: {e}")
            return 0.0
    
    def _parse_duration(self, duration_str: str) -> float:
        """解析时长字符串为秒数"""
        try:
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = parts
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
            return 0.0
        except:
            return 0.0
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-f", "null",
                "-"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            info = {
                "duration": 0.0,
                "width": 0,
                "height": 0,
                "fps": 0.0,
                "bitrate": 0,
                "format": ""
            }
            
            if result.returncode != 0:
                # 从stderr解析信息
                stderr = result.stderr
                
                # 解析时长
                for line in stderr.split('\n'):
                    if 'Duration:' in line:
                        duration_str = line.split('Duration:')[1].split(',')[0].strip()
                        info["duration"] = self._parse_duration(duration_str)
                    elif 'Video:' in line and 'fps' in line:
                        # 解析分辨率
                        if 'x' in line:
                            try:
                                res_part = line.split('Video:')[1].split()[0]
                                if 'x' in res_part:
                                    width, height = res_part.split('x')
                                    info["width"] = int(width)
                                    info["height"] = int(height)
                            except:
                                pass
                        
                        # 解析帧率
                        if 'fps' in line:
                            try:
                                fps_part = line.split('fps')[0].split()[-1]
                                info["fps"] = float(fps_part)
                            except:
                                pass
                
                # 解析格式
                for line in stderr.split('\n'):
                    if 'Input #0' in line:
                        info["format"] = line.split(',')[0].replace('Input #0,', '').strip()
            
            return info
            
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return {
                "duration": 0.0,
                "width": 0,
                "height": 0,
                "fps": 0.0,
                "bitrate": 0,
                "format": ""
            }
    
    def create_thumbnail_grid(self, thumbnail_paths: List[str], output_path: str, 
                             grid_size: tuple = (3, 2)) -> bool:
        """创建缩略图网格"""
        try:
            if len(thumbnail_paths) == 0:
                return False
            
            # 加载所有缩略图
            images = []
            for path in thumbnail_paths:
                if os.path.exists(path):
                    img = Image.open(path)
                    images.append(img)
            
            if not images:
                return False
            
            # 计算网格尺寸
            cols, rows = grid_size
            thumb_width, thumb_height = images[0].size
            
            # 创建网格画布
            grid_width = thumb_width * cols
            grid_height = thumb_height * rows
            grid_img = Image.new('RGB', (grid_width, grid_height), (0, 0, 0))
            
            # 放置缩略图
            for i, img in enumerate(images[:cols * rows]):
                row = i // cols
                col = i % cols
                x = col * thumb_width
                y = row * thumb_height
                grid_img.paste(img, (x, y))
            
            # 保存网格图
            grid_img.save(output_path, 'JPEG', quality=85)
            logger.info(f"缩略图网格生成成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"缩略图网格生成失败: {e}")
            return False
    
    def thumbnail_to_base64(self, thumbnail_path: str) -> Optional[str]:
        """将缩略图转换为base64字符串"""
        try:
            if not os.path.exists(thumbnail_path):
                return None
            
            with open(thumbnail_path, 'rb') as f:
                img_data = f.read()
                base64_str = base64.b64encode(img_data).decode('utf-8')
                return f"data:image/jpeg;base64,{base64_str}"
                
        except Exception as e:
            logger.error(f"缩略图转base64失败: {e}")
            return None
