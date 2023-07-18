import asyncio
from aiowebsocket.converses import AioWebSocket
from datetime import datetime
import json
import re
from ast import literal_eval
import os
import shutil
import time
import pandas as pd
import argparse
import csv
import requests


def parseArgsAndSetFunctions():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', required=True, help='Bifrost 環境 1=SIT 2=UAT', type=int)
    parser.add_argument('-r', '--error', default=3, help='time received by websocket - message delivery time ', type=int)
    parser.add_argument('-E', '--deviceId', required=True,  help='deviceId', type=str)
    args = parser.parse_args()
    return args

class Get_timeseries:
    def __init__(self):
        self.X_Authorization = []
        self.access_token = []
        self.device_id = []
        self.check = 0
        self.deviceId = args.deviceId
        currentPath = os.getcwd().replace('\\', '/') + '/'
        file = open(currentPath + '/initial/bifrost_env.csv')
        reader = csv.reader(file)
        data_list = list(reader)
        file.close()
        x = args.env
        self.env = data_list[int(x)][0]
        self.hosts = data_list[int(x)][1]
        self.username = data_list[int(x)][2]
        self.password = data_list[int(x)][3]
        print('hosts:' + self.hosts)
        print('username:' + self.username)
        print('password:' + self.password)

    def getError_interval(self):
        self.error = args.error
        return self.error

    def get_host(self):
        return self.hosts

    def login(self):
        data = {"username": self.username, "password": self.password}
        data2 = json.dumps(data)
        print(data2)
        login_api = 'API'
        r = requests.post(login_api, data=data2)
        j = json.loads(r.text)
        self.X_Authorization = j["token"]
        return self.X_Authorization

    def get_path(self):
        self.path = time.strftime("%Y-%m-%d-%H-%M-%S")+'.csv'
        return self.path

    def get_check(self):
        return self.check

    async def startup(self, uri):
        n1 = 0
        n2 = 0
        async with AioWebSocket(uri) as aws:
            converse = aws.manipulator
            message = '{"attrSubCmds":[],"tsSubCmds":[{"entityType":"DEVICE","entityId":"' + self.deviceId + '","scope":"LATEST_TELEMETRY","cmdId":1}],"historyCmds":[],"entityDataCmds":[],"entityDataUnsubscribeCmds":[],"alarmDataCmds":[],"alarmDataUnsubscribeCmds":[],"entityCountCmds":[],"entityCountUnsubscribeCmds":[]}'
            await converse.send(message)

            while True:
                n3 = n2
                n2 = n1
                n1 = 0

                receive = await converse.receive()

                if str(receive) == 'None':
                    n1 = 1
                else:
                    n1 = 0

                if n3 == 1 and n2 == 1 and n1 == 1:
                    f.close()
                    self.check = 1
                    return self.check

                aa = round(time.time() * 1000)
                with open('a.txt', 'a') as f:
                    f.write(str(aa) + ',' + str(receive) + '\n')

if __name__ == '__main__':
    args = parseArgsAndSetFunctions()
    get_timeseries = Get_timeseries()
    with open('a.txt', 'w') as f:
        f.write('')
        f.close()
    remote = 'websocket' + get_timeseries.login()
    while True:
        print(time.strftime("%Y-%m-%d-%H-%M-%S"),get_timeseries.get_check())
        if get_timeseries.get_check() == 1:
            break
        else:
            try:
                asyncio.get_event_loop().run_until_complete(get_timeseries.startup(remote))
            except:
                get_timeseries.login()
                asyncio.get_event_loop().run_until_complete(get_timeseries.startup(remote))

    src = get_timeseries.get_path()
    file = open(src,'w')
    seq = ['Attributes',
           'time received by websocket',
           'mqtt received time',
           'message delivery time',
           'mqtt_Error_interval',
           'Error_interval',
           'Error_interval_Boolean']

    new_df = pd.DataFrame(columns=seq)
    new_df.to_csv(src, mode='w', index=False)



    with open('a.txt', 'r') as f:
        a = f.readlines()

    for i in range(1, len(a)-2):
        try:
            aa = re.findall(",b'({.*?})'", str(a[i]))[0]
        except:
            pass
        aaa = a[i].split(',')[0]
        ja = json.loads(aa)
        alist = list(ja["data"].keys())
        for j in range(len(alist)):
            b = re.findall(r"\d+\.?\d*", str(ja["data"][alist[j]][0]))[0]
            c = re.findall(r", '(\d+\.?\d*)", str(ja["data"][alist[j]][0]))[0]
            d = int(c) - int(b)
            e = int(aaa) - int(c)
            #超過時間則false
            if e > get_timeseries.getError_interval()*1000:
                f = 'false'
            else:
                f = 'true'

            data = [alist[j], aaa, b, c, d, e, f]

            new_df = pd.DataFrame(columns=data)
            new_df.to_csv(src, mode='a', index=False)





