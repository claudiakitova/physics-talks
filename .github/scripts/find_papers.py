"""Find new open-access papers on the library's topics and download them into data/.

Searches OpenAlex for condensed matter papers from the last 16 days that have a
free PDF under an open license (CC BY, CC BY-SA, CC0, or public domain). Records every
added paper in data/papers.json and writes a summary for the pull request.
"""
import datetime as dt
import json
import os
import re
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

TOPICS = [
    '"orbital ordering"',
    '"orbital order"',
    '"Jahn-Teller"',
    '"Kugel-Khomskii"',
    "multiferroic",
    "magnetoelectric",
    "KCuF3",
    '"transition metal oxide"',
]
LICENSES = "cc-by|cc-by-sa|cc0|public-domain"
CONDENSED_MATTER = "subfields/3104"
MAX_NEW = 5
MAX_MB = 15
DEFAULT_DAYS = 16

DATA = Path("data")
MANIFEST = DATA / "papers.json"
SUMMARY = Path("new_papers.md")
HEADERS = {"User-Agent": "physics-talks-paper-finder"}


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as r:
        return json.load(r)


def search(topic, since):
    params = {
        "filter": ",".join([
            f"title_and_abstract.search:{topic}",
            f"from_publication_date:{since}",
            "open_access.is_oa:true",
            f"best_oa_location.license:{LICENSES}",
            "type:article|preprint",
            f"primary_topic.subfield.id:{CONDENSED_MATTER}",
        ]),
        "per_page": "50",
        "select": "id,doi,display_name,publication_date,authorships,best_oa_location",
    }
    return get_json("https://api.openalex.org/works?" + urllib.parse.urlencode(params))["results"]


def ascii_words(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"\$[^$]*\$", lambda m: re.sub(r"[^A-Za-z0-9]", "", m.group()), text)
    return re.findall(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", text)


def file_name(work):
    authors = work.get("authorships") or []
    name = (authors[0].get("author") or {}).get("display_name", "") if authors else ""
    parts = ascii_words(name)
    prefix = f"{parts[0][0]}.{parts[-1]}_" if len(parts) >= 2 else ""
    title, length = [], 0
    for word in ascii_words(work["display_name"]):
        if length + len(word) > 80:
            break
        title.append(word)
        length += len(word) + 1
    return prefix + "_".join(title) + ".pdf"


def download(url, path):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as r:
        content = r.read(MAX_MB * 1024 * 1024 + 1)
    if not content.startswith(b"%PDF") or len(content) > MAX_MB * 1024 * 1024:
        return False
    path.write_bytes(content)
    return True


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"papers": []}
    today = dt.date.today()
    since = str(today - dt.timedelta(days=DEFAULT_DAYS))
    known = {p["openalex_id"] for p in manifest["papers"]}
    existing_files = {p.name.lower() for p in DATA.glob("*.pdf")}

    found = {}
    for topic in TOPICS:
        for work in search(topic, since):
            pdf = (work.get("best_oa_location") or {}).get("pdf_url")
            if pdf and work["id"] not in known:
                entry = found.setdefault(work["id"], {"work": work, "topics": []})
                entry["topics"].append(topic.strip('"'))

    # Papers matching more topics first, then the newest.
    ranked = sorted(found.values(), key=lambda e: (len(e["topics"]), e["work"]["publication_date"]), reverse=True)

    added = []
    for entry in ranked:
        if len(added) == MAX_NEW:
            break
        work = entry["work"]
        name = file_name(work)
        if name.lower() in existing_files:
            continue
        location = work["best_oa_location"]
        try:
            ok = download(location["pdf_url"], DATA / name)
        except Exception as error:  # a broken link shouldn't stop the others
            print(f"Skipped {work['display_name']}: {error}")
            continue
        if not ok:
            print(f"Skipped {work['display_name']}: not a PDF or too large")
            continue
        existing_files.add(name.lower())
        authors = [(a.get("author") or {}).get("display_name", "") for a in work.get("authorships") or []]
        record = {
            "file": name,
            "title": work["display_name"],
            "authors": authors,
            "published": work["publication_date"],
            "doi": work.get("doi"),
            "openalex_id": work["id"],
            "pdf_url": location["pdf_url"],
            "license": location.get("license"),
            "topics": entry["topics"],
            "added": str(today),
        }
        manifest["papers"].append(record)
        added.append(record)

    if not added:
        print(f"No new papers since {since}")
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as out:
                out.write("added=0\n")
        return
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if added:
        lines = [f"Found {len(added)} new open-access paper(s) on the library's topics since {since}.", ""]
        for p in added:
            who = p["authors"][0] + (" et al." if len(p["authors"]) > 1 else "") if p["authors"] else "Unknown"
            link = p["doi"] or p["pdf_url"]
            lines.append(f"- **{p['title']}**  \n  {who}, {p['published']} · {p['license']} · topics: {', '.join(p['topics'])} · [link]({link})")
        lines += ["", "Merge to add them to the library (the search index rebuilds automatically). "
                  "To leave a paper out, delete its PDF from this pull request before merging."]
        SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Added {len(added)} paper(s) since {since}")

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as out:
            out.write(f"added={len(added)}\n")


if __name__ == "__main__":
    main()
