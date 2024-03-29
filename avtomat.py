import time
import threading
import paho.mqtt.client as mqtt
import math

from paho.mqtt import publish


def angle(x, y):
    return math.atan(x / y)


def cosinus(x1, x2, y1, y2):
    cos = abs(x1 * x2 + y1 * y2) / (math.sqrt(x1 ** 2 + y1 ** 2) * math.sqrt(x2 ** 2 + y2 ** 2))
    return cos


def angle_between_vectors(self):
    angle = math.acos(cosinus(self.x1, self.x2, self.y1, self.y2))
    return angle


def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class Robot:
    def __init__(self):
        self.state = "On_station"
        self.pink_x = None  # Позиция робота
        self.pink_y = None
        self.blue_x = None  # Позиция робота
        self.blue_y = None
        self.angle = None
        self.target_angle = None  # Позиция цели
        self.target_x = None
        self.target_y = None
        self.station_x = None  # Позиция станции
        self.station_y = None
        self.station_angle = None
        self.pouring_state = None
        self.mqtt_client = None  # MQTT
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
                client.subscribe("abot/command/alex")

            def on_message(client, userdata, msg):
                topic = msg.topic
                if topic == "tgbot":  # получает место заказа
                    self.state = "Get_order"
                elif topic == "robot":  # получает координаты робота
                    coords = msg.payload.decode()
                    self.pink_x, self.pink_y, self.blue_x, self.blue_y = coords.split()
                elif topic == "station":  # получает координаты станции
                    self.station_x, self.station_y = map(float, msg.payload.decode().split(","))
                elif topic == "target":  # получает координаты цели
                    self.target_x, self.target_y = map(float, msg.payload.decode().split(","))
                elif topic == "pivo_station":  # налито?
                    self.pouring_state = "nalito"

            if self.mqtt_client is None:
                self.mqtt_client = mqtt.Client()
                self.mqtt_client.on_connect = on_connect
                self.mqtt_client.on_message = on_message
                self.mqtt_client.connect("localhost", 1883, 60)
                self.mqtt_client.loop_start()
                time.sleep(1)

    def work_thread(self):
        while not self.stop_thread:
            if self.state == "On_station":
                print("Какой хороший день для пива")
                time.sleep(1)
                print("люблю доставлять людям счастье и пиво")
                time.sleep(1)
                print("Пам-парам, у меня есть пиво!")
                # стоять чилить
            elif self.state == "Get_order":
                if self.pouring_state == "nalito":
                    self.state = "Bring_order"
                    self.pouring_state = None
            elif self.state == "Bring_order":
                self.move_to_customer()
            elif self.state == "Goto_station":
                self.move_to_station()
                self.state = "On_station"

    def start_mqtt_thread(self):
        threading.Thread(target=self.mqtt_thread, daemon=True).start()

    def start_work_thread(self):
        threading.Thread(target=self.work_thread, daemon=True).start()

    def move_to_customer(self):
        while distance(self.x, self.y, self.target_x, self.target_y) >= 0: #больше не просто х и у!! поменять!!
        angle = angle_between_vectors(self.robot_vector(self), self.to_target_vector(self))
        robot_vector_x, robot_vector_y = self.robot_vector(self.pink_x, self.pink_y, self.blue_x, self.blue_y)
        target_vector_x, target_vector_y = self.to_target_vector(self.target_x, self.target_y, self.station_x, self.station_y)
        tangens_angle_robot = math.tan(robot_vector_y / robot_vector_x)
        tangens_angle_target = math.tan(target_vector_y / target_vector_x)
        while distance(self.x, self.y, self.target_x, self.target_y) >= 0:
            if angle != 0:  # повернуться
                if self.angle > self.target_angle:  # повернуться по часовой
                    msg = "{\"cmd\":\"right\",\"val\":2.0,\"spd\":0.6}"
                    publish("abot/command/alex", msg)
                elif self.angle < self.target_angle:  # повернуться против часовой
                    msg = "{\"cmd\":\"left\",\"val\":2.0,\"spd\":0.6}"
                    publish("abot/command/alex", msg)
            else:
                msg = "{\"cmd\":\"forward\",\"val\":2.0,\"spd\":0.6}"
                publish("abot/command/alex", msg)
                # ехать прямо

    def move_to_station(self):
        while distance(self.x, self.y, self.target_x, self.target_y) >= 0:#больше не просто х и у!! поменять!!
        angle = angle_between_vectors(self.robot_vector(self), self.to_target_vector(self))
        robot_vector_x, robot_vector_y = self.robot_vector(self.pink_x, self.pink_y, self.blue_x, self.blue_y)
        target_vector_x, target_vector_y = self.to_target_vector(self.target_x, self.target_y, self.station_x, self.station_y)
        tangens_angle_robot = math.tan(robot_vector_y / robot_vector_x)
        tangens_angle_target = math.tan(target_vector_y / target_vector_x)
        while distance(self.x, self.y, self.target_x, self.target_y) >= 0:
            if angle != 0:  # повернуться
                if self.angle > self.station_angle:  # повернуться по часовой
                    msg = "{\"cmd\":\"right\",\"val\":2.0,\"spd\":0.6}"
                    publish("abot/command/alex", msg)
                elif self.angle < self.station_angle:  # повернуться против часовой
                    msg = "{\"cmd\":\"left\",\"val\":2.0,\"spd\":0.6}"
                    publish("abot/command/alex", msg)
            else:
                msg = "{\"cmd\":\"forward\",\"val\":2.0,\"spd\":0.6}"
                publish("abot/command/alex", msg)
                # ехать прямо

    def run(self):
        self.start_mqtt_thread()
        self.start_work_thread()
