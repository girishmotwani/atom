"""Spike B: can Atom read a .docx with zero third-party dependencies?

Atom declares `dependencies = []`. Adding `python-docx` to read a problem
statement would be the first runtime dependency the project has ever taken, so
it deserves evidence rather than a shrug.

The question
------------
Can the standard library alone (`zipfile` + `xml.etree.ElementTree`) recover the
readable text of a real Word document -- including table cells and headers, and
correctly *excluding* text that the author deleted under tracked changes?

Why this is not merely "does it return a string"
------------------------------------------------
A naive extractor that concatenates every `<w:t>` node returns a string for any
document, so "it returned text" proves nothing. Two specific ways to be wrong:

  1. Tracked deletions live in `<w:delText>` inside `<w:del>`. Including them
     puts text the author *removed* into the problem statement -- worse than
     failing, because it is silently wrong.
  2. Paragraph and cell boundaries carry meaning. Concatenating without them
     runs the last word of one paragraph into the first word of the next.

Ground truth
------------
Word records its own `<Words>` count in `docProps/app.xml` when it saves. That
number is written by Word, not by this spike, so comparing against it is real
external validation rather than self-assessment. It is imperfect -- Word's count
may treat headers and footnotes differently -- so the bar below is a tolerance,
not an equality.

Privacy
-------
The corpus may be the operator's own documents. This spike prints statistics
only: counts, ratios and structural flags. It never prints document text, and
it never sends any content anywhere. No model is involved.
"""

from __future__ import annotations

import argparse
import statistics
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

# ---------------------------------------------------------------------------
# Pre-registered thresholds, fixed before looking at any result
# ---------------------------------------------------------------------------

# Share of documents that must yield non-empty text for the approach to be
# usable at all.
EXTRACTION_SUCCESS_RATE = 0.95

# Median relative difference against Word's own word count. Word counts headers
# and footnotes inconsistently, so an exact match is not the right bar.
WORD_COUNT_TOLERANCE = 0.15

# WordprocessingML namespace, and the OOXML property namespace used by app.xml.
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
APP_PROPERTIES = "{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}"


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def extract_paragraph(paragraph: ElementTree.Element) -> str:
    """Return the visible text of one paragraph, honouring tracked changes.

    Walks the paragraph in document order so that runs, tabs and line breaks
    keep their original sequence. Text under `<w:del>` is skipped because it
    represents content the author removed; text under `<w:ins>` is kept because
    it represents content the author added and is part of the current document.
    """

    pieces: list[str] = []

    for node in paragraph.iter():
        tag = node.tag

        # `<w:delText>` only ever appears inside a deletion, so skipping the
        # tag is sufficient -- there is no need to track ancestry.
        if tag == f"{W}delText":
            continue

        if tag == f"{W}t":
            pieces.append(node.text or "")
        elif tag == f"{W}tab":
            pieces.append("\t")
        elif tag in (f"{W}br", f"{W}cr"):
            pieces.append("\n")

    return "".join(pieces)


def extract_body(xml_bytes: bytes) -> str:
    """Return readable text from one document part.

    Paragraphs become lines. Table cells are separated with a tab and table
    rows with a newline, so a table keeps its shape well enough for a human or
    a model to read it as a table rather than as a run-on sentence.
    """

    root = ElementTree.fromstring(xml_bytes)
    lines: list[str] = []

    def visit(element: ElementTree.Element) -> None:
        for child in element:
            tag = child.tag
            if tag == f"{W}p":
                lines.append(extract_paragraph(child))
            elif tag == f"{W}tbl":
                for row in child.findall(f"{W}tr"):
                    cells = [
                        " ".join(
                            extract_paragraph(p) for p in cell.findall(f"{W}p")
                        ).strip()
                        for cell in row.findall(f"{W}tc")
                    ]
                    lines.append("\t".join(cells))
            else:
                # Section containers such as `<w:body>` and `<w:sdtContent>`
                # hold paragraphs one level further down.
                visit(child)

    visit(root)
    return "\n".join(lines)


def classify_container(path: Path) -> str:
    """Identify the real file format, ignoring the extension.

    A surprising share of files named `.docx` are actually legacy `.doc`
    binaries (an OLE2 compound file) that were renamed rather than converted.
    No `.docx` reader can open those -- the format is not a zip at all -- so
    counting them as extraction failures would blame the reader for a
    mislabelled input. They are reported separately instead.
    """

    with path.open("rb") as handle:
        head = handle.read(8)

    if head[:4] == b"PK\x03\x04":
        return "docx"
    if head == bytes.fromhex("D0CF11E0A1B11AE1"):
        return "legacy-doc"
    if head[:5] == b"{\\rtf":
        return "rtf"
    return "unknown"


def read_docx(path: Path) -> dict:
    """Extract text and structural facts from a .docx file.

    Returns a record rather than raising, so that one unreadable document does
    not end a survey of many.
    """

    record: dict = {
        "name": path.name,
        "bytes": path.stat().st_size,
        "container": "docx",
        "ok": False,
        "error": "",
        "text_characters": 0,
        "extracted_words": 0,
        "word_reported_words": None,
        "has_tables": False,
        "has_tracked_changes": False,
        "header_parts": 0,
    }

    record["container"] = classify_container(path)
    if record["container"] != "docx":
        record["error"] = f"not a .docx ({record['container']} wearing a .docx extension)"
        return record

    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())

            if "word/document.xml" not in names:
                record["error"] = "no word/document.xml"
                return record

            main_xml = archive.read("word/document.xml")
            text = extract_body(main_xml)

            # Headers and footers are separate parts; a problem statement may
            # carry its title there.
            header_names = sorted(
                n for n in names
                if n.startswith("word/header") and n.endswith(".xml")
            )
            record["header_parts"] = len(header_names)
            for name in header_names:
                header_text = extract_body(archive.read(name))
                if header_text.strip():
                    text = f"{header_text}\n{text}"

            record["has_tables"] = b"<w:tbl" in main_xml
            record["has_tracked_changes"] = b"<w:del " in main_xml or b"<w:ins " in main_xml

            if "docProps/app.xml" in names:
                app_root = ElementTree.fromstring(archive.read("docProps/app.xml"))
                words_node = app_root.find(f"{APP_PROPERTIES}Words")
                if words_node is not None and (words_node.text or "").strip().isdigit():
                    record["word_reported_words"] = int(words_node.text.strip())

            record["text_characters"] = len(text)
            record["extracted_words"] = len(text.split())
            record["ok"] = bool(text.strip())

    except zipfile.BadZipFile:
        record["error"] = "not a zip archive"
    except ElementTree.ParseError as error:
        record["error"] = f"xml parse error: {error}"
    except Exception as error:  # noqa: BLE001 - a survey must not stop on one file
        record["error"] = f"{type(error).__name__}: {error}"

    return record


# ---------------------------------------------------------------------------
# Deleted-text check
# ---------------------------------------------------------------------------


def deleted_text_is_excluded(path: Path) -> bool | None:
    """Confirm that tracked-deleted text is absent from the extracted output.

    Returns None when the document has no usable tracked deletions, so that
    documents which cannot exercise the rule are reported as untested rather
    than as passing. A check that silently passes on inapplicable input would
    inflate the result.
    """

    with zipfile.ZipFile(path) as archive:
        if "word/document.xml" not in archive.namelist():
            return None
        main_xml = archive.read("word/document.xml")

    root = ElementTree.fromstring(main_xml)
    deleted = [
        (node.text or "").strip()
        for node in root.iter(f"{W}delText")
        if (node.text or "").strip()
    ]
    if not deleted:
        return None

    # Use the longest deleted fragment: short fragments such as "a" would
    # coincidentally appear in surviving text and produce a false failure.
    longest = max(deleted, key=len)
    if len(longest) < 12:
        return None

    return longest not in extract_body(main_xml)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def report(records: list[dict], deletion_checks: list[bool | None]) -> int:
    """Print aggregate evidence and the verdict, without printing any content."""

    total = len(records)
    genuine = [r for r in records if r["container"] == "docx"]
    mislabelled = [r for r in records if r["container"] != "docx"]
    good = [r for r in genuine if r["ok"]]
    success_rate = len(good) / len(genuine) if genuine else 0.0

    print(f"files named .docx   : {total}")
    print(f"actually .docx      : {len(genuine)}")
    if mislabelled:
        kinds: dict[str, int] = {}
        for item in mislabelled:
            kinds[item["container"]] = kinds.get(item["container"], 0) + 1
        detail = ", ".join(f"{count} x {kind}" for kind, count in sorted(kinds.items()))
        print(f"mislabelled         : {len(mislabelled)}  ({detail})")
        print("                      no .docx reader can open these; the extension lies.")
    print(f"extracted non-empty : {len(good)}/{len(genuine)}  ({success_rate:.0%} of genuine)")

    failures = [r for r in genuine if not r["ok"]]
    if failures:
        print("\nfailures among genuine .docx:")
        for item in failures:
            print(f"  [{item['bytes']:>9,} bytes] {item['error'] or 'empty text'}")

    with_tables = sum(1 for r in good if r["has_tables"])
    with_changes = sum(1 for r in good if r["has_tracked_changes"])
    with_headers = sum(1 for r in good if r["header_parts"])
    print(f"\ncontaining tables   : {with_tables}")
    print(f"tracked changes     : {with_changes}")
    print(f"with header parts   : {with_headers}")

    # Accuracy against Word's own recorded count.
    comparable = [
        r for r in good
        if r["word_reported_words"] and r["word_reported_words"] > 50
    ]
    deviations = [
        abs(r["extracted_words"] - r["word_reported_words"]) / r["word_reported_words"]
        for r in comparable
    ]

    print(f"\ncomparable to Word's count : {len(comparable)}")
    if deviations:
        median_deviation = statistics.median(deviations)
        within = sum(1 for d in deviations if d <= WORD_COUNT_TOLERANCE)
        print(f"median deviation           : {median_deviation:.1%}")
        print(f"within {WORD_COUNT_TOLERANCE:.0%} tolerance          : {within}/{len(deviations)}")
    else:
        median_deviation = None
        print("median deviation           : not measurable")

    tested = [c for c in deletion_checks if c is not None]
    passed_deletion = sum(1 for c in tested if c)
    print(f"\ndeleted-text exclusion tested on : {len(tested)} documents")
    if tested:
        print(f"deleted text correctly excluded  : {passed_deletion}/{len(tested)}")
    else:
        print("deleted text correctly excluded  : untested (no tracked deletions found)")

    print()
    print(f"pre-registered: success >= {EXTRACTION_SUCCESS_RATE:.0%}, "
          f"median deviation <= {WORD_COUNT_TOLERANCE:.0%}")
    print()

    if success_rate < EXTRACTION_SUCCESS_RATE:
        print("Verdict: Refuted -- too many documents produced no text.")
        return 1
    if median_deviation is None:
        print("Verdict: Inconclusive -- no document carried a comparable word count.")
        return 2
    if median_deviation > WORD_COUNT_TOLERANCE:
        print("Verdict: Refuted -- extracted text diverges from Word's own count.")
        return 1
    if tested and passed_deletion < len(tested):
        print("Verdict: Refuted -- deleted text leaked into the extraction.")
        return 1

    print("Verdict: Confirmed -- the standard library alone reads these documents.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Survey .docx readability.")
    parser.add_argument("directory", type=Path, help="folder to scan for .docx files")
    parser.add_argument("--limit", type=int, default=0, help="scan at most N files")
    arguments = parser.parse_args()

    paths = sorted(
        p for p in arguments.directory.rglob("*.docx")
        if p.is_file() and not p.name.startswith("~$")
    )
    if arguments.limit:
        paths = paths[: arguments.limit]

    if not paths:
        print(f"No .docx files under {arguments.directory}", file=sys.stderr)
        return 2

    print("Question: can zipfile + ElementTree read a real .docx?\n")

    records = []
    deletion_checks: list[bool | None] = []
    for path in paths:
        records.append(read_docx(path))
        try:
            deletion_checks.append(deleted_text_is_excluded(path))
        except Exception:  # noqa: BLE001 - the survey continues
            deletion_checks.append(None)

    return report(records, deletion_checks)


if __name__ == "__main__":
    raise SystemExit(main())
