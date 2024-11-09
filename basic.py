# Tokens

TT_INT = 'TT_INT'
TT_FLOAT = 'TT_FLOAT'
TT_PLUS = 'TT_PLUS'
TT_MINUS = 'TT_MINUS'
TT_MUL = 'TT_MUL'
TT_DIV = 'TT_DIV'
TT_LPAR = 'TT_LPAR'
TT_RPAR = 'TT_RPAR'
TT_EOF = 'TT_EOF'

DIGITS = '1234567890'


class Error:
    def __init__(self, error, details, start_position, end_position):
        self.error = error
        self.details = details
        self.start_position = start_position
        self.end_position = end_position

    def __as_string__(self):
        result = f'{self.error}: {self.details}\n'
        result = result + f'File: {self.start_position.file_name}, Pos:({self.start_position.line + 1}, {self.start_position.column})'
        return result

class IllegalCharError(Error):
    def __init__(self, details, start_position, end_position):
        super().__init__('Illegal Character', details, start_position, end_position)

class IllegalSyntaxError(Error):
    def __init__(self, details, start_position, end_position):
        super().__init__('Invalid Syntax', details, start_position, end_position)

class Token:
    def __init__(self, type_, value=None, start_position=None, end_position=None):
        self.type = type_
        self.value = value
        if (start_position != None):
            self.start_position = start_position.copy()
            self.end_position = start_position.copy()
            self.end_position.advance()
        if (end_position != None):
            self.end_position = end_position.copy()

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

    def advance(self, current_char=None):
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
        result = ParseResult()
        token = self.current_token

        if (token.type in (TT_INT, TT_FLOAT)):
            result.register(self.advance())
            return result.success(NumberNode(token))

        return result.failure(IllegalSyntaxError("Invalid Number", token.start_position, token.end_position))

    def term(self):
        result = ParseResult()
        left = result.register(self.factor())
        if result.error:
            return result

        while (self.current_token.type in (TT_DIV, TT_MUL)):
            op = self.current_token
            result.register(self.advance())
            right = result.register(self.factor())
            if result.error:
                return result
            left = BinaryOp(left, op, right)

        return result.success(left)

    def expression(self):
        result = ParseResult()
        left = result.register(self.term())
        while(self.current_token.type in (TT_MINUS, TT_PLUS)):
            op = self.current_token
            result.register(self.advance())
            right = result.register(self.term())

            left = BinaryOp(left, op, right)

        print(left)
        return result.success(left)

    def parse(self):
        res = self.expression()

        if not res.error == None and self.current_token != TT_EOF:
            res.failure(IllegalSyntaxError("Error", self.current_token.start_position, self.current_token.end_position))

        return res

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, result):
        if isinstance(result, ParseResult):
            if result.error: 
                self.error = result.error
            return result.node
        return result

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

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
                tokens.append(Token(TT_PLUS, None, self.pos))
                self.advance()
            elif (self.current_char == '-'):
                tokens.append(Token(TT_MINUS, None, self.pos))
                self.advance()
            elif (self.current_char == '*'):
                tokens.append(Token(TT_MUL, None, self.pos))
                self.advance()
            elif (self.current_char == '/'):
                tokens.append(Token(TT_DIV, None, self.pos))
                self.advance()
            elif (self.current_char == '('):
                tokens.append(Token(TT_LPAR, None, self.pos))
                self.advance()
            elif (self.current_char == ')'):
                tokens.append(Token(TT_RPAR, None, self.pos))
                self.advance()
            else:
                start_position = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError("'" + char + "'", start_position, self.pos)

        tokens.append(Token(TT_EOF, start_position=self.pos))
        return tokens, None

    def make_num(self):
        num_str = ''
        is_float = False
        start_position = self.pos.copy()
        while (self.current_char != None and self.current_char in DIGITS + '.'):
            num_str += self.current_char
            self.advance()
            if (self.current_char == '.'):
                is_float = True

        end_position = self.pos.copy()
        if (is_float):
            return Token(TT_FLOAT, float(num_str), start_position, end_position)
        else:
            return Token(TT_INT, int(num_str), start_position, end_position)

def run(file_name, text):
    lexer = Lexer(file_name, text)
    tokens, error = lexer.make_tokens()

    parser = Parser(tokens).parse()
    return parser.node, parser.error