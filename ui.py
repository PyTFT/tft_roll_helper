from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QSizePolicy, QHeaderView, QTableWidgetItem
from PySide6.QtCore import Qt, QFile
from PySide6.QtUiTools import QUiLoader
# from PySide6.QtGui import QShortcut, QKeySequence
from roll import roll_chess, roll_anomalie
from global_hotkeys import register_hotkeys, start_checking_hotkeys, stop_checking_hotkeys
import threading
from roll import wait

class RollWindow:
    def __init__(self):

        # 加载 UI 文件
        loader = QUiLoader()
        ui_file = QFile('ui/roll.ui')
        ui_file.open(QFile.ReadOnly)
        self.window = loader.load(ui_file)
        ui_file.close()
        self.window.move(0, 0)

        self.roll_status = False

        # 设置窗口属性
        self.window.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.window.setWindowFlags(self.window.windowFlags() | Qt.WindowStaysOnTopHint)

        # 设置样式表
        self.window.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #a0d8ef;  /* 设置选中行的背景色 */
                color: black;  /* 设置选中行的文字颜色 */
            }
            QListWidget::item:selected {
                background-color: #a0d8ef;
                color: black;
            }
        """)

        # 填充异变列表
        yibian = ['冰霜触摸', '分享你的能量', '剔除弱者', '力量训练', '势不可挡', '千刀斩', '即兴发挥', '友谊之力', '双刀流', '双狼佣兽',
                  '史莱姆时间', '名片', '地下拳王', '坚不可破', '壁垒', '奥术浩荡', '小我多多', '巨人体型', '微缩化', '恃强凌弱',
                  '恕瑞玛的传承', '慢炖', '护甲山崩', '攻击吸收', '斥力发生器', '星原之准', '星界韵律', '最后机会', '根深蒂固', '法师护甲',
                  '法强吸收', '泰坦打击', '深入敌阵', '渴望能量', '火球', '物理专家', '狂战之怒', '猎头者', '真的会蟹', '石头皮肤',
                  '纳沃利精华', '终极英雄', '终结者', '绝不浪费', '翻盘故事', '荆棘满途', '贪财化身', '超高速', '进入未知', '连杀',
                  '重量级打击手', '镭射眼', '防御专家', '防御型护盾', '隐形', '震撼登场', '魔法专家', '魔法训练', '鹰眼', '龙魂']
        self.window.listWidget.addItems(yibian)

        # 设置列表字体大小
        font = self.window.listWidget.font()
        font.setPointSize(12)
        self.window.listWidget.setFont(font)
        self.window.listWidget_2.setFont(font)

        # 注册全局热键
        bindings = [
            ["shift+s", None, self.stop_roll, False],
        ]
        register_hotkeys(bindings)

        # 连接信号和槽
        self.window.btn_delete.clicked.connect(self.remove_row)
        self.window.btn_clear.clicked.connect(self.clear_table)
        self.window.lineEdit.textChanged.connect(self.filter_list)
        self.window.ybtn_add.clicked.connect(self.add_yitem)
        self.window.ybtn_del.clicked.connect(self.remove_yitem)
        self.window.btn_start.clicked.connect(self.start_roll)
        self.window.btn_stop.clicked.connect(self.stop_roll)

        # 设置按钮点击事件
        for i in range(1, 64):
            button_name = f"pushButton_{i}"
            button = getattr(self.window, button_name, None)
            if button:
                if button.accessibleName():
                    name = button.accessibleName()
                else:
                    name = button.text()
                button.clicked.connect(lambda _, n=name: self.append_row(n))

    def append_row(self, name):
        row_count = self.window.table.rowCount()
        self.window.table.insertRow(row_count)
        name_item = QTableWidgetItem(name)
        name_item.setTextAlignment(Qt.AlignCenter)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        no_item = QTableWidgetItem('9')
        no_item.setTextAlignment(Qt.AlignCenter)
        self.window.table.setItem(row_count, 0, name_item)
        self.window.table.setItem(row_count, 1, no_item)

    def remove_row(self):
        row = self.window.table.currentRow()
        self.window.table.removeRow(row)

    def clear_table(self):
        self.window.table.setRowCount(0)

    def filter_list(self, text):
        for index in range(self.window.listWidget.count()):
            item = self.window.listWidget.item(index)
            if text in item.text():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def add_yitem(self):
        item = self.window.listWidget.currentItem()
        if item:
            self.window.listWidget_2.addItem(item.text())

    def remove_yitem(self):
        item = self.window.listWidget_2.currentItem()
        if item:
            self.window.listWidget_2.takeItem(self.window.listWidget_2.row(item))

    def start_roll(self):
        self.roll_status = True
        self.window.btn_start.setEnabled(False)
        tab_index = self.window.tabWidget.currentIndex()
        start_checking_hotkeys()
        
        match tab_index:
            case 0:
                row_count = self.window.table.rowCount()
                need_chess_dict = {}
                for i in range(row_count):
                    need_chess_dict[self.window.table.item(i, 0).text()] = [0, int(self.window.table.item(i, 1).text())]
                d_n = self.window.spinBox.value()
                interval = self.window.spinBox_2.value()
                roll_chess(d_n, interval, need_chess_dict, self)
            case 1:
                row_count = self.window.listWidget_2.count()
                need_anomalie_list = [self.window.listWidget_2.item(i).text() for i in range(row_count)]
                d_n = self.window.spinBox_3.value()
                interval = self.window.spinBox_4.value()
                roll_anomalie(d_n, interval, need_anomalie_list, self)
        self.window.btn_start.setEnabled(True)
        stop_checking_hotkeys()

    def stop_roll(self):
        self.roll_status = False

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("云顶D牌")
        self.setFixedSize(50, 50)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建按钮
        btn = QPushButton("D")
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.clicked.connect(self.show_roll)
        
        # 添加按钮到布局
        main_layout.addWidget(btn)
        
        # 设置布局到中央部件
        central_widget.setLayout(main_layout)
        self.move(0, 0)

        self.roll = RollWindow()

    def show_roll(self):
        self.roll.window.show()
        self.roll.window.showNormal()
