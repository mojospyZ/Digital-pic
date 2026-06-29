import numpy as np
from PIL import Image
import time

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
    
    # # 使用优化的矩阵乘法进行卷积计算
    # output = np.einsum('ijklm,klm->ijm', windows, kernel, 
    #                   optimize='optimal', dtype=np.float32)
    # 扩展kernel维度以匹配windows
    kernel_expanded = kernel[np.newaxis, np.newaxis, ...]  # shape变为 (1,1,kh,kw,1)
    output = np.sum(windows * kernel_expanded, axis=(2,3))

    # 如果输入是单通道，则保持输出形状一致
    if c == 1:
        output = output.reshape(h, w)
        
    return output

if __name__ == '__main__':
    img = Image.open('human.jpg')
    img = np.array(img)
    start = time.time()
    convolve2d(img, np.ones((3, 3)))
    print(time.time() - start)