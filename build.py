"""Build the CCAO-F mock exam app.

1. Chunks every lesson in text/ into a retrieval knowledge base (kb.json).
2. Collects the question bank from src/q*.js.
3. Inlines both into src/template.html -> mock-exam/index.html (works offline via file://).
"""
import glob, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://claudecertificationguide.com"

DOMAINS = {
    1: ("Prompting and Task Execution", 14),
    2: ("Output Evaluation and Validation", 21),
    3: ("Product and Model Selection", 12),
    4: ("Workflow Integration and Solution Design", 16),
    5: ("Configuration and Knowledge Management", 12),
    6: ("Governance, Risk, and Responsible Use", 15),
    7: ("Troubleshooting and Optimisation", 10),
}

# lesson id -> url path (from the crawled link list)
paths = {}
for line in open(os.path.join(ROOT, "site_raw", "lessons.txt")):
    line = line.strip()
    if line:
        m = re.search(r"/(\d)-(\d)-[^/]+$", line)
        paths[f"{m.group(1)}.{m.group(2)}"] = BASE + line

chunks, lessons = [], []
for f in sorted(glob.glob(os.path.join(ROOT, "text", "*.txt"))):
    name = os.path.basename(f)[:-4]
    lid = ".".join(name.split("-")[:2])
    d = int(lid.split(".")[0])
    t = open(f, encoding="utf8", errors="replace").read().replace("�", "-")
    t = re.sub(r"Learn this interactively.*?\n", "", t)
    t = re.split(r"\n## Build Exercise", t)[0]
    title = re.search(r"^## (.+)$", t, re.M).group(1).strip()
    lessons.append({"id": lid, "d": d, "title": title, "url": paths[lid]})
    # sections by heading
    parts = re.split(r"\n## ", "\n" + t)
    for p in parts[1:]:
        head, _, body = p.partition("\n")
        head = head.strip()
        if head == title or not body.strip():
            continue
        body = re.sub(r"\n(Exam Trap|Key Concept|Check Answer)\n", r"\n[\1] ", body)
        body = re.sub(r"\n{2,}", "\n", body).strip()
        # window paragraphs into ~700 char chunks
        buf = ""
        for para in body.split("\n"):
            if buf and len(buf) + len(para) > 750:
                chunks.append((lid, d, head, buf.strip()))
                buf = ""
            buf += para + "\n"
        if buf.strip():
            chunks.append((lid, d, head, buf.strip()))

kb = [{"i": i, "l": c[0], "d": c[1], "h": c[2], "t": c[3]} for i, c in enumerate(chunks)]

questions = "var Q=[];\n" + "\n".join(
    open(p, encoding="utf8").read() for p in sorted(glob.glob(os.path.join(ROOT, "src", "q*.js")))
) + "\n" + open(os.path.join(ROOT, "src", "z_distractors.js"), encoding="utf8").read() + "\n" + open(os.path.join(ROOT, "src", "zz_patch.js"), encoding="utf8").read()

tpl = open(os.path.join(ROOT, "src", "template.html"), encoding="utf8").read()
out = (
    tpl.replace("/*DOMAINS*/", json.dumps({k: {"name": v[0], "w": v[1]} for k, v in DOMAINS.items()}))
    .replace("/*LESSONS*/", json.dumps(lessons))
    .replace("/*KB*/", json.dumps(kb, ensure_ascii=False))
    .replace("/*QUESTIONS*/", questions)
)
os.makedirs(os.path.join(ROOT, "mock-exam"), exist_ok=True)
open(os.path.join(ROOT, "mock-exam", "index.html"), "w", encoding="utf8").write(out)
json.dump(kb, open(os.path.join(ROOT, "mock-exam", "knowledge_base.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(f"lessons={len(lessons)} chunks={len(kb)} html={len(out)//1024}KB")
