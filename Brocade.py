import os

Version = False
SW_CMD = False
above_7_4 = False
sensor_CMD = False
ha_CMD = False
time_Check = False
slot_CMD = False
fabric_CMD = False
sw_state_CMD = False
fos_CMD = False
DS_model = False
clean = True

arr_errors = []

switch_type = ""


def chassis_check(SN_in, data, O):
    correct_SW = False
    for i, line in enumerate(data):
        if "chassisshow        :" in line:
            for l in data[i: i + 500]:
                if "Chassis Family" in l:
                    print(l)
                    model = l.split(":", 1)[1]
                    for x in range(len(arr_errors)):
                        if ("Model => " + model) not in arr_errors:
                            arr_errors.append("Model => " + model)
                if "Factory" in l:
                    continue
                elif "Serial Num:" in l:
                    l.split(":   ", 1)
                    print(l)
                    SN = l.split(":   ", 1)[1]
                    if SN_in in SN:
                        correct_SW = True
                        break
                    else:
                        O.write("Serial Number does not match" + "\n")
    return correct_SW


def firmware_check(data, O):
    Version = False
    for i, line in enumerate(data):
        if "firmwareshow -v       :" in line or "firmwareshow       :" in line and not Version:
            for l in data[i: i + 10]:
                if "FOS  " in l and not Version:
                    firmware = l.split("FOS ")[1].split()[0]
                    Version = True

    return firmware


def switchshow_check(data, O):
    SW_CMD = True
    checked = False
    in_arr = False
    for i, line in enumerate(data):
        if line.startswith("switchshow        :") and not checked:
            for l in data[i: i + 15]:
                if "switchType:" in l:
                    switch_type = l.split(":")[1]
                    if ("Switch Model => " + switch_type) not in arr_errors:
                        arr_errors.append("Switch Model => " + switch_type)
                        in_arr = True
                if "switchState" in l:
                    if "Online" in l:
                        continue
                    else:
                        if l not in arr_errors:
                            arr_errors.append(l)
                        SW_CMD = False
                if "switchMode" in l:
                    if "Native" in l:
                        continue
            checked = True
    return SW_CMD


def sensor_check(data, O):
    checked = False
    sensor_CMD = True
    for i, line in enumerate(data):
        if "sensorshow        :" in line and sensor_CMD and not checked:
            for l in data[i: i + 150]:
                if "FAULTY" in l:
                    if ("Fault Sensor Error => " + l) not in arr_errors:
                        #O.write("\n" + "Fault Sensor Error => " + "\n")
                        arr_errors.append(l)
                    sensor_CMD = False

    checked = True
    return sensor_CMD


def hashow_check(data, O):
    checked = False
    ha_CMD = True
    time_Check = False
    for i, line in enumerate(data):
        if "hashow" or "hadump" in line and ha_CMD and not DS_model and not checked:
            for l in data[i: i + 10]:
                if "TIME_STAMP:" in l and not time_Check:
                    time = l.split(": ")[1]
                    O.write("\n" + "Date = " + time + "\n")
                    time_Check = True
                    continue
                if "not supported" or "Not supported" in l and ha_CMD:
                    DS_model = True
                    ha_CMD = True
                    break
                else:
                    if "Recovered" in l and ha_CMD:
                        continue
                    if "Standby" in l and "Healthy" in l and ha_CMD:
                        continue
                    if "HA enabled, Heartbeat Up, HA State synchronized" in l:
                        ha_CMD = True
                    elif "HA disabled" or "Down" in l or "not" in l or "Not" in l:
                        ha_CMD = False
                        break
    checked = True
    return ha_CMD


def slotshow_check(data, O):
    slot_CMD = True
    checked = False
    for i, line in enumerate(data):
        if not DS_model:
            if "slotshow:" in line and slot_CMD and not checked:
                for l in data[i:i + 20]:
                    if "FAULTY" in l or "UNKNOWN" in l or "OFF" in l:
                        if l not in arr_errors:
                            arr_errors.append(l)
                        slot_CMD = False
                    else:
                        continue
    checked = True
    return slot_CMD


def fabric_check(data, O):
    checked = False
    version_chk = False
    for i, line in enumerate(data):
        if not checked:
            if "fabricshow        :" in line:
                for l in data[i+1: i+3]:
                    if "Switch ID" in l:
                        for k in data[i+1: i+50]:
                            if "The Fabric has" not in k:
                                O.write(k)
                            else:
                                break
            if "fabricshow -version" in line and not version_chk:
                for l in data[i+1: i+3]:
                    if "Switch ID" in l:
                        for k in data[i+1: i+50]:
                            if "The Fabric has" not in k:
                                O.write(k)
                                checked = True
                            else:
                                break


def state_check(data, O):
    checked = False
    sw_state_CMD = True
    for i, line in enumerate(data):
        if "Switch Health Report" in line and not checked:
            for l in data[i:i+20]:
                if "SwitchState:" in l:
                    if "HEALTHY" in l:
                        for k in data[i+1: i + 15]:
                            if "DOWN" in k or "UNKOWN" in k:
                                if k not in arr_errors:
                                    arr_errors.append("\n")
                                    arr_errors.append(l)
                                    arr_errors.append(k)
                                sw_state_CMD = False
                    else:
                        for k in data[i+1: i + 15]:
                            if "DOWN" in k or "UNKOWN" in k:
                                if k not in arr_errors:
                                    arr_errors.append("\n")
                                    arr_errors.append(l)
                                    arr_errors.append(k)
                        sw_state_CMD = False

        elif "Current Switch Policy Status" in line and not checked:
            if "HEALTHY" not in line:
                #O.write("\n" + "Error => " + line + "\n")
                if line not in arr_errors:
                    arr_errors.append(line)
                sw_state_CMD = False

    checked = True
    return sw_state_CMD


def fos_check(data, O):
    fos_CMD = False
    for i, line in enumerate(data):
        if "fosconfig --show       :" in line and not fos_CMD:
            for l in data[i:i + 10]:
                if "Virtual Fabric" or "Virtual Fabric:Service not supported on this Platform" in l:
                    if "disabled" in l:
                        break
                    elif "Service not supported on this Platform" in l:
                        break
                    elif "enable" in l:
                        if l not in arr_errors:
                            arr_errors.append(l)
        fos_CMD = True


def ficon(data, O):
    Ficon = False
    for i, line in enumerate(data):
        if "supportshow groups enabled:" in line:
            for l in data[i+1:i+30]:
                if "ficon" in l:
                    if "enabled" in l:
                        Ficon = True
                        if l not in arr_errors:
                            arr_errors.append(l)
                    else:
                        Ficon = False
    return Ficon


def clean_check(data, O):
    if sensor_check(data, O) and switchshow_check(data, O) and state_check(data, O) and \
            hashow_check(data, O) and slotshow_check(data, O):
        O.write("\n" + "Status of health checks : " + "clean" + "\n")
        clean = True
    else:
        O.write("\n" + "Status of health checks : " + "Not clean" + "\n")
        clean = False

    return clean


def model_vs_code(data):
    upto_7_4 = False
    sw_7_4_2d = ["62", "77", "71", "64", "67", "83"]
    for i, line in enumerate(data):
        if line.startswith("switchshow        :"):
            for l in data[i: i + 15]:
                if "switchType:" in l:
                    switch_type = l.split(":")[1]
                    for x in range(len(sw_7_4_2d)):
                        if switch_type.startswith(sw_7_4_2d[x]):
                            upto_7_4 = True
                        else:
                            upto_7_4 = False

    return upto_7_4


def upgrade_path(data, O, target):

    current = str(firmware_check(data, O))
    current_arr = ["6.1", "6.2", "6.3", "6.4", "7.0", "7.1", "7.2", "7.3", "7.4", "8.0", "8.1", "8.2"]
    target_arr = ["6.1", "6.2", "6.3", "6.4", "7.0", "7.1", "7.2", "7.3", "7.4", "8.0", "8.1", "8.2"]
    counter = 0
    if not ficon(data, O):
        print(model_vs_code(data))
        if not model_vs_code(data):
            print("aa")
            for i in range(len(current_arr)):
                if current_arr[i] in current and target_arr[i] in current:
                    O.write("Non-disruptive upgrade plan: ")
                    O.write(current + " => ")
                    for j in range(len(target_arr)):
                        if target_arr[j] in current:
                            k = j+1
                            while k in range(len(target_arr)):
                                if target.startswith(target_arr[k]):
                                    O.write(target)
                                    counter = counter + 1
                                    break
                                elif target_arr[k] == "6.2":
                                    O.write("6.2.2b => ")
                                    counter = counter + 1
                                elif target_arr[k] == "6.3":
                                    O.write("6.3.2b => ")
                                    counter = counter + 1
                                elif target_arr[k] == "6.4":
                                    O.write("6.4.3g => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.0":
                                    O.write("7.0.2c => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.1":
                                    O.write("7.1.1c1 => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.2":
                                    O.write("7.2.1g => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.3":
                                    O.write("7.3.2b => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.4":
                                    O.write("7.4.2d => ")
                                    counter = counter + 1
                                elif target_arr[k] == "8.0":
                                    O.write("8.0.2f => ")
                                    counter = counter + 1
                                elif target_arr[k] == "8.1":
                                    O.write("8.1.2f => ")
                                    counter = counter + 1
                                k = k+1
                    O.write("Number of steps => " + str(counter))
        else:
            print("ujyg")
            current_arr = ["6.1", "6.2", "6.3", "6.4", "7.0", "7.1", "7.2", "7.3", "7.4"]
            target_arr = ["6.1", "6.2", "6.3", "6.4", "7.0", "7.1", "7.2", "7.3", "7.4"]
            for i in range(len(current_arr)):
                if current_arr[i] in current:
                    O.write("Non-disruptive upgrade plan: ")
                    O.write(current + " => ")
                    for j in range(len(target_arr)):
                        if target_arr[j] in current:
                            k = j + 1
                            while k in range(len(target_arr)):
                                if target.startswith(target_arr[k]):
                                    O.write(target)
                                    counter = counter + 1
                                    break
                                elif target_arr[k] == "6.2":
                                    O.write("6.2.2b => ")
                                    counter = counter + 1
                                elif target_arr[k] == "6.3":
                                    O.write("6.3.2b => ")
                                    counter = counter + 1
                                elif target_arr[k] == "6.4":
                                    O.write("6.4.3g => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.0":
                                    O.write("7.0.2c => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.1":
                                    O.write("7.1.1c1 => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.2":
                                    O.write("7.2.1g => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.3":
                                    O.write("7.3.2b => ")
                                    counter = counter + 1
                                elif target_arr[k] == "7.4":
                                    O.write("7.4.2d")
                                    counter = counter + 1
                        else:
                            O.write("7.4.2d")
                            counter = counter + 1
                            O.write("\n" + "This switch model can only be upgraded to 7.4.x Family" + "\n")
                            break
                    O.write("Number of steps => " + str(counter))

    else:

        current_arr = ["6.1", "6.2", "6.3", "6.4", "7.0", "7.1", "7.2", "7.3", "7.4", "8.0", "8.1"]
        target_arr = ["6.1", "6.2", "6.3", "6.4", "7.0", "7.1", "7.2", "7.3", "7.4", "8.0", "8.1"]

        for i in range(len(current_arr)):
            if current_arr[i] in current and target_arr[i] in current:
                O.write("Non-disruptive upgrade plan: ")
                O.write(current + " => ")
                for j in range(len(target_arr)):
                    if target_arr[j] in current:
                        k = j+1
                        while k in range(len(target_arr)):
                            if target.startswith(target_arr[k]):
                                O.write(target)
                                counter = counter + 1
                                break
                            elif target_arr[k] == "7.1":
                                O.write("7.1.0c => ")
                                counter = counter + 1
                            elif target_arr[k] == "7.2":
                                O.write("7.2.1d => ")
                                counter = counter + 1
                            elif target_arr[k] == "7.3":
                                O.write("7.3.0b/7.3..1c => ")
                                counter = counter + 1
                            elif target_arr[k] == "7.4":
                                O.write("7.4.1d/7.4.2a => ")
                                counter = counter + 1
                            elif target_arr[k] == "8.0":
                                O.write("8.0.1b => ")
                                counter = counter + 1
                            elif target_arr[k] == "8.1":
                                O.write("8.1.0c/8.1.2a")
                                counter = counter + 1
                            else:
                                O.write("Not FICON Supported Code")
                            k = k+1
                    else:
                        O.write("8.1.0c/8.1.2a")
                        counter = counter + 1
                        O.write("Number of steps => " + str(counter))


def main(SN_in, target, basepath, fileName):
    #basepath = r'C:\Users\abdely3\Desktop\Automation'
    #entry = str(SN_in) + '-TC.txt'
    X = open(fileName)
    #X = open(r"C:\Users\abdely3\Desktop\22www.txt")
    #O = open(r"C:\Users\abdely3\Desktop\Automation\Test5.txt", "w")
    O = open(os.path.join(basepath, SN_in + '_SRNotes.txt'), "w")
    data = X.readlines()
    print(SN_in)

    if chassis_check(SN_in, data, O):
        print("done")
        O.write("\n" + "Results: " + "\n")
        if clean_check(data, O):
            O.write("\n" + "Current Code: " + firmware_check(data, O) + "\n")
            O.write("\n" + "Requested/Target code: " + target + "\n")
            O.write("\n")
            O.write("\n" + str(upgrade_path(data, O, target)) + "\n")
            O.write("\n")
            O.write("\n" + "Switch Serial Number: " + SN_in + "\n")
            O.write("\n")
            O.write("\n" + str(fabric_check(data, O)) + "\n")
        else:
            print("Not clean")
            O.write("\n" + "Current Code: " + firmware_check(data, O) + "\n")
            O.write("\n" + "Requested/Target code: " + target + "\n")
            O.write("\n" + "Switch Serial Number: " + SN_in + "\n")
            O.write("\n")
            O.write("\n" + str(fabric_check(data, O)) + "\n")
            if not sensor_check(data, O):
                O.write("\n" + "Sensor check failed" + "\n")
            if not switchshow_check(data, O):
                O.write("\n" + "switchshow check failed" + "\n")
            if not state_check(data, O):
                O.write("\n" + "Switch State check failed" + "\n")
            if not hashow_check(data, O):
                O.write("\n" + "Hashow check failed" + "\n")
            if not slotshow_check(data, O):
                O.write("\n" + "Slotshow check failed" + "\n")
            O.write("\n" + "#########################################################################" + "\n")

        for x in range(len(arr_errors)):
            O.write(arr_errors[x])

#main("BRCASS1937L00E", "8.2.0b", os.path.dirname(r'C:\Users\abdely3\Desktop\BRCASS1937L00E-TC.txt'), r'C:\Users\abdely3\Desktop\BRCASS1937L00E-TC.txt')

