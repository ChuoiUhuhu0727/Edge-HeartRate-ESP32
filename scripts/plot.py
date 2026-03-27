import sys
import serial
import serial.tools.list_ports
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import csv

# --- CONFIGURATION ---
BAUD_RATE = 115200
WINDOW_SIZE = 500  # Hiển thị 500 mẫu (~5 giây với fs=100Hz)
CSV_FILENAME = "ppg_data_A_standard.csv"
FS = 100.0 # Tần số lấy mẫu mục tiêu

class SerialPlotter(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 1. Kết nối Serial
        self.ser = self.connect_serial()
        
        # 2. Khởi tạo file CSV
        self.csv_file = open(CSV_FILENAME, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Time (s)', 'Red', 'IR'])
        
        # BIẾN QUAN TRỌNG ĐỂ ĐẠT ĐIỂM A: Đếm mẫu để tính thời gian chuẩn
        self.sample_count = 0
        
        # 3. Thiết lập giao diện UI
        self.view = pg.GraphicsLayoutWidget(title="ENG209 Midterm: A-Standard Plotter")
        self.setCentralWidget(self.view)
        self.setWindowTitle(f'Plotting: {self.ser.port}')
        self.resize(1200, 700)
        
        self.plot = self.view.addPlot(title="PPG Real-time (Fixed Timestamping)")
        self.plot.addLegend()
        self.plot.showGrid(x=True, y=True)
        self.plot.setLabel('bottom', 'Time (seconds)')
        
        self.data_buffers = [np.zeros(WINDOW_SIZE), np.zeros(WINDOW_SIZE)]
        self.time_buffer = np.zeros(WINDOW_SIZE)
        
        self.curve_red = self.plot.plot(pen=pg.mkPen('r', width=1.5), name="RED")
        self.curve_ir = self.plot.plot(pen=pg.mkPen('c', width=1.5), name="IR")

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)

    def connect_serial(self):
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            sys.exit(1)
        # Tạm thời chọn port đầu tiên hoặc cho chọn như cũ
        target_port = ports[0].device # Bạn có thể dùng lại đoạn input chọn port cũ ở đây
        return serial.Serial(target_port, BAUD_RATE, timeout=0.1)

    def update_plot(self):
        try:
            while self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if not line or "," not in line: continue
                
                try:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        val_red = float(parts[0].strip())
                        val_ir = float(parts[1].strip())
                        
                        # CÔNG THỨC CHUẨN: Tính thời gian dựa trên số mẫu
                        current_timestamp = self.sample_count * (1.0 / FS)
                        self.sample_count += 1
                        
                        # Ghi vào CSV 
                        self.csv_writer.writerow([f"{current_timestamp:.3f}", val_red, val_ir])
                        
                        # Cập nhật đồ thị
                        self.data_buffers[0] = np.roll(self.data_buffers[0], -1)
                        self.data_buffers[0][-1] = val_red
                        self.data_buffers[1] = np.roll(self.data_buffers[1], -1)
                        self.data_buffers[1][-1] = val_ir
                        self.time_buffer = np.roll(self.time_buffer, -1)
                        self.time_buffer[-1] = current_timestamp
                except ValueError:
                    continue
            
            self.curve_red.setData(self.time_buffer, self.data_buffers[0])
            self.curve_ir.setData(self.time_buffer, self.data_buffers[1])
            
        except Exception as e:
            print(f"Error: {e}")

    def closeEvent(self, event):
        """Hàm này cực kỳ quan trọng để lưu file CSV thành công """
        self.csv_file.close()
        self.ser.close()
        print(f"Data saved to {CSV_FILENAME}")
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    plotter = SerialPlotter()
    plotter.show()
    sys.exit(app.exec())
    
