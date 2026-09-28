# final_code_tamil_tokenizer_pure_rules.py
from reverse_sandhi_rules import REVERSE_RULES

def apply_sandhi_rules(word, depth=0):
    """Apply reverse sandhi rules purely based on patterns"""
    if depth > 3:  # Prevent infinite recursion
        return [word]
    
    # Try each reverse rule
    for rule in REVERSE_RULES:
        splits = rule(word)
        if splits:
            # Use the first valid split found
            w1, w2 = splits[0]
            # Recursively apply rules to both parts
            result1 = apply_sandhi_rules(w1, depth+1) if len(w1) > 1 else [w1]
            result2 = apply_sandhi_rules(w2, depth+1) if len(w2) > 1 else [w2]
            return result1 + result2
    
    return [word]

def tamil_tokenize_pure_rules(text):
    """Pure rule-based tokenizer - no vocabulary dependency"""
    words = text.split()
    tokens = []
    
    for word in words:
        result = apply_sandhi_rules(word)
        tokens.extend(result)
    
    return tokens

# Example usage
if __name__ == "__main__":
    examples = [
        "அலங்கடை"
    ]
    
    for ex in examples:
        result = tamil_tokenize_pure_rules(ex)
        print(f"{ex} -> {result}")
