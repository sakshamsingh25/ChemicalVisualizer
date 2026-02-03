import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFrame, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DesktopVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.setFixedSize(1150, 900) 
        self.setStyleSheet("background-color: #f8fafc;")
        self.raw_data = None
        
        # Main Stacked Widget for Navigation
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)
        
        self.init_home_page()
        self.init_results_page()
        
        # Start at Home Page
        self.central_stack.setCurrentIndex(0)

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        widget.setGraphicsEffect(shadow)

    # --- PAGE 1: HOME PAGE ---
    def init_home_page(self):
        self.home_page = QWidget()
        layout = QVBoxLayout(self.home_page)
        layout.setAlignment(Qt.AlignCenter)
        
        header_frame = QFrame()
        header_frame.setFixedSize(900, 300)
        header_frame.setStyleSheet("background-color: white; border-radius: 20px; border: 1px solid #e2e8f0;")
        self.apply_shadow(header_frame)
        
        h_layout = QVBoxLayout(header_frame)
        h_layout.setContentsMargins(40, 40, 40, 40)
        h_layout.setSpacing(30)

        title = QLabel("🧪 Chemical Equipment Parameter Visualizer")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0f172a;")
        
        btn_row = QHBoxLayout()
        self.upload_btn = QPushButton("📄 SELECT CSV FILE")
        self.upload_btn.setFixedSize(300, 60)
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setStyleSheet("""
            QPushButton { background-color: #f59e0b; color: white; border-radius: 12px; font-weight: bold; font-size: 16px; }
            QPushButton:hover { background-color: #d97706; }
        """)
        self.upload_btn.clicked.connect(self.select_file)

        self.analyze_btn = QPushButton("🚀 RUN ANALYSIS")
        self.analyze_btn.setFixedSize(300, 60)
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; border-radius: 12px; font-weight: bold; font-size: 16px; }
            QPushButton:hover { background-color: #2563eb; }
        """)
        self.analyze_btn.clicked.connect(self.run_analysis)

        btn_row.addStretch()
        btn_row.addWidget(self.upload_btn)
        btn_row.addSpacing(30)
        btn_row.addWidget(self.analyze_btn)
        btn_row.addStretch()

        h_layout.addWidget(title)
        h_layout.addLayout(btn_row)
        layout.addWidget(header_frame)
        self.central_stack.addWidget(self.home_page)

    # --- PAGE 2: RESULTS PAGE ---
    def init_results_page(self):
        self.results_page = QWidget()
        self.results_layout = QVBoxLayout(self.results_page)
        self.results_layout.setContentsMargins(25, 20, 25, 20)
        self.results_layout.setSpacing(15)

        self.back_btn = QPushButton("⬅ BACK TO UPLOAD")
        self.back_btn.setFixedSize(180, 35)
        self.back_btn.setStyleSheet("background-color: #64748b; color: white; border-radius: 8px; font-weight: bold;")
        self.back_btn.clicked.connect(lambda: self.central_stack.setCurrentIndex(0))
        self.results_layout.addWidget(self.back_btn)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(15)
        self.cards = {}
        metrics = [
            ("🔢 TOTAL UNITS", "#3b82f6", "TOTAL UNITS"), 
            ("🕒 AVG PRESSURE", "#f59e0b", "AVG PRESSURE"), 
            ("💧 AVG FLOWRATE", "#8b5cf6", "AVG FLOWRATE"), 
            ("🔥 AVG TEMPERATURE", "#ef4444", "AVG TEMPERATURE"), 
            ("🏥 HEALTH INDEX", "#10b981", "HEALTH INDEX")
        ]
        
        for display_name, color, data_key in metrics:
            card = QFrame()
            card.setStyleSheet(f"background-color: white; border-radius: 12px; border: 1px solid #e2e8f0;")
            card.setFixedHeight(120)
            self.apply_shadow(card)
            cl = QVBoxLayout(card)
            
            l1 = QLabel(display_name)
            l1.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
            l1.setAlignment(Qt.AlignCenter)
            
            l2 = QLabel("0.0")
            l2.setStyleSheet("color: #1e293b; font-size: 28px; font-weight: 900;")
            l2.setAlignment(Qt.AlignCenter)
            
            cl.addWidget(l1)
            cl.addWidget(l2)
            stats_row.addWidget(card)
            self.cards[data_key] = l2
            
        self.results_layout.addLayout(stats_row)

        charts_box = QHBoxLayout()
        self.bar_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        self.line_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        self.frontend_colors = ['#3b82f6', '#ef4444', '#8b5cf6', '#f59e0b', '#10b981', '#06b6d4', '#ec4899']

        for canvas, label in [(self.bar_canvas, "📊 Inventory Volume"), (self.line_canvas, "📈 Distribution Trend")]:
            f = QFrame()
            f.setStyleSheet("background-color: white; border-radius: 15px;")
            self.apply_shadow(f)
            v = QVBoxLayout(f)
            v.addWidget(QLabel(label, font=QFont("Arial", 14, QFont.Bold)))
            v.addWidget(canvas)
            charts_box.addWidget(f)
        self.results_layout.addLayout(charts_box)

        log_frame = QFrame()
        log_frame.setStyleSheet("background-color: white; border-radius: 15px;")
        self.apply_shadow(log_frame)
        lv = QVBoxLayout(log_frame)
        lv.setContentsMargins(20, 15, 20, 15)
        
        history_header = QLabel("🕒 History Management (Audit Trail)")
        history_header.setFont(QFont("Arial", 15, QFont.Bold))
        history_header.setStyleSheet("color: #000000;")
        lv.addWidget(history_header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Batch ID", "Filename", "Date & Time", "Avg Press", "Avg Flow", "Avg Temp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setFixedHeight(220)
        self.table.setStyleSheet("border: none; font-size: 12px; color: #334155;")
        lv.addWidget(self.table)
        self.results_layout.addWidget(log_frame)

        self.central_stack.addWidget(self.results_page)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if path:
            self.file_path = path
            self.upload_btn.setText(f"📄 {path.split('/')[-1]}")

    def run_analysis(self):
        if not hasattr(self, 'file_path'): return
        with open(self.file_path, 'rb') as f:
            try:
                r = requests.post("http://127.0.0.1:8000/api/summary/", files={'file': f})
                if r.status_code == 200:
                    self.raw_data = r.json()
                    self.central_stack.setCurrentIndex(1)
                    self.start_ui_update()
            except Exception as e:
                print(f"Backend Offline: {e}")

    def start_ui_update(self):
        d = self.raw_data
        self.cards["TOTAL UNITS"].setText(str(d.get('total_count', 0)))
        self.cards["AVG PRESSURE"].setText(f"{d.get('avg_pressure', 0.0):.2f} psi")
        self.cards["AVG FLOWRATE"].setText(f"{d.get('avg_flowrate', 0.0):.2f} m³/h")
        self.cards["AVG TEMPERATURE"].setText(f"{d.get('avg_temp', 0.0):.2f} °C")
        self.cards["HEALTH INDEX"].setText("94%" if d.get('avg_temp', 0) < 120 else "78%")

        self.anim_frame = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(35)

    def animate(self):
        dist = self.raw_data.get('type_distribution', {})
        # Keep original keys but clean for plotting
        keys = list(dist.keys())
        target_vals = list(dist.values())
        self.anim_frame += 1
        curr_vals = [ (v * self.anim_frame / 20) for v in target_vals ]

        self.bar_canvas.figure.clear()
        ax1 = self.bar_canvas.figure.add_subplot(111)
        ax1.bar(keys, curr_vals, color=self.frontend_colors[:len(keys)])
        
        # SOLUTION: Rotate labels and adjust layout to prevent collision
        ax1.set_xticklabels(keys, rotation=25, ha='right', fontsize=9)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        self.bar_canvas.figure.subplots_adjust(bottom=0.25) # More space for labels
        self.bar_canvas.draw()

        self.line_canvas.figure.clear()
        ax2 = self.line_canvas.figure.add_subplot(111)
        ax2.plot(keys, curr_vals, marker='o', color='#4f46e5', linewidth=2, markersize=6)
        ax2.fill_between(keys, curr_vals, color='#4f46e5', alpha=0.15)
        
        # SOLUTION: Same rotation logic for the line chart
        ax2.set_xticklabels(keys, rotation=25, ha='right', fontsize=9)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        self.line_canvas.figure.subplots_adjust(bottom=0.25) # More space for labels
        self.line_canvas.draw()

        if self.anim_frame >= 20:
            self.timer.stop()
            self.refresh_history_table()

    def refresh_history_table(self):
        if not self.raw_data or 'history' not in self.raw_data:
            return
        history = self.raw_data['history'][:5]
        self.table.setRowCount(0)
        for i, entry in enumerate(history):
            self.table.insertRow(i)
            raw_date = entry.get('upload_date', '2026-02-03')
            formatted_date = str(raw_date)[:16].replace('T', ' ')
            self.table.setItem(i, 0, QTableWidgetItem(f"#B-00{i+1}"))
            self.table.setItem(i, 1, QTableWidgetItem(entry.get('filename', 'Unknown')))
            self.table.setItem(i, 2, QTableWidgetItem(formatted_date))
            self.table.setItem(i, 3, QTableWidgetItem(f"{entry.get('avg_pressure', 0.0):.1f} psi"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{entry.get('avg_flowrate', 0.0):.1f} m³/h")) 
            self.table.setItem(i, 5, QTableWidgetItem(f"{entry.get('avg_temp', 0.0):.1f} °C"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DesktopVisualizer()
    window.show()
    sys.exit(app.exec_())