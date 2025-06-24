import paho.mqtt.client as mqtt
import time
import json
from vehicle_manager import VehicleManager
from vehicle import Vehicle
from map_client import MapClient
from rich.console import Console

# Cấu hình MQTT
BROKER_ADDRESS = "nozomi.proxy.rlwy.net"
BROKER_PORT = 32067

# Server - Publisher
# Server gửi lệnh điều khiển đến xe
TOPIC_SERVER_COMMAND = "training/agv/{vehicle_id}/command"
# Server gửi thông báo đăng ký thành công đến xe
TOPIC_SERVER_REGISTRATION = "training/agv/{vehicle_id}/registration"

# Server - Subscriber
# Xe gửi cập nhật trạng thái lên server
TOPIC_CLIENT_STATUS = "training/agv/+/status"
# Xe gửi yêu cầu đăng ký
TOPIC_CLIENT_REGISTER = "training/agv/register"

# Đối tượng quản lý xe
vehicle_manager = VehicleManager()
console = Console()

# Tải bản đồ
map_client = MapClient()
map_client.fetch_maps(console)
if not map_client.maps:
    print("Không có bản đồ nào được tải. Vui lòng kiểm tra kết nối hoặc dữ liệu bản đồ.")
    exit(1)

# Hàm callback khi kết nối đến broker thành công
def on_connect(mqtt_client, userdata, flags, rc):
    mqtt_client.subscribe(TOPIC_CLIENT_STATUS)
    mqtt_client.subscribe(TOPIC_CLIENT_REGISTER)

# Hàm callback khi nhận được tin nhắn từ broker
def on_message(mqtt_client, userdata, msg):
    if msg.topic == TOPIC_CLIENT_STATUS:
        try:
            payload = json.loads(msg.payload.decode())
            print(payload)
        except json.JSONDecodeError:
            print("Lỗi phân tích cú pháp JSON cho trạng thái xe.")
    elif msg.topic == TOPIC_CLIENT_REGISTER:
        try:
            payload = json.loads(msg.payload.decode())
            if handle_register(payload['vehicle_id'], payload['source'], payload['destination']):
                # Gửi thông báo đăng ký thành công
                register_payload = {
                    "vehicle_id": payload['vehicle_id'],
                    "status": "registered",
                }

                print(TOPIC_SERVER_REGISTRATION.format(vehicle_id=payload['vehicle_id']))
                mqtt_client.publish(TOPIC_SERVER_REGISTRATION.format(vehicle_id=payload['vehicle_id']), json.dumps(register_payload))
                print(f"Đăng ký thành công cho xe {payload['vehicle_id']}.")
        except json.JSONDecodeError:
            print("Lỗi phân tích cú pháp JSON cho lệnh đăng ký.")

# Hàm xử lý đăng ký xe mới
def handle_register(vehicle_id, source, destination):
    """Xử lý đăng ký xe mới"""
    if vehicle_id not in vehicle_manager.vehicles:
        vehicle = Vehicle(vehicle_id=vehicle_id,
                          source=int(source),
                          destination=int(destination),
                          map_client=map_client)
        vehicle_manager.add_vehicle(vehicle_id, vehicle)
        return True
    else:
        print(f"Xe {vehicle_id} đã được đăng ký trước đó.")
        return False



# Khởi tạo kết nối MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
try:
    mqtt_client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
except Exception as e:
    print(f"Không thể kết nối đến MQTT Broker: {e}")
    exit(1)
mqtt_client.loop_start()

while not vehicle_manager.vehicles_ready:
    time.sleep(1)  # Chờ cho đến khi có đủ xe đăng ký

# Kiểm tra va chạm tiềm năng
# if not vehicle_manager.collision_detected:
    # Instruct vehicles to start moving


print("Server đã dừng.")
mqtt_client.loop_stop()
mqtt_client.disconnect()

