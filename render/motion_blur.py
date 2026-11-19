"""运动模糊：快门、矢量与分层。

实现运动模糊管线里最容易做错的十件事：按实际帧间隔采样快门、把旋转与
缩放合入运动矢量、让背景深度参与重投影、按不透明度拆分模糊层、按像素
数自适应采样、钳制快门开角、裁剪 TAA 历史、滚动快门逐行偏移、为粒子
生成运动矢量，以及固定后处理顺序。
"""

MAX_SHUTTER_ANGLE = 360.0
REFERENCE_PIXELS = 1280 * 720
POSTPROCESS_ORDER = ("motion_blur", "dof", "taa")


def clamp_shutter_angle(angle):
    """快门开角钳制到 0–360 度。

    超过 360 度的开角不会让快门多转一圈，否则采样权重会被重复计入。
    """
    return float(min(MAX_SHUTTER_ANGLE, max(0.0, float(angle))))


def sample_shutter(frame_dt, open_angle, count):
    """在快门开角内按实际帧间隔均匀采样。

    frame_dt 是这一帧的真实间隔（可变帧率下逐帧不同），曝光时长按开角
    占 360 度的比例缩放；count 个采样点从 0 均匀覆盖到曝光结束。
    """
    count = int(count)
    if count <= 0:
        return []
    exposure = max(0.0, float(frame_dt)) * clamp_shutter_angle(open_angle) / 360.0
    if count == 1:
        return [0.0]
    step = exposure / (count - 1)
    return [i * step for i in range(count)]


def compose_motion_vector(dx, dy, rotation, scale):
    """把平移、旋转、缩放合成一个运动矢量。

    返回 ``[dx, dy, rotation_deg, scale_delta]``：旋转以角度保存，缩放保存
    为相对 1.0 的变化量（2 倍缩放记为 1.0），这样多帧矢量可以直接累加，
    不会因为只取上一帧的平移而丢掉旋转和缩放分量。
    """
    return [float(dx), float(dy), float(rotation), float(scale) - 1.0]


def depth_weight(depth, near, far):
    """按深度计算重投影权重。

    近处物体的模糊权重为 1，远处趋近 0；背景权重归零后就不会被前景
    边缘的矢量拖成条带。超出 [near, far] 的深度钳制到边界。
    """
    depth = float(depth)
    near = float(near)
    far = float(far)
    if far <= near:
        return 1.0 if depth <= near else 0.0
    t = (depth - near) / (far - near)
    return float(min(1.0, max(0.0, 1.0 - t)))


def split_layers(alphas):
    """按不透明度拆分不透明层与半透明层。

    返回 ``(opaque_count, translucent_count)``：``alpha >= 1`` 归入不透明
    层，``0 < alpha < 1`` 归入独立的半透明层，两层分别模糊后再合成，
    避免叠加出现双重轮廓；完全透明的样本不产生模糊贡献。
    """
    opaque = 0
    translucent = 0
    for alpha in alphas:
        value = float(alpha)
        if value >= 1.0:
            opaque += 1
        elif value > 0.0:
            translucent += 1
    return (opaque, translucent)


def adaptive_sample_count(base, pixels):
    """采样数量按屏幕像素数自适应。

    以 1280×720 为基准按像素面积线性缩放，保持每像素的采样密度：低分
    辨率不再浪费采样，高分辨率也不会因为固定采样数而噪点爆炸。
    """
    base = int(base)
    pixels = int(pixels)
    if base <= 0:
        return 0
    if pixels <= 0:
        return base
    count = int(round(base * pixels / float(REFERENCE_PIXELS)))
    return max(1, count)


def trim_history(vectors, max_len):
    """只保留最近 max_len 条历史矢量。

    TAA 历史只允许回看固定长度，未裁剪的旧矢量会让残影跨帧累积。
    """
    max_len = int(max_len)
    if max_len <= 0:
        return []
    return list(vectors[-max_len:])


def rolling_offset(row, width, skew):
    """滚动快门按行给出时间偏移。

    行号在画面中的归一化位置乘以整帧的滚动 skew（秒）。快速横移时按行
    偏移采样才不会出现斜切。
    """
    width = int(width)
    if width <= 0:
        return 0.0
    row = min(max(float(row), 0.0), float(width))
    return (row / float(width)) * float(skew)


def particle_vector(start, end):
    """粒子位置差生成运动矢量。

    粒子不写运动矢量时会被当成静止物体，火花被拖成整条线。
    """
    return [float(e) - float(s) for s, e in zip(start, end)]


def order_postprocess(steps):
    """固定后处理顺序：模糊→景深→TAA。

    先做运动模糊，再让景深处理边缘，最后进入 TAA；反过来先模糊会把
    景深边界和 TAA 历史一起抹开。未知步骤排在已知步骤之后并保持输入
    顺序。
    """
    flat = []
    for step in steps:
        if isinstance(step, (list, tuple)):
            flat.extend(step)
        else:
            flat.append(step)
    rank = {name: index for index, name in enumerate(POSTPROCESS_ORDER)}
    return sorted(flat, key=lambda name: rank.get(name, len(POSTPROCESS_ORDER)))
