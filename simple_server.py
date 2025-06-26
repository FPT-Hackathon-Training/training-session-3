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
TOPIC_SERVER_COMMAND = "dattt/training/agv/{vehicle_id}/command"
# Server gửi thông báo đăng ký thành công đến xe
TOPIC_SERVER_REGISTRATION = "dattt/training/agv/{vehicle_id}/registration"

# Server - Subscriber
# Xe gửi cập nhật trạng thái lên server
TOPIC_CLIENT_STATUS = "dattt/training/agv/{}/status"
# Xe gửi yêu cầu đăng ký
TOPIC_CLIENT_REGISTER = "dattt/training/agv/register"

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
    mqtt_client.subscribe(TOPIC_CLIENT_STATUS.format("+"))  # Đăng ký nhận tất cả trạng thái từ các xe
    mqtt_client.subscribe(TOPIC_CLIENT_REGISTER)

# Hàm callback khi nhận được tin nhắn từ broker
def on_message(mqtt_client, userdata, msg):
    payload = json.loads(msg.payload.decode())

    if msg.topic.endswith("status"):
        vehicle_id = payload['vehicle_id']
        if vehicle_manager.vehicles[vehicle_id].is_at_destination():
            vehicle_manager.vehicles[vehicle_id].change_status("finished")
        else:
            vehicle_manager.vehicles[vehicle_id].change_status(payload['status'])
        handle_update_status()

    elif msg.topic == TOPIC_CLIENT_REGISTER:
        try:
            print(f"Nhận yêu cầu đăng ký từ xe {payload['vehicle_id']}: {payload}")
            # Xử lý yêu cầu đăng ký
            if handle_register(payload['vehicle_id'], payload['source'], payload['destination']):
                # Gửi thông báo đăng ký thành công đến xe
                registration_payload = {
                    "vehicle_id": payload['vehicle_id'],
                    "status": "success",
                }
                mqtt_client.publish(TOPIC_SERVER_REGISTRATION.format(vehicle_id=payload['vehicle_id']), json.dumps(registration_payload))
        except json.JSONDecodeError:
            print("Lỗi phân tích cú pháp JSON cho lệnh đăng ký.")

# Hàm xử lý đăng ký xe mới
def handle_register(vehicle_id, source, destination):
    """Xử lý đăng ký xe mới"""
    vehicle = Vehicle(vehicle_id=vehicle_id,
                          source=int(source),
                          destination=int(destination),
                          map_client=map_client)
    try:
        vehicle_manager.add_vehicle(vehicle_id, vehicle)
        time.sleep(1)
        return True
    except ValueError:
        return False
    
def handle_update_status():
    # Kiểm tra xem các xe đã sẵn sàng chưa
    if not vehicle_manager.vehicles_ready:
        return
    
    # Các xe đã về đích chưa
    if vehicle_manager.is_complete():
        print("Tất cả xe đã đến đích.")
        return
    
    if vehicle_manager.has_moving_vehicle():
        return

    # Xử lý điều khiển xe
    vehicle_manager.schedule_vehicles()

    for vehicle_id, vehicle in vehicle_manager.vehicles.items():
        if vehicle.status == "finished":
            continue

        elif vehicle.status == "moving":
            command_payload = {
                "vehicle_id": vehicle_id,
                "command": "move",
                "is_moving": 1,
                "current_step": vehicle.get_current_step(),
                "current_node": vehicle.get_current_node(),
            }
            mqtt_client.publish(TOPIC_SERVER_COMMAND.format(vehicle_id=vehicle_id), json.dumps(command_payload))

        elif vehicle.status == "waiting":
            command_payload = {
                "vehicle_id": vehicle_id,
                "command": "wait",
                "is_moving": 0,
                "current_step": vehicle.get_current_step(),
                "current_node": vehicle.get_current_node(),
            }
            mqtt_client.publish(TOPIC_SERVER_COMMAND.format(vehicle_id=vehicle_id), json.dumps(command_payload))


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

# while not vehicle_manager.vehicles_ready:
#     time.sleep(1)  # Chờ cho đến khi có đủ xe 2 đăng ký
        
while True:
    try:
        # for vehicle_id, vehicle in vehicle_manager.vehicles.items():
        #     # Gửi lệnh điều khiển đến xe
        #     command_payload = {
        #         "vehicle_id": vehicle_id,
        #         "command": "move",
        #         "source": vehicle.source,
        #         "destination": vehicle.destination,
        #     }
        #     mqtt_client.publish(TOPIC_SERVER_COMMAND.format(vehicle_id=vehicle_id), json.dumps(command_payload))
        #     print(f"Gửi lệnh di chuyển đến xe {vehicle_id}.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nĐang dừng server...")
        break
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

mqtt_client.loop_stop()
mqtt_client.disconnect()
print("Server đã dừng.")