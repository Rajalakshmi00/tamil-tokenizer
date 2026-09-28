import tamil

# --- Tamil classification tables ---
KURIL = set("அஇஉஎஒ")
NEDIL = set("ஆஈஊஏஓஐஔ")

MEI = set([
    "க்","ச்","ட்","த்","ப்","ற்",
    "ஞ்","ங்","ண்","ந்","ம்","ன்","ய்","ர்","ல்","ள்","வ்","ழ்"
])

# ------------------------------
# Proper atomic split
# ------------------------------
def atomic_split(word):
    return tamil.utf8.get_letters(word)

# ------------------------------
# Combine letters into "units" for seer rules
# ------------------------------
def group_for_seer(letters):
    grouped = []
    i = 0
    while i < len(letters):
        L = letters[i]

        # Check mei + uyir = uyirmei (e.g., க + ி = கி)
        if i+1 < len(letters):
            combined = L + letters[i+1]
            try:
                base, uyir = tamil.utf8.splitMeiUyir(combined)
                if uyir != "":
                    grouped.append(combined)
                    i += 2
                    continue
            except:
                pass

        # otherwise single unit
        grouped.append(L)
        i += 1

    return grouped

# ------------------------------
# Seer classification
# ------------------------------
def classify_seer(syllable):
    txt = "".join(syllable)

    if len(syllable)==1 and txt in KURIL: return "நேர்"
    if len(syllable)==1 and txt in NEDIL: return "நேர்"

    if len(syllable)==2 and syllable[0] in KURIL and syllable[1] in MEI:
        return "நேர்"

    if len(syllable)==2 and syllable[0] in KURIL and syllable[1] in KURIL:
        return "நிரை"

    if len(syllable)==2 and syllable[0] in KURIL and syllable[1] in NEDIL:
        return "நிரை"

    if len(syllable)==2 and syllable[0] in NEDIL and syllable[1] in MEI:
        return "நேர்"

    if len(syllable)==3 and syllable[0] in KURIL and syllable[1] in KURIL and syllable[2] in MEI:
        return "நிரை"

    return "பொருந்தவில்லை"

# ------------------------------
# Main seer splitter
# ------------------------------
def split_into_seer(word):
    letters = atomic_split(word)
    units = group_for_seer(letters)

    result = []
    i = 0

    while i < len(units):
        matched = False

        for length in [3,2,1]:
            chunk = units[i:i+length]
            if len(chunk) < length:
                continue
            if classify_seer(chunk) != "பொருந்தவில்லை":
                result.append("".join(chunk))
                i += length
                matched = True
                break

        if not matched:
            result.append(units[i])
            i += 1

    return result

# ------------------------------
# TEST
# ------------------------------
if __name__ == "__main__":
    w = "அலங்கடை"
    print("Original:", w)
    print("Split into seer:", split_into_seer(w))
