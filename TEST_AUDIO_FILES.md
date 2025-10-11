# 测试音频文件说明

## 📁 测试文件结构

```
test_audios/
├── Recording.m4a      # 英语语音测试文件1
└── Recording (2).m4a  # 英语语音测试文件2
```

## 🎵 文件详情

### Recording.m4a
- **内容**: 英语语音 "other thing is"
- **格式**: M4A (MPEG-4 Audio)
- **编码**: AAC
- **采样率**: 44.1kHz
- **声道**: 立体声
- **时长**: 约1-2秒
- **文件大小**: 约20-50KB

### Recording (2).m4a
- **内容**: 英语语音 "hello hello"
- **格式**: M4A (MPEG-4 Audio)
- **编码**: AAC
- **采样率**: 44.1kHz
- **声道**: 立体声
- **时长**: 约1-2秒
- **文件大小**: 约20-50KB

## 🧪 测试方法

### 1. 使用测试框架

```bash
# 运行所有测试
cd tests
python run_all_tests.py

# 运行语音转文字测试
python test_speech_to_text.py

# 运行集成测试
python test_integration.py
```

### 2. 直接API测试

```bash
# 测试第一个音频文件
curl -X POST http://127.0.0.1:8012/api/crew \
  -F "customer_input=" \
  -F "input_type=voice" \
  -F "audio=@test_audios/Recording.m4a"

# 测试第二个音频文件
curl -X POST http://127.0.0.1:8012/api/crew \
  -F "customer_input=" \
  -F "input_type=voice" \
  -F "audio=@test_audios/Recording (2).m4a"
```

### 3. 前端界面测试

1. 启动前端和后端服务
2. 在聊天界面点击录音按钮
3. 上传这些音频文件进行测试

## 🎯 预期结果

### 语音识别结果
- `Recording.m4a` → "other thing is"
- `Recording (2).m4a` → "hello hello"

### 测试通过标准
- ✅ 音频文件成功上传
- ✅ 语音转文字识别成功
- ✅ 识别结果准确
- ✅ 后端返回正确响应

## ⚠️ 注意事项

### 语言设置
- 这些音频文件是英语内容
- 测试时请使用英语语言设置（en-US）
- 中文设置可能导致识别失败

### 环境要求
- **网络连接**: 语音识别需要网络连接（Google服务）
- **后端服务**: 确保后端服务正在运行
- **依赖库**: 确认已安装必要的音频处理库

### 文件要求
- 确保文件存在于正确路径
- 检查文件权限和完整性
- 验证音频文件格式支持

## 🐛 故障排除

### 识别失败
**症状**: 语音转文字返回空结果或错误
**解决方案**:
- 检查网络连接
- 确认音频文件完整性
- 验证语言设置是否正确
- 检查后端服务状态

### 文件找不到
**症状**: 测试脚本报告文件不存在
**解决方案**:
- 检查文件路径是否正确
- 确认文件存在于指定目录
- 检查文件权限设置

### 格式不支持
**症状**: 音频处理失败
**解决方案**:
- 确认后端已安装必要的音频处理库
- 检查ffmpeg是否正确安装
- 验证音频文件格式

## 📊 测试数据扩展

### 添加新的测试音频

1. **准备音频文件**
   - 格式: WAV, MP3, M4A, OGG, FLAC
   - 内容: 清晰的语音
   - 时长: 1-30秒

2. **放置文件**
   ```bash
   # 将新文件放在test_audios目录
   cp your_audio.wav test_audios/
   ```

3. **更新测试用例**
   ```python
   # 在test_speech_to_text.py中添加新测试用例
   test_files.append({
       "file": "../test_audios/your_audio.wav",
       "expected_language": "zh-CN",
       "description": "新测试音频"
   })
   ```

### 测试场景建议

- **清晰语音**: 安静环境，清晰发音
- **多语言**: 中文、英文、其他语言
- **不同格式**: WAV, M4A, MP3等
- **边界情况**: 静音、噪音、短音频等