from enum import Enum
from Lexer.lexical_analyzer import TokenType, Token

# Enumeration defining all possible node types in the Abstract Syntax Tree (AST)
# Each node type represents a different language construct or operation
class NodeType(Enum):
    let = 1              # Let expression binding
    fcn_form = 2         # Function form definition
    id = 3               # Identifier
    int = 4              # Integer literal
    str = 5           # String literal
    where = 6            # Where clause
    gamma = 7            # Function application
    lambda_expr = 8      # Lambda expression (anonymous function)
    tau = 9              # Tuple construction
    rec = 10             # Recursive definition
    aug = 11             # Augmentation operator
    conditional = 12     # Conditional expression (if-then-else)
    op_or = 13           # Logical OR operator
    op_and = 14          # Logical AND operator
    op_not = 15          # Logical NOT operator
    op_compare = 16      # Comparison operators (>, <, =, etc.)
    op_plus = 17         # Addition operator
    op_minus = 18        # Subtraction operator
    op_neg = 19          # Unary negation operator
    op_mul = 20          # Multiplication operator
    op_div = 21          # Division operator
    op_pow = 22          # Power/exponentiation operator
    at = 23              # At operator (@)
    true_value = 24      # Boolean true literal
    false_value = 25     # Boolean false literal
    nil = 26             # Nil/null value
    dummy = 27           # Dummy value
    within = 28          # Within clause
    and_op = 29          # And operator for definitions
    equal = 30           # Assignment/equality operator
    comma = 31           # Comma operator for lists
    empty_params = 32    # Empty parameter list ()

# AST Node class representing a single node in the syntax tree
class Node:
    def __init__(self, node_type, value, children):
        self.type = node_type           
        self.value = value              
        self.no_of_children = children  

# Main Parser class implementing a recursive descent parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens        
        self.ast = []              # Stack-based AST construction (nodes in reverse order)
        self.string_ast = []       # String representation of the AST

    def peek_token(self):
        """Safely peek at the current token without consuming it"""
        if self.tokens:
            return self.tokens[0]
        return None

    def consume_token(self):
        """Safely consume and return the current token"""
        if self.tokens:
            return self.tokens.pop(0)
        return None

    def parse(self):
        """Main parsing entry point - parses the entire token stream"""
        # Add end-of-tokens marker to simplify parsing logic
        self.tokens.append(Token(TokenType.END_OF_TOKENS, ""))
        
        # Start parsing from the top-level expression rule
        self.E()
        
        # Check if all tokens were consumed successfully
        if self.tokens[0].type == TokenType.END_OF_TOKENS:
            return self.ast
        else:
            # Print error information if parsing failed
            print("Parsing Unsuccessful!...........")
            print("REMAINING UNPARSED TOKENS:")
            for token in self.tokens:
                print("<" + str(token.type) + ", " + token.value + ">")
            return None

    def convert_ast_to_string_ast(self):
        """Convert the stack-based AST to a readable string representation with dot notation"""
        dots = ""      # Tracks indentation level
        stack = []     # Stack for managing node processing
        
        # Process nodes from the AST stack
        while self.ast:
            if not stack:
                # Base case: process leaf nodes directly
                if self.ast[-1].no_of_children == 0:
                    self.add_strings(dots, self.ast.pop())
                else:
                    # Non-leaf node: add to processing stack
                    node = self.ast.pop()
                    stack.append(node)
            else:
                if self.ast[-1].no_of_children > 0:
                    # Internal node: add to stack and increase indentation
                    node = self.ast.pop()
                    stack.append(node)
                    dots += "."
                else:
                    # Leaf node: add to stack and increase indentation
                    stack.append(self.ast.pop())
                    dots += "."
                    
                    # Process completed nodes from stack
                    while stack[-1].no_of_children == 0:
                        self.add_strings(dots, stack.pop())
                        if not stack:
                            break
                        # Backtrack: reduce indentation and decrement parent's child count
                        dots = dots[:-1]
                        node = stack.pop()
                        node.no_of_children -= 1
                        stack.append(node)

        # Reverse to get correct order for display
        self.string_ast.reverse()
        return self.string_ast

    def add_strings(self, dots, node):
        """Add formatted string representation of a node to string_ast"""
        # Special formatting for nodes with values
        if node.type in [NodeType.id, NodeType.int, NodeType.str, NodeType.true_value,
                         NodeType.false_value, NodeType.nil, NodeType.dummy]:
            self.string_ast.append(dots + "<" + node.type.name.upper() + ":" + node.value + ">")
        elif node.type == NodeType.fcn_form:
            # Special case for function form
            self.string_ast.append(dots + "function_form")
        else:
            # Standard formatting using node value
            self.string_ast.append(dots + node.value)

    # ===============================
    # EXPRESSION PARSING METHODS
    # ===============================
    
    # E -> 'let' D 'in' E         => 'let'      (Let expression)
    #   -> 'fn' Vb+ '.' E         => 'lambda'   (Lambda/function expression)
    #   -> Ew;                                  (Where expression)
    def E(self):
        """Parse top-level expressions: let bindings, lambda expressions, or where expressions"""
        token = self.peek_token()
        if not token:
            print("Parse error: Unexpected end of input in E")
            return
            
        if token.type == TokenType.KEYWORD and token.value == "let":
            # Parse let expression: let D in E
            self.consume_token()  # Remove "let"
            self.D()              # Parse definitions
            
            # Expect 'in' keyword
            in_token = self.peek_token()
            if not in_token or in_token.value != "in":
                print("Parse error at E: 'in' expected")
                return
            self.consume_token()  # Remove "in"
            
            self.E()              # Parse body expression
            self.ast.append(Node(NodeType.let, "let", 2))
            
        elif token.type == TokenType.KEYWORD and token.value == "fn":
            # Parse lambda expression: fn Vb+ . E
            self.consume_token()  # Remove "fn"
            n = 0  # Count parameter bindings
            
            # Ensure at least one variable binding exists
            next_token = self.peek_token()
            if not next_token or (next_token.type != TokenType.ID and next_token.value != "("):
                print("Parse error at E: At least one variable binding expected after 'fn'")
                return
                
            # Parse one or more variable bindings
            while self.peek_token() and (self.peek_token().type == TokenType.ID or self.peek_token().value == "("):
                self.Vb()
                n += 1
                
            # Expect dot separator
            dot_token = self.peek_token()
            if not dot_token or dot_token.value != ".":
                print("Parse error at E: '.' expected after variable bindings")
                return
            self.consume_token()  # Remove "."
            
            self.E()  # Parse function body
            self.ast.append(Node(NodeType.lambda_expr, "lambda", n + 1))
        else:
            # Default case: parse where expression
            self.Ew()

    # Ew -> T 'where' Dr          => 'where'    (Where clause)
    #    -> T;                                  (Simple tuple expression)
    def Ew(self):
        """Parse where expressions or simple tuple expressions"""
        self.T()  # Parse tuple expression
        where_token = self.peek_token()
        if where_token and where_token.value == "where":
            self.consume_token()  # Remove "where"
            self.Dr()             # Parse recursive definitions
            self.ast.append(Node(NodeType.where, "where", 2))

    # ===============================
    # TUPLE EXPRESSION PARSING
    # ===============================

    # T -> Ta ( ',' Ta )+         => 'tau'      (Multi-element tuple)
    #   -> Ta ;                                 (Single element)
    def T(self):
        """Parse tuple expressions (comma-separated values)"""
        self.Ta()  # Parse first element
        n = 1      # Count elements
        
        # Parse additional comma-separated elements
        while self.peek_token() and self.peek_token().value == ",":
            self.consume_token()  # Remove comma(,)
            self.Ta()
            n += 1
            
        # Create tuple node only if multiple elements
        if n > 1:
            self.ast.append(Node(NodeType.tau, "tau", n))

    # Ta -> Ta 'aug' Tc           => 'aug'      (Augmentation - left associative)
    #    -> Tc ;
    # Converted to right recursion: Ta -> Tc ('aug' Tc)*
    def Ta(self):
        """Parse augmentation expressions (list concatenation)"""
        self.Tc()
        # Handle multiple augmentations (left-associative)
        while self.peek_token() and self.peek_token().value == "aug":
            self.consume_token()  # Remove "aug"
            self.Tc()
            self.ast.append(Node(NodeType.aug, "aug", 2))

    # Tc -> B '->' Tc '|' Tc      => '->'       (Conditional expression)
    #    -> B ;                                 (Simple boolean expression)
    def Tc(self):
        """Parse conditional expressions (ternary operator equivalent)"""
        self.B()  # Parse condition
        if self.peek_token() and self.peek_token().value == "->":
            self.consume_token()  # Remove '->'
            self.Tc()             # Parse then-branch
            
            # Expect pipe separator
            pipe_token = self.peek_token()
            if not pipe_token or pipe_token.value != "|":
                print("Parse error at Tc: conditional '|' expected")
                return
            self.consume_token()  # Remove '|'
            
            self.Tc()             # Parse else-branch
            self.ast.append(Node(NodeType.conditional, "->", 3))

    # ===============================
    # BOOLEAN EXPRESSION PARSING
    # ===============================

    # B -> B 'or' Bt              => 'or'       (Logical OR - left associative)
    #   -> Bt ;
    # Converted to: B -> Bt ('or' Bt)*
    def B(self):
        """Parse logical OR expressions"""
        self.Bt()
        # Handle multiple OR operations (left-associative)
        while self.peek_token() and self.peek_token().value == "or":
            self.consume_token()  # Remove 'or'
            self.Bt()
            self.ast.append(Node(NodeType.op_or, "or", 2))

    # Bt -> Bt '&' Bs             => '&'        (Logical AND - left associative)
    #    -> Bs ;
    # Converted to: Bt -> Bs ('&' Bs)*
    def Bt(self):
        """Parse logical AND expressions"""
        self.Bs()
        # Handle multiple AND operations (left-associative)
        while self.peek_token() and self.peek_token().value == "&":
            self.consume_token()  # Remove '&'
            self.Bs()
            self.ast.append(Node(NodeType.op_and, "&", 2))

    # Bs -> 'not' Bp              => 'not'      (Logical NOT - unary)
    #    -> Bp ;
    def Bs(self):
        """Parse logical NOT expressions"""
        if self.peek_token() and self.peek_token().value == "not":
            self.consume_token()  # Remove 'not'
            self.Bp()
            self.ast.append(Node(NodeType.op_not, "not", 1))
        else:
            self.Bp()

    # Bp -> A ('gr' | '>' ) A     => 'gr'       (Greater than)
    #    -> A ('ge' | '>=') A     => 'ge'       (Greater than or equal)
    #    -> A ('ls' | '<' ) A     => 'ls'       (Less than)
    #    -> A ('le' | '<=') A     => 'le'       (Less than or equal)
    #    -> A 'eq' A              => 'eq'       (Equal)
    #    -> A 'ne' A              => 'ne'       (Not equal)
    #    -> A ;                                 (No comparison)
    def Bp(self):
        """Parse comparison expressions"""
        self.A()  # Parse left operand
        token = self.peek_token()
        
        # Check for comparison operators
        if token and token.value in [">", ">=", "<", "<=", "gr", "ge", "ls", "le", "eq", "ne"]:
            self.consume_token()  # Remove comparison operator
            self.A()              # Parse right operand
            
            # Map operators to internal representation
            if token.value == ">":
                self.ast.append(Node(NodeType.op_compare, "gr", 2))
            elif token.value == ">=":
                self.ast.append(Node(NodeType.op_compare, "ge", 2))
            elif token.value == "<":
                self.ast.append(Node(NodeType.op_compare, "ls", 2))
            elif token.value == "<=":
                self.ast.append(Node(NodeType.op_compare, "le", 2))
            else:
                # Use operator as-is for eq, ne, gr, ge, ls, le
                self.ast.append(Node(NodeType.op_compare, token.value, 2))

    # ===============================
    # ARITHMETIC EXPRESSION PARSING
    # ===============================

    # A -> A '+' At               => '+'        (Addition - left associative)
    #   -> A '-' At               => '-'        (Subtraction - left associative)
    #   -> '+' At                               (Unary plus)
    #   -> '-'At                  => 'neg'     (Unary minus/negation)
    #   -> At ;
    def A(self):
        """Parse addition/subtraction expressions and unary operators"""
        # Handle unary operators first
        if self.peek_token() and self.peek_token().value == "+":
            self.consume_token()  # Remove unary plus (no AST node needed)
            self.At()
        elif self.peek_token() and self.peek_token().value == "-":
            self.consume_token()  # Remove unary minus
            self.At()
            self.ast.append(Node(NodeType.op_neg, "neg", 1))
        else:
            self.At()

        # Handle binary addition/subtraction (left-associative)
        while self.peek_token() and self.peek_token().value in {"+", "-"}:
            current_token = self.consume_token()  # Remove operator
            self.At()
            if current_token.value == "+":
                self.ast.append(Node(NodeType.op_plus, "+", 2))
            else:
                self.ast.append(Node(NodeType.op_minus, "-", 2))

    # At -> At '*' Af             => '*'        (Multiplication - left associative)
    #    -> At '/' Af             => '/'        (Division - left associative)
    #    -> Af ;
    # Converted to: At -> Af ('*' Af | '/' Af)*
    def At(self):
        """Parse multiplication/division expressions"""
        self.Af()
        # Handle multiple multiplication/division operations (left-associative)
        while self.peek_token() and self.peek_token().value in {"*", "/"}:
            current_token = self.consume_token()  # Remove operator
            self.Af()
            if current_token.value == "*":
                self.ast.append(Node(NodeType.op_mul, "*", 2))
            else:
                self.ast.append(Node(NodeType.op_div, "/", 2))

    # Af -> Ap '**' Af            => '**'       (Exponentiation - right associative)
    #    -> Ap ;
    def Af(self):
        """Parse exponentiation expressions (right-associative)"""
        self.Ap()
        if self.peek_token() and self.peek_token().value == "**":
            self.consume_token()  # Remove power operator
            self.Af()             # Right recursion for right-associativity
            self.ast.append(Node(NodeType.op_pow, "**", 2))

    # Ap -> Ap '@' '<ID>' R       => '@'        (At operator - left associative)
    #    -> R ;
    # Converted to: Ap -> R ('@' '<ID>' R)*
    def Ap(self):
        """Parse 'at' operator expressions (indexing/selection)"""
        self.R()
        # Handle multiple @ operations (left-associative)
        while self.peek_token() and self.peek_token().value == "@":
            self.consume_token()  # Remove @ operator
            
            # Expect identifier after @
            id_token = self.peek_token()
            if not id_token or id_token.type != TokenType.ID:
                print("Parsing error at Ap: ID expected after '@'")
                return
            
            # Add identifier as separate node
            self.ast.append(Node(NodeType.id, id_token.value, 0))
            self.consume_token()  # Remove ID
            
            self.R()  # Parse right operand
            self.ast.append(Node(NodeType.at, "@", 3))  # @ takes 3 arguments

    # ===============================
    # RATORS AND RANDS (Function Application)
    # ===============================

    # R -> R Rn                   => 'gamma'    (Function application - left associative)
    #   -> Rn ;
    # Converted to: R -> Rn (Rn)*
    def R(self):
        """Parse function application expressions"""
        self.Rn()  # Parse function/first operand
        
        # Parse additional arguments (function application is left-associative)
        while (self.peek_token() and 
               (self.peek_token().type in [TokenType.ID, TokenType.INT, TokenType.STRING] or
                self.peek_token().value in ["true", "false", "nil", "dummy"] or
                self.peek_token().value == "(")):
            
            self.Rn()  # Parse argument
            self.ast.append(Node(NodeType.gamma, "gamma", 2))

    # Rn -> '<ID>'                              (Identifier)
    #    -> '<INT>'                             (Integer literal)
    #    -> '<STRING>'                          (String literal)
    #    -> 'true'                => 'true'     (Boolean true)
    #    -> 'false'               => 'false'    (Boolean false)
    #    -> 'nil'                 => 'nil'      (Nil value)
    #    -> '(' E ')'                           (Parenthesized expression)
    #    -> 'dummy'               => 'dummy'    (Dummy value)
    def Rn(self):
        """Parse atomic expressions (terminals and parenthesized expressions)"""
        token = self.peek_token()
        if not token:
            print("Parse error: Unexpected end of input in Rn")
            return
        
        if token.type == TokenType.ID:
            # Identifier
            self.ast.append(Node(NodeType.id, token.value, 0))
            self.consume_token()
        elif token.type == TokenType.INT:
            # Integer literal
            self.ast.append(Node(NodeType.int, token.value, 0))
            self.consume_token()
        elif token.type == TokenType.STRING:
            # String literal
            self.ast.append(Node(NodeType.str, token.value, 0))
            self.consume_token()
        elif token.type == TokenType.KEYWORD:
            # Handle keyword literals
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
            # Parenthesized expression
            self.consume_token()  # Remove '('
            self.E()              # Parse inner expression
            
            close_paren = self.peek_token()
            if not close_paren or close_paren.value != ")":
                print("Parsing error at Rn: Expected a matching ')'")
                return
            self.consume_token()  # Remove ')'
        else:
            print(f"Parsing error at Rn: Unexpected token {token.type}, {token.value}")

    # ===============================
    # DEFINITION PARSING METHODS
    # ===============================

    # D -> Da 'within' D          => 'within'   (Within clause)
    #   -> Da ;                                 (Simple definition)
    def D(self):
        """Parse definitions with optional within clauses"""
        self.Da()
        if self.peek_token() and self.peek_token().value == "within":
            self.consume_token()  # Remove 'within'
            self.D()              # Parse nested definitions
            self.ast.append(Node(NodeType.within, "within", 2))

    # Da -> Dr ( 'and' Dr )+      => 'and'      (Multiple simultaneous definitions)
    #    -> Dr ;                               (Single definition)
    def Da(self):
        """Parse simultaneous definitions (separated by 'and')"""
        self.Dr()  # Parse first definition
        n = 1      # Count definitions
        
        # Parse additional definitions separated by 'and'
        while self.peek_token() and self.peek_token().value == "and":
            self.consume_token()  # Remove 'and'
            self.Dr()
            n += 1
            
        # Create 'and' node only if multiple definitions
        if n > 1:
            self.ast.append(Node(NodeType.and_op, "and", n))

    # Dr -> 'rec' Db              => 'rec'       (Recursive definition)
    #    -> Db ;                                (Non-recursive definition)
    def Dr(self):
        """Parse recursive or non-recursive definitions"""
        is_rec = False
        if self.peek_token() and self.peek_token().value == "rec":
            self.consume_token()  # Remove 'rec'
            is_rec = True
            
        self.Db()  # Parse definition body
        
        if is_rec:
            self.ast.append(Node(NodeType.rec, "rec", 1))

    # Db -> Vl '=' E              => '='        (Variable assignment)
    #    -> '<ID>' Vb+ '=' E      => 'fcn_form' (Function definition)
    #    -> '(' D ')' ;                         (Parenthesized definition)
    def Db(self):
        """Parse definition bodies (assignments, function definitions, or grouped definitions)"""
        token = self.peek_token()
        if not token:
            print("Parse error: Unexpected end of input in Db")
            return
            
        if token.type == TokenType.PUNCTUATION and token.value == "(":
            # Parenthesized definition
            self.consume_token()  # Remove '('
            self.D()              # Parse inner definition
            
            close_paren = self.peek_token()
            if not close_paren or close_paren.value != ")":
                print("Parsing error at Db: Expected closing ')'")
                return
            self.consume_token()  # Remove ')'
            
        elif token.type == TokenType.ID:
            # Look ahead to determine definition type
            next_token = self.tokens[1] if len(self.tokens) > 1 else None
            
            if next_token and (next_token.value == "(" or next_token.type == TokenType.ID):
                # Function definition: ID Vb+ = E
                self.ast.append(Node(NodeType.id, token.value, 0))
                self.consume_token()  # Remove function name

                n = 1  # Count function name + parameters
                # Parse parameter bindings
                while self.peek_token() and (self.peek_token().type == TokenType.ID or self.peek_token().value == "("):
                    self.Vb()
                    n += 1
                    
                # Expect equals sign
                equals_token = self.peek_token()
                if not equals_token or equals_token.value != "=":
                    print("Parsing error at Db: '=' expected in function form")
                    return
                self.consume_token()  # Remove '='
                
                self.E()  # Parse function body
                self.ast.append(Node(NodeType.fcn_form, "fcn_form", n + 1))
                
            elif next_token and next_token.value == "=":
                # Simple variable assignment: ID = E
                self.ast.append(Node(NodeType.id, token.value, 0))
                self.consume_token()  # Remove variable name
                self.consume_token()  # Remove '='
                self.E()              # Parse value expression
                self.ast.append(Node(NodeType.equal, "=", 2))
                
            elif next_token and next_token.value == ",":
                # Variable list assignment: Vl = E
                self.Vl()  # Parse variable list
                
                equals_token = self.peek_token()
                if not equals_token or equals_token.value != "=":
                    print("Parsing error at Db: '=' expected after variable list")
                    return
                self.consume_token()  # Remove '='
                
                self.E()  # Parse value expression
                self.ast.append(Node(NodeType.equal, "=", 2))
            else:
                print("Parsing error at Db: Invalid definition form")

    # ===============================
    # VARIABLE PARSING METHODS
    # ===============================

    # Vb -> '<ID>'                              (Simple identifier)
    #    -> '(' Vl ')'                          (Parenthesized variable list)
    #    -> '(' ')'               => '()'       (Empty parameter list)
    def Vb(self):
        """Parse variable bindings (single variables, lists, or empty parameters)"""
        token = self.peek_token()
        if not token:
            print("Parse error: Unexpected end of input in Vb")
            return
            
        if token.type == TokenType.PUNCTUATION and token.value == "(":
            self.consume_token()  # Remove '('
            
            # Check if parameter list is empty or contains variables
            next_token = self.peek_token()
            if next_token and next_token.type == TokenType.ID:
                self.Vl()  # Parse variable list
                is_vl = True
            else:
                is_vl = False
            
            # Expect closing parenthesis
            close_paren = self.peek_token()
            if not close_paren or close_paren.value != ")":
                print("Parse error at Vb: Expected closing ')'")
                return
            self.consume_token()  # Remove ')'
            
            # Create empty parameter node if no variables
            if not is_vl:
                self.ast.append(Node(NodeType.empty_params, "()", 0))
                
        elif token.type == TokenType.ID:
            # Simple identifier
            self.ast.append(Node(NodeType.id, token.value, 0))
            self.consume_token()
        else:
            print("Parse error at Vb: Expected id or '('")

    # Vl -> '<ID>' list ','       => ','        (Comma-separated identifier list)
    def Vl(self):
        """Parse variable lists (comma-separated identifiers)"""
        n = 0  # Count variables
        
        while True:
            if n > 0:
                self.consume_token()  # Remove comma from previous iteration
                
            # Expect identifier
            current_token = self.peek_token()
            if not current_token or current_token.type != TokenType.ID:
                print("Parse error at Vl: id expected")
                return
                
            # Add identifier to AST
            self.ast.append(Node(NodeType.id, current_token.value, 0))
            self.consume_token()
            n += 1
            
            # Check for continuation (comma)
            next_token = self.peek_token()
            if not next_token or next_token.value != ",":
                break
        
        # Create comma node only if multiple variables
        if n > 1:
            self.ast.append(Node(NodeType.comma, ",", n))