# 🎤 音频功能测试文档

## 📋 概述

本文档描述了CrewAI客服机器人项目的音频功能测试方法，包括语音转文字和音频处理功能。

## 🎯 功能特性

### 前端功能
- ✅ 直接音频录制（使用MediaRecorder API）
- ✅ 音频文件上传
- ❌ ~~Web Speech API语音转文字~~（已移除）

### 后端功能
- ✅ 语音转文字转换
- ✅ 多格式音频支持（WAV, MP3, M4A, OGG, FLAC）
- ✅ 多语言识别支持
- ✅ 错误处理和用户友好提示

## 🧪 测试用例

### 快速开始

```bash
# 运行所有测试
cd tests
python run_all_tests.py

# 运行单个测试
python test_speech_to_text.py    # 语音转文字测试
python test_backend_api.py       # API测试
python test_integration.py       # 集成测试
```

### 测试结构

```
tests/
├── README.md               # 详细测试文档
├── run_all_tests.py        # 测试运行器
├── test_speech_to_text.py  # 语音转文字功能测试
├── test_backend_api.py     # 后端API功能测试
└── test_integration.py     # 集成测试
```

## 🔧 API接口测试

### 客服机器人API（包含音频）

```bash
curl -X POST http://127.0.0.1:8012/api/crew \
  -F "customer_input=" \
  -F "input_type=voice" \
  -F "audio=@your_audio.wav"
```

**响应示例:**
```json
{
  "job_id": "uuid-string"
}
```

**获取结果:**
```bash
curl http://127.0.0.1:8012/api/crew/{job_id}
```

### 错误处理测试

#### 语音识别失败
```bash
# 发送无法识别的音频
curl -X POST http://127.0.0.1:8012/api/crew \
  -F "customer_input=" \
  -F "input_type=voice" \
  -F "audio=@silent_audio.wav"
```

**预期响应:**
```json
{
  "error": "抱歉，我无法听清楚您刚才说的话。请您：\n\n1. 在安静的环境中重新录音\n2. 说话时声音稍微大一些，语速慢一些\n3. 或者您也可以直接输入文字，我会立即为您处理\n\n感谢您的理解，期待为您提供更好的服务！"
}
```

## 📊 测试数据

### 测试音频文件

#### 当前测试文件
- `test_audios/Recording.m4a` - 英语语音 "other thing is"
- `test_audios/Recording (2).m4a` - 英语语音 "hello hello"

#### 音频要求
- 格式: WAV, MP3, M4A, OGG, FLAC
- 采样率: 16kHz 或更高
- 声道: 单声道或立体声
- 时长: 1-30秒
- 内容: 清晰的语音

## 🐛 故障排除

### 常见问题

#### 1. 语音识别失败
**症状**: 后端返回识别失败错误
**解决方案**:
- 检查网络连接
- 验证音频文件质量
- 检查语音识别服务状态

#### 2. 音频格式不支持
**症状**: 音频上传失败
**解决方案**:
- 转换为支持的格式（WAV, M4A等）
- 检查文件大小限制
- 验证音频文件完整性

### 调试技巧

#### 后端调试
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查音频处理
print(f"音频数据大小: {len(audio_bytes)} bytes")
print(f"检测到的格式: {file_extension}")
```

## 📈 性能测试

### 响应时间测试

#### 语音转文字延迟
- 目标: < 5秒
- 测试方法: 测量从音频上传到文字返回的时间

#### 端到端延迟
- 目标: < 30秒
- 测试方法: 测量从录音到LLM回复的完整时间

## 🎯 最佳实践

### 测试策略

1. **分层测试**: 单元测试 → 集成测试 → 端到端测试
2. **数据驱动**: 使用多种测试音频文件
3. **边界测试**: 测试极限情况和错误场景
4. **回归测试**: 确保新功能不影响现有功能

---

## 📞 支持

如有测试相关问题，请参考：
- [项目README](../README.md)
- [详细测试文档](tests/README.md)
- [测试音频文件说明](TEST_AUDIO_FILES.md)