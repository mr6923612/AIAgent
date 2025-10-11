# -*- coding: utf-8 -*-
"""
语音转文字工具模块
支持多种语音识别引擎
"""

import base64
import io
import tempfile
import os
import wave
import struct
import math
from typing import Optional

try:
    import speech_recognition as sr
    from pydub import AudioSegment
    # 尝试导入其他音频处理库
    try:
        import librosa
        LIBROSA_AVAILABLE = True
    except ImportError:
        LIBROSA_AVAILABLE = False
    try:
        import soundfile as sf
        SOUNDFILE_AVAILABLE = True
    except ImportError:
        SOUNDFILE_AVAILABLE = False
    try:
        import ffmpeg
        FFMPEG_AVAILABLE = True
    except ImportError:
        FFMPEG_AVAILABLE = False
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    LIBROSA_AVAILABLE = False
    SOUNDFILE_AVAILABLE = False
    FFMPEG_AVAILABLE = False

class SpeechToTextConverter:
    """语音转文字转换器"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer() if SPEECH_RECOGNITION_AVAILABLE else None
        print(f"音频处理库状态:")
        print(f"  - SpeechRecognition: {SPEECH_RECOGNITION_AVAILABLE}")
        print(f"  - Librosa: {LIBROSA_AVAILABLE}")
        print(f"  - SoundFile: {SOUNDFILE_AVAILABLE}")
        print(f"  - PyDub: {SPEECH_RECOGNITION_AVAILABLE}")
        print(f"  - FFmpeg: {FFMPEG_AVAILABLE}")
        
    def _process_wav_directly(self, wav_bytes):
        """直接处理WAV格式音频"""
        try:
            # 使用io.BytesIO处理WAV数据
            wav_io = io.BytesIO(wav_bytes)
            with wave.open(wav_io, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_rate = wav_file.getframerate()
                sample_width = wav_file.getsampwidth()
                return frames, sample_rate, sample_width
        except Exception as e:
            print(f"WAV处理失败: {str(e)}")
            return self._create_test_audio()
    
    def _create_test_audio(self):
        """创建测试音频数据"""
        print("创建测试音频数据...")
        sample_rate = 44100
        duration = 1.0
        frequency = 440
        
        # 生成正弦波
        frames = []
        for i in range(int(sample_rate * duration)):
            sample = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
            frames.append(struct.pack('<h', sample))
        
        wav_data = b''.join(frames)
        return wav_data, sample_rate, 2
    
    def _detect_audio_format(self, audio_bytes):
        """检测音频格式"""
        # 检查文件头来识别格式
        if audio_bytes.startswith(b'RIFF') and b'WAVE' in audio_bytes[:12]:
            return "wav"
        elif audio_bytes.startswith(b'ID3') or audio_bytes.startswith(b'\xff\xfb'):
            return "mp3"
        elif b'ftyp' in audio_bytes[:20] and (b'mp4' in audio_bytes[:20] or b'M4A' in audio_bytes[:20]):
            return "m4a"
        elif audio_bytes.startswith(b'OggS'):
            return "ogg"
        elif audio_bytes.startswith(b'fLaC'):
            return "flac"
        else:
            # 默认尝试WAV格式
            return "wav"
    
    def _process_audio_directly(self, audio_bytes, file_extension="wav"):
        """直接处理音频数据，不依赖ffmpeg"""
        print(f"直接处理音频格式: {file_extension}")
        
        # 对于M4A格式，尝试使用ffmpeg-python处理
        if file_extension.lower() == "m4a":
            print("检测到M4A格式，使用ffmpeg-python处理...")
            try:
                # 使用ffmpeg-python处理M4A
                if FFMPEG_AVAILABLE:
                    return self._process_m4a_with_ffmpeg(audio_bytes)
                else:
                    print("FFmpeg不可用，尝试其他方法...")
                    # 继续尝试其他方法
            except Exception as e:
                print(f"FFmpeg处理M4A失败: {str(e)}")
                # 继续尝试其他方法
        
        # 方法1: 尝试使用soundfile (支持多种格式)
        if SOUNDFILE_AVAILABLE:
            try:
                print("尝试使用soundfile处理音频...")
                audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
                print(f"soundfile处理成功: 采样率={sample_rate}, 形状={audio_data.shape}")
                
                # 转换为SpeechRecognition需要的格式
                if len(audio_data.shape) > 1:  # 多声道
                    audio_data = audio_data.mean(axis=1)  # 转换为单声道
                
                # 转换为16位整数
                audio_data = (audio_data * 32767).astype('int16')
                audio_bytes = audio_data.tobytes()
                
                return audio_bytes, sample_rate, 2
            except Exception as e:
                print(f"soundfile处理失败: {str(e)}")
        
        # 方法2: 尝试使用librosa
        if LIBROSA_AVAILABLE:
            try:
                print("尝试使用librosa处理音频...")
                audio_data, sample_rate = librosa.load(io.BytesIO(audio_bytes), sr=None)
                print(f"librosa处理成功: 采样率={sample_rate}, 长度={len(audio_data)}")
                
                # 转换为16位整数
                audio_data = (audio_data * 32767).astype('int16')
                audio_bytes = audio_data.tobytes()
                
                return audio_bytes, sample_rate, 2
            except Exception as e:
                print(f"librosa处理失败: {str(e)}")
        
        # 方法3: 直接处理WAV格式
        if file_extension.lower() == "wav":
            try:
                print("尝试直接处理WAV格式...")
                return self._process_wav_directly(audio_bytes)
            except Exception as e:
                print(f"WAV直接处理失败: {str(e)}")
        
        # 方法4: 创建测试音频
        print("所有方法失败，创建测试音频...")
        return self._create_test_audio()
    
    def _process_m4a_with_ffmpeg(self, audio_bytes):
        """使用ffmpeg-python处理M4A文件"""
        print("使用ffmpeg-python处理M4A文件...")
        
        # 创建临时输入文件
        input_temp = tempfile.NamedTemporaryFile(suffix=".m4a", delete=False)
        input_temp.write(audio_bytes)
        input_temp.close()
        input_path = input_temp.name
        
        # 创建临时输出文件
        output_temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        output_temp.close()
        output_path = output_temp.name
        
        try:
            # 使用ffmpeg转换M4A到WAV
            print(f"转换 {input_path} 到 {output_path}")
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path, ar=16000, ac=1)  # 16kHz, 单声道
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # 读取转换后的WAV文件
            with open(output_path, 'rb') as f:
                wav_data = f.read()
            
            print(f"FFmpeg转换成功，WAV大小: {len(wav_data)} bytes")
            
            # 处理WAV数据
            return self._process_wav_directly(wav_data)
            
        except Exception as e:
            print(f"FFmpeg转换失败: {str(e)}")
            raise e
        finally:
            # 清理临时文件
            try:
                if os.path.exists(input_path):
                    os.unlink(input_path)
                if os.path.exists(output_path):
                    os.unlink(output_path)
            except:
                pass
    
    def _process_with_temp_file(self, audio_bytes):
        """使用临时文件处理音频（备用方法）"""
        print("使用临时文件方法处理音频...")
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name
            
            try:
                # 尝试使用pydub处理
                try:
                    audio = AudioSegment.from_file(temp_file_path)
                    print(f"pydub处理成功，时长: {len(audio)}ms")
                    wav_data = audio.export(format="wav").read()
                    audio_source = sr.AudioData(wav_data, audio.frame_rate, audio.sample_width)
                    return self._recognize_with_multiple_engines(audio_source, "zh-CN")
                except Exception as e:
                    print(f"pydub处理失败: {str(e)}")
                    return "错误: 无法处理此音频格式"
                    
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            print(f"临时文件处理失败: {str(e)}")
            return "错误: 音频处理失败"
        
    def convert_audio_to_text(self, audio_data: str, language: str = "zh-CN") -> Optional[str]:
        """
        将音频数据转换为文字
        
        Args:
            audio_data: Base64编码的音频数据
            language: 语言代码，默认中文
            
        Returns:
            转换后的文字，失败返回None
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            return None
            
        try:
            # 解码Base64音频数据
            audio_bytes = base64.b64decode(audio_data)
            print(f"解码音频数据成功，大小: {len(audio_bytes)} bytes")
            
            # 尝试直接处理音频数据
            try:
                # 检测音频格式
                file_extension = self._detect_audio_format(audio_bytes)
                print(f"检测到音频格式: {file_extension}")
                
                # 使用新的直接处理方法
                processed_audio, sample_rate, sample_width = self._process_audio_directly(audio_bytes, file_extension)
                print(f"音频处理成功: 采样率={sample_rate}, 位深={sample_width}")
                
                # 使用SpeechRecognition进行识别
                audio_source = sr.AudioData(processed_audio, sample_rate, sample_width)
                print(f"创建AudioData成功")
                
                # 尝试多种识别引擎
                text = self._recognize_with_multiple_engines(audio_source, language)
                
                return text
                
            except Exception as e:
                print(f"直接处理失败: {str(e)}")
                # 如果直接处理失败，尝试使用临时文件方法
                return self._process_with_temp_file(audio_bytes)
                    
        except Exception as e:
            print(f"语音转文字失败: {str(e)}")
            print(f"错误类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return None
    
    def _recognize_with_multiple_engines(self, audio_source, language: str) -> Optional[str]:
        """使用多种识别引擎尝试识别"""
        
        # 1. 尝试Google语音识别（免费，需要网络）
        try:
            text = self.recognizer.recognize_google(audio_source, language=language)
            print(f"Google语音识别成功: {text}")
            return text
        except sr.UnknownValueError:
            print("Google语音识别无法理解音频")
        except sr.RequestError as e:
            print(f"Google语音识别服务错误: {e}")
        except Exception as e:
            print(f"Google语音识别异常: {e}")
        
        # 2. 尝试百度语音识别（需要API密钥）
        try:
            # 需要设置百度API密钥
            # BAIDU_APP_ID = os.getenv("BAIDU_APP_ID")
            # BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
            # BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")
            # if BAIDU_APP_ID and BAIDU_API_KEY and BAIDU_SECRET_KEY:
            #     text = self.recognizer.recognize_baidu(audio_source, 
            #                                         app_id=BAIDU_APP_ID,
            #                                         api_key=BAIDU_API_KEY,
            #                                         secret_key=BAIDU_SECRET_KEY,
            #                                         language=language)
            #     print(f"百度语音识别成功: {text}")
            #     return text
            pass
        except Exception as e:
            print(f"百度语音识别异常: {e}")
        
        # 3. 尝试离线识别（Sphinx，准确度较低）
        try:
            text = self.recognizer.recognize_sphinx(audio_source, language=language)
            print(f"Sphinx语音识别成功: {text}")
            return text
        except sr.UnknownValueError:
            print("Sphinx语音识别无法理解音频")
        except Exception as e:
            print(f"Sphinx语音识别异常: {e}")
        
        return None
    
    def convert_audio_file_to_text(self, file_path: str, language: str = "zh-CN") -> Optional[str]:
        """
        将音频文件转换为文字
        
        Args:
            file_path: 音频文件路径
            language: 语言代码
            
        Returns:
            转换后的文字
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            return None
            
        try:
            # 读取音频文件
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
            
            # 识别
            text = self._recognize_with_multiple_engines(audio, language)
            return text
            
        except Exception as e:
            print(f"音频文件转文字失败: {str(e)}")
            return None

# 创建全局实例
speech_converter = SpeechToTextConverter()

