from sample import KURIL, NEDIL, MEI, classify_seer
import tamil

def get_syllables(word):
    letters = tamil.utf8.get_letters(word)
    syllables = []
    current = []

    for L in letters:
        base, mei = tamil.utf8.splitMeiUyir(L)

        if mei == "":
            # uyir → complete syllable
            if current:
                syllables.append(current)
                current = []
            current = [base]
            syllables.append(current)
            current = []
        else:
            # uyirmei → consonant + vowel
            if current:
                syllables.append(current)
                current = []
            current = [base + mei]
            syllables.append(current)
            current = []

    if current:
        syllables.append(current)

    return syllables


def split_into_seer(word):
    syllables = get_syllables(word)
    result = []

    for syl in syllables:
        result.append("".join(syl))

    return result


if __name__ == "__main__":
    w = "அலங்கடை"
    print(split_into_seer(w))
