"""Merge whisper sub-tokens ('-carrying', '.works.', '-up,') into the previous word."""
import json, sys
words = json.load(open(sys.argv[1]))
out = []
for w in words:
    t = w["w"]
    if out and (t.startswith("-") or t.startswith(".")):
        out[-1]["w"] += t.rstrip(".,") if t.startswith(".works") else t
        out[-1]["e"] = w["e"]
    else:
        out.append(dict(w))
json.dump(out, open(sys.argv[2], "w"))
print(len(words), "->", len(out))
