from urllib.request import Request, urlopen
import pymupdf

pdf_url = "https://resources.saylor.org/wwwresources/archived/site/textbooks/Personal%20Finance.pdf"

request = Request(
    pdf_url,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urlopen(request, timeout=30) as response:
    pdf_data = response.read()


# Load PDF with PyMuPDF
doc = pymupdf.open(stream=pdf_data, filetype="pdf")

print(f"Total pages: {len(doc)}")

# Read bookmarks to identify chapter boundaries.
toc = doc.get_toc()
chapter_1_start = 6
chapter_2_start = next(
    page for level, title, page in toc
    if title == "Chapter 2"
)

print(f"Chapter 1: pages {chapter_1_start}–{chapter_2_start - 1}")

# Extract Chapter 1 into chapter_text
chapter_text = "\n".join(
    doc[i].get_text("text")
    for i in range(chapter_1_start - 1, chapter_2_start - 1)
)

# Clean the text by removing unwanted URLs, headers, and sections
chapter_text = chapter_text.replace(
    "Saylor URL: http://www.saylor.org/books",
    ""
)
chapter_text = chapter_text.replace(
    "Saylor.org",
    ""
)

objective_end_markers = [
    "The circumstances or characteristics of your life",
    "Financial planning has to take into account conditions",
    "A financial planning process involves figuring out", 
    "Even after reading this book, or perhaps especially",
    # Add the starting paragraph of each remaining section
]

for marker in objective_end_markers:
    start = chapter_text.find("LEARNING OBJECTIVES")
    end = chapter_text.find(marker, start)

    if start != -1 and end != -1:
        chapter_text = chapter_text[:start] + chapter_text[end:]

print(chapter_text)