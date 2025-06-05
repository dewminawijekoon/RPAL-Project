from enum import Enum
from Lexer.lexical_analyzer import TokenType, Token

class NodeType(Enum):
    let = 1
    fcn_form = 2
    id = 3
    int = 4
    str = 5
    where = 6
    gamma = 7
    lambda_expr = 8
    tau = 9
    rec = 10
    aug = 11
    conditional = 12
    op_or = 13
    op_and = 14
    op_not = 15
    op_compare = 16
    op_plus = 17
    op_minus = 18
    op_neg = 19
    op_mul = 20
    op_div = 21
    op_pow = 22
    at = 23
    true_value = 24
    false_value = 25
    nil = 26
    dummy = 27
    within = 28
    and_op = 29
    equal = 30
    comma = 31
    empty_params = 32


class Node:
    def __init__(self, node_type, value, children):
        self.type = node_type
        self.value = value
        self.no_of_children = children

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.ast = []
        self.string_ast = []

    def peek_token(self):
        """Safely peek at the current token"""
        if self.tokens:
            return self.tokens[0]
        return None

    def consume_token(self):
        """Safely consume the current token"""
        if self.tokens:
            return self.tokens.pop(0)
        return None

    def parse(self):
        self.tokens.append(Token(TokenType.END_OF_TOKENS, ""))  # Add an End Of Tokens marker
        self.E()  # Start parsing from the entry point
        if self.tokens[0].type == TokenType.END_OF_TOKENS:
            return self.ast
        else:
            print("Parsing Unsuccessful!...........")
            print("REMAINING UNPARSED TOKENS:")
            for token in self.tokens:
                print("<" + str(token.type) + ", " + token.value + ">")
            return None

    def convert_ast_to_string_ast(self):
        dots = ""
        stack = []

        while self.ast:
            if not stack:
                if self.ast[-1].no_of_children == 0:
                    self.add_strings(dots, self.ast.pop())
                else:
                    node = self.ast.pop()
                    stack.append(node)
            else:
                if self.ast[-1].no_of_children > 0:
                    node = self.ast.pop()
                    stack.append(node)
                    dots += "."
                else:
                    stack.append(self.ast.pop())
                    dots += "."
                    while stack[-1].no_of_children == 0:
                        self.add_strings(dots, stack.pop())
                        if not stack:
                            break
                        dots = dots[:-1]
                        node = stack.pop()
                        node.no_of_children -= 1
                        stack.append(node)

        # Reverse the list
        self.string_ast.reverse()
        return self.string_ast

    def add_strings(self, dots, node):
        if node.type in [NodeType.id, NodeType.int, NodeType.str, NodeType.true_value,
                         NodeType.false_value, NodeType.nil, NodeType.dummy]:
            self.string_ast.append(dots + "<" + node.type.name.upper() + ":" + node.value + ">")
        elif node.type == NodeType.fcn_form:
            self.string_ast.append(dots + "function_form")
        else:
            self.string_ast.append(dots + node.value)

    # Expressions 
                
    # E	->'let' D 'in' E		=> 'let'
    # 	->'fn' Vb+ '.' E		=> 'lambda'
    # 	->Ew;

    def E(self):
        token = self.peek_token()
        if not token:
            print("Parse error: Unexpected end of input in E")
            return
            
        if token.type == TokenType.KEYWORD and token.value == "let":
            self.consume_token()  # Remove "let"
            self.D()
            
            in_token = self.peek_token()
            if not in_token or in_token.value != "in":
                print("Parse error at E: 'in' expected")
                return
            self.consume_token()  # Remove "in"
            
            self.E()
            self.ast.append(Node(NodeType.let, "let", 2))
            
        elif token.type == TokenType.KEYWORD and token.value == "fn":
            self.consume_token()  # Remove "fn"
            n = 0
            
            # Check for at least one Vb
            next_token = self.peek_token()
            if not next_token or (next_token.type != TokenType.ID and next_token.value != "("):
                print("Parse error at E: At least one variable binding expected after 'fn'")
                return
                
            while self.peek_token() and (self.peek_token().type == TokenType.ID or self.peek_token().value == "("):
                self.Vb()
                n += 1
                
            dot_token = self.peek_token()
            if not dot_token or dot_token.value != ".":
                print("Parse error at E: '.' expected after variable bindings")
                return
            self.consume_token()  # Remove "."
            
            self.E()
            self.ast.append(Node(NodeType.lambda_expr, "lambda", n + 1))
        else:
            self.Ew()

    # Ew	->T 'where' Dr			=> 'where'
    # 		->T;

    def Ew(self):
        self.T()
        where_token = self.peek_token()
        if where_token and where_token.value == "where":
            self.consume_token()  # Remove "where"
            self.Dr()
            self.ast.append(Node(NodeType.where, "where", 2))

    # Tuple Expressions

    # T 	-> Ta ( ',' Ta )+ => 'tau'
    # 		-> Ta ;
            
    def T(self):
        self.Ta()
        n = 1
        while self.peek_token() and self.peek_token().value == ",":
            self.consume_token()  # Remove comma(,)
            self.Ta()
            n += 1
        if n > 1:
            self.ast.append(Node(NodeType.tau, "tau", n))

    # Ta 	-> Ta 'aug' Tc => 'aug'
    # 		-> Tc ;
    # Converted to right recursion: Ta -> Tc ('aug' Tc)*
    
    def Ta(self):
        self.Tc()
        while self.peek_token() and self.peek_token().value == "aug":
            self.consume_token()  # Remove "aug"
            self.Tc()
            self.ast.append(Node(NodeType.aug, "aug", 2))

    # Tc 	-> B '->' Tc '|' Tc => '->'
    # 		-> B ;
    
    def Tc(self):
        self.B()
        if self.peek_token() and self.peek_token().value == "->":
            self.consume_token()  # Remove '->'
            self.Tc()
            
            pipe_token = self.peek_token()
            if not pipe_token or pipe_token.value != "|":
                print("Parse error at Tc: conditional '|' expected")
                return
            self.consume_token()  # Remove '|'
            
            self.Tc()
            self.ast.append(Node(NodeType.conditional, "->", 3))

    # Boolean Expressions
    # B 	-> B 'or' Bt 	=> 'or'
    #     -> Bt ;	
    # Converted to: B -> Bt ('or' Bt)*
    
    def B(self):
        self.Bt()
        while self.peek_token() and self.peek_token().value == "or":
            self.consume_token()  # Remove 'or'
            self.Bt()
            self.ast.append(Node(NodeType.op_or, "or", 2))

    # Bt	-> Bt '&' Bs => '&'
    # 		-> Bs ;
    # Converted to: Bt -> Bs ('&' Bs)*
    
    def Bt(self):
        self.Bs()
        while self.peek_token() and self.peek_token().value == "&":
            self.consume_token()  # Remove '&'
            self.Bs()
            self.ast.append(Node(NodeType.op_and, "&", 2))

    # Bs	-> 'not' Bp => 'not'
    # 		-> Bp ;

    def Bs(self):
        if self.peek_token() and self.peek_token().value == "not":
            self.consume_token()  # Remove 'not'
            self.Bp()
            self.ast.append(Node(NodeType.op_not, "not", 1))
        else:
            self.Bp()

    #  Bp 	-> A ('gr' | '>' ) A => 'gr'
    # 		-> A ('ge' | '>=') A => 'ge'
    # 		-> A ('ls' | '<' ) A => 'ls'
    # 		-> A ('le' | '<=') A => 'le'
    # 		-> A 'eq' A => 'eq'
    # 		-> A 'ne' A => 'ne'
    # 		-> A ;

    def Bp(self):
        self.A()
        token = self.peek_token()
        if token and token.value in [">", ">=", "<", "<=", "gr", "ge", "ls", "le", "eq", "ne"]:
            self.consume_token()
            self.A()
            if token.value == ">":
                self.ast.append(Node(NodeType.op_compare, "gr", 2))
            elif token.value == ">=":
                self.ast.append(Node(NodeType.op_compare, "ge", 2))
            elif token.value == "<":
                self.ast.append(Node(NodeType.op_compare, "ls", 2))
            elif token.value == "<=":
                self.ast.append(Node(NodeType.op_compare, "le", 2))
            else:
                self.ast.append(Node(NodeType.op_compare, token.value, 2))

    # Arithmetic Expressions
    # A 	-> A '+' At => '+'
    # 		-> A '-' At => '-'
    # 		-> '+' At
    # 		-> '-'At =>'neg'
    # 		-> At ;

    def A(self):
        if self.peek_token() and self.peek_token().value == "+":
            self.consume_token()  # Remove unary plus
            self.At()
        elif self.peek_token() and self.peek_token().value == "-":
            self.consume_token()  # Remove unary minus
            self.At()
            self.ast.append(Node(NodeType.op_neg, "neg", 1))
        else:
            self.At()

        while self.peek_token() and self.peek_token().value in {"+", "-"}:
            current_token = self.consume_token()  # Remove plus or minus operators
            self.At()
            if current_token.value == "+":
                self.ast.append(Node(NodeType.op_plus, "+", 2))
            else:
                self.ast.append(Node(NodeType.op_minus, "-", 2))

    # At 	-> At '*' Af => '*'
    # 		-> At '/' Af => '/'
    # 		-> Af ;
    # Converted to: At -> Af ('*' Af | '/' Af)*
           
    def At(self):
        self.Af()
        while self.peek_token() and self.peek_token().value in {"*", "/"}:
            current_token = self.consume_token()  # Remove multiply or divide operators
            self.Af()
            if current_token.value == "*":
                self.ast.append(Node(NodeType.op_mul, "*", 2))
            else:
                self.ast.append(Node(NodeType.op_div, "/", 2))

    # Af 	-> Ap '**' Af => '**'
    # 		-> Ap ;
    # Right associative, so keep as is

    def Af(self):
        self.Ap()
        if self.peek_token() and self.peek_token().value == "**":
            self.consume_token()  # Remove power operator
            self.Af()
            self.ast.append(Node(NodeType.op_pow, "**", 2))

    # Ap 	-> Ap '@' '<ID>' R => '@'
    # 		-> R ;
    # Converted to: Ap -> R ('@' '<ID>' R)*
   
    def Ap(self):
        self.R()
        while self.peek_token() and self.peek_token().value == "@":
            self.consume_token()  # Remove @ operator
            
            id_token = self.peek_token()
            if not id_token or id_token.type != TokenType.ID:
                print("Parsing error at Ap: ID expected after '@'")
                return
            
            self.ast.append(Node(NodeType.id, id_token.value, 0))
            self.consume_token()  # Remove ID
            
            self.R()
            self.ast.append(Node(NodeType.at, "@", 3))

    # Rators And Rands
    # R 	-> R Rn => 'gamma'
    # 		-> Rn ;
    # Converted to: R -> Rn (Rn)*
            
    def R(self):
        self.Rn()
        while (self.peek_token() and 
               (self.peek_token().type in [TokenType.ID, TokenType.INT, TokenType.STRING] or
                self.peek_token().value in ["true", "false", "nil", "dummy"] or
                self.peek_token().value == "(")):
            
            self.Rn()
            self.ast.append(Node(NodeType.gamma, "gamma", 2))

    # Rn 	-> '<ID>'
    # 		-> '<INT>'
    # 		-> '<STRING>'
    # 		-> 'true' => 'true'
    # 		-> 'false' => 'false'
    # 		-> 'nil' => 'nil'
    # 		-> '(' E ')'
    # 		-> 'dummy' => 'dummy' ;
            
    def Rn(self):
        token = self.peek_token()
        if not token:
            print("Parse error: Unexpected end of input in Rn")
            return
        
        if token.type == TokenType.ID:
            self.ast.append(Node(NodeType.id, token.value, 0))
            self.consume_token()
        elif token.type == TokenType.INT:
            self.ast.append(Node(NodeType.int, token.value, 0))
            self.consume_token()
        elif token.type == TokenType.STRING:
            self.ast.append(Node(NodeType.str, token.value, 0))
            self.consume_token()
        elif token.type == TokenType.KEYWORD:
            if token.value in ["true", "false", "nil", "dummy"]:
                if token.value == "true":
                    self.ast.append(Node(NodeType.true_value, token.value, 0))
                elif token.value == "false":
                    self.ast.append(Node(NodeType.false_value, token.value, 0))
                elif token.value == "nil":
                    self.ast.append(Node(NodeType.nil, token.value, 0))
                elif token.value == "dummy":
                    self.ast.append(Node(NodeType.dummy, token.value, 0))
                self.consume_token()
            else:
                print(f"Parse Error at Rn: Unexpected KEYWORD '{token.value}'")
        elif token.type == TokenType.PUNCTUATION and token.value == "(":
            self.consume_token()  # Remove '('
            self.E()
            
            close_paren = self.peek_token()
            if not close_paren or close_paren.value != ")":
                print("Parsing error at Rn: Expected a matching ')'")
                return
            self.consume_token()  # Remove ')'
        else:
            print(f"Parsing error at Rn: Unexpected token {token.type}, {token.value}")

    # Definitions
    # D 	-> Da 'within' D => 'within'
    # 		-> Da ;
            
    def D(self):
        self.Da()
        if self.peek_token() and self.peek_token().value == "within":
            self.consume_token()  # Remove 'within'
            self.D()
            self.ast.append(Node(NodeType.within, "within", 2))

    # Da  -> Dr ( 'and' Dr )+ => 'and'
    # 		-> Dr ;
            
    def Da(self): 
        self.Dr()
        n = 1
        while self.peek_token() and self.peek_token().value == "and":
            self.consume_token()
            self.Dr()
            n += 1
        if n > 1:
            self.ast.append(Node(NodeType.and_op, "and", n))

    # Dr  -> 'rec' Db => 'rec'
    # 	  -> Db ;
            
    def Dr(self):
        is_rec = False
        if self.peek_token() and self.peek_token().value == "rec":
            self.consume_token()
            is_rec = True
        self.Db()
        if is_rec:
            self.ast.append(Node(NodeType.rec, "rec", 1))

    # Db  -> Vl '=' E => '='
    # 		-> '<ID>' Vb+ '=' E => 'fcn_form'
    # 		-> '(' D ')' ; 
            
    def Db(self): 
        token = self.peek_token()
        if not token:
            print("Parse error: Unexpected end of input in Db")
            return
            
        if token.type == TokenType.PUNCTUATION and token.value == "(":
            self.consume_token()
            self.D()
            
            close_paren = self.peek_token()
            if not close_paren or close_paren.value != ")":
                print("Parsing error at Db: Expected closing ')'")
                return
            self.consume_token()
            
        elif token.type == TokenType.ID:
            # Look ahead to determine if it's fcn_form or simple assignment
            next_token = self.tokens[1] if len(self.tokens) > 1 else None
            
            if next_token and (next_token.value == "(" or next_token.type == TokenType.ID):
                # Function form: ID Vb+ = E
                self.ast.append(Node(NodeType.id, token.value, 0))
                self.consume_token()  # Remove ID

                n = 1  # Count the id
                while self.peek_token() and (self.peek_token().type == TokenType.ID or self.peek_token().value == "("):
                    self.Vb()
                    n += 1
                    
                equals_token = self.peek_token()
                if not equals_token or equals_token.value != "=":
                    print("Parsing error at Db: '=' expected in function form")
                    return
                self.consume_token()  # Remove '='
                
                self.E()
                self.ast.append(Node(NodeType.fcn_form, "fcn_form", n + 1))
                
            elif next_token and next_token.value == "=":
                # Simple assignment: ID = E
                self.ast.append(Node(NodeType.id, token.value, 0))
                self.consume_token()  # Remove id
                self.consume_token()  # Remove '='
                self.E()
                self.ast.append(Node(NodeType.equal, "=", 2))
                
            elif next_token and next_token.value == ",":
                # Variable list assignment: Vl = E
                self.Vl()
                
                equals_token = self.peek_token()
                if not equals_token or equals_token.value != "=":
                    print("Parsing error at Db: '=' expected after variable list")
                    return
                self.consume_token()  # Remove '='
                
                self.E()
                self.ast.append(Node(NodeType.equal, "=", 2))
            else:
                print("Parsing error at Db: Invalid definition form")

    # Variables
    # Vb  -> '<ID>'
    #     -> '(' Vl ')'
    #     -> '(' ')' => '()';

    def Vb(self):
        token = self.peek_token()
        if not token:
            print("Parse error: Unexpected end of input in Vb")
            return
            
        if token.type == TokenType.PUNCTUATION and token.value == "(":
            self.consume_token()
            
            next_token = self.peek_token()
            if next_token and next_token.type == TokenType.ID:
                self.Vl()
                is_vl = True
            else:
                is_vl = False
            
            close_paren = self.peek_token()
            if not close_paren or close_paren.value != ")":
                print("Parse error at Vb: Expected closing ')'")
                return
            self.consume_token()
            
            if not is_vl:
                self.ast.append(Node(NodeType.empty_params, "()", 0))
                
        elif token.type == TokenType.ID:
            self.ast.append(Node(NodeType.id, token.value, 0))
            self.consume_token()
        else:
            print("Parse error at Vb: Expected id or '('")

    # Vl -> '<ID>' list ',' => ','?;
            
    def Vl(self):
        n = 0
        while True:
            if n > 0:
                self.consume_token()  # Remove comma from previous iteration
                
            current_token = self.peek_token()
            if not current_token or current_token.type != TokenType.ID:
                print("Parse error at Vl: id expected")
                return
                
            self.ast.append(Node(NodeType.id, current_token.value, 0))
            self.consume_token()
            n += 1
            
            next_token = self.peek_token()
            if not next_token or next_token.value != ",":
                break
        
        if n > 1:
            self.ast.append(Node(NodeType.comma, ",", n))