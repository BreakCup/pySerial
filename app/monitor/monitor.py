# coding:utf-8

import serial
import threading
import time
import queue
import serial.serialutil
import binascii


DEBUG=False

class Serial(threading.Thread):
    queue:queue.Queue
    def __init__(self,queue,count,msg,lock,name="monitor"):
        """queue缓存队列，lock线程锁，name线程名字"""
        super(Serial,self).__init__(name=name)
        self.lock=lock
        self.mSerial=None
        self.queue=queue
        self.msg=msg
        self.count=count
        self.num=0
        pass

    def run(self):
        """线程运行函数"""
        while self.lock:
            # self.lock.acquire()
            time.sleep(0.5)
            #-*-线程运行部分-*-
            self.PutData()
            #-*-线程运行部分-*-
            # self.lock.release()

    def OpenSerial(self,pName):
        """打开端口"""
        try:
            if DEBUG:
                print(pName)
            if not pName:
                if DEBUG:
                    print('打开端口失败')
                return False
            else:
                if DEBUG:
                    print('打开端口')
                self.mSerial = serial.Serial(pName, 9600, timeout=60,bytesize=8,stopbits=1)
                return True
        except serial.serialutil.SerialException as e:
            if DEBUG:
                print("error:", e)
            return False

    def CloseSerial(self):
        """关闭端口"""
        if self.mSerial.isOpen():
            while self.mSerial.inWaiting():
                self.PutData()
            self.mSerial.close()

    def PutData(self):
        """将端口数据存入队列"""
        hex=''
        asci=''
        if self.mSerial.isOpen():
            try:
                data = ''
                data = data.encode('utf-8')
                n = self.mSerial.inWaiting()
                #接收到十六进制数，转化成十六进制格式表示的字符串，并将每一位存入队列中
                if n!=0:
                    hlist=[]
                    data = binascii.hexlify(self.mSerial.read(n))
                    data=str(data)[2:-1].upper()
                    i=0
                    while i<len(data)/2:
                        byte=data[2*i:2*i+2]
                        self.queue.put(byte)
                        self.queue.task_done()
                        hlist.append(byte)
                        i=i+1
                    if DEBUG:
                        print('接收到的十六进制data：',data)
                        print("data类型:",type(data))
                        print("十六进制数列表：",hlist)

                    self.msg.see('end')
                self.num = self.num + n
                self.count.set("接收：" + str(self.num) + "byte")
            except serial.serialutil.SerialException as e:
                if DEBUG:
                    print('serial error:', e)

