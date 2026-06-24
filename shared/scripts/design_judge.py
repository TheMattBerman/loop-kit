REQUIRED = ["done_criteria", "verification_method", "source_of_truth", "approval_boundary"]
VAGUE = ["good", "better", "until satisfied", "as needed", "improve", "high quality", "make it nice"]
VAGUE_FIELDS = ["done_criteria", "verification_method"]

def judge(spec):
    missing = [k for k in REQUIRED if not str(spec.get(k, "")).strip()]
    vague = []
    for k in VAGUE_FIELDS:
        v = str(spec.get(k, "")).lower()
        if v and any(m in v for m in VAGUE):
            vague.append(k)
    verdict = "PASS" if not missing and not vague else "FAIL"
    return {"verdict": verdict, "missing": missing, "vague": vague}

def judge_markdown(text):
    spec = {}
    for line in text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            spec[k.strip().lower().replace(" ", "_")] = v.strip()
    return judge(spec)

if __name__ == "__main__":
    import sys, json
    data = sys.stdin.read()
    print(json.dumps(judge_markdown(data), indent=2))
