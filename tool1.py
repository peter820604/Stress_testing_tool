import requests
import json
import re
import pandas as pd
import csv
import os
import argparse
import time


def parseArgsAndSetFunctions():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', required=True, help='Bifrost 環境 1=SIT 2=UAT', type=int)
    args = parser.parse_args()
    return args

class Get_access_toke:
    def __init__(self):
        self.X_Authorization = []
        self.currentPath = os.getcwd().replace('\\', '/') + '/'
        file = open(self.currentPath + '/initial/bifrost_env.csv')
        reader = csv.reader(file)
        data_list = list(reader)
        file.close()
        x = args.env
        self.env = data_list[int(x)][0]
        self.hosts = data_list[int(x)][1]
        self.username = data_list[int(x)][2]
        self.password = data_list[int(x)][3]

    def config(self):
        print('hosts:' + self.hosts)
        print('username:' + self.username)
        print('password:' + self.password)

    def host(self):
        return self.hosts

    def username1(self):
        return self.username

    def password1(self):
        return self.password

    def acctoken(self):
        self.acctoken = self.currentPath + 'initial/' + self.env + '_access_token.csv'
        return self.acctoken

    def login(self, host, username, password):
        data = {"username": username ,"password": password}
        data2 = json.dumps(data)
        login_api = 'http://' + host + '/api/auth/login'
        r = requests.post(login_api, data = data2)
        j = json.loads(r.text)
        self.X_Authorization = 'Bearer '+ j["token"]
        return self.X_Authorization

    def get_header(self, X_Authorization):
        headers = {'X-Authorization': X_Authorization}
        return headers

    def get_devices_infos(self, headers):
        deviceinfos_api = 'http://' + self.hosts + '/api/tenant/deviceInfos?pageSize=30&page=0&sortProperty=createdTime&sortOrder=DESC&deviceProfileId='
        rr = requests.get(deviceinfos_api, headers = headers)
        jj = json.loads(rr.text)
        return jj

    def get_devices_cred(self, headers, j):
        deviceinfos_api = 'http://' +  self.hosts + '/api/tenant/deviceInfos?pageSize=30&page=' + str(j) + '&sortProperty=createdTime&sortOrder=DESC&deviceProfileId='
        rr = requests.get(deviceinfos_api, headers=headers)
        jjj = json.loads(rr.text)
        return jjj


    def get_access_token(self, headers, device_id):
        asa = 'http://' + self.hosts +'/api/device/' + device_id[i] + '/credentials'
        rrr = requests.get(asa, headers = headers)
        return rrr

if __name__ == "__main__":
    print(time.strftime("%Y-%m-%d %H:%M:%S"))
    args = parseArgsAndSetFunctions()
    Get_access_toke = Get_access_toke()
    Get_access_toke.config()
    host = Get_access_toke.host()
    username = Get_access_toke.username1()
    password = Get_access_toke.password1()
    acctoken = Get_access_toke.acctoken()
    headers = Get_access_toke.get_header(Get_access_toke.login(host,username,password))

    device_id = []
    device_name = []
    device_id2 = []
    device_id3 = []
    device_id4 = []
    device_id5 = []
    aa = str("'gateway': True")

    jj = Get_access_toke.get_devices_infos(headers)

    for j in range(jj['totalPages']):
        jjj = Get_access_toke.get_devices_cred(headers, j)
        device_id2.clear()
        device_id3.clear()
        device_id4.clear()
        device_id5.clear()

        for i in range(len(jjj['data'])):
            device_id2.append(str(jjj['data'][i]['id']))
            device_id3.append(str(jjj['data'][i]['additionalInfo']))
            device_id5.append(str(jjj['data'][i]['name']))

        for i in range(len(device_id3)):
            if aa not in str(device_id3[i]):
                device_id4.append(device_id2[i])
                device_name.append(device_id5[i])

        for i in range(len(device_id4)):
            device_id.append(str(re.findall("'id': '(.{36})'}", device_id4[i])).strip("/[/]/''"))

    with open(acctoken, 'w') as f:
        l = ['device name,access token' + '\n']
        f.writelines(l)
        f.close()

    for i in range(0, len(device_id)):
        rrr = Get_access_toke.get_access_token(headers, device_id)
        cccc = re.findall('"credentialsId":"(.+?)"', rrr.text)
        data = [device_name[i], cccc[0]]

        new_df = pd.DataFrame(columns=data)
        new_df.to_csv(acctoken, mode='a', index=False)

    print('匯出 ' + acctoken + ' 成功')
    print(time.strftime("%Y-%m-%d %H:%M:%S"))

