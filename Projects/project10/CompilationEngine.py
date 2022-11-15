"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: typing.TextIO,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output = output_stream
        self.tokenizer = JackTokenizer(input_stream)
        self.stack_of_tags = []

    def write_token(self):
        type_dict = {"KEYWORD": "keyword", "SYMBOL": "symbol", "INT_CONST": "integerConstant",
                     "STRING_CONST": "stringConstant", "IDENTIFIER": "identifier"}
        token_type = type_dict[self.tokenizer.token_type()]
        token = "<" + token_type + ">" + self.tokenizer.get_cur_token() + "</" + token_type + ">\n"
        self.output.write(token)
        self.tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output.write("<class>\n")
        self.write_token()  # class
        self.write_token()  # class_name
        self.write_token()  # {
        self.compile_class_var_dec()
        self.compile_subroutine()
        self.write_token()  # }
        self.output.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        while self.tokenizer.get_cur_token() in ["static", "field"]:
            self.output.write("<classVarDec>\n")
            self.write_token()
            while self.tokenizer.get_cur_token() != ";":
                self.write_token()
            self.write_token()
            self.output.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        while self.tokenizer.get_cur_token() in ["constructor", "function", "method"]:
            self.output.write("<subroutineDec>\n")
            self.write_token()  # method, function, or constructor
            self.write_token()  # void | type
            self.write_token()  # subroutine name
            self.write_token()  # (
            self.compile_parameter_list()
            self.write_token()  # )
            self.output.write("<subroutineBody>\n")
            self.write_token()  # {
            self.compile_var_dec()
            self.compile_statements()
            self.write_token()  # }
            self.output.write("</subroutineBody>\n")
            self.output.write("</subroutineDec>\n")


    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output.write("<parameterList>\n")
        while self.tokenizer.get_cur_token() != ")":
            self.write_token()
        self.output.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        while self.tokenizer.get_cur_token() == "var":
            self.output.write("<varDec>\n")
            while self.tokenizer.get_cur_token() != ";":
                self.write_token()
            self.write_token()
            self.output.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output.write("<statements>\n")
        while self.tokenizer.get_cur_token() in ["let", "if", "while", "do", "return"]:
            if self.tokenizer.get_cur_token() == "let":
                self.compile_let()
            elif self.tokenizer.get_cur_token() == "if":
                self.compile_if()
            elif self.tokenizer.get_cur_token() == "while":
                self.compile_while()
            elif self.tokenizer.get_cur_token() == "do":
                self.compile_do()
            elif self.tokenizer.get_cur_token() == "return":
                self.compile_return()
        self.output.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output.write("<doStatement>\n")
        self.write_token()  # do
        self.compile_subroutine_call()
        self.write_token()  # ;
        self.output.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output.write("<letStatement>\n")
        self.write_token()  # let
        self.write_token()  # varName
        if self.tokenizer.get_cur_token() == "[":
            self.write_token()   # [
            self.compile_expression()
            self.write_token()   # ]
        self.write_token()   # =
        self.compile_expression()
        self.write_token()   # ;
        self.output.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output.write("<whileStatement>\n")
        self.write_token()  # while
        self.write_token()  # (
        self.compile_expression()
        self.write_token()  # )
        self.write_token()  # {
        self.compile_statements()
        self.write_token()  # }
        self.output.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output.write("<returnStatement>\n")
        self.write_token()  # return
        if self.tokenizer.get_cur_token() != ";":
            self.compile_expression()
        self.write_token()  # ;
        self.output.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output.write("<ifStatement>\n")
        self.write_token()  # if
        self.write_token()  # (
        self.compile_expression()
        self.write_token()  # )
        self.write_token()  # {
        self.compile_statements()
        self.write_token()  # }
        if self.tokenizer.get_cur_token() == "else":
            self.write_token()  # else
            self.write_token()  # {
            self.compile_statements()
            self.write_token()  # }
        self.output.write("</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output.write("<expression>\n")
        self.compile_term()
        while self.tokenizer.get_cur_token() in ["+", "-", "*", "/", "&", "|", "<", ">", "=", "&lt;", "&gt;", "&amp;"]:
            self.write_token()  # the op
            self.compile_term()
        self.output.write("</expression>\n")


    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.output.write("<term>\n")
        if self.tokenizer.token_type() in ["INT_CONST", "STRING_CONST"]:
            self.write_token()  # the number
        elif self.tokenizer.get_cur_token() in ["true", "false", "null", "this"]:
            self.write_token()  # the keywordConstant
        elif self.tokenizer.get_cur_token() == "(":
            self.write_token()  # (
            self.compile_expression()
            self.write_token()  # )
        elif self.tokenizer.get_cur_token() in ["-", "~"]:
            self.write_token()  # ~ or -
            self.compile_term()
        elif self.tokenizer.get_next_token() in [".", "("]:
            self.compile_subroutine_call()
        else:
            self.write_token()  #varName
            if self.tokenizer.get_cur_token() == "[":
                self.write_token()  # [
                self.compile_expression()
                self.write_token()  # ]
        self.output.write("</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output.write("<expressionList>\n")
        if self.tokenizer.get_cur_token() != ")":
            self.compile_expression()
            while self.tokenizer.get_cur_token() == ",":
                self.write_token()  # ,
                self.compile_expression()
        self.output.write("</expressionList>\n")


    def compile_subroutine_call(self) -> None:
        self.write_token()
        if self.tokenizer.get_cur_token() == "(":
            self.write_token()
            self.compile_expression_list()
            self.write_token()
        elif self.tokenizer.get_cur_token() == ".":
            self.write_token()
            self.write_token()
            self.write_token()
            self.compile_expression_list()
            self.write_token()
