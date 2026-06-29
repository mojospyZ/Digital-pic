from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QFileDialog
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from image_effects import apply_color_effect, apply_filter, apply_enhance
from image_ui import ImageProcessorUI
import torch
from Zero_DCE.model import Zero 
import os
import sys
def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于 PyInstaller 打包后的环境 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ImageProcessor(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = ImageProcessorUI(self)  # 创建UI组件
        self.original_image = None
        self.current_image = None
        self.processed_image = None  # 存储应用效果后但未缩放的图像
        self.Zero = Zero()
        model_path = resource_path(os.path.join('Zero_DCE', 'Epoch99.pth'))
        self.Zero.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=True))
        self.Zero.eval()

    def load_image(self):
        
        file_name, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 
                                                 'Images (*.png *.xpm *.jpg *.bmp)')
        if file_name:
            file_path = os.path.normpath(file_name)  # 规范化路径
            self.original_image = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if len(self.original_image.shape) == 2:
            # 若是灰度图，转换为RGB格式（三通道）
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_GRAY2RGB)
            else:
            # 否则转换BGR到RGB
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.processed_image = self.original_image   
            # 重置控件状态
            self.ui.reset_controls()
            # 更新图像
            self.update_image(self.original_image)

    def update_image(self, image):
        """更新并显示图像
        
        Args:
            image: numpy数组格式的RGB图像
        """
        # 保存当前图像
        self.current_image = image
        
        # 获取图像的高度、宽度和通道数
        height, width, channel = image.shape
        
        # 计算每行字节数 (RGB格式每像素3字节)
        bytes_per_line = 3 * width
        
        # 将numpy数组转换为QImage对象
        # Format_RGB888表示使用24位RGB格式
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # 将QImage转换为QPixmap用于显示
        pixmap = QPixmap.fromImage(q_image)
        
        # 使用UI组件更新图像显示
        self.ui.update_image_display(pixmap)
        
        # 更新窗口标题显示当前图像尺寸
        self.setWindowTitle(f'图像处理软件 - 图像尺寸: {width}x{height}')

    def scale_image(self):
        if self.original_image is None:
            return
        
        scale = self.ui.scale_slider.value() / 100.0
        # 更新缩放比例标签
        self.ui.update_scale_label(int(scale * 100))
        
        # 如果有处理过的图像，则基于处理过的图像进行缩放，否则基于原始图像
        base_image = self.processed_image if self.processed_image is not None else self.original_image
        
        # 应用亮度、对比度和饱和度调整
        # 获取滑块值并转换为增强系数（0-200% 对应 0-2.0）
        brightness_value = self.ui.brightness_slider.value() / 100.0
        contrast_value = self.ui.contrast_slider.value() / 100.0
        saturation_value = self.ui.saturation_slider.value() / 100.0
        
        # 更新UI标签
        self.ui.brightness_value_label.setText(f'{int(brightness_value * 100)}%')
        self.ui.contrast_value_label.setText(f'{int(contrast_value * 100)}%')
        self.ui.saturation_value_label.setText(f'{int(saturation_value * 100)}%')
        
        # 应用图像增强
        adjusted_image = base_image.copy()
        
        # 只有当值不是100%（1.0）时才应用调整，以提高性能
        if brightness_value != 1.0 or contrast_value != 1.0 or saturation_value != 1.0:
            pil_image = Image.fromarray(adjusted_image)
            
            # 应用亮度调整
            if brightness_value != 1.0:
                enhancer = ImageEnhance.Brightness(pil_image)
                pil_image = enhancer.enhance(brightness_value)
            
            # 应用对比度调整
            if contrast_value != 1.0:
                enhancer = ImageEnhance.Contrast(pil_image)
                pil_image = enhancer.enhance(contrast_value)
            
            # 应用饱和度调整
            if saturation_value != 1.0:
                enhancer = ImageEnhance.Color(pil_image)
                pil_image = enhancer.enhance(saturation_value)
            
            adjusted_image = np.array(pil_image)
        
        # 获取图像尺寸
        height, width = adjusted_image.shape[:2]
        # 计算缩放尺寸
        new_size = (int(width * scale), int(height * scale))
        
        # 根据选择的插值方法进行缩放
        interp_method = self.ui.interp_combo.currentText()
        if interp_method == '最近邻':
            interpolation = cv2.INTER_NEAREST
        elif interp_method == '双线性':
            interpolation = cv2.INTER_LINEAR
        else:  # 双三次
            interpolation = cv2.INTER_CUBIC
            
        # 进行缩放
        scaled_image = cv2.resize(adjusted_image, new_size, interpolation=interpolation)
        self.update_image(scaled_image)

    def apply_color_effect(self, effect):
        if self.original_image is None:
            return

        self.processed_image = apply_color_effect(self.original_image, effect)
        self.scale_image()

    def apply_filter(self, filter_type):
        if self.original_image is None:
            return

        self.processed_image = apply_filter(self.original_image, filter_type)
        self.scale_image()

    def apply_enhance(self, enhance_type):
        if self.original_image is None:
            return
        if enhance_type == 'Zero_DCE模型(低光照增强)':
            image = self.original_image
            image = image.astype(np.float32) / 255.0  # 归一化到[0,1]
            image = torch.from_numpy(image).float()
            image = image.permute(2,0,1)  # 转换为(C,H,W)格式
            image = image.unsqueeze(0)    # 添加batch维度
            
            with torch.no_grad():
                _, enhanced_image, _ = self.Zero(image)
            
            # 将增强后的图像转换回numpy数组并进行后处理
            enhanced_image_np = enhanced_image.squeeze(0).permute(1, 2, 0).numpy()
            # 确保值域在[0,1]范围内
            enhanced_image_np = np.clip(enhanced_image_np, 0, 1)
            # 转换为0-255范围
            enhanced_image_np = (enhanced_image_np * 255).astype(np.uint8)
            self.processed_image = enhanced_image_np
            
        else: 
            self.processed_image = apply_enhance(self.original_image, enhance_type)
        self.scale_image()

    def save_image(self):
        if self.current_image is None:
            return
            
        from PyQt6.QtWidgets import QFileDialog
        file_name, _ = QFileDialog.getSaveFileName(self, '保存图片', '', 
                                                 'Images (*.png *.xpm *.jpg *.bmp)')
        if file_name:
            save_image = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2BGR)
            # 获取文件扩展名
            ext = os.path.splitext(file_name)[1]
            # 根据扩展名确定图像编码格式
            if ext.lower() == '.jpg' or ext.lower() == '.jpeg':
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                result, encoded_img = cv2.imencode(ext, save_image, encode_param)
            else:
                result, encoded_img = cv2.imencode(ext, save_image)
            
            if result:
                # 将编码后的图像数据写入文件
                with open(file_name, 'wb') as f:
                    encoded_img.tofile(f)
    
    def reset(self):
        """重置所有控件到初始状态"""
        self.ui.reset_controls()
        self.processed_image = self.original_image  # 重置为原始图像
        self.scale_image()

    def show_original_image(self):
        """显示原图"""
        if self.original_image is not None:
            # 获取当前缩放比例
            scale = self.ui.scale_slider.value() / 100.0
            height, width = self.original_image.shape[:2]
            new_size = (int(width * scale), int(height * scale))
            
            # 使用当前的插值方法进行缩放
            interp_method = self.ui.interp_combo.currentText()
            if interp_method == '最近邻':
                interpolation = cv2.INTER_NEAREST
            elif interp_method == '双线性':
                interpolation = cv2.INTER_LINEAR
            else:  # 双三次
                interpolation = cv2.INTER_CUBIC
                
            # 缩放原图并显示
            scaled_image = cv2.resize(self.original_image, new_size, interpolation=interpolation)
            self.update_image(scaled_image)
    
    def show_processed_image(self):
        """显示处理后的图片"""
        if self.processed_image is not None:
            # 重新应用当前的缩放比例
            self.scale_image()