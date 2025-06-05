import re
from enum import Enum

class TokenType(Enum):
    KEYWORD = 1
    ID = 2
    INT = 3
    STRING = 4
    END_OF_TOKENS = 5
    PUNCTUATION = 6
    OPERATOR = 7

# Token class to represent a single token
class Token:
    def __init__(self, token_type, value):
        if not isinstance(token_type, TokenType):
            raise ValueError("token_type must be an instance of TokenType enum")
        self.type = token_type
        self.value = value

    # Getters for type and value
    def get_type(self):
        return self.type

    def get_value(self):
        return self.value



def tokenize(input_str):
    tokens = []
    keywords = {
        # Single-line comment: starts with // and goes until the end of the line
        'COMMENT': r'//.*',
        # Keywords: exact matches for reserved words, ending on a word boundary
        'KEYWORD': r'(let|in|fn|where|aug|or|not|gr|ge|ls|le|eq|ne|true|false|nil|dummy|within|and|rec)\b',
        # String literals enclosed in single quotes, allowing escaped single quotes
        'STRING': r'\'(?:\\\'|[^\'])*\'',
        # Identifiers: start with a letter, followed by letters, digits, or underscores
        'ID': r'[a-zA-Z][a-zA-Z0-9_]*',
        # Integer literals: one or more digits
        'INT': r'\d+',
        # Operators: one or more of the specified symbols
        'OPERATOR': r'[+\-*<>&.@/:=~|$\#!%^_\[\]{}"\'?]+',
        # Whitespace: one or more spaces, tabs, or newlines
        'SPACES': r'[ \t\n]+',
        # Punctuation characters
        'PUNCTUATION': r'[();,]'
    }
    
    while input_str:
        # Flag to check if a pattern matched
        matched = False
        for key, pattern in keywords.items():
            match = re.match(pattern, input_str)
            if match:
                # print(key, match.group(0))
                if key != 'SPACES':
                    if key == 'COMMENT':
                        # If it's a comment, remove the comment from input
                        comment = match.group(0)
                        input_str = input_str[match.end():]
                        matched = True
                        break
                    else:
                        # Get the corresponding TokenType
                        token_type = getattr(TokenType, key)  
                        if not isinstance(token_type, TokenType):
                            raise ValueError(f"Token type '{key}' is not a valid TokenType")
                        # Create and add the token to the list
                        tokens.append(Token(token_type, match.group(0)))
                        input_str = input_str[match.end():]
                        matched = True
                        break
                input_str = input_str[match.end():]
                matched = True
                break
        if not matched:
            print("Error: Unable to tokenize input")
    return tokens
