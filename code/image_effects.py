import numpy as np

def gaussian_kernel_2d(size, sigma=2):
    x, y = np.meshgrid(np.linspace(-size//2, size//2, size),
                      np.linspace(-size//2, size//2, size))
    g = np.exp(-(x**2 + y**2)/(2*sigma**2))
    return g / g.sum()

def convolve2d(image, kernel):
    # 确保内存连续
    kernel = np.ascontiguousarray(kernel, dtype=np.float32)
    image = np.ascontiguousarray(image, dtype=np.float32)
    
    # 获取图像和核的尺寸
    if len(image.shape) == 3:
        h, w, c = image.shape
    else:
        h, w = image.shape
        c = 1
        image = image.reshape(h, w, 1)
    
    kh, kw = kernel.shape
    pad_h = ( kh - 1 )// 2
    pad_w = (kw - 1) // 2
    
    # 创建输出数组和填充后的输入数组
    output = np.zeros((h, w, c), dtype=np.float32, order='C')
    # 实现边界填充
    padded = np.zeros((h + 2*pad_h, w + 2*pad_w, c), dtype=np.float32)
    padded[pad_h:pad_h+h, pad_w:pad_w+w] = image
    
    # 填充边界（镜像填充）
    # 填充上下边界
    padded[:pad_h, pad_w:pad_w+w] = image[pad_h-1::-1, :]
    padded[pad_h+h:, pad_w:pad_w+w] = image[-1:-pad_h-1:-1, :]
    
    # 填充左右边界
    padded[:, :pad_w] = padded[:, 2*pad_w-1:pad_w-1:-1]
    padded[:, pad_w+w:] = padded[:, pad_w+w-1:pad_w + w - pad_w -1:-1]
    
    stride_h = padded.strides[0]
    stride_w = padded.strides[1]
    stride_c = padded.strides[2]
    
    # 创建优化的视图数组
    windows = np.lib.stride_tricks.as_strided(
        padded,
        shape=(h, w, kh, kw, c),
        strides=(stride_h, stride_w, stride_h, stride_w, stride_c),
        writeable=False 
    )
    
    # 重塑kernel
    kernel = kernel.reshape(kh, kw, 1)
    
    # 使用优化的矩阵乘法进行卷积计算
    output = np.einsum('ijklm,klm->ijm', windows, kernel, 
                      optimize='optimal', dtype=np.float32)
    
    # 如果输入是单通道，则保持输出形状一致
    if c == 1:
        output = output.reshape(h, w)
        
    return output

def _histogram_equalization_1d(channel):
    L = 256
    
    #统计直方图（计算每个灰度级的概率）
    h, w = channel.shape
    total_pixels = h * w
    hist = [0] * L

    # 统计每个灰度级的像素数量
    for i in range(h):
        for j in range(w):
            pixel_idx = channel[i, j]
            hist[pixel_idx] += 1
    
    #计算每个灰度级的概率 p_r(r_k)
    p_r = [count / total_pixels for count in hist]
    
    #计算累积分布函数 s_k = T(r_k)
    cdf = [0] * L
    cdf[0] = p_r[0]
    for i in range(1, L):
        cdf[i] = cdf[i-1] + p_r[i]
    
    #找到第一个非零CDF值（s_min）
    s_min = 0
    for i in range(L):
        if cdf[i] > 0:
            s_min = cdf[i]
            break
    
    # 使用公式: s_k = int[(L-1)/(1-s_min) * (s_k - s_min) + 0.5]
    lut = [0] * L
    for i in range(L):
        if cdf[i] > 0:
            lut[i] = int((L-1) / (1-s_min) * (cdf[i] - s_min) + 0.5)
            # 确保映射值在有效范围内
            lut[i] = max(0, min(lut[i], L-1))
    
    # 应用查找表进行像素替换
    equalized = np.zeros_like(channel)
    for i in range(h):
        for j in range(w):
            pixel_idx = channel[i, j] 
            # 将均衡化后的值映射回原始灰度范围
            equalized[i, j] = lut[pixel_idx]
    return equalized

def histogram_equalization(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        # 单通道图像（灰度图）
        return _histogram_equalization_1d(image)

    elif len(image.shape) == 3 and image.shape[2] == 3:
        # 三通道图像（彩色图），分别对每个通道进行均衡化
        r = _histogram_equalization_1d(image[:, :, 0])
        g = _histogram_equalization_1d(image[:, :, 1])
        b = _histogram_equalization_1d(image[:, :, 2])
        return np.stack([r, g, b], axis=2)
    else:
        raise ValueError("Unsupported image format")
        
def apply_color_effect(image, effect):
    if effect == '原图':
        return image
    elif effect == '灰度图':
        # 使用BT.601标准的RGB权重进行向量化灰度转换
        weights = np.array([0.299, 0.587, 0.114])
        gray = np.dot(image, weights).astype(np.uint8)
        return np.stack([gray] * 3, axis=-1)
    elif effect == '反色':
        # 向量化实现反色
        return 255 - image
    elif effect == '怀旧':
        weights = np.array([[0.393, 0.769, 0.189],
                            [0.349, 0.686, 0.168],
                            [0.272, 0.534, 0.131]])
        
        sepia = image @ weights.T  # 矩阵乘法：(H, W, 3) × (3, 3) → (H, W, 3)
        sepia = np.clip(sepia, 0, 255).astype(np.uint8)
        return sepia
    return image

def apply_filter(image, filter_type):
    if filter_type == '无':
        return image
    elif filter_type == '模糊':
        # 向量化实现高斯模糊
        kernel = gaussian_kernel_2d(15)
        return convolve2d(image, kernel).astype(np.uint8)
    
    elif filter_type == '锐化':
        # 向量化实现锐化
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]], dtype=np.float32)
        return np.clip(convolve2d(image, kernel), 0, 255).astype(np.uint8)

    elif filter_type == '浮雕':
        # 向量化实现浮雕效果
        kernel = np.array([[-2, -1, 0],
                          [-1,  1, 1],
                          [ 0,  1, 2]])
        return np.clip(convolve2d(image, kernel), 0, 255).astype(np.uint8)
    
    elif filter_type == '边缘检测':
        # 向量化实现Sobel边缘检测
        # 转换为灰度图
        gray = np.dot(image, [0.299, 0.587, 0.114]).astype(np.float32)
        
        # Sobel算子
        kernel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]], dtype=np.float32)
        kernel_y = np.array([[-1, -2, -1],
                            [ 0,  0,  0],
                            [ 1,  2,  1]], dtype=np.float32)
        
        # 计算梯度
        grad_x = convolve2d(gray, kernel_x)
        grad_y = convolve2d(gray, kernel_y)
        
        # 计算梯度幅值
        magnitude = np.clip(np.sqrt(grad_x**2 + grad_y**2), 0, 255).astype(np.uint8)
        return np.stack([magnitude] * 3, axis=-1)
    
    return image

def apply_enhance(image, enhance_type, net = None):
    if enhance_type == '无':
        return image
    elif enhance_type == '直方图均衡化':
        return histogram_equalization(image)

