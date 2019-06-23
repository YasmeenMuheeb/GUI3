#X = open(r"C:\Users\abdely3\Desktop\Automation\JAF1830ADTK-TC.txt")
#O = open(r"C:\Users\abdely3\Desktop\Automation\CiscoTry7.txt", "w")
#data = X.readlines()
import os
from builtins import enumerate

check_SN = False
notes_arr = [""]
def SN_check(SN_in, data, O):
    check_SN = False
    for i, line in enumerate(data):
        if "`show sprom backplane 1`" in line and not check_SN:
            for l in data[i:i+500]:
                if "Serial Number   :" in l:
                    SN = l.split(":", 1)[1]
                    if SN_in in SN:
                        check_SN = True
                        break
                    else:
                        check_SN = False
                if 'Product Number  :' in l:
                    if "C" in l.split("-")[1]:
                        model = "MDS-" + l.split("-")[1].split("C")[1]
                        notes_arr.append("Model => " + model)

    return check_SN


def MOD_check(data, O):
    check_MOD = True
    check_ED = False
    char_check = ""
    checked = False
    for i, line in enumerate(data):
        if "`show module`" in line:
            char_check = ''.join(line.split()[0][0])
            for l in data[i+1:i+10]:
                if "Mod" in l.split():
                    for j in data[i:i+1000]:
                        if "`show" not in j.split():
                            if "DS-X9316-SSNK9" in j:
                                #O.write("Disruptive Model Exists => Module " + j + "\n")
                                notes_arr.append("Disruptive Model Exists => Module " + j + "\n")
                                check_MOD = False
                            if "Supervisor" in j:
                                if "active *" or "ha-standby" in j and not check_ED:
                                    #O.write("Director Model" + "\n")
                                    check_ED = True
                            if "faulty" in j or "shutdown" in j or "powered-dn" in j or "down" in j or "DOWN" in j \
                                    or "UNKNOWN" in j or "fail" in j or "FAULTY" in j or "Faulty" in j or \
                                    "Powered-DN" in j or "Powered-Down" in j:
                                #O.write("Faulty Module => " + j + "\n")
                                notes_arr.append("Faulty Module => " + j + "\n")
                                check_MOD = False
                                break
                        else:
                            break
                else:
                    continue
    return check_MOD


def HW_check(data, O):
    check_HW = True
    v_check = False
    for i, line in enumerate(data):
        if "`show hardware`" in line and check_HW:
            char_check = ''.join(line.split()[0][0])
            for l in data[i + 1:i + 100]:
                if "Switch is booted up" in l:
                    for j in data[i+1:i+10000]:
                        if char_check not in j.split() and not v_check:
                            if "kickstart:" in j:
                                kickstart_version = j.split(": ", 1)[1].split()[1]
                                #O.write("\n" + "Current Version = " + kickstart_version + "\n")
                                v_check = True
                                #O.write("version --- Checked" + "\n")

                            if "Module" in j or "PS" in j or "Fan" in j or "Xbar" in j:
                                if "faulty" in j or "shutdown" in j or "powered-dn" in j or "down" in j or "DOWN" in j \
                                        or "UNKNOWN" in j or "fail" in j or "FAULTY" in j or "Faulty" in j or \
                                        "Powered-DN" in j or "Powered-Down" in j:
                                    #O.write("Faulty => " + j + "\n")
                                    notes_arr.append("Faulty => " + j + "\n")
                                    check_HW = False
                                    break
                        else:
                            break
    return kickstart_version


def ENV_check(data, O):
    check_env = True
    for i, line in enumerate(data):
        if "`show environment`" in line:
            char_check = ''.join(line.split()[0][0])
            for l in data[i + 1:i + 10]:
                if "Power Supply:" in l:
                    for j in data[i+1:i+10000]:
                        if "`show" not in j.split():
                            if "faulty" in j or "shutdown" in j or "powered-dn" in j or "down" in j or "DOWN" in j \
                                    or "UNKNOWN" in j or "fail" in j or "FAULTY" in j or "Faulty" in j or \
                                    "Powered-DN" in j or "Powered-Down" in j:
                                #O.write("Faulty => " + j + "\n")
                                notes_arr.append("Faulty => " + j + "\n")
                                check_env = False
                        else:
                            break
    return check_env


def vsan_check(data, O):
    check_vsan = True
    for i, line in enumerate(data):
        if "`show vsan`" in line:
            char_check = ''.join(line.split()[0][0])
            for l in data[i + 1:i + 1000]:
                if "`show" not in l:
                    if "vsan 1 information" in l:
                        for j in data[i+1:i+5]:
                            if "interoperability mode" in j:
                                if "default" not in j:
                                    #O.write("vsan 1 => " + j + "\n")
                                    notes_arr.append("vsan 1 => " + j + "\n")
                            if "state" in j:
                                if "active" not in j:
                                    #O.write("vsan 1 =>" + j + "\n")
                                    notes_arr.append("vsan 1 => " + j + "\n")

                        for t in data[i+5:i+1000]:
                            if "`show" not in t:
                                if "name: " in t:
                                    vsan_name = t.split("name:")[1]
                                    #O.write(vsan_name + "\n")
                                    notes_arr.append(vsan_name + "\n")
                                    for k in data[i:i+6]:
                                        if "state" in k:
                                            if "active" not in k:
                                                #O.write(k + "\n")
                                                notes_arr.append(k + "\n")
                                        if "interoperability mode" in k:
                                            if "default" not in k:
                                                #O.write(j + k + "\n")
                                                notes_arr.append(j + k + "\n")
                                        if "operational state" in k:
                                            if "down" in k:
                                                #O.write(j + k + "\n")
                                                notes_arr.append(j + k + "\n")
                                                check_vsan = False
                            else:
                                break
                else:
                    break

    return check_vsan


def fcs_check(data, O):
    check_fcs = True
    for i, line in enumerate(data):
        if "`show fcs ie`" in line:
            char_check = ''.join(line.split()[0][0])
            O.write(line)
            for l in data[i+1:i + 1000]:
                if "`show" not in l:
                    O.write(l)
                else:
                    break
    return check_fcs


def red_check(data, O):
    check_red = True
    for i, line in enumerate(data):
        if "`show system redundancy status`" in line:
            char_check = ''.join(line.split()[0][0])
            for l in data[i+1:i + 1000]:
                if "`show" not in l:
                    if "supervisor" in l:
                        for j in data[i:i+5]:
                            if "Redundancy state:" in j:
                                if "Standby" or "Active" in j:
                                    check_red = True
                                else:
                                    check_red = False
                else:
                    break
    return check_red

def model_vs_code(data):
    flag_6_2 = False
    flag_7_3 = False
    flag_8_4 = False
    upto_6_2 = ["9222i"]
    upto_7_3 = ["9506", "9509", "9513", "9148"]
    upto_8_4 = ["9710", "9250i", "9706", "9148S", "9148T", "9396S", "9178", "9132T", "9396T"]
    for i, line in enumerate(data):
        if "`show sprom backplane 1`" in line:
            for l in data[i:i + 500]:
                if 'Product Number  :' in l:
                    if "C" in l.split("-")[1]:
                        model =l.split("-")[1].split("C")[1]
                        for x in range(len(upto_6_2)):
                            if upto_6_2[x] in model:
                                flag_6_2 = True
                                break
                        for x in range(len(upto_7_3)):
                            if upto_7_3[x] in model:
                                flag_7_3 = True
                                break
                        for x in range(len(upto_8_4)):
                            if upto_8_4[x] in model:
                                flag_8_4 = True
                                break
    return flag_6_2, flag_7_3, flag_8_4


def upgrade_plan(data, O, current, target):

    flag_6_2, flag_7_3, flag_8_4 = model_vs_code(data)

    if flag_6_2:
        if "7.3" in target or "8.1" in target:
            O.write("\n" + "This model can only be upgraded to 6.2(x)" + "\n")
            return ""
    if flag_7_3:
        if "8." in target:
            O.write("\n" + "This model can only be upgraded to 7.3x" + "\n")
            return ""

    O.write("\n" + "Non-disruptive Path: " + current + " => ")
    if "5.0" in current:
        if "5.2" in target:
            # target_arr = ["5.2(8b)", "5.2(8c)", "5.2(8d)", "5.2(8e)", "5.2(8f)", "5.2(8h)", "5.2(8i)"]
            O.write(target)
            O.write("\n" + "\n" + "Number of steps => 1 Step" + "\n")
        elif "6.2" in target:
            arr_8f = ["6.2(3)", "6.2(5a)", "6.2(7)", "6.2(11b)", "6.2(13)", "6.2(13a)", "6.2(15)", "6.2(17)"]
            arr_8e = ["6.2(11)", "6.2(11c)", "6.2(11e)"]
            arr_8h = ["6.2(19)", "6.2(21)", "6.2(23)", "6.2(25)"]
            arr_8d = ["6.2(9a)", "6.2(9)", "6.2(7)"]
            for x in range(len(arr_8f)):
                if target in arr_8f:
                    O.write("5.2(8f) => " + target)
                    O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")
                    break
            for x in range(len(arr_8e)):
                if target in arr_8e:
                    O.write("5.2(8e) => " + target)
                    O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")
                    break
            for x in range(len(arr_8h)):
                if target in arr_8h:
                    O.write("5.2(8h) => " + target)
                    O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")
                    break
        #elif flag_6_2:
            #O.write("\n"+ "This model can only be upgarded to 6.2x" + "\n")
        elif "7.3" in target:
            if "7.3(0)D1(1)" in target:
                O.write("5.2(8h) => " + target)
                O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")
            else:
                O.write("5.2(8h) => 6.2(9) => " + target)
                O.write("\n" + "\n" + "Number of steps => 3 Steps" + "\n")
        #elif flag_7_3:
            #O.write("\n" + "This model can only be upgarded to 7.3x" + "\n")

    elif "5.2" in current:
        if "5.2" in target:
            O.write(target)
            O.write("\n" + "\n" + "Number of steps => 1 Step" + "\n")
        elif "6.2" in target:
            O.write(target)
            O.write("\n" + "\n" + "Number of steps => 1 Step" + "\n")
        elif flag_6_2:
            O.write("\n"+ "This model can only be upgarded to 6.2x" + "\n")

        elif "7.3" in target:
            if "7.3(0)D1(1)" in target:
                O.write(target)
                O.write("\n" + "\n" + "Number of steps => 1 Step" + "\n")
            else:
                O.write("6.2(9) => " + target)
                O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")

        elif "8." in target:
            if "5.2(8h)" not in current:
                O.write("5.2(8h) => 6.2(23) => ")
                if "8.1(1)" in target or "8.1(1a)" in target:
                    O.write(target)
                    O.write("\n" + "\n" + "Number of steps => 3 Step" + "\n")
                else:
                    O.write("8.1(1a) => " + target)
                    O.write("\n" + "\n" + "Number of steps => 4 Steps" + "\n")

    elif "6.2" in current:
        if "6.2" in target:
            O.write(target)
            O.write("\n" + "\n" + "Number of steps => 1 Step" + "\n")

        elif "7.3" in target:
            in_arr = False
            arr_2steps = ["6.2(3)", "6.2(5)", "6.2(5a)", "6.2(7)"]
            for x in range(len(arr_2steps)):
                if current in arr_2steps[x]:
                    O.write("6.2(9) => " + target)
                    O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")
                    in_arr = True
                    break
            if not in_arr:
                O.write(target)
                O.write("\n" + "\n" + "Number of steps => 1 Step" + "\n")

        elif "8." in target:
            curr_arr = ["6.2(3)", "6.2(5)", "6.2(5a)", "6.2(7)", "6.2(9)", "6.2(9a)", "6.2(11)",
                        "6.2(11b)", "6.2(11c)", "6.2(13)"]
            curr_arr2 = ["6.2(13a)", "6.2(17)", "6.2(19)", "6.2(23)", "6.2(25)", "6.2(27)"]
            curr_arr3 = ["6.2(21)"]

            if "8.1(1)" in target or "8.1(1a)" in target:
                for x in range(len(curr_arr)):
                    if current in curr_arr:
                        O.write("6.2(13a) => " + target)
                        O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")
                        break
                for x in range(len(curr_arr2)):
                    if current in curr_arr2:
                        O.write(target)
                        O.write("\n" + "\n" + "Number of steps => 1 Step" + "\n")
                        break
                for x in range(len(curr_arr3)):
                    if current in curr_arr3:
                        O.write("6.2(23) => " + target)
                        O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")
                        break
            else:
                for x in range(len(curr_arr)):
                    if current in curr_arr:
                        O.write("6.2(13a) => 8.1(1a) => " + target)
                        O.write("\n" + "\n" + "Number of steps => 3 Steps" + "\n")
                        break
                for x in range(len(curr_arr2)):
                    if current in curr_arr2:
                        O.write("8.1(1a) => " + target)
                        O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")
                        break
                for x in range(len(curr_arr3)):
                    if current in curr_arr3:
                        O.write("6.2(23) => 8.1(1a) => " + target)
                        O.write("\n" + "\n" + "Number of steps => 3 Steps" + "\n")
                        break

    elif "7.3" in current:
        if "7.3" in target:
            O.write("7.3(0)D1(1) => " + target)
            O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")

        if "8." in  target:
            if "8.1" in target:
                O.write(target)
                O.write("\n" + "\n" + "Number of steps => 1 Step" + "\n")

            else:
                O.write("8.1(1a) => " + target)
                O.write("\n" + "\n" + "Number of steps => 2 Steps" + "\n")

    elif "8." in current:
        O.write(target)
        O.write("\n" + "\n" + "Number of steps => 1 Step" + "\n")


def main(SN_in, target, basepath, fileName):
    X = open(fileName)
    O = open(os.path.join(basepath, SN_in + '_SRNotes.txt'), "w")
    data = X.readlines()
    #SN_in = input("Please Enter the SN \n")
    #target = input("Please Enter the target code \n ")

    if SN_check(SN_in, data, O):
        if MOD_check(data, O) and HW_check(data, O) and ENV_check(data, O) and vsan_check(data, O):
            O.write("\n" + "Results: " + "\n")
            O.write("\n" + "Status of health checks : " + "clean" + "\n")
            O.write("\n" + "Current Code: " + str(HW_check(data, O)) + "\n")
            O.write("\n" + "Requested/Target code: " + target + "\n")
            O.write("\n" + str(upgrade_plan(data, O, str(HW_check(data, O)), target)) + "\n")
            O.write("\n" + "Switch Serial Number: " + SN_in + "\n")
            O.write("\n")
            fcs_check(data, O)

        else:
            O.write("\n" + "Results: " + "\n")
            O.write("\n" + "Status of health checks : " + "Not clean" + "\n")
            O.write("\n" + "Current Code: " + str(HW_check(data, O)) + "\n")
            O.write("\n" + "Requested/Target code: " + target + "\n")
            O.write("\n" + "Switch Serial Number: " + SN_in + "\n")
            O.write("\n")
            fcs_check(data, O)
            O.write("Show module  => " + str(MOD_check(data, O)) + "\n")
            O.write("Show hardware  => " + str(HW_check(data, O)) + "\n")
            O.write("Show environment  => " + str(ENV_check(data, O)) + "\n")
            O.write("Show vsan  => " + str(vsan_check(data, O)) + "\n")
            O.write("Show fcs ie  => ")

    O.write("\n"+ "########################################################################################" + "\n")
    for x in range(len(notes_arr)):
        O.write("\n" + notes_arr[x] + "\n")

#main('JPG2103008D', '8.1(1a)', r'C:\Users\abdely3\Desktop', r'C:\Users\abdely3\Desktop\JPG2103008D-TC.txt')