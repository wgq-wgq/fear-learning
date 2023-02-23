import tkinter as tk
import time
from datetime import datetime

win = tk.Tk()
win.geometry('700x600')
win.title('恐惧学习')
canvas = tk.Canvas(win, bg='white', height=600, width=600)
canvas.grid(column=0, row=0)


# 刷新界面
def display():
    time.sleep(0.1)
    canvas.update()


# 创建环境
def create_env():
    for i in range(0, 650, 50):
        x0, y0, x1, y1 = i, 0, i, 600
        canvas.create_line(x0, y0, x1, y1)
    for j in range(0, 650, 50):
        x0, y0, x1, y1, = 0, j, 600, j
        canvas.create_line(x0, y0, x1, y1)


# 机器人模块
class Robot:
    FEAR_MEMORY = {}
    SENSORY_MEMORY = {}

    def __init__(self, column, row):  # 列，行
        self.points = [10, 10, 25, 10, 25, -15, 25, 10, 40, 10, 40, 25, 65, 25, 40, 25, 40, 40, 25, 40, 25, 65, 25, 40,
                       10, 40, 10, 25, -15, 25, 10, 25]
        self.column = column
        self.raw = row

    # 创建机器人，同时传递给机器人的具体位置
    def create_robot(self):
        for i in range(32):
            if i % 2 == 0:
                self.points[i] += 50 * (self.column - 1)
            else:
                self.points[i] += 50 * (self.raw - 1)
        return canvas.create_polygon(self.points, fill='yellow', outline="LightSkyBlue", width=2)

    # 感知模块
    @staticmethod
    def perception(robot, hunter):
        coor_robot = canvas.coords(robot)  # 获取机器人坐标
        coor_hunter = canvas.coords(hunter)  # 获取危险物坐标

        coor_robot_center = coor_robot[0] + 15, coor_robot[1] + 15  # 机器人的中心坐标
        coor_hunter_center = (coor_hunter[0] + coor_hunter[2]) / 2, (coor_hunter[1] + coor_hunter[3]) / 2  # 危险物的中心坐标

        # 如果机器人的坐标和危险物的坐标小于一格，则危险物处于机器人的感知范围，机器人能够感知到危险物的颜色
        if abs(coor_robot_center[0] - coor_hunter_center[0]) <= 50:
            color_hunter = canvas.itemcget(hunter, 'fill')
            return color_hunter

    # 感觉记忆模块
    @staticmethod
    def sensory_memory(perception):

        # 获取当前时间
        now = (time.time())

        # 感觉记忆的保留时间为2秒，如果大于2秒则删除感觉记忆
        Robot.SENSORY_MEMORY = {key: value for key, value in Robot.SENSORY_MEMORY.items() if now - key < 2}

        # 将感知的事物添加进感觉记忆
        Robot.SENSORY_MEMORY[now] = perception

        print('感觉记忆：', Robot.SENSORY_MEMORY)

    # 恐惧记忆提取模块
    @staticmethod
    def remember(perception):
        try:
            neuron_weight = Robot.FEAR_MEMORY[perception]
        except KeyError:
            neuron_weight = 0
        return neuron_weight

    # 受伤模块
    @staticmethod
    def hurt(robot, hunter):
        coor_robot = canvas.coords(robot)
        coor_hunter = canvas.coords(hunter)

        coor_robot_center = coor_robot[0] + 15, coor_robot[1] + 15
        coor_hunter_center = (coor_hunter[0] + coor_hunter[2]) / 2, (coor_hunter[1] + coor_hunter[3]) / 2
        if abs(coor_robot_center[0] - coor_hunter_center[0]) < 50:
            for i in range(3):
                display()
                canvas.itemconfig(robot, fill='pink')
                display()
                canvas.itemconfig(robot, fill='yellow')
            Robot.run(robot)
            return True

    # 学习模块
    @staticmethod
    def learning():

        # 首先提取感觉记忆，如果有，则强化，否则不强化
        try:
            time_list = sorted(list(Robot.SENSORY_MEMORY.keys()))
            last_time = time_list[-1]
        except IndexError:
            return

        now = float(time.time())
        if now - last_time < 2:  # 这个时间代表了感觉记忆的保留时间
            try:
                weight = Robot.FEAR_MEMORY[Robot.SENSORY_MEMORY[last_time]]
            except KeyError:
                Robot.FEAR_MEMORY[Robot.SENSORY_MEMORY[last_time]] = 0.5
                return

            weight += 0.5
            Robot.FEAR_MEMORY[Robot.SENSORY_MEMORY[last_time]] = weight

    # 逃跑模块
    @staticmethod
    def run(robot):
        canvas.move(robot, -100, 0)


# 危险物模块
class Hunter:
    def __init__(self, center, diameter, color):
        self.center = center
        self.diameter = diameter
        self.color = color

        self.left = (self.center[0] - 1) * 50 + (50 - self.diameter) / 2
        self.right = self.left + self.diameter
        self.top = (self.center[1] - 1) * 50 + (50 - self.diameter) / 2
        self.down = self.top + diameter

    # 创造危险物，同时赋予其位置和颜色
    def create_hunter(self):
        return canvas.create_oval(self.left, self.top, self.right, self.down, fill=self.color)

    # 危险物的前进模块
    @staticmethod
    def move(hunter):
        canvas.move(hunter, -50, 0)


# 开始按钮
def start(robot, hunter):
    print('恐惧记忆：', Robot.FEAR_MEMORY)
    while True:
        perception_result = Robot.perception(robot, hunter)  # 感知到的信息

        # 信息流动的第一条路，形成感觉记忆，并根据是否被攻击决定是否启动学习
        if perception_result:
            Robot.sensory_memory(perception_result)

            # 被攻击后启动学习
            hurt_result = Robot.hurt(robot, hunter)
            if hurt_result:
                Robot.learning()
                break

        # 信息流动的第二条路，提取恐惧记忆，并根据预测结果做出行为
        if perception_result:
            remember_result = Robot.remember(perception_result)  # 提取记忆
            if remember_result >= 1:  # 预测，做出行为
                Robot.run(robot)
                break

        Hunter.move(hunter_1)
        display()


# 复位按钮
def reset(robot, robot_coor, hunter, hunter_coor):
    canvas.coords(robot, robot_coor)
    canvas.coords(hunter, hunter_coor)


# 改变颜色按钮
def change_color(hunter):
    canvas.itemconfig(hunter, fill='blue')


if __name__ == '__main__':

    #cccc
    create_env()

    hunter_1 = Hunter((12, 3), 30, color='red').create_hunter()
    origin_hunter = canvas.coords(hunter_1)

    robot_1 = Robot(3, 3).create_robot()
    origin_robot = canvas.coords(robot_1)

    tk.Button(win, text='start', command=lambda: start(robot_1, hunter_1)).place(x=610, y=100)
    tk.Button(win, text='reset', command=lambda: reset(robot_1, origin_robot, hunter_1, origin_hunter)).place(x=610,
                                                                                                              y=300)
    tk.Button(win, text='change', command=lambda: change_color(hunter_1)).place(x=610, y=500)
    canvas.mainloop()
