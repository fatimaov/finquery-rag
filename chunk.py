from prepare import prepare_chapter
from langchain_text_splitters import MarkdownHeaderTextSplitter

# Prepare the cleaned chapter text before splitting it into smaller sections.
chapter_text = prepare_chapter()

# Use the Markdown heading hierarchy to keep chapter, section, and subsection
# titles available as metadata on each resulting document.
headers_to_split_on = [
    ("#", "chapter"),
    ("##", "section"),
    ("###", "subsection"),
]

# Keep the headings in the section content so each chunk remains readable on
# its own, in addition to recording heading values in the metadata.
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False,
)

# Split at the configured heading levels; the splitter attaches the matching
# heading path to each section's metadata.
sections = markdown_splitter.split_text(chapter_text)

# Print a quick summary and preview of every section to inspect the split and
# confirm that its heading metadata and text content look as expected.
print(f"Total sections: {len(sections)}")

for i, section in enumerate(sections):
    print(f"\n--- Section {i + 1} ---")
    print("Metadata:", section.metadata)
    print("Length:", len(section.page_content))
    print("Preview:", section.page_content[:200])
