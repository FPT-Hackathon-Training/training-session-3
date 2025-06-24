import paho.mqtt.client as mqtt
import json
import time
import sys

# Cấu hình MQTT
BROKER_ADDRESS = "nozomi.proxy.rlwy.net"
BROKER_PORT = 32067

# Thông tin client
VEHICLE_ID = sys.argv[1]
SOURCE = sys.argv[2]
DESTINATION = sys.argv[3]

# Client - Subscriber
# Server gửi lệnh điều khiển đến xe
TOPIC_SERVER_COMMAND = "training/agv/{vehicle_id}/command"
# Server gửi thông báo đăng ký thành công đến xe
TOPIC_SERVER_REGISTRATION = "training/agv/d/registration"

# Client - Publisher
# Xe gửi cập nhật trạng thái lên server
TOPIC_CLIENT_STATUS = "training/agv/{vehicle_id}/status"
# Xe gửi yêu cầu đăng ký
TOPIC_CLIENT_REGISTER = "training/agv/register"

# Hàm callback khi kết nối đến broker thành công
def on_connect(client, userdata, flags, rc):
    # Đăng ký chủ đề nhận vị trí xe từ server
    client.subscribe(TOPIC_SERVER_COMMAND.format(vehicle_id=VEHICLE_ID))
    print(TOPIC_SERVER_REGISTRATION.format(vehicle_id=VEHICLE_ID))
    client.subscribe(TOPIC_SERVER_REGISTRATION.format(vehicle_id=str(VEHICLE_ID)))

# Hàm callback khi nhận được tin nhắn từ broker
def on_message(client, userdata, msg):
    print(f"Nhận tin nhắn từ {msg.topic}: {msg.payload.decode()}")

# Khởi tạo MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
try:
    client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
except Exception as e:
    print(f"Không thể kết nối đến MQTT Broker: {e}")
    exit(1)
client.loop_start()

# Gửi yêu cầu đăng ký xe
registration_payload = {
            "vehicle_id": VEHICLE_ID,
            "status": "ready",
            "source": SOURCE,
            "destination": DESTINATION,
        }
client.publish(TOPIC_CLIENT_REGISTER, json.dumps(registration_payload))

while True:
    try:
        # Chờ phản hồi từ server
        time.sleep(1)  # Giả lập thời gian chờ phản hồi
    except KeyboardInterrupt:
        print("\nĐang thoát client...")
        break
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

# Dừng vòng lặp và ngắt kết nối
client.loop_stop()
client.disconnect()
print("Client đã dừng.")