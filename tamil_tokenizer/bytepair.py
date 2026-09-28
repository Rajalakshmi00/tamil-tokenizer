import tiktoken

enc = tiktoken.get_encoding("cl100k_base")   # GPT-4/GPT-5 tokenizer

samples = [
    "அரசுத்துறைஅமைச்சர்",
    "செம்மலர்ந்துபார்த்தான்",
    "massஆனா",
    "வணக்கம்😊",
    "😂🔥அம்மாaa!!!"
]

for s in samples:
    tokens = enc.encode(s)
    print(s, "→", tokens, "→ decoded:", enc.decode(tokens))
