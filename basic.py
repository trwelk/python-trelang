# Tokens

TT_INT = 'TT_INT'
TT_FLOAT = 'TT_FLOAT'
TT_PLUS = 'TT_PLUS'
TT_MINUS = 'TT_MINUS'
TT_MUL = 'TT_MUL'
TT_DIV = 'TT_DIV'
TT_LPAR = 'TT_LPAR'
TT_RPAR = 'TT_RPAR'

DIGITS = '1234567890'


class Error:
    def __init__(self, error, details, pos_start, pos_end):
        self.error = error
        self.details = details
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __as_string__(self):
        result = f'{self.error}: {self.details}\n'
        result = result + f'File: {self.pos_start.file_name}, Pos:({self.pos_start.line + 1}, {self.pos_start.column})'
        return result

class IllegalCharError(Error):
    def __init__(self, details, pos_start, pos_end):
        super().__init__('Illegal Character', details, pos_start, pos_end)

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

class Position:
    def __init__(self, index, line, column, file_name, file_text):
        self.index = index
        self.line = line 
        self.column = column
        self.file_name = file_name
        self.file_text = file_text

    def advance(self, current_char):
        self.index += 1
        self.column += 1

        if (current_char == '\n'):
            self.column = 0
            self.line += 1

        return self

    def copy(self):
        return Position(self.index, self.line, self.column, self.file_name, self.file_text)


# Nodes
class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'
    
class BinaryOp:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'

# Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        if (self.token_index < len(self.tokens)):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def factor(self):
        token = self.current_token

        if (token.type in (TT_INT, TT_FLOAT)):
            self.advance()
            return NumberNode(token)

    def term(self):
        left = self.factor()

        while (self.current_token.type in (TT_DIV, TT_MUL)):
            op = self.current_token
            self.advance()
            right = self.factor()
            left = BinaryOp(left, op, right)

        return left

    def expression(self):
        left = self.term()
        while(self.current_token.type in (TT_MINUS, TT_PLUS)):
            op = self.current_token
            self.advance()
            right = self.term()
            print(op)

            left = BinaryOp(left, op, right)

        return left

    def parse(self):
        res = self.expression()
        return res

class Lexer:
    def __init__(self, file_name, text):
        self.file_name = file_name
        self.text = text
        self.pos = Position(-1, 0 , -1, file_name, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if (self.current_char in ' \t'):
                self.advance()
            elif (self.current_char in DIGITS):
                tokens.append(self.make_num())
            elif (self.current_char == '+'):
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif (self.current_char == '-'):
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif (self.current_char == '*'):
                tokens.append(Token(TT_MUL))
                self.advance()
            elif (self.current_char == '/'):
                tokens.append(Token(TT_DIV))
                self.advance()
            elif (self.current_char == '('):
                tokens.append(Token(TT_LPAR))
                self.advance()
            elif (self.current_char == ')'):
                tokens.append(Token(TT_RPAR))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError("'" + char + "'", pos_start, self.pos)

        return tokens, None

    def make_num(self):
        num_str = ''
        is_float = False

        while (self.current_char != None and self.current_char in DIGITS + '.'):
            num_str += self.current_char
            self.advance()
            if (self.current_char == '.'):
                is_float = True

        if (is_float):
            return Token(TT_FLOAT, float(num_str))
        else:
            return Token(TT_INT, int(num_str))

def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()

    parser = Parser(tokens).parse()
    return parser, error