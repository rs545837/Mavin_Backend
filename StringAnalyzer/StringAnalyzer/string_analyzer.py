import string

def analyze_string(input_string):
    # Initialize counters
    total_chars = len(input_string)
    alphabetic_chars = 0
    numeric_chars = 0
    whitespace_chars = 0
    special_chars = 0
    word_count = 0

    # Check each character in the string
    for char in input_string:
        if char.isalpha():
            alphabetic_chars += 1
        elif char.isdigit():
            numeric_chars += 1
        elif char.isspace():
            whitespace_chars += 1
        elif char in string.punctuation:
            special_chars += 1

    # Count words by splitting the string on whitespace
    words = input_string.split()
    word_count = len(words)

    # Print the results
    print("String Metrics:")
    print(f"Total characters: {total_chars}")
    print(f"Alphabetic characters: {alphabetic_chars}")
    print(f"Numeric characters: {numeric_chars}")
    print(f"Whitespace characters: {whitespace_chars}")
    print(f"Special characters: {special_chars}")
    print(f"Word count: {word_count}")

# Test cases
analyze_string("The quick brown fox jumped over the lazy dog")
print()  # Separator for better readability
analyze_string("There are 5 apples and 12 oranges in the basket.")
print()
analyze_string("Wow, Python is great... don't you think?!? It's my #1 favorite programming language.")
print()
analyze_string("")