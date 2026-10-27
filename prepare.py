from urllib.request import Request, urlopen
import pymupdf
import re


def normalize_paragraphs(text):
    """Join wrapped PDF lines while preserving headings and list items."""
    # Accumulate paragraphs and lists separately so PDF line wraps can be
    # joined without flattening Markdown headings or list structure.
    blocks = []
    paragraph_lines = []
    list_items = []

    def flush_paragraph():
        # A paragraph is stored as one line, then separated from other blocks.
        if paragraph_lines:
            blocks.append(" ".join(paragraph_lines))
            paragraph_lines.clear()

    def flush_list():
        # Keep list items on separate lines for Markdown rendering.
        if list_items:
            blocks.append("\n".join(list_items))
            list_items.clear()

    def is_list_item(line):
        # Recognize the list markers produced by the cleanup below.
        return re.match(r"^[ \t]*(?:-[ \t]+|\d+[.)][ \t]+)", line) is not None

    lines = text.splitlines()
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if not stripped:
            # Blank PDF lines end completed prose and lists when the next
            # nonblank line is not another list item.
            if paragraph_lines and re.search(r"[.!?]$", paragraph_lines[-1]):
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
            # Preserve existing Markdown headings as standalone blocks.
            flush_paragraph()
            flush_list()
            blocks.append(line)
            continue

        list_item = re.match(
            r"^([ \t]*)(?P<marker>-|\d+[.)])[ \t]+(?P<text>.*)$",
            raw_line,
        )
        if list_item:
            # Start a new list item, keeping nested items indented.
            flush_paragraph()
            indent = "  " if list_item.group(1) else ""
            item_text = re.sub(r"[ \t]+", " ", list_item.group("text").strip())
            list_items.append(f"{indent}{list_item.group('marker')} {item_text}")
            continue

        if list_items:
            # Wrapped lines belonging to a list item continue its text.
            list_items[-1] += f" {line}"
        else:
            # Join ordinary wrapped lines until punctuation ends a sentence.
            paragraph_lines.append(line)
            if re.search(r"[.!?]$", line):
                flush_paragraph()

    flush_paragraph()
    flush_list()
    return "\n\n".join(block for block in blocks if block).strip()


def format_chapter(
    chapter_text,
    chapter_number,
    toc,
    chapter_start,
    chapter_end,
    end_markers=(),
):
    """Clean extracted text and format chapter and section headings."""
    # Remove page-number-only lines inserted by PDF extraction.
    chapter_text = re.sub(r"(?m)^[ \t]*\d+[ \t]*$", "", chapter_text)

    # Strip repeated publisher branding from page headers and footers.
    for branding in (
        "Saylor URL: http://www.saylor.org/books",
        "Saylor.org",
    ):
        chapter_text = chapter_text.replace(branding, "")

    # Drop figure caption lines so they do not interrupt the chapter prose.
    chapter_text = re.sub(r"(?m)^Figure\s+\d+(?:\.\d+)?[^\n]*", "", chapter_text)

    # PDF extraction can put a list marker on its own line; attach it to the
    # following item text and convert bullets into Markdown list markers.
    chapter_text = re.sub(
        r"(?m)^([ \t]*)\u2022[ \t]*\r?\n([ \t]*)?(?=\S)",
        lambda match: f"{match.group(1)}- {match.group(2) or ''}",
        chapter_text,
    )
    chapter_text = re.sub(
        r"(?m)^([ \t]*)o[ \t]*\r?\n([ \t]*)?(?=\S)",
        lambda match: f"{match.group(1) or '  '}- {match.group(2) or ''}",
        chapter_text,
    )
    chapter_text = re.sub(
        r"(?m)^([ \t]*)(\d+[.)])[ \t]*\r?\n([ \t]*)(?=\S)",
        r"\1\2 \3",
        chapter_text,
    )
    chapter_text = re.sub(r"(?m)^([ \t]*)\u2022[ \t]*", r"\1- ", chapter_text)


    # Combine the chapter number and its title, whether the title is on the
    # same line or the following line. Do not mistake the objectives heading
    # for the chapter title.
    chapter_heading = re.compile(
        rf"^[ \t]*(?P<number>Chapter\s+{chapter_number})"
        r"(?:[ \t]+(?P<same_line>\S[^\r\n]*)"
        r"|[ \t]*\r?\n[ \t]*(?P<next_line>(?!LEARNING OBJECTIVES\b)[^\r\n]+))?",
        re.IGNORECASE | re.MULTILINE,
    )
    match = chapter_heading.search(chapter_text)

    if match:
        chapter_name = match.group("same_line") or match.group("next_line")
        heading = " ".join(
            part.strip() for part in (match.group("number"), chapter_name) if part
        )
        # Replace the original heading lines with a single Markdown H1.
        chapter_text = (
            chapter_text[:match.start()]
            + f"# {heading}"
            + chapter_text[match.end():]
        )

    # Find the chapter's TOC entry to determine the relative heading levels.
    chapter_index = next(
        (
            index for index, (level, title, page) in enumerate(toc)
            if re.match(rf"Chapter\s+{chapter_number}\b", title, re.IGNORECASE)
        ),
        None,
    )
    
    if chapter_index is not None:
        chapter_level = toc[chapter_index][0]
        chapter_headings = [
            (level, title)
            for level, title, page in toc
            if chapter_start <= page < chapter_end
        ]
        
        # Match TOC section titles in order within this chapter's page range.
        search_from = 0
        for level, title in chapter_headings:
            title_words = title.split()
            title_pattern = r"\s+".join(re.escape(word) for word in title_words)
            is_chapter_heading = bool(
                re.match(rf"Chapter\s+{chapter_number}\b", title, re.IGNORECASE)
            )
            if is_chapter_heading:
                continue

            number_prefix = r"(?:\d+(?:\.\d+)*[.:]?\s+)?"
            heading_pattern = (
                rf"^[ \t]*(?P<heading>{number_prefix}{title_pattern})[ \t]*$"
            )
            heading_match = re.search(
                heading_pattern,
                chapter_text[search_from:],
                flags=re.IGNORECASE | re.MULTILINE,
            )
            if heading_match is None:
                continue

            start = search_from + heading_match.start()
            end = search_from + heading_match.end()
            markdown_level = max(2, level - chapter_level + 1)
            heading = re.sub(r"\s+", " ", heading_match.group("heading")).strip()
            markdown_heading = f"{'#' * markdown_level} {heading}"
            # Replace each matched section title with its Markdown heading.
            chapter_text = chapter_text[:start] + markdown_heading + chapter_text[end:]
            search_from = start + len(markdown_heading)

    # Join wrapped PDF text and apply paragraph/list spacing for Markdown.
    chapter_text = normalize_paragraphs(chapter_text)

    # Each configured marker corresponds to one learning objectives section
    # in this chapter. Remove them in order and keep each marker sentence.
    search_from = 0
    for marker in end_markers:
        objective_heading = re.search(
            r"(?m)^### LEARNING OBJECTIVES[ \t]*$",
            chapter_text[search_from:],
        )
        if objective_heading is None:
            break

        start = search_from + objective_heading.start()
        marker_start = chapter_text.find(
            marker,
            search_from + objective_heading.end(),
        )
        if marker_start == -1:
            # This marker has no matching section in this chapter; try the next
            # configured section marker without changing the chapter text.
            search_from = search_from + objective_heading.end()
            continue

        chapter_text = chapter_text[:start] + chapter_text[marker_start:]
        search_from = start + len(marker)

    # Exercise sections end at the next Markdown heading. Remove each section
    # through that boundary while preserving the following heading.
    search_from = 0
    while True:
        exercise_heading = re.search(
            r"(?m)^###[ \t]+EXERCISES?[ \t]*$",
            chapter_text[search_from:],
        )
        if exercise_heading is None:
            break

        start = search_from + exercise_heading.start()
        next_heading = chapter_text.find(
            "\n#",
            search_from + exercise_heading.end(),
        )
        if next_heading == -1:
            chapter_text = chapter_text[:start].rstrip()
            break

        chapter_text = chapter_text[:start] + chapter_text[next_heading:]
        search_from = start

    return chapter_text


def prepare_selected_chapters():
    """Load, clean, format, and join the selected chapters from the PDF."""
    # Download the source PDF with a browser-like user agent.
    pdf_url = "https://resources.saylor.org/wwwresources/archived/site/textbooks/Personal%20Finance.pdf"
    request = Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})

    with urlopen(request, timeout=30) as response:
        pdf_data = response.read()

    # Open the PDF from memory and read its table of contents for page ranges.
    doc = pymupdf.open(stream=pdf_data, filetype="pdf")
    toc = doc.get_toc()
    # Map each chapter number to its 1-based starting page from the TOC.
    chapter_pages = {
        int(chapter_match.group(1)): page
        for level, title, page in toc
        if (chapter_match := re.match(r"Chapter\s+(\d+)\b", title))
    }

    selected_chapters = [1, 2, 3, 5, 7, 8]
    # Add the end sentence(s) for each chapter whose learning objectives
    # should be removed. Leave a chapter's tuple empty to keep its section.
    learning_objective_end_markers = {
        1: (
            "The circumstances or characteristics of your life",
            "Financial planning has to take into account conditions",
            "A financial planning process involves figuring out",
            "Even after reading this book",
        ),
        2: (
            "Personal finance is the process of paying",
            "As defined earlier in this chapter",
            "Buying capital",
            "Personal finance is not just",
        ),
        3: (
            "Clay tablets interested Sumerian",
            "Financial statements are valuable",
            "Many software products are available",
        ),
        5: (
            "The budget process is an infinite loop",
            "Gathering data and creating",
            "\n## The Cash Budget",
            "A budget variance occurs",
            "Whatever type of budget you create",
        ),
        7: (
            "Most people use a checking account",
            "When incomes are larger than expenses",
            "“Credit” derives from the Latin",
            "Debt is long-term credit",
        ),
        8: (
            "Consumer purchases refer",
            "Many adults will buy a car",
        ),
    }
    extracted_chapters = []
    for chapter_number in selected_chapters:
        # Use the next chapter's start page as the exclusive end of this one.
        chapter_start = chapter_pages[chapter_number]
        next_chapter = next(
            (number for number in sorted(chapter_pages) if number > chapter_number),
            None,
        )
        chapter_end = (
            chapter_pages[next_chapter]
            if next_chapter is not None
            else len(doc) + 1
        )
        # Extract page text in reading order across the chapter's page range.
        raw_chapter_text = "\n".join(
            doc[index].get_text("text")
            for index in range(chapter_start - 1, chapter_end - 1)
        )
        # Clean and format each extracted chapter before combining them.
        extracted_chapters.append(
            format_chapter(
                raw_chapter_text,
                chapter_number,
                toc,
                chapter_start,
                chapter_end,
                learning_objective_end_markers.get(chapter_number, ()),
            )
        )


    # Separate formatted chapters with a blank line for readable Markdown.
    return "\n\n".join(extracted_chapters)


if __name__ == "__main__":
    print(prepare_selected_chapters())
