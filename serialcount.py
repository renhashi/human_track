import time
import serial

#シリアルポートを開放する
def serial_open():
    global serial_port
    serial_port = serial.Serial(
        port="/dev/ttyTHS0",
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
    )
    
def serial_close():
    global serial_port
    serial_port.close()

#シリアル通信する
#マイナスの値が入ったときに通信は行えるのか？？
def serial_send(to_right, to_left, to_upper, to_lower, stay_num_Ri, stay_num_Up, reset_count_lr, reset_count_ud):
    msg = 'XX:'
    msg += format(to_right, '02X')
    msg += format(to_left, '02X')
    msg += format(to_upper, '02X')
    msg += format(to_lower, '02X')
    msg += format(stay_num_Ri, '02X')
    msg += format(stay_num_Up, '02X')
    msg += format(reset_count_lr, '02X')
    msg += format(reset_count_ud, '02X')
    #msg += format(-10, '02X')
    for i in range(1):
        msg += format(0, '02X')
    print(msg)
    #time.sleep(3)
    serial_port.write(msg.encode())
    
def serial_send_2data(to_in, to_out):
    msg = 'XX:'
    msg += format(to_in, '02X')
    msg += format(to_out, '02X')
    #msg += format(-10, '02X')
    for i in range(7):
        msg += format(0, '02X')
    print(msg)
    #time.sleep(3)
    serial_port.write(msg.encode())
    
def serial_send_4data(to_right, to_left, to_upper, to_lower):
    msg = 'XX:'
    msg += format(to_right, '02X')
    msg += format(to_left, '02X')
    msg += format(to_upper, '02X')
    msg += format(to_lower, '02X')
    #msg += format(-10, '02X')
    for i in range(5):
        msg += format(0, '02X')
    print(msg)
    #time.sleep(3)
    serial_port.write(msg.encode())
    
    
def send_action():
    msg = 'XX:00'
    print(msg)
    serial_port.write(msg.encode())

def send_data_create(data):
    msg = 'XX:'
    num = int(data)
    msg += format(data, '02X')
    print(msg)
    serial_port.write(msg.encode())

def send_data_flash(data):
    msg = 'PX:'
    num = str(data)
    for i in range(8):
        msg += num
        #msg += format(num, '02X')
    print(msg)
    serial_port.write(msg.encode())
