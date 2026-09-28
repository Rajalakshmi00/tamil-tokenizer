# --- Tamil classification tables ---

KURIL = set("அஇஉஎஒ")
NEDIL = set("ஆஈஊஏஓஐஔ")

MEI = set([
    "க்","ச்","ட்","த்","ப்","ற்",
    "ஞ்","ங்","ண்","ந்","ம்","ன்","ய்","ர்","ல்","ள்","வ்","ழ்"
])

# returns: "நேர்", "நிரை", "பொருந்தவில்லை"
def classify_seer(syllable):
    """
    syllable = [base vowel OR consonant+vowel OR +mei]
    Example: ['அ'] OR ['ல','ம்']
    """

    # simplify
    txt = "".join(syllable)

    # patterns
    if len(syllable) == 1 and txt in KURIL:
        return "நேர்"                           # தனிக்குறில்

    if len(syllable) == 1 and txt in NEDIL:
        return "நேர்"                           # தனிநெடில்

    if (len(syllable) == 2 
        and syllable[0] in KURIL 
        and syllable[1] in MEI):
        return "நேர்"                           # குறில் + ஒற்று

    if (len(syllable) == 2
        and syllable[0] in NEDIL
        and syllable[1] in MEI):
        return "நேர்"                           # நெடில் + ஒற்று

    if (len(syllable) == 2 
        and syllable[0] in KURIL 
        and syllable[1] in KURIL):
        return "நிரை"                           # குறில் + குறில்

    if (len(syllable) == 2 
        and syllable[0] in KURIL 
        and syllable[1] in NEDIL):
        return "நிரை"                           # குறில் + நெடில்

    if (len(syllable) == 3
        and syllable[0] in KURIL
        and syllable[1] in KURIL
        and syllable[2] in MEI):
        return "நிரை"                           # குறில் + குறில் + ஒற்று

    if (len(syllable) == 3
        and syllable[0] in KURIL
        and syllable[1] in NEDIL
        and syllable[2] in MEI):
        return "நிரை"                           # குறில் + நெடில் + ஒற்று

    return "பொருந்தவில்லை"
