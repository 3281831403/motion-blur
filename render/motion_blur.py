"""运动模糊：快门、矢量与分层：待实现的核心模块。"""


def sample_shutter(frame_dt, open_angle, count):
    """在快门开角内按实际帧间隔均匀采样。"""
    raise NotImplementedError

def compose_motion_vector(dx, dy, rotation, scale):
    """把平移、旋转、缩放合成一个运动矢量。"""
    raise NotImplementedError

def depth_weight(depth, near, far):
    """按深度计算重投影权重。"""
    raise NotImplementedError

def split_layers(alphas):
    """按不透明度拆分不透明层与半透明层。"""
    raise NotImplementedError

def adaptive_sample_count(base, pixels):
    """采样数量按屏幕像素数自适应。"""
    raise NotImplementedError

def clamp_shutter_angle(angle):
    """快门开角钳制到 0–360 度。"""
    raise NotImplementedError

def trim_history(vectors, max_len):
    """只保留最近 max_len 条历史矢量。"""
    raise NotImplementedError

def rolling_offset(row, width, skew):
    """滚动快门按行给出时间偏移。"""
    raise NotImplementedError

def particle_vector(start, end):
    """粒子位置差生成运动矢量。"""
    raise NotImplementedError

def order_postprocess(steps):
    """固定后处理顺序：模糊→景深→TAA。"""
    raise NotImplementedError
