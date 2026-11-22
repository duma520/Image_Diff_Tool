import sys
import os
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QMessageBox, QSizePolicy,
                             QFileDialog, QSplitter)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QIcon
from PyQt5.QtCore import Qt, QSize, QSettings, QPoint, QRect, QTranslator, QLibraryInfo, QByteArray, QBuffer, QIODevice
import cv2
import numpy as np
from PIL import Image, ImageChops
import io

class ImageDiffTool(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化设置
        self.settings = QSettings("ImageDiffTool", "ImageDiffTool")
        self.db_conn = sqlite3.connect('image_diff_tool.db')
        self.init_db()
        
        # 初始化UI
        self.init_ui()
        
        # 加载上次的设置
        self.load_settings()
        
        # 检查并设置图标
        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
    
    def init_db(self):
        cursor = self.db_conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image1 BLOB,
                image2 BLOB,
                diff_image BLOB,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.db_conn.commit()
    
    def init_ui(self):
        # 主窗口设置
        self.setWindowTitle("图像差异比较工具")
        self.setMinimumSize(800, 600)
        
        # 主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主布局
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 顶部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        self.paste_btn = QPushButton("粘贴图像 (Ctrl+V)")
        self.paste_btn.clicked.connect(self.paste_image)
        self.paste_btn.setShortcut("Ctrl+V")
        button_layout.addWidget(self.paste_btn)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_images)
        button_layout.addWidget(self.clear_btn)
        
        self.save_btn = QPushButton("保存结果")
        self.save_btn.clicked.connect(self.save_result)
        button_layout.addWidget(self.save_btn)
        
        self.compare_btn = QPushButton("比较差异")
        self.compare_btn.clicked.connect(self.compare_images)
        button_layout.addWidget(self.compare_btn)
        
        main_layout.addLayout(button_layout)
        
        # 图像显示区域
        image_splitter = QSplitter(Qt.Horizontal)
        
        # 截图一区
        self.image1_area = QScrollArea()
        self.image1_area.setWidgetResizable(True)
        self.image1_label = QLabel()
        self.image1_label.setAlignment(Qt.AlignCenter)
        self.image1_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image1_area.setWidget(self.image1_label)
        image_splitter.addWidget(self.image1_area)
        
        # 截图二区
        self.image2_area = QScrollArea()
        self.image2_area.setWidgetResizable(True)
        self.image2_label = QLabel()
        self.image2_label.setAlignment(Qt.AlignCenter)
        self.image2_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image2_area.setWidget(self.image2_label)
        image_splitter.addWidget(self.image2_area)
        
        # 差异结果区
        self.diff_area = QScrollArea()
        self.diff_area.setWidgetResizable(True)
        self.diff_label = QLabel()
        self.diff_label.setAlignment(Qt.AlignCenter)
        self.diff_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.diff_area.setWidget(self.diff_label)
        image_splitter.addWidget(self.diff_area)
        
        image_splitter.setSizes([300, 300, 300])
        main_layout.addWidget(image_splitter)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
        # 初始化图像变量
        self.image1 = None
        self.image2 = None
        self.diff_image = None
    
    def load_settings(self):
        # 窗口大小和位置
        size = self.settings.value("window/size", QSize(1000, 700))
        self.resize(size)
        
        pos = self.settings.value("window/position", QPoint(100, 100))
        self.move(pos)
        
        # 分割器位置
        splitter_sizes = self.settings.value("splitter/sizes", [300, 300, 300])
        if splitter_sizes:
            self.centralWidget().findChild(QSplitter).setSizes([int(s) for s in splitter_sizes])
    
    def save_settings(self):
        # 窗口大小和位置
        self.settings.setValue("window/size", self.size())
        self.settings.setValue("window/position", self.pos())
        
        # 分割器位置
        splitter = self.centralWidget().findChild(QSplitter)
        if splitter:
            self.settings.setValue("splitter/sizes", splitter.sizes())
    
    def closeEvent(self, event):
        self.save_settings()
        self.db_conn.close()
        super().closeEvent(event)
    
    def paste_image(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasImage():
            image = clipboard.image()
            self.process_pasted_image(image)
        elif mime_data.hasUrls():
            # 处理文件路径
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    image = QImage(file_path)
                    self.process_pasted_image(image)
                    break
        else:
            QMessageBox.information(self, "提示", "剪贴板中没有找到图像")
    
    def process_pasted_image(self, image):
        if self.image1 is None:
            self.image1 = image
            self.update_image_display(self.image1_label, self.image1)
            self.status_bar.showMessage("已粘贴第一张图像")
        elif self.image2 is None:
            self.image2 = image
            self.update_image_display(self.image2_label, self.image2)
            self.status_bar.showMessage("已粘贴第二张图像")
        else:
            reply = QMessageBox.question(self, "确认", 
                                       "已经有两张图像了，是否替换第一张图像?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.image1 = image
                self.update_image_display(self.image1_label, self.image1)
                self.status_bar.showMessage("已替换第一张图像")
            elif reply == QMessageBox.No:
                self.image2 = image
                self.update_image_display(self.image2_label, self.image2)
                self.status_bar.showMessage("已替换第二张图像")
    
    def update_image_display(self, label, image):
        if image is None:
            label.clear()
            return
        
        # 缩放图像以适应显示区域
        scroll_area = label.parent().parent()  # label -> viewport -> scroll_area
        size = scroll_area.size()
        w, h = size.width() - 10, size.height() - 10  # 留一些边距
        
        scaled_image = image.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(QPixmap.fromImage(scaled_image))
        label.adjustSize()
    
    def clear_images(self):
        self.image1 = None
        self.image2 = None
        self.diff_image = None
        self.image1_label.clear()
        self.image2_label.clear()
        self.diff_label.clear()
        self.status_bar.showMessage("已清除所有图像")
    
    def save_result(self):
        if self.diff_image is None:
            QMessageBox.warning(self, "警告", "没有可保存的差异结果")
            return
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存差异图像", "", 
            "PNG图像 (*.png);;JPEG图像 (*.jpg *.jpeg);;位图 (*.bmp)", 
            options=options)
        
        if file_path:
            self.diff_image.save(file_path)
            self.status_bar.showMessage(f"差异图像已保存到: {file_path}")
            
            # 保存到数据库
            try:
                cursor = self.db_conn.cursor()
                
                # 将图像转换为字节
                ba1 = QByteArray()
                buffer1 = QBuffer(ba1)
                buffer1.open(QIODevice.WriteOnly)
                self.image1.save(buffer1, "PNG") if self.image1 else None
                
                ba2 = QByteArray()
                buffer2 = QBuffer(ba2)
                buffer2.open(QIODevice.WriteOnly)
                self.image2.save(buffer2, "PNG") if self.image2 else None
                
                ba_diff = QByteArray()
                buffer_diff = QBuffer(ba_diff)
                buffer_diff.open(QIODevice.WriteOnly)
                self.diff_image.save(buffer_diff, "PNG")
                
                cursor.execute('''
                    INSERT INTO image_pairs (image1, image2, diff_image)
                    VALUES (?, ?, ?)
                ''', (ba1.data(), ba2.data(), ba_diff.data()))
                self.db_conn.commit()
                
                self.status_bar.showMessage(f"差异图像已保存到数据库和文件: {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "数据库错误", f"保存到数据库时出错: {str(e)}")
    
    def compare_images(self):
        if self.image1 is None:
            QMessageBox.warning(self, "警告", "请至少粘贴一张图像")
            return
        
        self.status_bar.showMessage("正在比较图像...")
        QApplication.processEvents()  # 更新UI
        
        try:
            if self.image2 is None:
                # 单图模式 - 尝试在图像内找到两个相似区域进行比较
                self.diff_image = self.compare_single_image()
            else:
                # 双图模式 - 比较两个图像
                self.diff_image = self.compare_two_images()
            
            if self.diff_image:
                self.update_image_display(self.diff_label, self.diff_image)
                self.status_bar.showMessage("图像比较完成")
            else:
                self.status_bar.showMessage("无法比较图像")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"比较图像时出错: {str(e)}")
            self.status_bar.showMessage("比较图像时出错")
    
    def compare_two_images(self):
        # 将QImage转换为PIL Image
        pil_image1 = self.qimage_to_pil(self.image1)
        pil_image2 = self.qimage_to_pil(self.image2)
        
        # 调整图像大小使其相同
        width = min(pil_image1.width, pil_image2.width)
        height = min(pil_image1.height, pil_image2.height)
        pil_image1 = pil_image1.resize((width, height))
        pil_image2 = pil_image2.resize((width, height))
        
        # 计算差异
        diff = ImageChops.difference(pil_image1, pil_image2)
        
        # 转换为灰度并增强差异
        diff = diff.convert("L")
        diff = diff.point(lambda x: 0 if x < 25 else 255)  # 阈值处理
        
        # 在原始图像上绘制差异
        result = pil_image1.copy()
        mask = diff.convert("1")
        highlight = Image.new("RGBA", result.size, (255, 0, 0, 128))
        result.paste(highlight, (0, 0), mask)
        
        return self.pil_to_qimage(result)
    
    def compare_single_image(self):
        # 将QImage转换为OpenCV格式
        cv_image = self.qimage_to_cv(self.image1)
        
        # 转换为灰度
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # 使用ORB检测特征点
        orb = cv2.ORB_create()
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        
        if len(keypoints) < 10:
            QMessageBox.warning(self, "警告", "无法在图像中找到足够的特征点")
            return None
        
        # 使用特征点匹配找到相似区域
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(descriptors, descriptors)
        
        # 过滤掉自匹配
        matches = [m for m in matches if m.queryIdx != m.trainIdx]
        
        if len(matches) < 5:
            QMessageBox.warning(self, "警告", "无法在图像中找到足够的相似区域")
            return None
        
        # 获取最佳匹配对
        matches = sorted(matches, key=lambda x: x.distance)
        best_match = matches[0]
        
        # 获取关键点坐标
        kp1 = keypoints[best_match.queryIdx]
        kp2 = keypoints[best_match.trainIdx]
        
        # 定义区域大小
        size = 100  # 区域大小
        x1, y1 = int(kp1.pt[0] - size/2), int(kp1.pt[1] - size/2)
        x2, y2 = int(kp2.pt[0] - size/2), int(kp2.pt[1] - size/2)
        
        # 确保区域在图像范围内
        h, w = gray.shape
        x1 = max(0, min(x1, w - size))
        y1 = max(0, min(y1, h - size))
        x2 = max(0, min(x2, w - size))
        y2 = max(0, min(y2, h - size))
        
        # 提取两个区域
        region1 = cv_image[y1:y1+size, x1:x1+size]
        region2 = cv_image[y2:y2+size, x2:x2+size]
        
        # 比较两个区域
        diff = cv2.absdiff(region1, region2)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(diff_gray, 25, 255, cv2.THRESH_BINARY)
        
        # 在原始图像上绘制差异
        result = cv_image.copy()
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # 绘制区域1的矩形
        cv2.rectangle(result, (x1, y1), (x1+size, y1+size), (0, 255, 0), 2)
        # 绘制区域2的矩形
        cv2.rectangle(result, (x2, y2), (x2+size, y2+size), (0, 255, 255), 2)
        # 绘制差异轮廓
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(result, (x1+x, y1+y), (x1+x+w, y1+y+h), (0, 0, 255), 1)
            cv2.rectangle(result, (x2+x, y2+y), (x2+x+w, y2+y+h), (0, 0, 255), 1)
        
        return self.cv_to_qimage(result)
    
    def qimage_to_pil(self, qimage):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        qimage.save(buffer, "PNG")
        pil_image = Image.open(io.BytesIO(buffer.data()))
        buffer.close()
        return pil_image
    
    def pil_to_qimage(self, pil_image):
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        qimage = QImage()
        qimage.loadFromData(buffer.getvalue())
        return qimage
    
    def qimage_to_cv(self, qimage):
        qimage = qimage.convertToFormat(QImage.Format_RGB888)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(qimage.byteCount())
        arr = np.array(ptr).reshape(height, width, 3)  # 3 for RGB
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    
    def cv_to_qimage(self, cv_image):
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        height, width, channel = cv_image.shape
        bytes_per_line = 3 * width
        qimage = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return qimage.copy()  # 避免数据被释放的问题
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 更新图像显示以适应新的大小
        if self.image1:
            self.update_image_display(self.image1_label, self.image1)
        if self.image2:
            self.update_image_display(self.image2_label, self.image2)
        if self.diff_image:
            self.update_image_display(self.diff_label, self.diff_image)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置中文语言
    translator = QTranslator()
    if translator.load("qt_zh_CN.qm", QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
        app.installTranslator(translator)
    
    window = ImageDiffTool()
    window.show()
    sys.exit(app.exec_())