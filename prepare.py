from urllib.request import Request, urlopen
import pymupdf
import re

pdf_url = "https://resources.saylor.org/wwwresources/archived/site/textbooks/Personal%20Finance.pdf"

# Download the source PDF into memory so it can be opened directly without
# creating an intermediate file.
request = Request(
    pdf_url,
    headers={"User-Agent": "Mozilla/5.0"},
)

with urlopen(request, timeout=30) as response:
    pdf_data = response.read()


# Open the downloaded bytes as a PDF and inspect its page count.
doc = pymupdf.open(stream=pdf_data, filetype="pdf")

# Use the PDF bookmarks to find where Chapter 2 begins. The fixed starting
# page skips the book's front matter, so the slice below contains Chapter 1.
toc = doc.get_toc()
chapter_1_start = 6
chapter_2_start = next(
    page for level, title, page in toc
    if title == "Chapter 2"
)

# Extract each page in the Chapter 1 page range as text, then join the pages
# with newlines to preserve readable separation between them.
chapter_text = "\n".join(
    doc[i].get_text("text")
    for i in range(chapter_1_start - 1, chapter_2_start - 1)
)

# Remove page numbers that appear alone on a line
chapter_text = re.sub(r"(?m)^[ \t]*\d+[ \t]*$", "", chapter_text)

# Remove repeated publisher branding and URL text that is not useful in the
# cleaned chapter content.
to_remove = [
    "Saylor URL: http://www.saylor.org/books",
    "Saylor.org",
    "and sources of income.",
]
for word in to_remove:
    chapter_text = chapter_text.replace(word, "\n")

# Keep the chapter title before the cleanup below removes its objectives block.
chapter_heading_match = re.search(
    r"(?im)^[ \t]*(?P<chapter_number>Chapter 1)"
    r"(?:[ \t]+(?P<same_line_title>[^\r\n]+)"
    r"|[ \t]*\r?\n[ \t]*(?P<next_line_title>(?!LEARNING OBJECTIVES\b)[^\r\n]+))?",
    chapter_text,
)
chapter_heading_text = ""
if chapter_heading_match:
    chapter_name = (
        chapter_heading_match.group("same_line_title")
        or chapter_heading_match.group("next_line_title")
    )
    chapter_heading_text = " ".join(
        part.strip()
        for part in (chapter_heading_match.group("chapter_number"), chapter_name)
        if part
    )
    chapter_text = (
        chapter_text[:chapter_heading_match.start()]
        + chapter_heading_text
        + chapter_text[chapter_heading_match.end():]
    )


objective_end_markers = [
    "The circumstances or characteristics of your life",
    "Financial planning has to take into account conditions",
    "A financial planning process involves figuring out",
    "Even after reading this book, or perhaps especially",
]

# Each marker identifies the first prose line after the objectives list in a
# different PDF extraction layout. Remove the heading and list up to that line.
for marker in objective_end_markers:
    start = chapter_text.find("LEARNING OBJECTIVES")
    end = chapter_text.find(marker, start)

    if start != -1 and end != -1:
        chapter_text = chapter_text[:start] + chapter_text[end:]


exercises_end_markers = [
    "1.2 Systemic or “Macro” Factors",
    "1.3 The Planning Process",
    "1.4 Financial Planning Professionals",
    "e.htm)",
]

# Each marker identifies where the chapter resumes after the exercises in a
# different extraction layout. Remove that section while retaining later text.
for marker in exercises_end_markers:
    start = chapter_text.find("EXERCISES")
    end = chapter_text.find(marker, start)

    if start != -1 and end != -1:
        chapter_text = chapter_text[:start] + chapter_text[end:]


# Remove figure caption lines such as "Figure 1.2 ..." while leaving the
# surrounding chapter text intact.
pattern = r"(?m)^Figure\s+\d+(?:\.\d+)?[^\n]*"
chapter_text = re.sub(pattern, "", chapter_text)

# Join standalone PDF bullet markers to their text and use Markdown list syntax.
def format_bullet(match):
    marker_indent, text_indent = match.groups()
    return f"{marker_indent}- {text_indent or ''}"


# Convert the PDF's standalone bullet symbol into a Markdown list marker while
# carrying over any indentation on the following text line.
chapter_text = re.sub(
    r"(?m)^([ \t]*)•[ \t]*\r?\n([ \t]*)?(?=\S)",
    format_bullet,
    chapter_text,
)


def format_nested_bullet(match):
    marker_indent, text_indent = match.groups()
    indent = marker_indent or "  "
    return f"{indent}- {text_indent or ''}"


# Preserve nested list indentation when the PDF uses a standalone letter o as
# its sub-item marker.
chapter_text = re.sub(
    r"(?m)^([ \t]*)o[ \t]*\r?\n([ \t]*)?(?=\S)",
    format_nested_bullet,
    chapter_text,
)

# Join numbered list markers that PDF extraction placed on a separate line.
chapter_text = re.sub(
    r"(?m)^([ \t]*)(\d+[.)])[ \t]*\r?\n([ \t]*)(?=\S)",
    r"\1\2 \3",
    chapter_text,
)

# Convert any bullet markers that extraction already kept on the text line.
chapter_text = re.sub(r"(?m)^([ \t]*)•[ \t]*", r"\1- ", chapter_text)


# Mark chapter and section titles using the PDF bookmark hierarchy.
chapter_1_index = next(
    index for index, (level, title, page) in enumerate(toc)
    if title == "Chapter 1"
)
chapter_1_level = toc[chapter_1_index][0]
# Keep only bookmarks whose pages fall within Chapter 1; their order in the
# table of contents is also the order used to search for headings in the text.
chapter_headings = [
    (level, title)
    for level, title, page in toc
    if chapter_1_start <= page < chapter_2_start
]

search_from = 0
for level, title in chapter_headings:
    title_words = title.split()
    title_pattern = r"\s+".join(re.escape(word) for word in title_words)

    # Section titles in the extracted text may include a numeric prefix that
    # the corresponding bookmark omits. Chapter bookmarks may also precede
    # the full chapter title on the same line.
    number_prefix = r"(?:\d+(?:\.\d+)*[.:]?\s+)?"
    if re.fullmatch(r"Chapter\s+\d+", title, re.IGNORECASE):
        heading_pattern = (
            rf"^[ \t]*(?P<chapter_number>{title_pattern})"
            rf"(?:[ \t]+(?P<same_line_title>[^\r\n]+)"
            rf"|[ \t]*\r?\n[ \t]*(?P<next_line_title>(?!LEARNING OBJECTIVES\b)[^\r\n]+))?"
        )
    else:
        heading_pattern = (
            rf"^[ \t]*(?P<heading>{number_prefix}{title_pattern})[ \t]*$"
        )

    # Search after the last matched heading so repeated title text elsewhere
    # in the chapter is less likely to be mistaken for a bookmark heading.
    match = re.search(
        heading_pattern,
        chapter_text[search_from:],
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if match is None:
        continue

    start = search_from + match.start()
    end = search_from + match.end()
    is_chapter_heading = bool(re.fullmatch(r"Chapter\s+\d+", title, re.IGNORECASE))
    markdown_level = (
        1
        if is_chapter_heading
        else max(2, level - chapter_1_level + 1)
    )
    if is_chapter_heading:
        chapter_name = match.group("same_line_title") or match.group("next_line_title")
        heading_text = " ".join(
            part.strip()
            for part in (match.group("chapter_number"), chapter_name)
            if part
        )
    else:
        heading_text = re.sub(r"\s+", " ", match.group("heading")).strip()
    markdown_heading = f"{'#' * markdown_level} {heading_text}"
    chapter_text = chapter_text[:start] + markdown_heading + chapter_text[end:]
    search_from = start + len(markdown_heading)

# If cleanup or extraction left adjacent level 1 headings, combine their text.
while True:
    chapter_text, merged_count = re.subn(
        r"(?m)^(# [^\n]+)\n[ \t]*(# [^\n]+)$",
        lambda match: f"{match.group(1)} {match.group(2)[2:]}",
        chapter_text,
        count=1,
    )
    if not merged_count:
        break


def normalize_paragraphs(text):
    """Collapse PDF line wraps while keeping paragraphs, headings, and lists."""
    blocks = []
    paragraph_lines = []
    list_items = []

    def flush_paragraph():
        if paragraph_lines:
            blocks.append(" ".join(paragraph_lines))
            paragraph_lines.clear()

    def flush_list():
        if list_items:
            blocks.append("\n".join(list_items))
            list_items.clear()

    def is_list_item(line):
        # Recognize both Markdown bullets and numbered items when deciding
        # whether a blank line separates one list from the next paragraph.
        return re.match(r"^[ \t]*(?:-[ \t]+|\d+[.)][ \t]+)", line) is not None

    lines = text.splitlines()
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped:
            # Blank lines from page breaks do not end a paragraph unless the
            # preceding prose line ends in a period. A list stays open across
            # blank lines when another list item follows.
            if paragraph_lines and re.search(r"\.$", paragraph_lines[-1]):
                flush_paragraph()
            if list_items:
                next_line = next(
                    (line for line in lines[index + 1:] if line.strip()),
                    "",
                )
                if not is_list_item(next_line):
                    flush_list()
            continue

        line = re.sub(r"[ \t]+", " ", stripped)

        if line.startswith("#"):
            flush_paragraph()
            flush_list()
            blocks.append(line)
            continue

        list_item = re.match(
            r"^([ \t]*)(?P<marker>-|\d+[.)])[ \t]+(?P<text>.*)$",
            raw_line,
        )
        if list_item:
            # Keep nested bullet indentation and normalize spacing within each
            # item's text before adding it to the current list block.
            flush_paragraph()
            indent = "  " if list_item.group(1) else ""
            item_text = re.sub(r"[ \t]+", " ", list_item.group("text").strip())
            list_items.append(f"{indent}{list_item.group('marker')} {item_text}")
            continue

        if list_items:
            list_items[-1] += f" {line}"
        else:
            paragraph_lines.append(line)
            # In the extracted prose, a physical line ending with a period
            # marks the paragraph end. Wrapped lines continue until then.
            if re.search(r"\.$", line):
                flush_paragraph()

    flush_paragraph()
    flush_list()
    return "\n\n".join(block for block in blocks if block).strip()


chapter_text = normalize_paragraphs(chapter_text)

# Print the cleaned Chapter 1 text for inspection or use in the next stage.
print(chapter_text)

