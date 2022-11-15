"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-',
                        '*', '/', '&', ',', '<', '>', '=', '~', "#", "^", "|"}
        self.special_symbols = {"<": "&lt;", ">": "&gt;", chr(34): "&quot;",
                                "&": "&amp;"}
        self.keywords = {'class', 'constructor', 'function', 'method', 'field',
                         'static', 'var', 'int', 'char', 'boolean', 'void',
                         'true', 'false', 'null', 'this', 'let', 'do', 'if',
                         'else', 'while', 'return'}
        self.input_lines = input_stream.read().splitlines()
        self.create_processed_tokens()
        self.index = 0
        self.size_of_tokens = len(self.input_lines)



    def create_processed_tokens(self):
        self.input_lines = self.comments_remover()
        self.input_lines = self.remove_all_useless()
        self.input_lines = self.split_to_single()
        self.input_lines = self.final_split()

    def remove_all_useless(self):
        after_lst = []
        for line in self.input_lines:
            temp = line.replace("\t", " ")
            if temp != "":
                after_lst.append(temp)
        return after_lst

    def comments_remover(self):
        output = []
        incomment = False
        inquote = False
        for line in self.input_lines:
            new_line = ""
            last_one = ''
            for char in line:
                if incomment:
                    if last_one + char == "*/":
                        incomment = False
                elif not inquote and last_one + char == "/*":
                    new_line = new_line[:-1]
                    incomment = True
                elif not inquote and not incomment and last_one + char == "//":
                    new_line = new_line[:-1]
                    break
                elif char == chr(34) and not incomment:
                    if inquote:
                        inquote = False
                    else:
                        inquote = True
                    new_line += char
                elif inquote or not incomment:
                    new_line += char
                last_one = char
            output.append(new_line)
        return output

    def split_to_single(self):
        new_lst = []
        for line in self.input_lines:
            if chr(34) in line:
                qu_lst = line.split(chr(34))
                for i in range(len(qu_lst)):
                    if i % 2 == 0:
                        new_lst.extend(qu_lst[i].split())
                    else:
                        new_lst.append(chr(34) + qu_lst[i] + chr(34))
            else:
                new_lst.extend(line.split())
        return new_lst

    def final_split(self):
        new_lst = []
        for word in self.input_lines:
            if word.startswith(chr(34)):
                new_lst.append(word)
            elif word in self.symbols or word in self.keywords:
                new_lst.append(word)
            else:
                cur_word = ""
                for char in word:
                    if char in self.symbols:
                        if cur_word != "":
                            new_lst.append(cur_word)
                            cur_word = ""
                        new_lst.append(char)
                    else:
                        cur_word += char
                if cur_word != "":
                    new_lst.append(cur_word)
        return new_lst

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.index + 1 < self.size_of_tokens

    def get_cur_token(self):
        type = self.token_type()
        if type == "KEYWORD":
            return self.keyword()
        elif type == "SYMBOL":
            return self.symbol()
        elif type == "IDENTIFIER":
            return self.identifier()
        elif type == "INT_CONST":
            return str(self.int_val())
        elif type == "STRING_CONST":
            return self.string_val()


    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if self.has_more_tokens():
            self.index += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.input_lines[self.index] in self.keywords:
            return "KEYWORD"
        elif self.input_lines[self.index] in self.symbols:
            return "SYMBOL"
        elif self.input_lines[self.index].isdecimal():
            return "INT_CONST"
        elif self.input_lines[self.index].startswith(chr(34)):
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def next_token_type(self):
        if self.has_more_tokens():
            self.index += 1
            next_type = self.token_type()
            self.index -= 1
            return next_type

    def get_next_token(self):
        if self.has_more_tokens():
            self.index += 1
            next_token = self.get_cur_token()
            self.index -= 1
            return next_token

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.input_lines[self.index]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        if self.input_lines[self.index] in self.special_symbols:
            return self.special_symbols[self.input_lines[self.index]]
        else:
            return self.input_lines[self.index]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.input_lines[self.index]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.input_lines[self.index])

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.input_lines[self.index].replace(chr(34), "")


