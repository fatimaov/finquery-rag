from prepare import prepare_chapter
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# Prepare the cleaned chapter text before splitting it into smaller sections.
chapter_text = prepare_chapter()

# Use the Markdown heading hierarchy to keep chapter, section, and subsection
# titles available as metadata on each resulting document.
headers_to_split_on = [
    ("#", "chapter"),
    ("##", "section"),
    ("###", "subsection"),
]

# Remove headings from section text after recording their values in metadata, so
# each section can be split into content-focused chunks with heading context.
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=True,
)

# Split at the configured heading levels; the splitter attaches the matching
# heading path to each section's metadata.
sections = markdown_splitter.split_text(chapter_text)

# Print a quick summary and preview of every section to inspect the split and
# confirm that its heading metadata and text content look as expected.
print(f"Total sections: {len(sections)}")

# Inspect each section's heading metadata, text length, and opening text to
# check how the Markdown heading split grouped the chapter.
for i, section in enumerate(sections):
    print(f"\n--- Section {i + 1} ---")
    print("Metadata:", section.metadata)
    print("Length:", len(section.page_content))
    print("Preview:", section.page_content[:200])


# Break long sections into smaller pieces that fit the target chunk size. The
# overlap keeps some surrounding context when related text spans a boundary.
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
)

chunks = recursive_splitter.split_documents(sections)

# Review the final chunks and their inherited heading metadata after splitting.
print(f"Total chunks: {len(chunks)}")

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print("Metadata:", chunk.metadata)
    print("Length:", len(chunk.page_content))
    print("Preview:", chunk.page_content[:200])

lengths = [len(chunk.page_content) for chunk in chunks]

# Summarize the chunk size range and average to check the resulting distribution.
print("Smallest chunk:", min(lengths))
print("Largest chunk:", max(lengths))
print("Average chunk:", round(sum(lengths) / len(lengths)))

