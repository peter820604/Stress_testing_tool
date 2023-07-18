import os
import shutil
import pandas as pd
import argparse
import random
import csv


parser = argparse.ArgumentParser()
parser.add_argument('-e', '--env', required=True, help='Bifrost 環境 1=SIT 2=UAT', type=int)
parser.add_argument('-m', '--mqtts', default=1, help='mqtt數,預設為1', type=int)
parser.add_argument('-s', '--sensors', default=1, help='sensor數,預設為1', type=int)
parser.add_argument('-a', '--attributes', default=1, help='attribute數,預設為1', type=int)
parser.add_argument('-f', '--frequency', default=1, help='frequency數,預設為1/s', type=int)
parser.add_argument('-d', '--duration', default=30, help='duration數,預設為30 單位:s', type=int)
parser.add_argument('-v', '--slaves', default=1, help='slave機數,預設為1', type=int)
parser.add_argument('-n', '--name', help='ssh_username', type=str, required=True)
args = parser.parse_args()

def data_list():
    currentPath = os.getcwd().replace('\\', '/') + '/'
    file = open(currentPath + '/initial/bifrost_env.csv')
    reader = csv.reader(file)
    data_list = list(reader)
    file.close()
    return data_list

def env(list):
    x = args.env
    env = list[int(x)][0]
    return env

def host(list):
    x = args.env
    hosts = list[int(x)][1]
    return hosts

def info(hosts):
    print('hosts:', hosts)
    print('mqtts:', args.mqtts)
    print('sensors:', args.sensors)
    print('attributes:', args.attributes)
    print('frequency:', args.frequency, '/s')
    print('datapoints:', args.mqtts * args.sensors * args.attributes * args.frequency, '/s')
    print('duration:', args.duration, 's')
    print('The location of the mqtt.jmx in the linux server:/home/' + args.name + '/jmx', )
    print('The location of the resource folder in the linux server:/home/' + args.name + '/jmx/resource', )

def folder_create():
    file_dir = 'resource'
    if os.path.isdir(file_dir):
        shutil.rmtree(file_dir)
        for i in range(1, args.slaves + 1):
            file_cdir = 'resource/slave' + str(i) + '/resource'
            os.makedirs(file_cdir)
    else:
        for i in range(1, args.slaves + 1):
            file_cdir = 'resource/slave' + str(i) + '/resource'
            os.makedirs(file_cdir)

    ffile_dir = 'jmx'
    if os.path.isdir(ffile_dir):
        shutil.rmtree(ffile_dir)
        os.makedirs(ffile_dir)
    else:
        os.makedirs(ffile_dir)

def generate_jmx(hosts):
    file_dir = 'jmx'
    if os.path.isdir(file_dir):
        shutil.rmtree(file_dir)
        os.mkdir(file_dir)
    else:
        os.mkdir(file_dir)
    filename = os.path.join(file_dir, 'mqtt.jmx')

    jmx = []
    jmx2 = []
    n = 14
    nn = 61
    aa = args.attributes-1
    att = ""
    currentPath = os.getcwd()+'/'

    for i in range(args.attributes):
        att += 'att' + str(i) + ','

    with open(currentPath+"/initial/init.jmx", 'r') as f:
        for i in f.readlines():
            jmx.append(i)

    with open(currentPath+"/initial/Odin.jmx", 'r') as f1:
        for j in f1.readlines():
            jmx2.append(j)

    for k in range(args.attributes):
        if (args.attributes-1)>k:
            bb = '    &quot;att'+ str(k) +'&quot;:${__time()}' + ',' + '\n'
            jmx2.insert(nn, bb)
            nn += 1
        else:
            bb = '    &quot;att'+ str(k) +'&quot;:${__time()}' + '\n'
            jmx2.insert(nn, bb)
            nn += 1

    x9 = 66 + args.attributes
    jmx2[x9] = '            <stringProp name="filename">/home/' + args.name + '/jmx/resource/telemetry.csv</stringProp>\n'

    x7 = 68 + args.attributes
    jmx2[x7] = '            <stringProp name="variableNames">' + att + '</stringProp>\n'

    x8 = 97 + args.attributes
    jmx2[x8] = '      </hashTree>\n'

    for l in range(int(args.mqtts)):
        for j in jmx2:
            jmx.insert(n, j)
            n += 1

    for i in range(int(args.mqtts)):
        x1 = 14 + i * ( 98 + args.attributes)
        x2 = 20 + i * ( 98 + args.attributes)
        x3 = 23 + i * ( 98 + args.attributes)
        x7 = 31 + aa + i * (98 + args.attributes)
        x4 = 53 + i * ( 98 + args.attributes)
        x5 = 101 + aa + i * ( 98 + args.attributes)
        x6 = 106 + aa + i * ( 98 + args.attributes)

        jmx[x1] ='       <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Odin_' + str(i) + '" enabled="true">\n'
        jmx[x2] ='        <stringProp name="ThreadGroup.num_threads">' + str(args.sensors) + '</stringProp>\n'
        jmx[x3] ='        <stringProp name="ThreadGroup.duration">' + str(args.duration) + '</stringProp>\n'
        jmx[x7] = '	          <stringProp name="mqtt.server">' + hosts + '</stringProp>\n'
        jmx[x4] ='            <stringProp name="filename">/home/' + args.name + '/jmx/resource/acctoken' + str(i) + '.csv</stringProp>\n'
        jmx[x5] ='          <longProp name="duration">' + str(args.duration) + '</longProp>\n'
        jmx[x6] ='            <value>' + str(args.sensors*args.frequency) + '</value>\n'

    for k in jmx:
        print(k,end='\t' ,file=open( filename, 'a'))

def gemerate_access_token_csv(env):
    file = 'initial/' + env + '_access_token.csv'
    file_adir = 'resource/slave'
    n = 1
    row_list = []
    df = pd.DataFrame(pd.read_csv(file))
    row_num = int(df.shape[0])

    if args.mqtts*args.sensors >= row_num:
        raise Exception('too much!!')
    try:
        for i in list(range(args.sensors,args.mqtts*args.sensors*args.slaves+1,args.sensors)):
            row_list.append(i)

    except Exception as e:
        print(e)

    for m in row_list:
        nn = (n-1) // args.mqtts
        nnn = (n - 1) % args.mqtts
        filename = os.path.join(file_adir + str(nn+1) + '/resource','acctoken' + str(nnn) + '.csv')
        if m <(args.mqtts*args.sensors*args.slaves+1):
            df_handle=df.iloc[m-args.sensors:m]
            df_handle.to_csv(filename, index=False, header=0)
        elif m == (args.mqtts*args.sensors*args.slaves+1):
            remainder=int(int(row_num)%args.sensors)
            df_handle=df.iloc[m-remainder:m]
            df_handle.to_csv(filename, index=False, header=0)
        n = n + 1

def generate_tempery_csv():

    src = "resource/slave1/resource/telemetry.csv"

    seq = []

    for k in range(args.mqtts * args.sensors + 1):
        b = list(range(0,  args.attributes))
        seq.append(b)

    for j in range(args.mqtts * args.sensors + 1):
        for i in range(args.attributes):
            if j == 0:
                seq[j][i] = 'att' + str(seq[0][i])
            else:
                seq[j][i] = str(random.uniform(1, 100))

    with open(src,"w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(seq)

    for i in range(args.slaves):
        if i < 1:
            pass
        else:
            shutil.copyfile(src, "resource/slave" + str(i+1) + "/resource/telemetry.csv")

if __name__ == "__main__":
    info(host(data_list()))
    folder_create()
    generate_jmx(host(data_list()))
    gemerate_access_token_csv(env(data_list()))
    generate_tempery_csv()



