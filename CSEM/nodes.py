# Base class for all symbols used in the CSE machine.
class Symbol:
    def __init__(self, data):
        self.data = data  # Core value or label of the symbol.

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

# Rand represents operands (constants, identifiers, etc.).
class Rand(Symbol):
    def __init__(self, data):
        super().__init__(data)

    def get_data(self):
        return super().get_data()

# Rator represents operators in the CSE machine (unary or binary).
class Rator(Symbol):
    def __init__(self, data):
        super().__init__(data)

# B represents the beginning of a new control stack segment (used for scoping).
class B(Symbol):
    def __init__(self):
        super().__init__("b")
        self.symbols = []  # Used to store symbols within a block (optional).

# Beta symbol for conditional branching in the control structure.
class Beta(Symbol):
    def __init__(self):
        super().__init__("beta")

# Boolean constant.
class Bool(Rand):
    def __init__(self, data):
        super().__init__(data)

# Binary operator (like +, -, *, /, etc.).
class Bop(Rator):
    def __init__(self, data):
        super().__init__(data)

# Delta is a subtree or lambda body stored in the control structure.
class Delta(Symbol):
    def __init__(self, i):
        super().__init__("delta")
        self.index = i            # Delta index used to reference it.
        self.symbols = []         # Symbols (AST nodes) inside this delta.

    def set_index(self, i):
        self.index = i

    def get_index(self):
        return self.index

# Dummy is used for dummy variable bindings, such as in recursion (like Y combinator).
class Dummy(Rand):
    def __init__(self):
        super().__init__("dummy")

# E represents an environment record in the environment stack.
class E(Symbol):
    def __init__(self, i):
        super().__init__("e")
        self.index = i            # Index to identify the environment.
        self.parent = None        # Reference to the parent environment (lexical scoping).
        self.is_removed = False   # Tracks if the environment is removed from stack.
        self.values = {}          # Map from Id symbols to their bound values.

    def set_parent(self, e):
        self.parent = e

    def get_parent(self):
        return self.parent

    def set_index(self, i):
        self.index = i

    def get_index(self):
        return self.index

    def set_is_removed(self, is_removed):
        self.is_removed = is_removed

    def get_is_removed(self):
        return self.is_removed

    # Lookup searches for the value of a variable in the environment chain.
    def lookup(self, id):
        for key in self.values:
            if key.get_data() == id.get_data():
                return self.values[key]
        if self.parent is not None:
            return self.parent.lookup(id)
        else:
            return Symbol(id.get_data())  # Return an unbound symbol if not found.

# Err represents an error symbol.
class Err(Symbol):
    def __init__(self):
        super().__init__("")

# Eta is a closure: a triple of environment, identifier, and lambda body.
class Eta(Symbol):
    def __init__(self):
        super().__init__("eta")
        self.index = None
        self.environment = None
        self.identifier = None    # The identifier being abstracted.
        self.lambda_ = None       # The actual lambda expression body (control structure).

    def set_index(self, i):
        self.index = i

    def get_index(self):
        return self.index

    def set_environment(self, e):
        self.environment = e

    def get_environment(self):
        return self.environment

    def set_identifier(self, identifier):
        self.identifier = identifier

    def set_lambda(self, lambda_):
        self.lambda_ = lambda_

    def get_lambda(self):
        return self.lambda_

# Gamma is the apply operator in the CSE machine (used to apply functions).
class Gamma(Symbol):
    def __init__(self):
        super().__init__("gamma")

# Id represents variable identifiers.
class Id(Rand):
    def __init__(self, data):
        super().__init__(data)

    def get_data(self):
        return super().get_data()

# Integer constants.
class Int(Rand):
    def __init__(self, data):
        super().__init__(data)

# Lambda symbol representing a function in the control structure.
class Lambda(Symbol):
    def __init__(self, i):
        super().__init__("lambda")
        self.index = i              # Index assigned during control structure creation.
        self.environment = None     # The environment in which the lambda was created.
        self.identifiers = []       # List of formal parameters.
        self.delta = None           # The body of the lambda (as a Delta symbol).

    def set_environment(self, n):
        self.environment = n

    def get_environment(self):
        return self.environment

    def set_delta(self, delta):
        self.delta = delta

    def get_delta(self):
        return self.delta

    def get_index(self):
        return self.index

# String constants.
class Str(Rand):
    def __init__(self, data):
        super().__init__(data)

# Tau is used to create a tuple of size n.
class Tau(Symbol):
    def __init__(self, n):
        super().__init__("tau")
        self.set_n(n)

    def set_n(self, n):
        self.n = n

    def get_n(self):
        return self.n

# Tup is the tuple data structure to hold a sequence of values.
class Tup(Rand):
    def __init__(self):
        super().__init__("tup")
        self.symbols = []  # Elements of the tuple.

# Uop represents unary operators.
class Uop(Rator):
    def __init__(self, data):
        super().__init__(data)

# Y* is a special symbol used for recursive function application (Y combinator).
class Ystar(Symbol):
    def __init__(self):
        super().__init__("<Y*>")
