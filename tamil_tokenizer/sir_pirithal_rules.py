# sir_pirithal_rules.py
# Tamil Siri Pirithal (சீர் பிரித்தல்) – Rule-based Tokenizer

# ----------------------------------------------------
# Tamil Character Sets
# ----------------------------------------------------

KURIL = set("அஇஉஎஒ")
NEDIL = set("ஆஈஊஏஓ")
UYIR = KURIL | NEDIL

VOWEL_SIGNS_KURIL = set("ிுெொ")
VOWEL_SIGNS_NEDIL = set("ாீூேோைௌ")

MEI = set("க் ச் ட் த் ப் ற் ஞ் ங் ந் ண் ம் ல் ள் ய் ர் வ்")  # Pure consonants (mei)

# Helper —
def is_mei(ch):
    return len(ch) == 2 and ch[-1] == "்"

# ----------------------------------------------------
# Sir (சீர்) Identification Rules
# ----------------------------------------------------

def is_thani_kuril(seq):
    """Rule 1: தனிக்குறில் = single short vowel (க)"""
    return len(seq) == 1 and seq in KURIL

def is_thani_nedil(seq):
    """Rule 2: தனிநெடில் = single long vowel (ஆ)"""
    return len(seq) == 1 and seq in NEDIL

def is_kuril_ottu(seq):
    """Rule 3: குறில் + ஒற்று  (க + ள்) = கல்"""
    return len(seq) == 2 and seq[0] in KURIL and is_mei(seq[1] + "்")  # simulated check

def is_nedil_ottu(seq):
    """Rule 4: நெடில் + ஒற்று  (கா + ள்) = கால்"""
    return len(seq) >= 2 and seq[0] in NEDIL and seq[-1] == "்"

def is_kuril_kuril(seq):
    """Rule 5: குறில் + குறில் (or குறிலிணை) = பனை"""
    return len(seq) == 2 and seq[0] in KURIL and seq[1] in KURIL

def is_kuril_nedil(seq):
    """Rule 6: குறில் + நெடில் = பலா"""
    return len(seq) == 2 and seq[0] in KURIL and seq[1] in NEDIL

def is_kuril_inai_ottu(seq):
    """Rule 7: குறிலிணை + ஒற்று = மல + ர்"""
    if len(seq) < 3: 
        return False
    return seq[-1] == "்" and seq[:-1][0] in KURIL and seq[:-1][1] in KURIL

def is_kuril_nedil_ottu(seq):
    """Rule 8: குறில் + நெடில் + ஒற்று = கணீர்"""
    return len(seq) >= 3 and seq[0] in KURIL and seq[1] in NEDIL and seq[-1] == "்"

# ----------------------------------------------------
# Main Splitter
# ----------------------------------------------------

def split_by_rules(word):
    sir_list = []
    i = 0

    while i < len(word):
        # Try longest → shortest match

        # Rule 8
        if i + 3 <= len(word) and is_kuril_nedil_ottu(word[i:i+3]):
            sir_list.append(word[i:i+3])
            i += 3
            continue

        # Rule 7
        if i + 3 <= len(word) and is_kuril_inai_ottu(word[i:i+3]):
            sir_list.append(word[i:i+3])
            i += 3
            continue

        # Rule 6
        if i + 2 <= len(word) and is_kuril_nedil(word[i:i+2]):
            sir_list.append(word[i:i+2])
            i += 2
            continue

        # Rule 5
        if i + 2 <= len(word) and is_kuril_kuril(word[i:i+2]):
            sir_list.append(word[i:i+2])
            i += 2
            continue

        # Rule 4
        if i + 2 <= len(word) and is_nedil_ottu(word[i:i+2]):
            sir_list.append(word[i:i+2])
            i += 2
            continue

        # Rule 3
        if i + 2 <= len(word) and is_kuril_ottu(word[i:i+2]):
            sir_list.append(word[i:i+2])
            i += 2
            continue

        # Rule 2
        if is_thani_nedil(word[i]):
            sir_list.append(word[i])
            i += 1
            continue

        # Rule 1
        if is_thani_kuril(word[i]):
            sir_list.append(word[i])
            i += 1
            continue

        # Fallback (unknown char)
        sir_list.append(word[i])
        i += 1

    return sir_list


# ----------------------------------------------------
# Test
# ----------------------------------------------------

if __name__ == "__main__":
    tests = ["கல்", "கால்", "பனை", "பலா", "மலர்", "கணீர்"]
    for t in tests:
        print(t, "→", split_by_rules(t))
