"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


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
        self.tokenizer = JackTokenizer(input_stream)
        self.tables = SymbolTable()
        self.output = VMWriter(output_stream)
        self.class_name = ""
        self.counter = 0

    def return_token(self):
        cur = self.tokenizer.get_cur_token()
        self.tokenizer.advance()
        return cur

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.tokenizer.advance()  # class
        self.class_name = self.return_token()  # class_name
        self.tokenizer.advance()  # {
        self.compile_class_var_dec()
        self.compile_subroutine()
        self.tokenizer.advance()  # }

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        while self.tokenizer.get_cur_token() in ["static", "field"]:
            kind_of = self.return_token()  # static or field
            type_of = self.return_token()  # type
            cur_var = self.return_token()  # the var
            self.tables.define(cur_var, type_of, kind_of)
            while self.tokenizer.get_cur_token() == ",":
                self.tokenizer.advance()  # ,
                cur_var = self.return_token()  # the var
                self.tables.define(cur_var, type_of, kind_of)
            self.tokenizer.advance()  # ;

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        while self.tokenizer.get_cur_token() in ["constructor", "function", "method"]:
            self.tables.start_subroutine()
            subroutine_kind = self.return_token()  # method, function, or constructor
            subroutine_type = self.return_token()  # void | type
            subroutine_name = self.return_token()  # subroutine name
            if subroutine_kind == "method":
                self.tables.define("this", self.class_name, "arg")
            self.tokenizer.advance()  # (
            n_arg = self.compile_parameter_list()
            if subroutine_kind == "method":
                n_arg += 1
            self.tokenizer.advance()  # )
            self.tokenizer.advance()  # {
            self.compile_var_dec()
            self.output.write_function(self.class_name + "." + subroutine_name, self.tables.var_count("var"))
            if subroutine_kind == "constructor":
                self.output.write_push("constant", self.tables.var_count("field"))
                self.output.write_call("Memory.alloc", 1)
                self.output.write_pop("pointer", 0)
            elif subroutine_kind == "method":
                self.output.write_push("arg", 0)
                self.output.write_pop("pointer", 0)
            self.compile_statements()
            self.tokenizer.advance()  # }

    def compile_parameter_list(self) -> int:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        arg_counter = 0
        if self.tokenizer.get_cur_token() != ")":
            arg_counter += 1
            arg_type = self.return_token()
            arg_name = self.return_token()
            self.tables.define(arg_name, arg_type, "arg")
            while self.tokenizer.get_cur_token() == ",":
                self.tokenizer.advance()
                arg_counter += 1
                arg_type = self.return_token()
                arg_name = self.return_token()
                self.tables.define(arg_name, arg_type, "arg")
        return arg_counter

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        while self.tokenizer.get_cur_token() == "var":
            self.tokenizer.advance()  # var
            var_type = self.return_token()  # var type
            var_name = self.return_token()  # var name
            self.tables.define(var_name, var_type, "var")
            while self.tokenizer.get_cur_token() != ";":
                self.tokenizer.advance()  # ,
                var_name = self.return_token()  # var name
                self.tables.define(var_name, var_type, "var")
            self.tokenizer.advance()  # ;

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
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

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.tokenizer.advance()  # do
        self.compile_subroutine_call()
        self.tokenizer.advance()  # ;
        self.output.write_pop("temp", 0)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.tokenizer.advance()  # let
        var_name = self.return_token()  # varName
        kind = self.tables.kind_of(var_name)
        index = self.tables.index_of(var_name)
        if self.tokenizer.get_cur_token() == "[":
            self.tokenizer.advance()   # [
            self.output.write_push(kind, index)
            self.compile_expression()
            self.output.write_arithmetic("add")
            self.tokenizer.advance()   # ]
            self.tokenizer.advance()  # =
            self.compile_expression()
            self.output.write_pop("temp", 0)
            self.output.write_pop("pointer", 1)
            self.output.write_push("temp", 0)
            self.output.write_pop("that", 0)
        else:
            self.tokenizer.advance()   # =
            self.compile_expression()
            self.output.write_pop(kind, index)
        self.tokenizer.advance()   # ;

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.tokenizer.advance()  # while
        label1 = self.class_name+"$while." + str(self.counter)
        label2 = self.class_name + "$while." + str(self.counter + 1)
        self.counter += 2
        self.output.write_label(label1)
        self.tokenizer.advance()  # (
        self.compile_expression()
        self.tokenizer.advance()  # )
        self.output.write_arithmetic("not")
        self.output.write_if(label2)
        self.tokenizer.advance()  # {
        self.compile_statements()
        self.output.write_goto(label1)
        self.output.write_label(label2)
        self.counter += 2
        self.tokenizer.advance()  # }

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.tokenizer.advance()  # return
        if self.tokenizer.get_cur_token() != ";":
            self.compile_expression()
        else:
            self.output.write_push("constant", 0)
        self.output.write_return()
        self.tokenizer.advance()  # ;

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.tokenizer.advance()  # if
        self.tokenizer.advance()  # (
        self.compile_expression()
        self.tokenizer.advance()  # )
        self.output.write_arithmetic("not")
        label1 = self.class_name + "$if." + str(self.counter)
        label2 = self.class_name + "$else." + str(self.counter)
        self.counter += 1
        self.output.write_if(label1)
        self.tokenizer.advance()  # {
        self.compile_statements()
        self.tokenizer.advance()  # }
        self.output.write_goto(label2)
        self.output.write_label(label1)
        if self.tokenizer.get_cur_token() == "else":
            self.tokenizer.advance()  # else
            self.tokenizer.advance()  # {
            self.compile_statements()
            self.tokenizer.advance()  # }
        self.output.write_label(label2)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        arith_dict = {"+": "add", "-": "sub", "*": "call Math.multiply 2", "/": "call Math.divide 2", "&": "and",
                      "|": "or", "<": "lt", ">": "gt", "=": "eq"}
        self.compile_term()
        while self.tokenizer.get_cur_token() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            the_op = arith_dict[self.return_token()]  # the op
            self.compile_term()
            self.output.write_arithmetic(the_op)

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
        if self.tokenizer.token_type() == "STRING_CONST":
            self.enter_string(self.return_token())  # the string
        elif self.tokenizer.token_type() == "INT_CONST":
            self.output.write_push("constant", int(self.return_token()))  # the number
        elif self.tokenizer.get_cur_token() in ["true", "false", "null", "this"]:
            keyword_dict = {"true": ["constant", 1], "false": ["constant", 0], "null": ["constant", 0],
                            "this": ["pointer", 0]}
            keyword = self.return_token()
            self.output.write_push(keyword_dict[keyword][0], keyword_dict[keyword][1])
            if keyword == "true":
                self.output.write_arithmetic("neg")
        elif self.tokenizer.get_cur_token() == "(":
            self.tokenizer.advance()  # (
            self.compile_expression()
            self.tokenizer.advance()  # )
        elif self.tokenizer.get_cur_token() in ["-", "~", "#", "^"]:
            arth_dict = {"-": "neg", "~": "not", "#": "shiftright", "^": "shiftleft"}
            op = self.return_token()  # ~ or - or more
            self.compile_term()
            self.output.write_arithmetic(arth_dict[op])
        elif self.tokenizer.get_next_token() in [".", "("]:
            self.compile_subroutine_call()
        else:
            var_name = self.return_token()  # varName
            kind = self.tables.kind_of(var_name)
            place = self.tables.index_of(var_name)
            self.output.write_push(kind, place)
            if self.tokenizer.get_cur_token() == "[":
                self.tokenizer.advance()  # [
                self.compile_expression()
                self.output.write_arithmetic("add")
                self.output.write_pop("pointer", 1)
                self.tokenizer.advance()  # ]
                self.output.write_push("that", 0)

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        expression_counter = 0
        if self.tokenizer.get_cur_token() != ")":
            self.compile_expression()
            expression_counter += 1
            while self.tokenizer.get_cur_token() == ",":
                self.tokenizer.advance()  # ,
                self.compile_expression()
                expression_counter += 1
        return expression_counter

    def compile_subroutine_call(self) -> None:
        sub_or_class_name = self.return_token()  # subroutine name | var/class name
        if self.tokenizer.get_cur_token() == "(":
            self.tokenizer.advance()  # (
            self.output.write_push("pointer", 0)
            n_arg = self.compile_expression_list() + 1
            self.output.write_call(self.class_name + "." +sub_or_class_name, n_arg)
            self.tokenizer.advance()  # )
        elif self.tokenizer.get_cur_token() == ".":
            self.tokenizer.advance()  # .
            func_name = self.return_token()
            sub_name = sub_or_class_name + "." + func_name  # subroutine name
            self.tokenizer.advance()  # (
            n_arg = 0
            if self.tables.type_of(sub_or_class_name) is not None:
                n_arg = 1
                type_of = self.tables.type_of(sub_or_class_name)
                kind_of = self.tables.kind_of(sub_or_class_name)
                index_of = self.tables.index_of(sub_or_class_name)
                sub_name = type_of + "." + func_name
                self.output.write_push(kind_of, index_of)
            n_arg += self.compile_expression_list()
            self.output.write_call(sub_name, n_arg)
            self.tokenizer.advance()  # )

    def enter_string(self, st):
        n = len(st)
        self.output.write_push("constant", n)
        self.output.write_call("String.new", 1)
        for char in st:
            self.output.write_push("constant", ord(char))
            self.output.write_call("String.appendChar", 2)


