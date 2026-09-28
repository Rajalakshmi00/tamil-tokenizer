# seer_split.py

KURIL = set("அஇஉஎஒ")
NEDIL = set("ஆஈஊஏஓஐஔ")

MEI = set([
    "க்","ச்","ட்","த்","ப்","ற்",
    "ஞ்","ங்","ண்","ந்","ம்","ன்","ய்","ர்","ல்","ள்","வ்","ழ்"
])

# --- Seer classification ---
def classify_seer(syllable):
    txt = "".join(syllable)
    if len(syllable) == 1 and txt in KURIL:
        return "நேர்"
    if len(syllable) == 1 and txt in NEDIL:
        return "நேர்"
    if len(syllable) == 2 and syllable[0] in KURIL and syllable[1] in MEI:
        return "நேர்"
    if len(syllable) == 2 and syllable[0] in NEDIL and syllable[1] in MEI:
        return "நேர்"
    if len(syllable) == 2 and syllable[0] in KURIL and syllable[1] in KURIL:
        return "நிரை"
    if len(syllable) == 2 and syllable[0] in KURIL and syllable[1] in NEDIL:
        return "நிரை"
    if len(syllable) == 3 and syllable[0] in KURIL and syllable[1] in KURIL and syllable[2] in MEI:
        return "நிரை"
    if len(syllable) == 3 and syllable[0] in KURIL and syllable[1] in NEDIL and syllable[2] in MEI:
        return "நிரை"
    return "பொருந்தவில்லை"

# --- Correct atomic split (uyir+mei combined) ---
def atomic_split(word):
    letters = []
    i = 0
    while i < len(word):
        c = word[i]
        # Check for mei + vowel combination (uyirmei)
        if i+1 < len(word):
            combo = c + word[i+1]
            # If first is consonant and next is vowel sign, combine
            if combo not in MEI and word[i+1] not in MEI and c not in KURIL | NEDIL:
                letters.append(combo)
                i += 2
                continue
        # Check if two-char mei
        if i+1 < len(word) and (c+word[i+1]) in MEI:
            letters.append(c+word[i+1])
            i += 2
        else:
            letters.append(c)
            i += 1
    return letters

# --- Split using Seer rules ---
def split_into_seer(word):
    letters = atomic_split(word)
    result = []
    i = 0
    while i < len(letters):
        matched = False
        # Try 3 → 2 → 1 letters to match seer patterns
        for length in [3,2,1]:
            chunk = letters[i:i+length]
            if len(chunk) < length:
                continue
            if classify_seer(chunk) != "பொருந்தவில்லை":
                result.append("".join(chunk))
                i += length
                matched = True
                break
        if not matched:
            result.append(letters[i])
            i += 1
    return result

# --- MAIN ---
if __name__ == "__main__":
    word = "அலங்கடை"
    syllables = split_into_seer(word)
    print("Original Word:", word)
    print("Split into Seer syllables:", syllables)
