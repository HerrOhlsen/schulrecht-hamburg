# -*- coding: utf-8 -*-
"""Parse the pdftotext dump of the Hamburgisches Schulgesetz (HmbSG, 2023 edition)
into structured JSON: parts -> sections -> paragraphs -> Absaetze.

Usage: python3 -I parse_hmbsg.py <HmbSG_2023.txt> <out.json>
"""
import json
import re
import sys
from pathlib import Path

PART_RE = re.compile(r"^\s*–\s*([A-ZÄÖÜ]+)\s+TEIL\s*–\s*$")
SECTION_RE = re.compile(r"^\s{12,}(Erster|Zweiter|Dritter|Vierter|Fünfter|Sechster|Siebter|Achter|Neunter)\s+Abschnitt\s*$")
PARA_RE = re.compile(r"^\s*§\s*(\d+\s*[a-z]?)\s*$")
HEADER_RE = re.compile(r"^\s*[A-ZÄÖÜ]+\s+TEIL:\s+.*$")
ABSATZ_RE = re.compile(r"^\((\d+[a-z]?)\)\*?\s+")


def load_lines(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8").splitlines()
    # body starts at the second "– ERSTER TEIL –" (first one is the table of contents)
    starts = [i for i, l in enumerate(raw) if PART_RE.match(l) and "ERSTER" in l]
    body = raw[starts[1]:]
    out = []
    i = 0
    while i < len(body):
        l = body[i]
        s = l.strip()
        # page footer: number followed (after blanks) by "ZURÜCK ZUM INHALTSVERZEICHNIS"
        if re.fullmatch(r"\d+", s):
            j = i + 1
            while j < len(body) and not body[j].strip():
                j += 1
            if j < len(body) and body[j].strip().startswith("ZURÜCK ZUM INHALTSVERZEICHNIS"):
                i = j + 1
                # running header line follows
                while i < len(body) and (not body[i].strip() or HEADER_RE.match(body[i])):
                    i += 1
                continue
            # lone sentence number (superscript rendered on its own line)
            if len(s) == 1:
                i += 1
                continue
        if s.startswith("*"):
            while i < len(body) and body[i].strip():
                i += 1
            continue
        if s.startswith("www.landesrecht-hamburg.de") or s.startswith("ZURÜCK ZUM INHALTSVERZEICHNIS") or HEADER_RE.match(l):
            i += 1
            continue
        out.append(l)
        i += 1
    return out


def clean_text(lines: list[str]) -> str:
    """Join wrapped lines, de-hyphenate, strip sentence superscripts."""
    text = ""
    for l in lines:
        s = l.strip()
        if not s:
            continue
        if text.endswith("-") and s[:1].islower():
            text = text[:-1] + s
        elif text.endswith("-") and s[:1].isupper() and not text.endswith(" -"):
            # hyphenated compound broken at line end ("Erziehungs-\nmaßnahmen" stays, "Gesetz-\nund" keeps hyphen)
            text = text + " " + s if s.split()[0] in ("und", "oder") else text + s
        else:
            text = (text + " " + s) if text else s
    # sentence numbers: digit glued to a capital letter or opening quote, preceded by space/paren/start
    text = re.sub(r"\.(\d{1,2})(?=[A-ZÄÖÜ„»§])", ". ", text)
    text = re.sub(r"(^|[\s(„»])(\d{1,2})(?=[A-ZÄÖÜ„»§])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_absaetze(body_lines: list[str]) -> list[dict]:
    """Return list of {"nr": "1"|None, "text": ...}; lists are kept inline with 'Nummer n:' markers."""
    chunks: list[list[str]] = []
    for l in body_lines:
        s = l.strip()
        if ABSATZ_RE.match(s):
            chunks.append([s])
        elif chunks:
            chunks[-1].append(l)
        else:
            chunks.append([l])
    result = []
    for ch in chunks:
        nr = None
        m = ABSATZ_RE.match(ch[0])
        if m:
            nr = m.group(1)
            ch[0] = ch[0][m.end():]
        # list items: ">> " bullets and "1. " numbers
        norm = []
        expected = 1   # enumerations run 1, 2, 3 ...; "18. Lebensjahres" or "23. März" never match the expected number
        for raw in ch:
            s = raw.strip()
            s2 = re.sub(r"^>>\s*", "", s)
            m = re.match(r"^(\d{1,2})\.\s+\S", s)
            if m and int(m.group(1)) in (expected, 1):   # a new enumeration inside the same Absatz restarts at 1
                s2 = re.sub(r"^(\d{1,2})\.\s+", r"Nummer \1: ", s2)
                expected = int(m.group(1)) + 1
            norm.append(s2)
        txt = clean_text(norm)
        if txt:
            result.append({"nr": nr, "text": txt})
    return result


def parse(lines: list[str]) -> dict:
    parts, cur_part, cur_sec, cur_para = [], None, None, None
    body: list[str] = []
    pending_title = None  # ("part"|"section"|"para")

    def flush_para():
        nonlocal cur_para, body
        if cur_para is not None:
            cur_para["absaetze"] = split_absaetze(body)
            cur_para["aufgehoben"] = any("aufgehoben" in a["text"] for a in cur_para["absaetze"]) and len(cur_para["absaetze"]) == 1
            cur_sec["paragraphen"].append(cur_para)
        cur_para, body = None, []

    i = 0
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if PART_RE.match(l):
            flush_para()
            cur_part = {"roman": PART_RE.match(l).group(1).title(), "title": "", "abschnitte": []}
            parts.append(cur_part)
            cur_sec = None
            pending_title = "part"
            i += 1
            continue
        if SECTION_RE.match(l):
            flush_para()
            cur_sec = {"title": "", "paragraphen": []}
            cur_part["abschnitte"].append(cur_sec)
            pending_title = "section"
            i += 1
            continue
        if PARA_RE.match(l):
            flush_para()
            if cur_sec is None:
                cur_sec = {"title": "", "paragraphen": []}
                cur_part["abschnitte"].append(cur_sec)
            cur_para = {"id": PARA_RE.match(l).group(1).replace(" ", ""), "title": "", "absaetze": []}
            pending_title = "para"
            i += 1
            continue
        if pending_title:
            if not s:
                if (pending_title == "part" and cur_part["title"]) or (pending_title == "section" and cur_sec["title"]) or (pending_title == "para" and cur_para["title"]):
                    pending_title = None
                i += 1
                continue
            target = {"part": cur_part, "section": cur_sec, "para": cur_para}[pending_title]
            target["title"] = (target["title"] + " " + s).strip()
            i += 1
            continue
        if cur_para is not None:
            body.append(l)
        i += 1
    flush_para()
    return {"gesetz": "Hamburgisches Schulgesetz (HmbSG)", "stand": "zuletzt geändert am 3. Mai 2023", "teile": parts}


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    data = parse(load_lines(src))
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(sec["paragraphen"]) for t in data["teile"] for sec in t["abschnitte"])
    words = sum(len(a["text"].split()) for t in data["teile"] for sec in t["abschnitte"] for p in sec["paragraphen"] for a in p["absaetze"])
    print(f"{len(data['teile'])} Teile, {n} Paragrafen, {words} Wörter")
    for t in data["teile"]:
        print(f"  {t['roman']} Teil: {t['title']}  [{', '.join(str(len(s['paragraphen'])) for s in t['abschnitte'])}]")
