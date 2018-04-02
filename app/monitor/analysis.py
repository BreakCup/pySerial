# coding:utf-8

DEBUG=False

BCI_PACK_LEN = 7
SYNC_Y = 0x80
SYNC_N = 0x00

bciData=[0 for i in range(8)]

def analysis(self,data):
    # 获取包数据
    for i in range(BCI_PACK_LEN - 1):
        bciData[i] = bciData[i + 1]
    bciData[BCI_PACK_LEN - 1] = int(data)
    if DEBUG:
        print("get data:", bciData)
    # 判断是否为完整的包
    if ((bciData[0] & 0x80) == SYNC_Y and (bciData[1] & 0x80) == SYNC_N and
            (bciData[2] & 0x80) == SYNC_N and (bciData[3] & 0x80) == SYNC_N and
            (bciData[4] & 0x80) == SYNC_N and (bciData[5] & 0x80) == SYNC_N and
            (bciData[6] & 0x80) == SYNC_N):
        if DEBUG:
            print('bcidata:', bciData)
        res = []
        # 解析数据
        res.append((bciData[0] & 0x0f) >> 0)  # 0
        res.append((bciData[0] & 0x10) >> 4)  # 1
        res.append((bciData[2] & 0x10) >> 4)
        res.append((bciData[0] & 0x40) >> 6)
        res.append((bciData[1] & 0x7f) >> 0)
        res.append((bciData[2] & 0x40) << 1 | (bciData[3] & 0x7f) >> 0)
        res.append((bciData[4] & 0x7f) >> 0)
        res.append((bciData[2] & 0x0f) >> 0)
        res.append((bciData[2] & 0x20) >> 5)

        return res
    else:
        return False
