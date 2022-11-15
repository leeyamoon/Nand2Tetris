import sys
import os

arithmetic_dict = {"add": "@SP\nA=M-1\nD=M\nM=0\nA=A-1\nD=D+M\nM=D"
                          "\nD=A+1\n@SP\nM=D\n",
                   "sub": "@SP\nA=M\nA=A-1\nD=M\nD=-D\nM=0\nA=A-1\nD=D+M\nM=D"
                          "\nD=A+1\n@SP\nM=D\n",
                   "neg": "@SP\nA=M-1\nM=-M\n",
                   "and": "@SP\nA=M\nA=A-1\nD=M\nM=0\nA=A-1\nD=D&M\nM=D"
                          "\nD=A+1\n@SP\nM=D\n",
                   "or": "@SP\nA=M\nA=A-1\nD=M\nM=0\nA=A-1\nD=D|M\nM=D"
                         "\nD=A+1\n@SP\nM=D\n",
                   "not": "@SP\nA=M-1\nM=!M\n",
                   "shiftright": "@SP\nA=M-1\nM=M>>\n",
                   "shiftleft": "@SP\nA=M-1\nM=M<<\n"
                   }
bool_dict = {"eq": "@SP\nA=M-1\nD=M\nM=0\nA=A-1\nD=D-M\nM=-1\n"
                   "@{0}\nD;JEQ\n@SP\nA=M-1\nA=A-1\nM=0\n({0})\n"
                   "@SP\nA=M-1\nD=A\n@SP\nM=D\n",
             "gt": "@SP\nM=M-1\nA=M\nD=M\n@R14\nM=D\n@SP\nA=M-1\nD=M\n@R13\n"
                   "M=D\n@FIRSTMIN{0}\nD;JLT\n@R14\nD=M\n@BOTHSAME{0}\nD;JGE\n"
                   "@SP\nA=M-1\nM=-1\n@ENDOF{0}\n0;JMP\n(FIRSTMIN{0})\n@R14\n"
                   "D=M\n@BOTHSAME{0}\nD;JLT\n@SP\nA=M-1\nM=0\n@ENDOF{0}\n"
                   "0;JMP\n(BOTHSAME{0})\n@SP\nA=M\nD=M\nA=A-1\nD=M-D\n"
                   "M=-1\n@ENDOF{0}\nD;JGT\n@SP\nA=M-1\nM=0\n(ENDOF{0})\n",
             "lt": "@SP\nM=M-1\nA=M\nD=M\n@R14\nM=D\n@SP\nA=M-1\nD=M\n@R13\n"
                   "M=D\n@FIRSTMIN{0}\nD;JLT\n@R14\nD=M\n@BOTHSAME{0}\nD;JGE\n"
                   "@SP\nA=M-1\nM=0\n@ENDOF{0}\n0;JMP\n(FIRSTMIN{0})\n@R14\n"
                   "D=M\n@BOTHSAME{0}\nD;JLT\n@SP\nA=M-1\nM=-1\n@ENDOF{0}\n"
                   "0;JMP\n(BOTHSAME{0})\n@SP\nA=M\nD=M\nA=A-1\nD=D-M\nM=-1\n"
                   "@ENDOF{0}\nD;JGT\n@SP\nA=M-1\nM=0\n(ENDOF{0})\n"}

push_pop_lcl_dict = {"push": "@{1}\nD=A\n@{0}\nA=D+M\nD=M\n@SP\nA=M\nM=D\n"
                             "@SP\nM=M+1\n",
                     "pop": "@{1}\nD=A\n@{0}\nA=D+M\nD=A\n@R13\nM=D\n@SP\n"
                            "M=M-1\nA=M\nD=M\nM=0\n@R13\nA=M\nM=D\n@R13\nM=0\n"}
first_type_seg = {"local": "LCL", "argument": "ARG", "this": "THIS",
                  "that": "THAT"}
cons_type_seg = {"constant": "@{0}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"}
static_dict = {"push": "@{0}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
               "pop": "@SP\nM=M-1\nA=M\nD=M\nM=0\n@{0}\nM=D\n"}
temp_dict = {
    "push": "@{0}\nD=A\n@5\nA=A+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
    "pop": "@{0}\nD=A\n@5\nA=A+D\nD=A\n@R13\nM=D\n@SP\nM=M-1\nA=M\n"
           "D=M\nM=0\n@R13\nA=M\nM=D\n@R13\nM=0\n"}
pointer_dict = {"push": "@{0}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n",
                "pop": "@SP\nM=M-1\nA=M\nD=M\nM=0\n@{0}\nM=D\n"}
branch_dict = {"label": "({0})\n", "goto": "@{0}\n0;JMP\n",
               "if-goto": "@SP\nM=M-1\nA=M\nD=M\n@{0}\nD;JNE\n"}
function_dict = {"function": "({0})\n",
                 "call": "@{0}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                         "@LCL\nD=M\n@SP\nA=M\nM=D\n" 
                         "@SP\nM=M+1\n@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                         "@THIS\nD=M\n@SP\nA=M\n"
                         "M=D\n@SP\nM=M+1\n@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\n"
                         "M=M+1\n@5\nD=A\n@SP\n"
                         "D=M-D\n@{2}\nD=D-A\n@ARG\nM=D\n@SP\nD=M\n"
                         "@LCL\nM=D\n@{1}\n"
                         "0;JMP\n({0})\n",
                 "return": "@LCL\nD=M\n@R13\nM=D\n@5\nD=A\n@R13\nD=M-D\nA=D"
                           "\nD=M\n@R14\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@ARG\n"
                           "A=M\nM=D\n@ARG\nD=M+1\n@SP\nM=D\n@R13\nM=M-1\n"
                           "A=M\nD=M\n@THAT\nM=D\n@R13\nM=M-1\nA=M\nD=M\n"
                           "@THIS\nM=D\n@R13\nM=M-1\nA=M\nD=M\n@ARG\nM=D\n"
                           "@R13\nM=M-1\nA=M\nD=M\n@LCL\nM=D\n@R14\nA=M\n"
                           "0;JMP\n"}
counter_dict = {"counter": 0, "ret_counter":0}

file_name = sys.argv[1]


def remove_all_useless(one_line):
    fixed_line = one_line.split("/")[0]
    fixed_line = fixed_line.replace("\n", "")
    return fixed_line


def arith_log_translate(splited_command):
    if splited_command[0] in arithmetic_dict:
        return arithmetic_dict[splited_command[0]]
    elif splited_command[0] in bool_dict:
        temp = bool_dict[splited_command[0]].format("PLACE." +
                                                    str(counter_dict[
                                                            "counter"]))
        counter_dict["counter"] += 1
        return temp
    else:
        return ""


def memory_translator(splited_commend, cur_name):
    if splited_commend[0] in push_pop_lcl_dict and splited_commend[1] in\
            first_type_seg:
        return push_pop_lcl_dict[splited_commend[0]].format \
            (first_type_seg[splited_commend[1]], splited_commend[2])
    elif splited_commend[1] in cons_type_seg:
        return cons_type_seg["constant"].format(splited_commend[2])
    elif splited_commend[1] == "static":
        var_name = cur_name.split(chr(92))[-1] + "." + str(splited_commend[2])
        return static_dict[splited_commend[0]].format(var_name)
    elif splited_commend[1] == "temp":
        return temp_dict[splited_commend[0]].format(splited_commend[2])
    elif splited_commend[1] == "pointer":
        this_or_that = 3 + int(splited_commend[2])
        return pointer_dict[splited_commend[0]].format(this_or_that)
    else:
        return ""


def branch_translator(splited_command):
    return branch_dict[splited_command[0]].format(splited_command[1])


def function_translator(splited_commend):
    if splited_commend[0] == "return":
        return function_dict["return"]
    elif splited_commend[0] == "function":
        temp_exp = function_dict["function"].format(splited_commend[1])
        for i in range(int(splited_commend[2])):
            temp_exp += cons_type_seg["constant"].format("0")
        return temp_exp
    elif splited_commend[0] == "call":
        gen_return = splited_commend[1] + "." + splited_commend[2] + "." + \
                     str(counter_dict["ret_counter"]) + ".return"
        counter_dict["ret_counter"] += 1
        return function_dict["call"].format(gen_return, splited_commend[1],
                                            splited_commend[2])


def kind_of_command(command, cur_name):
    final_command = "//" + command + "\n"
    temp_com = remove_all_useless(command).split()
    if temp_com == "" or temp_com == []:
        return ""
    elif temp_com[0] in arithmetic_dict or temp_com[0] in bool_dict:
        final_command += arith_log_translate(temp_com)
    elif temp_com[0] in push_pop_lcl_dict and (temp_com[1] in first_type_seg or
            temp_com[1] in ["constant", "static", "temp", "pointer"]):
        final_command += memory_translator(temp_com, cur_name)
    elif temp_com[0] in branch_dict:
        final_command += branch_translator(temp_com)
    elif temp_com[0] in function_dict:
        final_command += function_translator(temp_com)
    else:
        final_command += ""
    return final_command


def Translator():
    lst_of_vm = []
    loc_file_name = file_name
    if os.path.isdir(file_name):
        temp_lst = os.listdir(file_name)
        for unknown_file in temp_lst:
            if unknown_file.endswith(".vm"):
                lst_of_vm.append(os.path.join(file_name, unknown_file))
        loc_file_name = os.path.join(file_name, os.path.split(file_name)[-1])
    else:
        lst_of_vm.append(file_name)
    asm_file = open(os.path.join(os.getcwd() ,loc_file_name.split(".")[0]+ ".asm"), "w")
    asm_file.write("@256\nD=A\n@SP\nM=D\n")
    asm_file.write(kind_of_command("call Sys.init 0", "Sys"))
    for file in lst_of_vm:
        cur_name = file[0:-3].split("/")[-1]
        with open(file, "r") as VMfile:
            for line in VMfile:
                translation_output = kind_of_command(line, cur_name)
                asm_file.write(translation_output)
    asm_file.close()


Translator()
