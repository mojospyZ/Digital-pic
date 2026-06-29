from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
QPushButton, QLabel,  QSlider, QComboBox, QScrollArea, \
QFrame, QSizePolicy, QGroupBox
from PyQt6.QtGui import QPixmap,  QFont,  QIcon
from PyQt6.QtCore import Qt
import os
import sys

def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于 PyInstaller 打包后的环境 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ImageProcessorUI:
    """
    图像处理软件的UI组件类
    负责创建和管理所有UI元素
    """
    def __init__(self, parent):
        """
        初始化UI组件
        
        Args:
            parent: 父窗口，通常是ImageProcessor实例
        """
        self.parent = parent
        self.setup_ui()
        # 为所有ComboBox禁用滚轮事件
        self.interp_combo.wheelEvent = lambda event: None
        self.color_combo.wheelEvent = lambda event: None
        self.filter_combo.wheelEvent = lambda event: None
        self.enhance_combo.wheelEvent = lambda event: None
        
    def setup_ui(self):
        """
        设置UI布局和组件
        """
        # 设置窗口标题和大小
        self.parent.setWindowTitle('MojoPs')
        self.parent.setWindowIcon(QIcon(resource_path(os.path.join('icon', 'app.jpg'))))
        self.parent.setGeometry(100, 100, 1200, 800)
        # self.parent.statusBar().showMessage('Ready')
        # 设置应用程序样式
        self.set_application_style()

        # 创建主窗口部件和布局
        main_widget = QWidget()
        self.parent.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        layout.setSpacing(8)  # 减小布局间距
        layout.setContentsMargins(8, 8, 8, 8)  # 减小布局边距
        main_widget.setLayout(layout)

        # 创建左侧工具栏
        tools_widget = self.create_tools_panel()
        
        # 创建右侧图片显示区域
        image_container = QFrame()
        image_container.setFrameShape(QFrame.Shape.NoFrame)  # 移除边框
        image_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        image_container.setStyleSheet("""
            background-color: #00ffff;
            border-radius: 2px;
            border: 1px solid #0066cc;
        """)
        
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(10, 10, 10, 10)  # 减小内部边距
        
        # 创建图片标签
        self.image_label = QLabel('图片显示区域')
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(1, 1)  # 设置最小尺寸
        self.image_label.setStyleSheet("""
            background-color: #fafafa;
            border-radius: 2px;
            font-size: 14pt;
            font-weight: bold;
        """)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # 不自动调整大小
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中显示
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # 移除边框
        self.scroll_area.setStyleSheet("""
            background-color: rgba(250, 250, 250, 0.89);
            border-radius: 4px;
            border: none;
        """)
        
        image_layout.addWidget(self.scroll_area)
        
        layout.addWidget(tools_widget, 1)  # 1是相对宽度比例
        layout.addWidget(image_container, 4)  # 4是相对宽度比例
    
    def create_tools_panel(self):
        """
        创建左侧工具面板
        
        Returns:
            QWidget: 工具面板部件
        """
        # 创建外层容器
        tools_container = QWidget()
        tools_container.setFixedWidth(250)  # 减小工具栏宽度
        tools_container.setStyleSheet("""
            background-color: #f0f2f0;
            border-radius: 6px;
        """)
        
        # 创建滚动区域
        tools_scroll = QScrollArea()
        tools_scroll.setWidgetResizable(True)  # 允许调整大小
        tools_scroll.setFrameShape(QFrame.Shape.NoFrame)  # 移除边框
        tools_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # 禁用水平滚动条
        tools_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)  # 启用垂直滚动条并始终显示
        tools_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        # 创建内部部件和布局
        tools_widget = QWidget()
        tools_layout = QVBoxLayout(tools_widget)
        tools_layout.setSpacing(12)  # 减小组件之间的间距
        tools_layout.setContentsMargins(12, 12, 12, 12)  # 减小边距
        
        # 设置滚动区域的部件
        tools_scroll.setWidget(tools_widget)
        
        # 设置外层容器的布局
        container_layout = QVBoxLayout(tools_container)
        container_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        container_layout.addWidget(tools_scroll)

        '''文件操作组'''
        file_group = QGroupBox("文件")
        file_layout = QVBoxLayout()
        file_layout.setContentsMargins(10, 16, 10, 10)  # 减小内部边距
        file_layout.setSpacing(8)  # 减小组件间距
        file_group.setLayout(file_layout)
        
        # 添加按钮
        self.load_btn = QPushButton('打开图片', self.parent)
        open_icon = QIcon(QPixmap(resource_path(os.path.join('icon', 'open.png'))))
        self.load_btn.setIcon(open_icon)
        self.load_btn.clicked.connect(self.parent.load_image)
        file_layout.addWidget(self.load_btn)
        
        # 保存按钮
        self.save_btn = QPushButton('保存图片', self.parent)
        save_icon = QIcon(QPixmap(resource_path(os.path.join('icon', 'save.png'))))
        self.save_btn.setIcon(save_icon)
        self.save_btn.clicked.connect(self.parent.save_image)
        file_layout.addWidget(self.save_btn)
        
        # 对比原图按钮
        self.compare_btn = QPushButton('对比原图', self.parent)
        contrast_icon = QIcon(QPixmap(resource_path(os.path.join('icon', 'contrast.png'))))
        self.compare_btn.setIcon(contrast_icon)
        self.compare_btn.pressed.connect(self.parent.show_original_image)
        self.compare_btn.released.connect(self.parent.show_processed_image)
        file_layout.addWidget(self.compare_btn)
        
        # 重置按钮
        self.reset_btn = QPushButton('重置', self.parent)
        reset_icon = QIcon(QPixmap(resource_path(os.path.join('icon', 'reset.png'))))
        self.reset_btn.setIcon(reset_icon)
        self.reset_btn.clicked.connect(self.parent.reset)
        file_layout.addWidget(self.reset_btn)

        tools_layout.addWidget(file_group)

        '''图片调整组'''
        adjust_group = QGroupBox("图片调整")
        adjust_layout = QVBoxLayout()
        adjust_layout.setContentsMargins(10, 16, 10, 10)  # 减小内部边距
        adjust_layout.setSpacing(8)  # 减小组件间距
        adjust_group.setLayout(adjust_layout)
        
         # 缩放插值方法选择
        interp_label = QLabel('插值方法')
        adjust_layout.addWidget(interp_label)
        
        self.interp_combo = QComboBox()
        self.interp_combo.addItems(['最近邻', '双线性', '双三次'])
        self.interp_combo.setCurrentIndex(0)  # 默认选择双三次
        self.interp_combo.currentTextChanged.connect(self.parent.scale_image)
        adjust_layout.addWidget(self.interp_combo)
        
        tools_layout.addWidget(adjust_group)

        # 缩放控制
        # scale_label = QLabel('缩放比例')
        scale_label = QLabel(f'<img src="{resource_path(os.path.join("icon", "zoom.png"))}" width="16" height="16" style="vertical-align: middle; margin-right: 4px;"> 缩放比例')
        adjust_layout.addWidget(scale_label)
        
        # 添加水平布局来放置滑块和显示比例的标签
        scale_layout = QHBoxLayout()
        scale_layout.setSpacing(8)  # 减小水平布局间距
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setObjectName("scale_slider")  # 设置对象名称
        self.scale_slider.setRange(10, 200)
        self.scale_slider.setValue(100)
        self.scale_slider.setFixedHeight(24)  # 减小固定高度
        self.scale_slider.valueChanged.connect(self.parent.scale_image)
        scale_layout.addWidget(self.scale_slider)
        
        # 添加显示缩放比例的标签
        self.scale_value_label = QLabel('100%')
        self.scale_value_label.setObjectName("scale_value_label")  # 设置对象名称
        self.scale_value_label.setMinimumWidth(40)  # 减小最小宽度
        self.scale_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scale_layout.addWidget(self.scale_value_label)
        adjust_layout.addLayout(scale_layout)
        

        #亮度控制
        # brightness_label = QLabel('亮度')
        brightness_label = QLabel(f'<img src="{resource_path(os.path.join("icon", "bright.png"))}" width="16" height="16" style="vertical-align: middle; margin-right: 4px;"> 亮度')
        adjust_layout.addWidget(brightness_label)

        # 添加水平布局来放置滑块和显示亮度的标签
        brightness_layout = QHBoxLayout()
        brightness_layout.setSpacing(8)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setObjectName("brightness_slider")  # 设置对象名称
        self.brightness_slider.setRange(10, 200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setFixedHeight(24)
        self.brightness_slider.valueChanged.connect(self.parent.scale_image)
        brightness_layout.addWidget(self.brightness_slider)

        #添加显示缩放比例的标签
        self.brightness_value_label = QLabel('100%')
        self.brightness_value_label.setObjectName("brightness_value_label")  # 设置对象名称
        self.brightness_value_label.setMinimumWidth(40)
        self.brightness_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brightness_layout.addWidget(self.brightness_value_label)
        adjust_layout.addLayout(brightness_layout)

        #饱和度控制
        # saturation_label = QLabel('饱和度')
        saturation_label = QLabel(f'<img src="{resource_path(os.path.join("icon", "satur.png"))}" width="16" height="16" style="vertical-align: middle; margin-right: 4px;"> 饱和度')
        adjust_layout.addWidget(saturation_label)

        # 添加水平布局来放置滑块和显示饱和度的标签
        saturation_layout = QHBoxLayout()
        saturation_layout.setSpacing(8)
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setObjectName("saturation_slider")  # 设置对象名称
        self.saturation_slider.setRange(10, 200)
        self.saturation_slider.setValue(100)
        self.saturation_slider.setFixedHeight(24)
        self.saturation_slider.valueChanged.connect(self.parent.scale_image)
        saturation_layout.addWidget(self.saturation_slider)

        #添加显示缩放比例的标签
        self.saturation_value_label = QLabel('100%')
        self.saturation_value_label.setObjectName("saturation_value_label")  # 设置对象名称
        self.saturation_value_label.setMinimumWidth(40)
        self.saturation_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        saturation_layout.addWidget(self.saturation_value_label)
        adjust_layout.addLayout(saturation_layout)

        #对比度控制
        # contrast_label = QLabel('对比度')
        contrast_label = QLabel(f'<img src="{resource_path(os.path.join("icon", "compare.png"))}" width="16" height="16" style="vertical-align: middle; margin-right: 4px;"> 对比度')
        adjust_layout.addWidget(contrast_label)

        # 添加水平布局来放置滑块和显示对比度的标签
        contrast_layout = QHBoxLayout()
        contrast_layout.setSpacing(8)
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setObjectName("contrast_slider")  # 设置对象名称
        self.contrast_slider.setRange(10, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setFixedHeight(24)
        self.contrast_slider.valueChanged.connect(self.parent.scale_image)
        contrast_layout.addWidget(self.contrast_slider)

        #添加显示缩放比例的标签
        self.contrast_value_label = QLabel('100%')
        self.contrast_value_label.setObjectName("contrast_value_label")  # 设置对象名称
        self.contrast_value_label.setMinimumWidth(40)
        self.contrast_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contrast_layout.addWidget(self.contrast_value_label)
        adjust_layout.addLayout(contrast_layout)

        '''效果处理组'''
        effect_group = QGroupBox("图片效果")
        effect_layout = QVBoxLayout()
        effect_layout.setContentsMargins(10, 16, 10, 10)  # 减小内部边距
        effect_layout.setSpacing(8)  # 减小组件间距
        effect_group.setLayout(effect_layout)
        
        # 颜色调整
        # color_label = QLabel('颜色调整')
        color_label = QLabel(f'<img src="{resource_path(os.path.join("icon", "color.png"))}" width="16" height="16" style="vertical-align: middle; margin-right: 4px;"> 颜色调整')
        effect_layout.addWidget(color_label)
        
        self.color_combo = QComboBox()
        self.color_combo.addItems(['原图', '灰度图', '反色','怀旧'])
        self.color_combo.currentTextChanged.connect(self.parent.apply_color_effect)
        effect_layout.addWidget(self.color_combo)

        # 滤镜效果
        # filter_label = QLabel('滤镜效果')
        filter_label = QLabel(f'<img src="{resource_path(os.path.join("icon", "filter.png"))}" width="16" height="16" style="vertical-align: middle; margin-right: 4px;"> 滤镜效果')
        effect_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['无', '模糊', '锐化', '浮雕','边缘检测'])
        self.filter_combo.currentTextChanged.connect(self.parent.apply_filter)
        effect_layout.addWidget(self.filter_combo)
        
        tools_layout.addWidget(effect_group)

        #图像增强
        # enhance_label = QLabel('图像增强')
        enhance_label = QLabel(f'<img src="{resource_path(os.path.join("icon", "enhance.png"))}" width="16" height="16" style="vertical-align: middle; margin-right: 4px;"> 图像增强')
        effect_layout.addWidget(enhance_label)

        self.enhance_combo = QComboBox()
        self.enhance_combo.addItems(['无', '直方图均衡化','Zero_DCE模型(低光照增强)'])
        self.enhance_combo.currentTextChanged.connect(self.parent.apply_enhance)
        
        effect_layout.addWidget(self.enhance_combo)

        #其他功能
        other_label = QLabel('其他功能')

        # 添加弹簧
        tools_layout.addStretch()
        
        # 添加版权信息
        copyright_label = QLabel('© 2025 mojospy')
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #a0a0a0; font-size: 8pt;")
        tools_layout.addWidget(copyright_label)
        
        return tools_container
    
    def update_scale_label(self, scale_value):
        """
        更新缩放比例标签
        
        Args:
            scale_value: 缩放比例值（百分比）
        """
        self.scale_value_label.setText(f'{scale_value}%')
    
    def update_image_display(self, pixmap):
        """
        更新图像显示
        
        Args:
            pixmap: QPixmap对象，要显示的图像
        """
        self.image_label.setPixmap(pixmap)
        self.image_label.resize(pixmap.size())
    
    def reset_controls(self):
        """
        重置所有控件到默认状态
        """
        # 重置缩放滑块和标签
        self.scale_slider.setValue(100)
        self.scale_value_label.setText('100%')
        self.brightness_slider.setValue(100)
        self.brightness_value_label.setText('100%')
        self.saturation_slider.setValue(100)
        self.saturation_value_label.setText('100%')
        self.contrast_slider.setValue(100)
        self.contrast_value_label.setText('100%')

        # 重置下拉框选项
        self.interp_combo.setCurrentIndex(0)  # 设置为最邻近
        self.color_combo.setCurrentIndex(0)   # 设置为原图
        self.filter_combo.setCurrentIndex(0)  # 设置为无
        self.enhance_combo.setCurrentIndex(0)

    def set_application_style(self):
        """
        设置应用程序的整体样式
        """
        # 设置应用程序样式表 - 简约风格
        style = """
        QMainWindow, QWidget {
            background-color: #f5f5f5;
            color: #333333;
        }
        QPushButton {
            background-color: #f0f0f0;
            color: #333333;
            border: 2px solid #e0e0e0;
            border-radius: 4px;
            padding: 8px 12px;
            font-weight: normal;
            min-height: 32px;
        }
        
        /* 文件组按钮样式 */
        QGroupBox[title="文件"] QPushButton:hover {
            background-color: #e8f5e9;
            border: 2px solid #4CAF50;
            color: #2E7D32;
        }
        QGroupBox[title="文件"] QPushButton:pressed {
            background-color: #c8e6c9;
            border: 2px solid #388E3C;
            color: #1B5E20;
        }
        
        /* 图片调整组按钮样式 */
        QGroupBox[title="图片调整"] QPushButton:hover {
            background-color: #e3f2fd;
            border: 2px solid #2196F3;
            color: #1976D2;
        }
        QGroupBox[title="图片调整"] QPushButton:pressed {
            background-color: #bbdefb;
            border: 2px solid #1565C0;
            color: #0D47A1;
        }
        
        /* 图片效果组按钮样式 */
        QGroupBox[title="图片效果"] QPushButton:hover {
            background-color: #f3e5f5;
            border: 2px solid #9C27B0;
            color: #7B1FA2;
        }
        QGroupBox[title="图片效果"] QPushButton:pressed {
            background-color: #e1bee7;
            border: 2px solid #7B1FA2;
            color: #4A148C;
        }
        QLabel {
            color: #333333;
            font-weight: normal;
            margin: 2px 0;
        }
       
        QComboBox {
            border: 1px solid black;
            border-radius: 4px;
            padding: 6px 10px;
            min-height: 32px;
            background-color: white;
            selection-background-color: #e0e0e0;
            selection-color: #333333;
        }
        
        /* 文件组ComboBox样式 */
        QGroupBox[title="文件"] QComboBox:hover {
            border: 2px solid #4CAF50;
        }
        QGroupBox[title="文件"] QComboBox:pressed,
        QGroupBox[title="文件"] QComboBox:open {
            border: 2px solid #388E3C;
            background-color: #e8f5e9;
        }
        
        /* 图片调整组ComboBox样式 */
        QGroupBox[title="图片调整"] QComboBox:hover {
            border: 2px solid #2196F3;
        }
        QGroupBox[title="图片调整"] QComboBox:pressed,
        QGroupBox[title="图片调整"] QComboBox:open {
            border: 2px solid #1565C0;
            background-color: #e3f2fd;
        }
        
        /* 图片效果组ComboBox样式 */
        QGroupBox[title="图片效果"] QComboBox:hover {
            border: 2px solid #9C27B0;
        }
        QGroupBox[title="图片效果"] QComboBox:pressed,
        QGroupBox[title="图片效果"] QComboBox:open {
            border: 2px solid #7B1FA2;
            background-color: #f3e5f5;
        }

        QGroupBox {
            font-weight: normal;
            border-radius: 4px;
            margin-top: 20px;
            padding-top: 16px;
            padding-bottom: 10px;
            background-color: rgba(255, 255, 255, 0.7);
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 6px;
            background-color: #f5f5f5;
            font-size: 10pt;
        }
        QGroupBox[title="文件"] {
            border: 2px solid #4CAF50;
        }
        QGroupBox[title="图片调整"] {
            border: 2px solid #2196F3;
        }
        QGroupBox[title="图片效果"] {
            border: 2px solid #9C27B0;
        }
        QGroupBox[title="文件"]::title {
            color: #4CAF50;
        }
        QGroupBox[title="图片调整"]::title {
            color: #2196F3;
        }
        QGroupBox[title="图片效果"]::title {
            color: #9C27B0;
        }

        QSlider::groove:horizontal {
            border: 1px solid black;
            height: 6px;
            background: #f0f0f0;
            margin: 2px 0;
            border-radius: 3px;
        }
        /* 默认滑块样式 */
        QSlider::handle:horizontal {
            width: 14px;
            height: 14px;
            margin: -5px 0;
            border-radius: 7px;
            border: 1px solid #333333;
        }
        
        /* 缩放滑块样式 */
        #scale_slider::handle:horizontal {
            background: OrangeRed;
        }
        #scale_slider::handle:horizontal:hover {
            background: #FF6347;
            border: 1px solid #FF4500;
        }
        #scale_slider::handle:horizontal:pressed {
            background: #B22222;
            border: 1px solid #8B0000;
        }
        
        /* 亮度滑块样式 */
        #brightness_slider::handle:horizontal {
            background: #FFD700; /* 金色 */
        }
        #brightness_slider::handle:horizontal:hover {
            background: #FFFF00;
            border: 1px solid #FFD700;
        }
        #brightness_slider::handle:horizontal:pressed {
            background: #DAA520;
            border: 1px solid #B8860B;
        }
        
        /* 饱和度滑块样式 */
        #saturation_slider::handle:horizontal {
            background: #32CD32; /* 绿色 */
        }
        #saturation_slider::handle:horizontal:hover {
            background: #00FF00;
            border: 1px solid #32CD32;
        }
        #saturation_slider::handle:horizontal:pressed {
            background: #228B22;
            border: 1px solid #006400;
        }
        
        /* 对比度滑块样式 */
        #contrast_slider::handle:horizontal {
            background: #1E90FF; /* 蓝色 */
        }
        #contrast_slider::handle:horizontal:hover {
            background: #00BFFF;
            border: 1px solid #1E90FF;
        }
        #contrast_slider::handle:horizontal:pressed {
            background: #0000CD;
            border: 1px solid #00008B;
        }
        /* 百分比标签样式 */
        #scale_value_label, #brightness_value_label, #saturation_value_label, #contrast_value_label {
            padding: 2px 4px;
            border-radius: 4px;
            color: #333333;
        }
        #scale_value_label {
            border: 2px solid OrangeRed;
        }
        #brightness_value_label {
            border: 2px solid #FFD700;
        }
        #saturation_value_label {
            border: 2px solid #32CD32;
        }
        #contrast_value_label {
            border: 2px solid #1E90FF;
        }

        QScrollArea {
            border-radius: 4px;
            background-color: #fafafa;
        }
        QScrollBar:vertical {
            background: #f5f5f5;
            width: 8px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #c0c0c0;
            min-height: 30px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #a0a0a0;
        }
        QScrollBar::add-line:vertical {
            height: 0px;
        }
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        QScrollBar:horizontal {
            background: #f5f5f5;
            height: 8px;
            margin: 0px;
            border-radius: 4px;
        }
        QScrollBar::handle:horizontal {
            background: #c0c0c0;
            min-width: 30px;
            border-radius: 4px;
        }
        QScrollBar::handle:horizontal:hover { 
            background: #a0a0a0; 
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 2px;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
        """
        self.parent.setStyleSheet(style)
        
        # 设置字体
        font = QFont("Segoe UI", 9)  # Windows 10 默认字体
        self.parent.setFont(font)
    