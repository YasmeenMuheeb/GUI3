import paramiko
from tqdm import tqdm_gui
import time
txt_arr = []
def connection(ip, username, password):
    empty = ""
    empty_bol = True
    cmd = ""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port=22, username=username, password=password)
    cmd = "supportshow"
    cmd2 = "show tech-support details"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    time.sleep(1000)
    output = stdout.readlines()
    for line in output:
        txt_arr.append(line)
        if line == empty:
            empty_bol = True
        else:
            empty_bol = False

    if cmd == "chassisshow":
        if not empty_bol:
            txt_arr.append("Brocade")
        else:
            txt_arr.append("Cisco")
    if cmd == "show sprom backplane 1":
        if not empty_bol:
            txt_arr.append("Cisco")
        else:
            txt_arr.append("Brocade")

    stdin, stdout, stderr = ssh.exec_command(cmd2)
    time.sleep(1000)
    output = stdout.readlines()
    for line in output:
        txt_arr.append(line)
        if line == empty:
            empty_bol = True
        else:
            empty_bol = False

    if cmd == "chassisshow":
        if not empty_bol:
            txt_arr.append("Brocade")
        else:
            txt_arr.append("Cisco")
    if cmd == "show sprom backplane 1":
        if not empty_bol:
            txt_arr.append("Cisco")
        else:
            txt_arr.append("Brocade")
    ssh.close()
    return txt_arr


def main(ip,username, password):
    connection(ip, username, password)

#main('10.60.23.26', 'root', 'Serv4EMC')
