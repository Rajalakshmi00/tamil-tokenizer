# tokenizer.py

from typing import List, Dict, Tuple
import unicodedata
from collections import Counter

from rules import classify_unit, SEER_RULES

# ---------- Low-level helpers ----------

def split_tamil_graphemes(text: str) -> List[str]:
    """
    Split Tamil string into logical grapheme clusters (consonant + signs).
    Works by grouping base + all following combining marks.
    This is enough for Tamil uyirmei segmentation.
    """
    clusters = []
    current = ""

    for ch in text:
        # combining marks have Unicode category starting with 'M'
        if not current:
            current = ch
        else:
            if unicodedata.category(ch).startswith("M"):
                current += ch
            else:
                clusters.append(current)
                current = ch

    if current:
        clusters.append(current)

    return clusters


def to_pattern(units: List[str]) -> str:
    """
    Convert list of grapheme units into pattern string:
    K = kuril, N = nedil, M = mei, X = unknown.
    """
    pattern = []
    for u in units:
        t = classify_unit(u)
        if t == "kuril":
            pattern.append("K")
        elif t == "nedil":
            pattern.append("N")
        elif t == "mei":
            pattern.append("M")
        else:
            pattern.append("X")
    return "".join(pattern)


def group_for_seer(graphemes: List[str], pattern: str) -> List[Tuple[List[str], str]]:
    """
    Groups for your exact rules: K,N,KM,NM,KK,KN,KKM,KNM
    """
    groups = []
    i = 0
    n = len(pattern)
    while i < n:
        # 3-unit patterns first (longest match)
        if i + 2 < n:
            if pattern[i:i+3] == "KKM":
                groups.append((graphemes[i:i+3], "KKM"))
                i += 3
                continue
            if pattern[i:i+3] == "KNM":
                groups.append((graphemes[i:i+3], "KNM"))
                i += 3
                continue

        # 2-unit patterns
        if i + 1 < n:
            if pattern[i] == "K" and pattern[i+1] == "M":
                groups.append((graphemes[i:i+2], "KM"))
                i += 2
                continue
            if pattern[i] == "N" and pattern[i+1] == "M":
                groups.append((graphemes[i:i+2], "NM"))
                i += 2
                continue
            if pattern[i] == "K" and pattern[i+1] == "K":
                groups.append((graphemes[i:i+2], "KK"))
                i += 2
                continue
            if pattern[i] == "K" and pattern[i+1] == "N":
                groups.append((graphemes[i:i+2], "KN"))
                i += 2
                continue

        # 1-unit patterns (K, N, M, X)
        groups.append(([graphemes[i]], pattern[i]))
        i += 1
    return groups


# ---------- Core seer splitter ----------

def split_into_seer(word: str) -> List[Dict]:
    """
    Main function:
    1. Split word into Tamil grapheme units.
    2. Map to K/N/M pattern.
    3. Group pattern into asai units using group_for_seer.
    4. For each group, look up in SEER_RULES.
    Returns list of dicts; each seer has:
      {
        'graphemes': [...],
        'pattern': 'K'/'KM'/...,
        'name': 'நேர் தனிக்குறில்', ...
        'asai': 'நேர்' or 'நிரை'
      }
    """
    graphemes = split_tamil_graphemes(word)
    raw_pattern = to_pattern(graphemes)
    grouped = group_for_seer(graphemes, raw_pattern)

    seers = []
    for gr_list, pat in grouped:
        if pat in SEER_RULES:
            rule = SEER_RULES[pat]
            seers.append({
                "graphemes": gr_list,
                "pattern": pat,
                "name": rule["name"],
                "asai": rule["asai"],
            })
        # unknown patterns are silently skipped

    return seers


# ---------- Corpus processing (detailed debug output) ----------

def process_corpus(input_file: str, output_file: str):
    """
    Read Tamil words from input_file (one word per line),
    process with split_into_seer, write detailed results to output_file.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]

        print(f"Processing {len(words)} words...")

        results = []
        for i, word in enumerate(words, 1):
            seers = split_into_seer(word)
            graphemes = split_tamil_graphemes(word)
            pattern = to_pattern(graphemes)

            result = f"WORD: {word}\n"
            result += f"  Graphemes: {graphemes}\n"
            result += f"  Raw pattern: {pattern}\n"

            if seers:
                for s in seers:
                    text = "".join(s["graphemes"])
                    result += f"  {text} -> {s['pattern']} -> {s['name']} ({s['asai']})\n"
                coverage = sum(len(s["graphemes"]) for s in seers)
                total_units = len(graphemes)
                result += f"  Coverage: {coverage}/{total_units} units ({coverage/total_units*100:.1f}%)\n\n"
            else:
                result += "  NO MATCHES FOUND\n\n"

            results.append(result)
            if i % 100 == 0:
                print(f"Processed {i}/{len(words)} words")

        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(results))

        print(f"✅ Results saved to {output_file}")

    except FileNotFoundError:
        print(f"❌ Input file '{input_file}' not found!")
    except Exception as e:
        print(f"❌ Error: {e}")


# ---------- Vocab building & encoding ----------

def build_vocab_from_corpus(input_file: str, vocab_file: str, min_freq: int = 1):
    """
    Read Tamil words from input_file, tokenize with split_into_seer,
    build vocabulary of unique tokens (seer units), and save to vocab_file.
    Each line: token \t id \t freq
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]

    token_counter = Counter()

    for word in words:
        seers = split_into_seer(word)
        for s in seers:
            tok = "".join(s["graphemes"])   # e.g. "அலங்", "கடை"
            token_counter[tok] += 1

    tokens = [t for t, c in token_counter.items() if c >= min_freq]
    tokens.sort(key=lambda x: (-token_counter[x], x))

    vocab = ["[PAD]", "[UNK]", "[BOS]", "[EOS]"] + tokens

    with open(vocab_file, 'w', encoding='utf-8') as vf:
        for idx, tok in enumerate(vocab):
            freq = token_counter.get(tok, 0)
            vf.write(f"{tok}\t{idx}\t{freq}\n")

    print(f"Vocab size (incl. specials): {len(vocab)}")
    print(f"✅ Saved vocab to {vocab_file}")


def load_vocab(vocab_file: str):
    """
    Load vocab file back into token->id and id->token dicts.
    """
    token2id = {}
    id2token = {}
    with open(vocab_file, 'r', encoding='utf-8') as vf:
        for line in vf:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            tok, idx = parts[0], int(parts[1])
            token2id[tok] = idx
            id2token[idx] = tok
    return token2id, id2token


def encode_word(word: str, token2id: dict):
    """
    Use your seer tokenizer to convert a Tamil word into token ids.
    Example: 'அலங்கடை' -> ['அலங்', 'கடை'] -> [id1, id2]
    """
    seers = split_into_seer(word)
    tokens = ["".join(s["graphemes"]) for s in seers]
    unk_id = token2id.get("[UNK]", 1)
    ids = [token2id.get(tok, unk_id) for tok in tokens]
    return tokens, ids


# ---------- Main entry ----------

if __name__ == "__main__":
    import sys

    # 1) Detailed seer analysis for whole corpus
    #    python tokenizer.py --corpus tamil_corpus.txt
    if len(sys.argv) == 3 and sys.argv[1] == "--corpus":
        input_file = sys.argv[2]
        process_corpus(input_file, "tamil_seer_results.txt")

    # 2) Build vocab from corpus
    #    python tokenizer.py --vocab tamil_corpus.txt
    elif len(sys.argv) == 3 and sys.argv[1] == "--vocab":
        corpus_file = sys.argv[2]
        build_vocab_from_corpus(corpus_file, "tamil_seer_vocab.txt")

    # 3) Encode a single word using existing vocab
    #    python tokenizer.py --encode அலங்கடை
    elif len(sys.argv) == 3 and sys.argv[1] == "--encode":
        word = sys.argv[2]
        token2id, id2token = load_vocab("tamil_seer_vocab.txt")
        toks, ids = encode_word(word, token2id)
        print("Word:", word)
        print("Tokens:", toks)
        print("IDs:   ", ids)

    else:
        print("Usage:")
        print("  python tokenizer.py --corpus tamil_corpus.txt")
        print("  python tokenizer.py --vocab tamil_corpus.txt")
        print("  python tokenizer.py --encode அலங்கடை")
