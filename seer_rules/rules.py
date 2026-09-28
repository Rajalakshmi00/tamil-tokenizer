# rules.py

# 1. Basic Tamil sets
KURIL = set("அஇஉஎஒ")  # short vowels
NEDIL = set("ஆஈஊஏஐஓஔ")  # long vowels

# Common mei letters (க to ன without vowel sign)
MEI = set("கஙசஞடணதநபமயரலவழளறனஜஷஸஹக்ஷ")

# Dependent vowel signs (kuril-type and nedil-type)
KURIL_SIGNS = set(["ி", "ு", "ெ", "ொ"])     
NEDIL_SIGNS = set(["ா", "ீ", "ூ", "ே", "ை", "ோ", "ௌ"])  

# Tamil virama (pulli) for pure consonant
PULLI = "்"

def is_kuril_char(ch: str) -> bool:
    return ch in KURIL

def is_nedil_char(ch: str) -> bool:
    return ch in NEDIL

def classify_uyirmei(base: str, signs: str) -> str:
    if signs == PULLI:
        return "mei"
    if any(s in NEDIL_SIGNS for s in signs):
        return "nedil"
    if any(s in KURIL_SIGNS for s in signs):
        return "kuril"
    return "unknown"

def classify_unit(unit: str) -> str:
    """
    IMPORTANT: Bare consonants (no vowel sign, no pulli) → kuril (implicit அ)
    """
    # Single standalone vowel
    if len(unit) == 1:
        if is_kuril_char(unit):
            return "kuril"
        if is_nedil_char(unit):
            return "nedil"
        # bare consonant → treat as kuril-uyirmei (implicit அ)
        if unit in MEI:
            return "kuril"  # ← KEY FIX
        return "unknown"

    # uyirmei cluster: base + signs
    base = unit[0]
    signs = unit[1:]
    
    if signs.endswith(PULLI):
        return "mei"
    
    t = classify_uyirmei(base, signs)
    if t in ("kuril", "nedil", "mei"):
        return t
    return "unknown"

# 2. YOUR EXACT சீர் பிரித்தல் rules
SEER_RULES = {
    # நேர் rules
    "K":  {"name": "நேர் தனிக்குறில்",       "asai": "நேர்"},
    "N":  {"name": "நேர் தனிநெடில்",        "asai": "நேர்"},
    "KM": {"name": "நேர் குறில் ஒற்று",      "asai": "நேர்"},
    "NM": {"name": "நேர் நெடில் ஒற்று",      "asai": "நேர்"},
    
    # நிரை rules  
    "KK": {"name": "நிரை குறில் குறில்",     "asai": "நிரை"},
    "KN": {"name": "நிரை குறில் நெடில்",     "asai": "நிரை"},
    "KKM":{"name": "நிரை குறிலிணை ஒற்று",   "asai": "நிரை"},
    "KNM":{"name": "நிரை குறில் நெடில் ஒற்று","asai": "நிரை"},
}
