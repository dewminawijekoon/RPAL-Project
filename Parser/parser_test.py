from lexical_analyzer import tokenize
from parser import Parser

# Test input with various language constructs
test_input = r"""
    let Is_Odd N =
    (N / 2) * 2 eq N -> 'Even'
    | 'Odd'
    in
    Print (Is_Odd (-8))
    """

# Additional test cases for different constructs
test_cases = {
    "function_definition": r"""
        let factorial(n) = n eq 0 -> 1 | n * factorial(n-1)
        in factorial(5)
    """,
    
    "lambda_expression": r"""
        fn x y . x + y
    """,
    
    "conditional_expression": r"""
        x > 0 -> "positive" | "non-positive"
    """,
    
    "tuple_operations": r"""
        let coords = (x, y, z) 
        in coords aug (1, 2, 3)
    """,
    
    "boolean_operations": r"""
        (x > 0) & (y < 10) or not z
    """,
    
    "arithmetic_expressions": r"""
        -x + y * z / w ** 2
    """,
    
    "function_application": r"""
        map @ f @ (1, 2, 3)
    """,
    
    "within_construct": r"""
        let x = 5 within
        let y = x + 1
        in y * 2
    """,
    
    "multiple_definitions": r"""
        let x = 1 and y = 2 and z = 3
        in x + y + z
    """,
    
    "recursive_function": r"""
        let rec fibonacci(n) = 
            n eq 0 -> 0 |
            n eq 1 -> 1 |
            fibonacci(n-1) + fibonacci(n-2)
        in fibonacci(10)
    """
}

def run_parser_tests(test_input=test_input, test_name="default"):
    print(f"\n=== Running parser test: {test_name} ===")
    print("Input:")
    print(test_input.strip())
    print("\n" + "="*50)
    
    try:
        # Tokenize the input
        tokens = tokenize(test_input)
        print(f"Generated {len(tokens)} tokens.")
        
        # Parse the tokens
        parser = Parser(tokens)
        ast = parser.parse()
        
        if ast is not None:
            print("✓ Parsing successful!")
            print(f"Generated AST with {len(ast)} nodes.")
            
            # Convert to string representation
            string_ast = parser.convert_ast_to_string_ast()
            print("\nAST Structure:")
            for line in string_ast:
                print(line)
                
            # Print expected node types found
            node_types_found = set()
            for node in ast:
                node_types_found.add(node.type.name)
            
            print(f"\nNode types found: {', '.join(sorted(node_types_found))}")
            
        else:
            print("✗ Parsing failed!")
            
    except Exception as e:
        print(f"✗ Error during parsing: {e}")
        import traceback
        traceback.print_exc()

def run_all_parser_tests():
    """Run all test cases"""
    print("Running comprehensive parser tests...\n")
    
    # Run the main test
    run_parser_tests(test_input, "main_test")
    
    # Run additional test cases
    for test_name, test_code in test_cases.items():
        run_parser_tests(test_code, test_name)

def run_specific_constructs_test():
    """Test specific language constructs individually"""
    print("\n=== Testing Individual Language Constructs ===")
    
    constructs = {
        "simple_let": "let x = 5 in x",
        "function_call": "f(x, y)",
        "tuple": "(1, 2, 3)",
        "conditional": "true -> 1 | 0",
        "boolean_and": "true & false",
        "boolean_or": "true or false",
        "boolean_not": "not true",
        "comparison": "x eq 5",
        "arithmetic": "x + y * z",
        "power": "x ** 2",
        "unary_minus": "-x",
        "at_operator": "f @ x",
        "augment": "x aug y",
        "parentheses": "(x + y)",
        "string_literal": '"hello world"',
        "integer_literal": "42",
        "identifier": "variable_name",
        "nil_value": "nil",
        "dummy_value": "dummy"
    }
    
    for construct_name, construct_code in constructs.items():
        print(f"\nTesting {construct_name}: {construct_code}")
        try:
            tokens = tokenize(construct_code)
            parser = Parser(tokens)
            ast = parser.parse()
            
            if ast:
                print(f"  ✓ Parsed successfully ({len(ast)} nodes)")
                # Show the main node type
                if ast:
                    main_type = ast[-1].type.name if ast else "unknown"
                    print(f"  Main node type: {main_type}")
            else:
                print("  ✗ Parse failed")
        except Exception as e:
            print(f"  ✗ Error: {e}")

# Main execution
if __name__ == "__main__":
    # Run the basic test
    run_parser_tests()
    
    # Uncomment to run all tests
    #run_all_parser_tests()
    
    # Uncomment to test individual constructs
    # run_specific_constructs_test()