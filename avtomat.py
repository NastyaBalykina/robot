import time
import threading
import paho.mqtt.client as mqtt
import math

def angle(x,y):
    return math.atan(x/y)

def distance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2+(y2-y1)**2)

class Robot:
    def __init__(self):
        self.state = "On_station"
        self.x = None   #Позиция робота
        self.y = None
        self.angle = None
        self.order_place = None
        self.target_angle = None #Позиция цели
        self.target_x = None
        self.target_y = None
        self.station_x = None    #Позиция станции
        self.station_y = None
        self.station_angle = None
        self.pouring_state = None
        self.mqtt_client = None #MQTT
        self.stop_thread = False

    def mqtt_thread(self):
        while not self.stop_thread:
            def on_connect(client, userdata, flags, rc):
                print("MQTT Connected with result code " + str(rc))
                client.subscribe("tgbot")
                client.subscribe("pivo_station")
                client.subscribe("robot")
                client.subscribe("station")
                client.subscribe("target")

            def on_message(client, userdata, msg):
                topic = msg.topic
                if topic == "tgbot":    #получает место заказа
                    self.order_place = int(msg)
                    self.state = "Get_order"
                elif topic == "robot":  #получает координаты робота
                    self.x, self.y = map(float, msg.payload.decode().split(","))
                elif topic == "station":    #получает координаты станции
                    self.station_x, self.station_y = map(float, msg.payload.decode().split(","))
                elif topic == "target": #получает координаты цели
                    self.target_x, self.target_y = map(float, msg.payload.decode().split(","))
                elif topic == "pivo_station":   #
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

    def move_to_customer(self, order_place):
        #выбрать цель в зависимости от значения order_place
        while distance(self.x, self.y, self.target_x, self.target_y) >= 0:
            if self.angle != self.target_angle:
                    #повернуться
            else:
                    #ехать прямо

    def move_to_station(self):
        # выбрать цель в зависимости от значения order_place
        while distance(self.x, self.y, self.station_x, self.station_y) >= 0:
            if self.angle != self.station_angle:
                # повернуться
            else:
                # ехать прямо

    def run(self):
        self.start_mqtt_thread()
        self.start_work_thread()
