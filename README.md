# 运动模糊：快门、矢量与分层

相机快速平移时运动模糊把静态物体也拖出残影：快门按固定 1/60 秒采样、运动矢量只取上一帧变换、背景深度不参与重投影、半透明未分层、采样数固定、快门开角不钳制、历史矢量不裁剪、滚动快门无行偏移、粒子不写矢量、后处理顺序冲突。

## 目录结构

```
README.md
conftest.py
.gitignore
render/__init__.py
render/motion_blur.py
tests/test_motion_blur.py
```

## 当前状态

`render/motion_blur.py` 中所有函数只保留签名与文档字符串，函数体统一
`raise NotImplementedError`。`tests/test_motion_blur.py` 有 15 个参数化用例，
初始全部失败。

## 需要修复的 10 个问题

1. 按实际帧间隔采样快门
2. 运动矢量包含旋转与缩放
3. 背景深度参与重投影
4. 半透明物体分离模糊层
5. 采样数随分辨率自适应
6. 快门开角钳制到 360 度
7. TAA 历史矢量裁剪
8. 滚动快门按行偏移
9. 粒子系统写运动矢量
10. 固定后处理顺序

## 验收

```bash
python -m pytest -q
```

初始应得到 `15 failed`，且没有 collection error。实现 `render/motion_blur.py`
后 15 条用例应全部通过。
