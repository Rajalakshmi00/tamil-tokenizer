# reverse_sandhi_rules.py
# Tamil Reverse Sandhi Rules - optimized for hybrid tokenizer

VOWELS = "அஆஇஈஉஊஎஏஒஓஐஔ"
SHORT_VOWELS = "அஇஉஎஒ"

def reverse_consonant_double_rule(word):
    """Split doubled consonants like ல்ல → ல் + ல"""
    splits = []
    for i in range(1, len(word)-1):
        if i < len(word) and word[i] == word[i-1]:
            w1 = word[:i]
            w2 = word[i:]
            splits.append((w1, w2))
    return splits

def reverse_y_insertion_rule(word):
    """Split ய் insertion like நரியா → நரி + ஆ"""
    splits = []
    for i in range(len(word)-1):
        if word[i:i+2] == "ய்":
            w1 = word[:i]
            w2 = word[i+2:]
            if w1 and w2 and w1[-1] in "அஆஇஈஉஊ" and w2[0] in VOWELS:
                splits.append((w1, w2))
    return splits

def reverse_v_insertion_rule(word):
    """Split வ் insertion like பூவா → பூ + ஆ"""
    splits = []
    for i in range(len(word)-1):
        if word[i:i+2] == "வ்":
            w1 = word[:i]
            w2 = word[i+2:]
            if w1 and w2 and w1[-1] in "ஓஊ" and w2[0] in VOWELS:
                splits.append((w1, w2))
    return splits

def reverse_n_k_rule(word):
    """Split ங்க → ந் + க"""
    splits = []
    for i in range(len(word)-1):
        if word[i:i+2] == "ங்":
            w1 = word[:i] + "ந்"
            w2 = "க" + word[i+2:]
            splits.append((w1, w2))
    return splits

def reverse_l_l_rule(word):
    """Split ல்ல → ல் + ல"""
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ல்ல":
            w1 = word[:i] + "ல்"
            w2 = "ல" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_simple_concatenation(word):
    """Simple splits for obvious compound words"""
    splits = []
    # Common compound word patterns
    common_patterns = [
        ("சாலை", 4), ("நாடு", 3), ("கல்வி", 4), 
        ("அரசு", 3), ("ஊர்", 2), ("வீடு", 3)
    ]
    
    for pattern, min_prefix in common_patterns:
        if word.endswith(pattern) and len(word) > len(pattern) + min_prefix:
            w1 = word[:-len(pattern)]
            w2 = pattern
            splits.append((w1, w2))
    
    return splits

# Export optimized rules for hybrid tokenizer
REVERSE_RULES = [
    reverse_consonant_double_rule,
    reverse_y_insertion_rule, 
    reverse_v_insertion_rule,
    reverse_n_k_rule,
    reverse_l_l_rule,
    reverse_simple_concatenation
]
