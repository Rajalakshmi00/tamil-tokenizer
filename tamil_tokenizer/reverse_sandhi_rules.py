# reverse_sandhi_rules.py
# Tamil Reverse Sandhi Rules - converted from joining rules to splitting rules

VOWELS = "அஆஇஈஉஊஎஏஒஓஐஔ"
SHORT_VOWELS = "அஇஉஎஒ"

# ------------------------
# Reverse Rule Definitions
# ------------------------

def reverse_pulli_vowel_rule(word):
    """ Reverse Rule 1: Split Pulli + Vowel Joining """
    splits = []
    for i in range(1, len(word)):
        if word[i] in VOWELS:
            w1 = word[:i] + "்"
            w2 = word[i:]
            splits.append((w1, w2))
    return splits

def reverse_ugar_rule(word):
    """ Reverse Rule 2: Split உகர Sandhi """
    splits = []
    for i in range(1, len(word)):
        if word[i] == "உ":
            w1 = word[:i] + "உ" 
            w2 = "உ" + word[i+1:]
            if w1.endswith("உ"):
                splits.append((w1, w2))
    return splits

def reverse_vowel_lengthen_rule(word):
    """ Reverse Rule 3: Split Vowel Lengthening """
    splits = []
    long_map = {"ஆ": "அ", "ஈ": "இ", "ஊ": "உ", "ஏ": "எ", "ஓ": "ஒ"}
    for i in range(len(word)):
        if word[i] in long_map:
            w1 = word[:i] + long_map[word[i]]
            w2 = long_map[word[i]] + word[i+1:]
            splits.append((w1, w2))
    return splits

def reverse_consonant_double_rule(word):
    """ Reverse Rule 4: Split Consonant Doubling """
    splits = []
    for i in range(1, len(word)):
        if word[i] == word[i-1]:
            w1 = word[:i]
            w2 = word[i:]
            splits.append((w1, w2))
    return splits

def reverse_n_k_rule(word):
    """ Reverse Rule 5: Split ங்க → ந் + க """
    splits = []
    for i in range(len(word)-1):
        if word[i:i+2] == "ங்":
            w1 = word[:i] + "ந்"
            w2 = "க" + word[i+2:]
            splits.append((w1, w2))
    return splits

def reverse_m_p_rule(word):
    """ Reverse Rule 6: Split ம்ப → ம் + ப """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ம்ப":
            w1 = word[:i] + "ம்"
            w2 = "ப" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_y_insertion_rule(word):
    """ Reverse Rule 7: Split ய் Insertion """
    splits = []
    for i in range(len(word)-1):
        if word[i:i+2] == "ய்":
            w1 = word[:i]
            w2 = word[i+2:]
            if w1 and w1[-1] in "அஆஇஈஉஊ" and w2 and w2[0] in VOWELS:
                splits.append((w1, w2))
    return splits

def reverse_v_insertion_rule(word):
    """ Reverse Rule 8: Split வ் Insertion """
    splits = []
    for i in range(len(word)-1):
        if word[i:i+2] == "வ்":
            w1 = word[:i]
            w2 = word[i+2:]
            if w1 and w1[-1] in "ஓஊ" and w2 and w2[0] in VOWELS:
                splits.append((w1, w2))
    return splits

def reverse_l_t_rule(word):
    """ Reverse Rule 9: Split ள்ட → ள் + ட """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ள்ட":
            w1 = word[:i] + "ள்"
            w2 = "ட" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_r_r_rule(word):
    """ Reverse Rule 10: Split ர்ர → ர் + ர """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ர்ர":
            w1 = word[:i] + "ர்"
            w2 = "ர" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_l_l_rule(word):
    """ Reverse Rule 11: Split ல்ல → ல் + ல """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ல்ல":
            w1 = word[:i] + "ல்"
            w2 = "ல" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_n_t_rule(word):
    """ Reverse Rule 12: Split ண்ட → ந் + ட """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ண்ட":
            w1 = word[:i] + "ந்"
            w2 = "ட" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_m_m_rule(word):
    """ Reverse Rule 13: Split ம்ம → ம் + ம """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ம்ம":
            w1 = word[:i] + "ம்"
            w2 = "ம" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_y_y_rule(word):
    """ Reverse Rule 14: Split ய்ய → ய் + ய """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ய்ய":
            w1 = word[:i] + "ய்"
            w2 = "ய" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_v_v_rule(word):
    """ Reverse Rule 15: Split வ்வ → வ் + வ """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "வ்வ":
            w1 = word[:i] + "வ்"
            w2 = "வ" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_r_c_rule(word):
    """ Reverse Rule 16: Split ற்ச → ற் + ச """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ற்ச":
            w1 = word[:i] + "ற்"
            w2 = "ச" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_n_c_rule(word):
    """ Reverse Rule 17: Split ஞ்ச → ந் + ச """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ஞ்ச":
            w1 = word[:i] + "ந்"
            w2 = "ச" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_l_c_rule(word):
    """ Reverse Rule 18: Split ல்ச → ல் + ச """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ல்ச":
            w1 = word[:i] + "ல்"
            w2 = "ச" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_n_th_rule(word):
    """ Reverse Rule 19: Split ந்த → ந் + த """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ந்த":
            w1 = word[:i] + "ந்"
            w2 = "த" + word[i+3:]
            splits.append((w1, w2))
    return splits

def reverse_m_c_rule(word):
    """ Reverse Rule 20: Split ஞ்ச → ம் + ச """
    splits = []
    for i in range(len(word)-2):
        if word[i:i+3] == "ஞ்ச":
            w1 = word[:i] + "ம்"
            w2 = "ச" + word[i+3:]
            splits.append((w1, w2))
    return splits

# ------------------------
# Export list of reverse rules
# ------------------------

REVERSE_RULES = [
    reverse_pulli_vowel_rule, reverse_ugar_rule, reverse_vowel_lengthen_rule, reverse_consonant_double_rule,
    reverse_n_k_rule, reverse_m_p_rule, reverse_y_insertion_rule, reverse_v_insertion_rule,
    reverse_l_t_rule, reverse_r_r_rule, reverse_l_l_rule, reverse_n_t_rule,
    reverse_m_m_rule, reverse_y_y_rule, reverse_v_v_rule, reverse_r_c_rule,
    reverse_n_c_rule, reverse_l_c_rule, reverse_n_th_rule, reverse_m_c_rule
]
