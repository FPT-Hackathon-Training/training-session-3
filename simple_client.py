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
TOPIC_SERVER_COMMAND = "dattt/training/agv/{vehicle_id}/command"
# Server gửi thông báo đăng ký thành công đến xe
TOPIC_SERVER_REGISTRATION = "dattt/training/agv/{vehicle_id}/registration"

# Client - Publisher
# Xe gửi cập nhật trạng thái lên server
TOPIC_CLIENT_STATUS = "dattt/training/agv/{vehicle_id}/status"
# Xe gửi yêu cầu đăng ký
TOPIC_CLIENT_REGISTER = "dattt/training/agv/register"

# Hàm callback khi kết nối đến broker thành công
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC_SERVER_COMMAND.format(vehicle_id=VEHICLE_ID))
    client.subscribe(TOPIC_SERVER_REGISTRATION.format(vehicle_id=VEHICLE_ID))

# Hàm callback khi nhận được tin nhắn từ broker
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    
    if msg.topic.endswith("registration"):
        print(f"ĐĂNG KÝ THÀNH CÔNG")
        time.sleep(1)
        # Gửi trạng thái ban đầu của xe
        status_payload = {
            "vehicle_id": VEHICLE_ID,
            "status": "waiting",
            "current_step": 0,
        }
        client.publish(TOPIC_CLIENT_STATUS.format(vehicle_id=VEHICLE_ID), json.dumps(status_payload))
        
    elif msg.topic == TOPIC_SERVER_COMMAND.format(vehicle_id=payload['vehicle_id']):
        # Xử lý lệnh điều khiển từ server
        if payload['command'] == "move":
            print("Xe {} di chuyển đến {}".format(payload['vehicle_id'], payload['current_node']))
            time.sleep(2)
            status_payload = {
                "vehicle_id": VEHICLE_ID,
                "status": "waiting",
                "current_step": payload['current_step'],
            }
            client.publish(TOPIC_CLIENT_STATUS.format(vehicle_id=VEHICLE_ID), json.dumps(status_payload))
        
        elif payload['command'] == "wait":
            print("Xe {} đang chờ tại {}".format(payload['vehicle_id'], payload['current_node']))
            time.sleep(1)
            status_payload = {
                "vehicle_id": VEHICLE_ID,
                "status": "waiting",
                "current_step": payload['current_step'],
            }
            client.publish(TOPIC_CLIENT_STATUS.format(vehicle_id=VEHICLE_ID), json.dumps(status_payload))
        # time.sleep(1)  # Giả lập thời gian xử lý lệnh
        # command_payload = {
        #     "vehicle_id": payload['vehicle_id'],
        #     "status": "executed",
        #     "command": "move",
        # }
        # client.publish(TOPIC_CLIENT_STATUS.format(vehicle_id=payload['vehicle_id']), json.dumps(command_payload))
        # print(f"Đã gửi trạng thái lệnh: {command_payload}")

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
register_payload = {
            "vehicle_id": VEHICLE_ID,
            "status": "ready",
            "source": SOURCE,
            "destination": DESTINATION,
        }
client.publish(TOPIC_CLIENT_REGISTER, json.dumps(register_payload))

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
