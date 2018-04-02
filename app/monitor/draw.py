# coding:utf-8
import threading
import time
from enum import Enum
from app.setting import canvas_setting

DEBUG=False

BCI_PACK_LEN = 7
SYNC_Y = 0x80
SYNC_N = 0x00
# XVIEW=(canvas_setting.width-2*canvas_setting.margin_lift)-(canvas_setting.width-2*canvas_setting.margin_lift)%canvas_setting.width_sign
XVIEW=540
STEP=1

class Draw(threading.Thread):
    def __init__(self,queue,sub,isOpened=False,name="draw"):
        super(Draw, self).__init__(name=name)
        self.spo2=sub.get('spo2')
        self.cv=sub.get('canvas')
        self.pulse=sub.get('pulse')
        self.isOpened=isOpened
        self.queue=queue
        self.bciData=[0,0,0,0,0,0,0]
        self.unpackData=list(range(DataType.BCI_DATA_MAX.value))
        # self.pos=list(range(XVIEW))
        self.point=list(range(int(XVIEW/STEP)))
        self.pos=0
        self.temp=-1


    def run(self):
        if DEBUG:
            print('drawing run')
        while self.isOpened:
            if not self.queue.empty():
                #获取包数据
                for i in range(BCI_PACK_LEN-1):
                    self.bciData[i]=self.bciData[i+1]
                self.bciData[BCI_PACK_LEN-1]=int(self.queue.get(False),16)
                if DEBUG:
                    print("get data:",self.bciData)
                #判断是否为完整的包
                if ((self.bciData[0] & 0x80) == SYNC_Y and (self.bciData[1] & 0x80) == SYNC_N and
                    (self.bciData[2] & 0x80) == SYNC_N and (self.bciData[3] & 0x80) == SYNC_N and
                    (self.bciData[4] & 0x80) == SYNC_N and (self.bciData[5] & 0x80) == SYNC_N and
                    (self.bciData[6] & 0x80) == SYNC_N):
                    if DEBUG:
                        print('bcidata:', self.bciData)
                    data=[]
                    #解析数据
                    data.append((self.bciData[0] & 0x0f) >> 0)      #0
                    data.append((self.bciData[0] & 0x10) >> 4)      #1
                    data.append((self.bciData[2] & 0x10) >> 4)
                    data.append((self.bciData[0] & 0x40) >> 6)
                    data.append((self.bciData[1] & 0x7f) >> 0)
                    data.append((self.bciData[2] & 0x40) << 1 | (self.bciData[3] & 0x7f) >> 0)
                    data.append((self.bciData[4] & 0x7f) >> 0)
                    data.append((self.bciData[2] & 0x0f) >> 0)
                    data.append((self.bciData[2] & 0x20) >> 5)
                    #画图
                    self.DrawGraph(data)

                    # self.SetBciData(0, (self.bciData[0] & 0x0f) >> 0)
                    # self.SetBciData(1, (self.bciData[0] & 0x10) >> 4)
                    # # SetBciData(2, (self.bciData[0] & 0x20) >> 5)
                    # self.SetBciData(3, (self.bciData[0] & 0x40) >> 6)
                    # self.SetBciData(4, (self.bciData[1] & 0x7f) >> 0)
                    # self.SetBciData(5, (self.bciData[2] & 0x40) << 1 | (self.bciData[3] & 0x7f) >> 0)
                    # self.SetBciData(6, (self.bciData[4] & 0x7f) >> 0)
                    # self.SetBciData(7, (self.bciData[2] & 0x0f) >> 0)
                    # self.SetBciData(2, (self.bciData[2] & 0x10) >> 4)
                    # self.SetBciData(8, (self.bciData[2] & 0x20) >> 5)

            time.sleep(0.001)

    def DrawGraph(self,data):
        marLeft=canvas_setting.margin_lift
        marBot=canvas_setting.margin_bottom
        height=canvas_setting.height
        width=canvas_setting.width

        if DEBUG:
            print("BCI data:",data)

        if DEBUG:
            print("脉率")
        if self.pos==XVIEW/STEP-1:
            self.cv.delete(self.point[0])
        if self.pos<XVIEW/STEP-1:
            self.pos=self.pos+1
        i=0
        while i<XVIEW/STEP-1:
            self.point[i] = self.point[i+1]
            if XVIEW/STEP-i<=self.pos:
                self.cv.move(self.point[i], -STEP, 0)
            i=i+1
        if self.temp==-1:
            self.point[-1] = self.cv.create_line(XVIEW+marLeft-1, height-marBot-data[4]*2,XVIEW+marLeft,
                                                 height-marBot - data[4]*2,fill="red")
        else:
            self.point[-1] = self.cv.create_line(XVIEW + marLeft-1, height - marBot - self.temp * 2, XVIEW + marLeft,
                                                 height - marBot - data[4] * 2, fill="red")
        self.temp=data[4]
        self.spo2.set("血氧："+str(data[6]))
        self.pulse.set('脉搏：'+str(data[5]))
        if DEBUG:
            pass
            # print("points：", self.point)

    def Stop(self):
        self.isOpened=False

    def Run(self):
        self.isOpened=True
        self.start()

    def Drawing(self):
        pass

class DataType(Enum):
    BCI_DATA_SIGNAL_STRONG=0    # 信号强度
    BCI_DATA_SEARCH_LONG=1      # 搜索时间太长
    BCI_DATA_SENSOR_OFF=2       # 传感器脱落
    BCI_DATA_PULSE_BEAT=3         # 脉搏跳动
    BCI_DATA_PLETH_WAVE=4       # 体积描记波
    BCI_DATA_PULSE_RATE=5       # 脉率
    BCI_DATA_SPO2_VALUE=6        # 血氧值
    BCI_DATA_BAR_GRAPH=7         # 棒图
    # BCI_DATA_SENFOR_ERR # 传感器错误
    BCI_DATA_SEARCH_PULSE=8     # 搜索脉搏
    BCI_DATA_MAX=9

