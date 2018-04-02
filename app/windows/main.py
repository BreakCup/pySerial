# coding:utf-8
import tkinter as tk
from tkinter import ttk
from app.monitor.monitor import Serial
from app.monitor.draw import Draw
import threading
from queue import Queue
import time
import serial.tools.list_ports
from tkinter.messagebox import askyesno
import _tkinter
from tkinter.scrolledtext import ScrolledText
from app.setting import canvas_setting

class MainWin:
    def __init__(self):
        self.getSerialList=threading.Thread(name="GetSerialList",target=self.GetSerialList)
        self.getSerialList.daemon = True
        self.queue=Queue()
        #控制
        self.canRun=True
        self.isMonite=False
        self.isOpenDrawWin = False
        #主窗口参数
        self.window = tk.Tk()
        self.title='myWindow'
        # self.size='400x500+40+40'
        self.window.title(self.title)
        self.window.resizable(0, 0)  # 禁止改变窗口大小
        #打开绘图窗口按钮
        self.openWinBtn=tk.Button(self.window,text="打开绘图窗口",command=self.OpenWin)
        #按钮文字
        self.btnText=tk.StringVar(self.window)
        self.btnText.set("打开监控")
        self.editText=''
        #文本框
        self.message=ScrolledText(self.window,background='#ffffff')
        #按钮
        self.button=tk.Button(self.window, textvariable=self.btnText,command=self.Start,width=10)
        #标签
        self.label=tk.Label(self.window,text="选择端口:")
        #提示标签
        self.info=tk.StringVar(self.window)
        self.infoLabel = tk.Label(self.window, textvariable=self.info)
        #计数标签
        self.count = tk.StringVar(self.window)
        self.countLabel = tk.Label(self.window, textvariable=self.count)
        #获取端口数据线程
        self.serial = Serial(self.queue,self.count,self.message,self.canRun, "monitor")
        self.serial.daemon = True
        #监听端口线程
        self.getSerialList = threading.Thread(name="GetSerialList", target=self.GetSerialList)
        self.getSerialList.daemon = True
        # 创建一个下拉列表
        self.serialName = tk.StringVar()
        # self.serialName.set('显示端口')
        self.serialChosen = ttk.Combobox(self.window,state='readonly',textvariable=self.serialName,width=15)
        # 血氧标签
        self.spo2Text = tk.StringVar(self.window)
        self.spo2Text.set("血氧：")
        self.spo2 = tk.Label(self.window, textvariable=self.spo2Text, width=15)
        self.spo2.grid(row=13, column=0, columnspan=2, sticky="w")
        # 脉率标签
        self.pulseText = tk.StringVar(self.window)
        self.pulseText.set("脉搏：")
        self.pulse = tk.Label(self.window, textvariable=self.pulseText, width=15)
        self.pulse.grid(row=13, column=2, columnspan=2, sticky="w")
        # 画板
        self.cvWid = canvas_setting.width
        self.cvHeight = canvas_setting.height
        self.cv = tk.Canvas(self.window, bg='black', width=self.cvWid, height=self.cvHeight)
        self.InitCanvas(self.cv, self.cvWid, self.cvHeight)
        self.cv.grid(row=1, rowspan=12, column=0, columnspan=6)

        #标签
        self.label.grid(row=0,sticky='w')
        # 打开绘图按钮
        # self.openWinBtn.grid(row=0, column=3)
        # 监听按钮
        self.button.grid(row=0, column=2, sticky='w')
        # 文本框
        # self.message.grid(row=2, rowspan=20, column=0, columnspan=10)
        #提示标签
        self.info.set('未打开端口')
        self.infoLabel.grid(row=16,column=0,columnspan=2,sticky="w")
        #数据信息标签
        self.count.set('接收：0byte')
        self.countLabel.grid(row=16,column=2,columnspan=2, sticky="w")
        #端口选择器
        self.serialChosen.grid(row=0,column=1, sticky='w')  # 设置其在界面中出现的位置  column代表列   row 代表行
        #启动监视端口线程
        self.getSerialList.start()
        # self.serialChosen.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
        #窗口销毁事件
        self.window.protocol('WM_DELETE_WINDOW', self.CloseMainWin)

        #绘图线程
        self.sub = {
            'canvas': self.cv,
            'spo2': self.spo2Text,
            'pulse': self.pulseText
        }
        self.draw = Draw(queue=self.queue, sub=self.sub)

        self.window.mainloop()


    def Start(self):
        """开始监听程序"""


        try:
            pName=self.serialChosen.get()
            if not self.isMonite:
                if self.serial.OpenSerial(pName):
                    self.canRun = False
                    if not self.serial.is_alive():
                        self.serial.start()
                        self.isMonite=True
                    if not self.draw.is_alive():
                        self.draw.Run()
                        self.draw.daemon=True
                    self.btnText.set("停止监控")
                    self.info.set("打开端口"+self.serialChosen.get()+"成功。")
                else:
                    self.info.set("打开端口" + self.serialChosen.get() + "失败。")
            else:

                self.isMonite=False
                self.canRun=False
                self.serial.CloseSerial()
                self.btnText.set("打开监控")
                self.info.set("未打开端口")
        except RuntimeError as e:
            print("run error:", e)

    def GetSerialList(self):
        """获取串口名函数"""
        while True:
            ports=serial.tools.list_ports.comports()
            plists = list(ports)
            if len(plists) > 0:
                name = ()
                lname = []
                for plist in plists:
                    lname.append(plist[0])
                name=tuple(lname)
                self.serialChosen['value']=(0)
                self.serialChosen['value']=name
                # print('发现端口：',name)
            else:
                print("没有发现端口!")
            time.sleep(0.5)

    def OpenWin(self):
        """打开绘图窗口"""
        try:

            if self.isOpenDrawWin:
                askyesno("提示", message="窗口已经打开")
            else:
                # 绘图窗口

                self.drawWin = tk.Tk()
                self.drawWin.protocol('WM_DELETE_WINDOW', self.CloseDrawWindow)
                self.drawWin.title("数据")
                self.drawWin.resizable(0, 0)
                # 绘图窗口的组件：

                #血氧标签
                spo2Text=tk.StringVar(self.drawWin)
                spo2Text.set("血氧：")
                spo2=tk.Label(self.drawWin,textvariable=spo2Text,width=15)
                spo2.grid(row=1,column=12,columnspan=3,sticky='w')
                # 脉率标签
                pulseText = tk.StringVar(self.drawWin)
                pulseText.set("脉搏：")
                pulse = tk.Label(self.drawWin, textvariable=pulseText, width=15)
                pulse.grid(row=2, column=12, columnspan=3, sticky='w')
                #画板
                cvWid = canvas_setting.width
                cvHeight = canvas_setting.height
                cv = tk.Canvas(self.drawWin, bg='black', width=cvWid, height=cvHeight)
                self.InitCanvas(cv, cvWid, cvHeight)
                cv.grid(row=0, rowspan=12, column=6, columnspan=6)

                self.isOpenDrawWin = True

                sub={
                    'canvas':cv,
                    'spo2':spo2Text,
                    'pulse':pulseText
                }
                # 绘图线程
                self.draw = Draw(queue=self.queue, sub=sub)
                self.draw.daemon = True
                if not self.draw.is_alive():
                    self.draw.Run()
                self.drawWin.mainloop()
        except RuntimeError as e:
            print("open draw window error：",e)

    def InitCanvas(self,cv,cvW,cvH):
        ew=canvas_setting.width_sign
        eh=canvas_setting.height_sign
        marLeft=canvas_setting.margin_lift
        marBot=canvas_setting.margin_bottom
        h=0
        w=0

        cv.create_line(marLeft, marBot, marLeft, cvH - marBot, fill="green")
        cv.create_line(marLeft, cvH - marBot, cvW - marLeft, cvH - marBot, fill="green")
        #Y轴
        cv.create_text((16, cvH - 35), text='0', anchor='w', fill="#fff")
        #X轴
        cv.create_text((30, cvH - 15), text='0', anchor='w', fill="#fff")

        #横线
        while h<cvH-cvH%eh:
            h = h + eh
            cv.create_line(marLeft, cvH-marBot-h, cvW-(cvW-marLeft)%ew, cvH-marBot-h, fill="#808080",dash=(4,4))
            cv.create_text((5, cvH -marBot-h), text=int(h/2), anchor='w', fill="#fff",justify='right')
        #竖线
        while w<cvW-(cvW%ew):
            w = w + ew
            cv.create_line( w+marLeft, cvH-marBot, w+marLeft ,(cvH-marBot)%eh, fill="#808080",dash=(4,4))


    def CloseMainWin(self):
        """销毁主窗口时运行"""
        ans=askyesno("提示",message="退出程序？")
        if ans:
            try:
                self.draw.Stop()
                if self.serial.is_alive():
                    self.serial.join(1)
                if self.getSerialList.is_alive():
                    self.serial.join(1)
                if self.draw.is_alive():
                    self.serial.join(1)
                self.window.destroy()
                self.drawWin.destroy()
            except AttributeError as e:
                print("error:",e)
            except _tkinter.TclError as e:
                print("error:", e)
            except RuntimeError as e:
                print("thread error:", e)

        else:
            return
    def CloseDrawWindow(self):
        """销毁绘图窗口时运行"""
        self.isOpenDrawWin = False
        self.draw.Stop()
        self.draw.join(1)
        self.drawWin.destroy()











