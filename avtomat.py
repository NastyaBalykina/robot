import time
import threading
import paho.mqtt.client as mqtt
import math

def angle(x,y):
    return math.atan(x/y)

class Robot:
    def __init__(self):
        self.state = "On_station"
        self.x = 0.0   #Позиция робота
        self.y = 0.0
        self.angle = 0.0
        self.order_place = 0
        self.target_angle = 0.0 #Позиция цели
        self.target_x = 0.0
        self.target_y = 0.0
        self.station_x = 0.0    #Позиция станции
        self.station_y = 0.0
        self.station_angle = 0.0
        self.pouring_state = None
        self.mqtt_client = None #MQTT
        self.stop_thread = False

    def mqtt_thread(self):
        while not self.stop_thread:
            def on_connect(client, userdata, flags, rc):
                print("MQTT Connected with result code " + str(rc))
                client.subscribe("camera")
                client.subscribe("tgbot")
                client.subscribe("pivo_station")

            def on_message(client, userdata, msg):
                topic = msg.topic
                if topic == "tgbot":
                    self.order_place = int(msg)
                elif topic == "camera":
                    self.station_x, self.station_y = map(float, msg.payload.decode().split(","))
                    self.x, self.y = map(float, msg.payload.decode().split(","))
                    if self.state == "Bring_order":
                        self.target_x, self.target_y = map(float, msg.payload.decode().split(","))
                elif topic == "pivo_station":
                    self.pouring_state = "nalito"

            if self.mqtt_client is None:
                self.mqtt_client = mqtt.Client()
                self.mqtt_client.on_connect = on_connect
                self.mqtt_client.on_message = on_message
                self.mqtt_client.connect("localhost", 1883, 60)
                self.mqtt_client.loop_start()
                time.sleep(1)

    def work_thread(self):
        order_place = None
        while not self.stop_thread:
            if self.state == "On_station":
                if self.order_place != 0:
                    self.state = "Get_order"
        
            elif self.state == "Get_order":
                order_place = self.order_place
                if self.pouring_state == "nalito":
                    self.state = "Bring_order"
                    self.pouring_state = None
            elif self.state == "Bring_order":
                self.move_to_customer(order_place)
                order_place = None
            elif self.state == "Goto_station":
                self.move_to_station()
                self.state = "On_station"

    def start_mqtt_thread(self):
        threading.Thread(target=self.mqtt_thread, daemon=True).start()

    def start_work_thread(self):
        threading.Thread(target=self.work_thread, daemon=True).start()

    def run(self):
        self.start_mqtt_thread()
        self.start_work_thread()
