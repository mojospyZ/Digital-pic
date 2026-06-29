import sys
import os
from PyQt6.QtWidgets import QApplication
from image_processor import ImageProcessor

def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于 PyInstaller 打包后的环境 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()