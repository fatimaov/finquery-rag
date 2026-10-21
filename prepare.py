from urllib.request import Request, urlopen
import pymupdf
import re

pdf_url = "https://resources.saylor.org/wwwresources/archived/site/textbooks/Personal%20Finance.pdf"

# Download the source PDF into memory so it can be opened directly without
# creating an intermediate file.
request = Request(
    pdf_url,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urlopen(request, timeout=30) as response:
    pdf_data = response.read()


# Open the downloaded bytes as a PDF and inspect its page count.
doc = pymupdf.open(stream=pdf_data, filetype="pdf")

print(f"Total pages: {len(doc)}")

# Use the PDF bookmarks to find where Chapter 2 begins. The fixed starting
# page skips the book's front matter, so the slice below contains Chapter 1.
toc = doc.get_toc()
chapter_1_start = 6
chapter_2_start = next(
    page for level, title, page in toc
    if title == "Chapter 2"
)

print(f"Chapter 1: pages {chapter_1_start}-{chapter_2_start - 1}")

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
to_remove = ["Saylor URL: http://www.saylor.org/books", "Saylor.org", "and sources of income."]
for word in to_remove:
    chapter_text = chapter_text.replace(word, "\n")


objective_end_markers = [
    "The circumstances or characteristics of your life",
    "Financial planning has to take into account conditions",
    "A financial planning process involves figuring out", 
    "Even after reading this book, or perhaps especially",
  
]

# Find the objectives heading and the first listed body-text marker after it.
# Drop the heading and objectives list while keeping the chapter text from
# that marker onward.
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

# Find the exercises heading and the first listed subsection marker after it.
# Drop the exercises heading and material before that subsection, preserving
# the rest of the chapter text.
for marker in exercises_end_markers:
    start = chapter_text.find("EXERCISES")
    end = chapter_text.find(marker, start)

    if start != -1 and end != -1:
        chapter_text = chapter_text[:start] + chapter_text[end:]


# Remove figure caption lines such as "Figure 1.2 ..." while leaving the
# surrounding chapter text intact.
pattern = r"(?m)^Figure\s+\d+(?:\.\d+)?[^\n]*"
chapter_text = re.sub(pattern, "", chapter_text)


# Replace runs of spaces or tabs with one space.
chapter_text = re.sub(r"[ \t]+", " ", chapter_text)
# Replace runs of newlines with one newline.
chapter_text = re.sub(r"\n+", "\n", chapter_text)

# Print the cleaned Chapter 1 text for inspection or use in the next stage.
print(chapter_text)

