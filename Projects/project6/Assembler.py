import sys
import os

dest_dict = {"": "000", "M": "001", "D": "010", "MD": "011", "A": "100",
             "AM": "101", "AD": "110", "AMD": "111"}
comp_dict = {"0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100",
             "A": "0110000", "M": "1110000", "!D": "0001101", "!A": "0110001",
             "!M": "1110001", "-D": "0001111", "-A": "0110011",
             "-M": "1110011",
             "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
             "D-1": "0001110",
             "A-1": "0110010", "M-1": "1110010", "D+A": "0000010",
             "D+M": "1000010",
             "D-A": "0010011", "D-M": "1010011", "A-D": "0000111",
             "M-D": "1000111",
             "D&A": "0000000", "D&M": "1000000", "D|A": "0010101",
             "D|M": "1010101", "D<<": "0110000", "A<<": "0100000",
             "M<<": "1100000", "D>>": "0010000", "A>>": "0000000",
             "M>>": "1000000"}
jump_dict = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100",
             "JNE": "101", "JLE": "110", "JMP": "111"}

var_dict = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6,
            "R7": 7, "R8": 8,
            "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14,
            "R15": 15,
            "THIS": 3, "THAT": 4, "SCREEN": 16384, "KBD": 24576, "SP": 0,
            "LCL": 1, "ARG": 2}

the_asm_file = sys.argv[1]


def convert_to_bin(address):
    """type 0 (with @)"""
    if not address[0].isdigit():
        temp = var_dict[address]
    else:
        temp = address
    n = int(temp)
    n = bin(n)
    n = n[2:]
    amount_of_zero = 16 - len(n)
    return (amount_of_zero * "0") + n


def type_one_to_bin(commend):
    """convert to type one"""
    the_dest = dest_dict[""]
    temp_comp = comp_dict["D"]
    the_jump = jump_dict[""]
    if "=" in commend and ";" in commend:
        the_dest = dest_dict[commend.split("=")[0]]
        temp_commend = commend.replace(commend.split("=")[0], "")
        temp_commend = temp_commend.replace("=", "")
        temp_comp = temp_commend.split(";")[0]
        the_jump = jump_dict[temp_commend.split(";")[1]]
    elif "=" in commend:
        the_dest = dest_dict[commend.split("=")[0]]
        temp_comp = commend.split("=")[1]
    elif ";" in commend:
        temp_comp = commend.split(";")[0]
        the_jump = jump_dict[commend.split(";")[1]]
    the_comp = comp_dict[temp_comp]
    if "<" in temp_comp or ">" in temp_comp:
        the_output = "101" + the_comp + the_dest + the_jump
    else:
        the_output = "111" + the_comp + the_dest + the_jump
    return the_output


def remove_all_useless(one_line):
    fixed_line = one_line.replace(" ", "")
    fixed_line = fixed_line.split("/")[0]
    fixed_line = fixed_line.replace("\n", "")
    return fixed_line


def pre_run(file):
    counter = 0
    with open(file, "r") as the_file:
        for line in the_file:
            temp_line = remove_all_useless(line)
            if temp_line == "":
                continue
            elif temp_line[0] == "(":
                var_dict[temp_line[1:-1]] = counter
            else:
                counter += 1
    with open(file, "r") as the_file:
        n = 16
        for line in the_file:
            temp_line = remove_all_useless(line)
            if temp_line == "":
                continue
            elif temp_line[0] == "@" and not temp_line[1].isdigit():
                if temp_line[1:] not in var_dict:
                    var_dict[temp_line[1:]] = n
                    n += 1


def translate_one_file(file):
    hack_name = file.replace(".asm", ".hack")
    hack_file = open(hack_name, "w+")
    pre_run(file)
    with open(file, 'r+') as asm_file:
        for line in asm_file:
            temp_line = remove_all_useless(line)
            if temp_line == "" or temp_line[0] == "(":
                continue
            elif temp_line[0] == "@":
                line_commend = convert_to_bin(temp_line[1:])
            else:
                line_commend = type_one_to_bin(temp_line)
            hack_file.write(line_commend + "\n")
    hack_file.close()

def assembler():
    if os.path.isdir(the_asm_file):
        lst_of_all = os.listdir(the_asm_file)
        lst_of_asm = []
        for file in lst_of_all:
            if file.endswith(".asm"):
                lst_of_asm.append(file)
        for true_file in lst_of_asm:
            translate_one_file(the_asm_file +"/" + true_file)
    else:
        translate_one_file(the_asm_file)



assembler()
