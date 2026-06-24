import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
INDEX = ROOT / "shared" / "library" / "loop-index.json"

def _load():
    return json.loads(INDEX.read_text())

def _tokens(text):
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]

def _score(entry, q_tokens):
    hay = " ".join([entry["title"], entry["archetype"], " ".join(entry["tags"]), entry["slug"]]).lower()
    hay_tokens = _tokens(hay)
    if not hay_tokens:
        return 0.0
    score = 0.0
    for qt in q_tokens:
        tf = hay_tokens.count(qt)
        if tf:
            score += 1.0 + 0.3 * (tf - 1)          # keyword TF
        if any(qt in ht for ht in hay_tokens):      # substring partial
            score += 0.25
    return score

def match(query, limit=5):
    q = _tokens(query)
    data = _load()
    ranked = sorted(data, key=lambda e: (-_score(e, q), int(e["id"])))
    return ranked[:limit]

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    for e in match(query, lim):
        print(f'{e["id"]:>3}  {e["title"]}  [{e["source"]}]  {e["url"]}')
