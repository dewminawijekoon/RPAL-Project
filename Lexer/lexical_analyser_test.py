from lexical_analyzer import tokenize, TokenType

test_input = r"""
    let Sum(A) = Psum (A,Order A )
    where rec Psum (T,N) = N eq 0 -> 0
    | Psum(T,N-1)+T N in Print ( Sum (1,2,3,4,5) )

    // This is a comment
    """

def run_tokenizer_tests(test_input=test_input):
    print("Running tokenizer tests...")
    tokens = tokenize(test_input)
    print(f"Generated {len(tokens)} tokens.")
    print("Expected tokens:")

    for token in tokens:
        print(f"{token.get_type().name}: {token.get_value()}")

# Call the function to run tests
run_tokenizer_tests()
