import fitz  # PyMuPDF
import re
import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ==============================
# CONFIG
# ==============================
SECTION_PATTERN = re.compile(r'^(\d+(\.\d+)+)\s+(.+)')
REF_PATTERN = re.compile(r'(Section|Chapter|Appendix)\s+(\d+(\.\d+)*)', re.IGNORECASE)

# ==============================
# STEP 1: IMAGE HELPERS (you already have these)
# ==============================
def encode_image_bytes(image_bytes):
    import base64
    return base64.b64encode(image_bytes).decode("utf-8")

def describe_image_base64(base64_image):
    # Replace with your VLM / API call
    return "Image description placeholder"

# ==============================
# STEP 2: EXTRACT ELEMENTS (ORDER PRESERVED)
# ==============================
def extract_pdf_elements(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        elements = []

        # 🔹 TEXT BLOCKS WITH POSITION
        blocks = page.get_text("blocks")
        for b in blocks:
            x0, y0, x1, y1, text, *_ = b
            if text.strip():
                elements.append({
                    "type": "text",
                    "content": text.strip(),
                    "bbox": (x0, y0, x1, y1)
                })

        # 🔹 IMAGES
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            base64_image = encode_image_bytes(image_bytes)
            description = describe_image_base64(base64_image)

            elements.append({
                "type": "image",
                "content": f"[IMAGE]: {description}",
                "bbox": (0, 0, 0, 0)  # fallback
            })

        # 🔹 SORT BY Y POSITION (IMPORTANT)
        elements = sorted(elements, key=lambda x: x["bbox"][1])

        pages.append({
            "page": page_num + 1,
            "elements": elements
        })

    return pages

# ==============================
# STEP 3: SECTION DETECTION
# ==============================
def detect_section(text):
    match = SECTION_PATTERN.match(text.strip())
    if match:
        return {
            "level": match.group(1).count(".") + 1,
            "number": match.group(1),
            "title": match.group(3)
        }
    return None

# ==============================
# STEP 4: BUILD DOCUMENT TREE
# ==============================
def build_document_tree(pages):
    tree = []
    stack = []

    for page in pages:
        for el in page["elements"]:
            if el["type"] != "text":
                # attach images to current section
                if stack:
                    stack[-1]["content"].append(el["content"])
                continue

            text = el["content"]
            section = detect_section(text)

            if section:
                node = {
                    "title": section["title"],
                    "number": section["number"],
                    "level": section["level"],
                    "content": [],
                    "children": [],
                    "page": page["page"]
                }

                # maintain hierarchy
                while stack and stack[-1]["level"] >= node["level"]:
                    stack.pop()

                if stack:
                    stack[-1]["children"].append(node)
                else:
                    tree.append(node)

                stack.append(node)

            else:
                if stack:
                    stack[-1]["content"].append(text)

    return tree

# ==============================
# STEP 5: CROSS-REFERENCE EXTRACTION
# ==============================
def extract_references(text):
    matches = REF_PATTERN.findall(text)
    return [m[1] for m in matches]

# ==============================
# STEP 6: TREE → STRUCTURED CHUNKS
# ==============================
def tree_to_chunks(tree):
    chunks = []

    def traverse(node, parent_titles=[]):
        full_path = parent_titles + [node["title"]]
        content = "\n".join(node["content"])

        chunk = {
            "content": content,
            "section": node["number"],
            "title": node["title"],
            "path": " > ".join(full_path),
            "page": node["page"],
            "references": extract_references(content),
        }

        chunks.append(chunk)

        for child in node["children"]:
            traverse(child, full_path)

    for root in tree:
        traverse(root)

    return chunks

# ==============================
# STEP 7: TOKEN-SAFE SPLITTING
# ==============================

def split_chunks(chunks, chunk_size=500, overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )

    final_chunks = []

    for chunk in chunks:
        splits = splitter.split_text(chunk["content"])

        for i, split in enumerate(splits):
            final_chunks.append({
                "content": split,
                "section": chunk["section"],
                "title": chunk["title"],
                "path": chunk["path"],
                "page": chunk["page"],
                "references": chunk["references"],
                "chunk_id": f"{chunk['section']}_{i}"
            })

    return final_chunks

# ==============================
# STEP 8: MAIN PIPELINE
# ==============================
def process_pdf_to_chunks(pdf_path, output_path="chunks.jsonl"):
    print("🔹 Extracting elements...")
    pages = extract_pdf_elements(pdf_path)

    print("🔹 Building document tree...")
    tree = build_document_tree(pages)

    print("🔹 Converting to structured chunks...")
    chunks = tree_to_chunks(tree)

    print("🔹 Splitting into token-safe chunks...")
    final_chunks = split_chunks(chunks)

    print("🔹 Saving...")
    with open(output_path, "w", encoding="utf-8") as f:
        for chunk in final_chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"✅ Done! Saved {len(final_chunks)} chunks.")
    return final_chunks

if __name__ == '__main__':
    process_pdf_to_chunks("D:/signal/data/nasa_systems_engineering_handbook_0.pdf")