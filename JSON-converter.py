import json
import re
from datetime import datetime
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx2pdf import convert  # Windows-only
from ebooklib import epub
import os

# === Configure Input File ===
# You can use a Day One .json export or a standard .md file.
# Just change the filename here.
input_filename = "Journal1.json" 

# === Setup output folder and prefix ===
# Creates a folder named after the input file (e.g., "Journal1")
folder_name = os.path.splitext(input_filename)[0]
os.makedirs(folder_name, exist_ok=True)

# Creates a base name for all output files, e.g., "output_Journal1.json_2025-07-16"
today_str = datetime.now().strftime("%Y-%m-%d")
base_filename = f"output_{os.path.basename(input_filename)}_{today_str}"
output_prefix = os.path.join(folder_name, base_filename)

# === Process notes based on file type ===
notes = []

# Logic for Day One JSON files
if input_filename.lower().endswith('.json'):
    print(f"Processing Day One JSON file: {input_filename}")
    with open(input_filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    entries = data.get("entries", [])
    if not entries:
        print("[!] Error: No 'entries' found in the JSON file.")
        exit()
        
    entries.sort(key=lambda x: x.get('creationDate', '')) # Sort by date
    
    for entry in entries:
        creation_date_str = entry.get("creationDate", "")
        date_obj = datetime.strptime(creation_date_str, "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        note_text = entry.get("text", "").strip()
        notes.append({
            'date': formatted_date,
            'text': note_text
        })

# Logic for standard Markdown files
elif input_filename.lower().endswith('.md'):
    print(f"Processing Markdown file: {input_filename}")
    with open(input_filename, "r", encoding="utf-8") as f:
        md_content = f.read()
    
    # Use the file's last modified date for the entry
    mod_time = os.path.getmtime(input_filename)
    mod_date_obj = datetime.fromtimestamp(mod_time)
    formatted_date = mod_date_obj.strftime("%Y-%m-%d")
    
    # Treat the entire file as a single note
    notes.append({
        'date': formatted_date,
        'text': md_content.strip()
    })
    
else:
    print(f"[!] Error: Unsupported file type for '{input_filename}'. Please use a .json or .md file.")
    exit()

# === Markdown Processing Functions (used for non-MD outputs) ===
def markdown_to_plain_text(text):
    """Convert markdown to plain text"""
    text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'```.*?\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
    return text

def markdown_to_latex(text):
    """Convert markdown to LaTeX with proper formatting"""
    text = re.sub(r'^# (.+)$', r'\\section{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'\\subsection{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'\\subsubsection{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^#{4,6} (.+)$', r'\\paragraph{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'__(.+?)__', r'\\textbf{\1}', text)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'\\textit{\1}', text)
    text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', r'\\textit{\1}', text)
    text = re.sub(r'`(.+?)`', r'\\texttt{\1}', text)
    text = re.sub(r'```.*?\n(.*?)\n```', r'\\begin{verbatim}\n\1\n\\end{verbatim}', text, flags=re.DOTALL)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'\\href{\2}{\1}', text)
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if line.strip().startswith('\\'):
            processed_lines.append(line)
        else:
            processed_line = ""
            i = 0
            while i < len(line):
                if line[i:i+1] == '\\' and i < len(line) - 1:
                    j = i + 1
                    while j < len(line) and (line[j].isalpha() or line[j] in '{}'):
                        j += 1
                        if j < len(line) and line[j-1] == '}': break
                    processed_line += line[i:j]
                    i = j
                else:
                    char = line[i]
                    if char in '&_#%$': processed_line += '\\' + char
                    elif char == '^': processed_line += '\\textasciicircum{}'
                    elif char == '~': processed_line += '\\textasciitilde{}'
                    else: processed_line += char
                    i += 1
            processed_lines.append(processed_line)
    return '\n'.join(processed_lines)

def markdown_to_html(text):
    """Convert markdown to HTML"""
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
    text = re.sub(r'^###### (.+)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'```.*?\n(.*?)\n```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\n\n', '</p><p>', text)
    text = re.sub(r'\n', '<br>', text)
    return f'<p>{text}</p>'

def add_markdown_to_docx(doc, text):
    """Add markdown text to Word document with proper formatting"""
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('# '): doc.add_heading(line[2:], level=1)
        elif line.startswith('## '): doc.add_heading(line[3:], level=2)
        elif line.startswith('### '): doc.add_heading(line[4:], level=3)
        elif line.startswith('#### '): doc.add_heading(line[5:], level=4)
        elif line.startswith('##### '): doc.add_heading(line[6:], level=5)
        elif line.startswith('###### '): doc.add_heading(line[7:], level=6)
        else:
            para = doc.add_paragraph()
            parts = re.split(r'(\*\*.*?\*\*|__.*?__|(?<!\*)\*(?!\*)[^*]*?\*(?!\*)|(?<!_)_(?!_)[^_]*?_(?!_)|`[^`]*?`)', line)
            for part in parts:
                if part.startswith('**') and part.endswith('**'): para.add_run(part[2:-2]).bold = True
                elif part.startswith('__') and part.endswith('__'): para.add_run(part[2:-2]).bold = True
                elif part.startswith('*') and part.endswith('*') and not part.startswith('**'): para.add_run(part[1:-1]).italic = True
                elif part.startswith('_') and part.endswith('_') and not part.startswith('__'): para.add_run(part[1:-1]).italic = True
                elif part.startswith('`') and part.endswith('`'):
                    run = para.add_run(part[1:-1])
                    run.font.name = 'Courier New'
                else: para.add_run(part)
        i += 1

def extract_h1_titles(text):
    """Extract all H1 titles from markdown text"""
    return re.findall(r'^# (.+)$', text, flags=re.MULTILINE)

def split_content_by_h1(text):
    """Split content into sections based on H1 headings"""
    sections, lines, current_section, current_h1 = [], text.split('\n'), [], None
    for line in lines:
        if line.startswith('# '):
            if current_h1 is not None: sections.append({'title': current_h1, 'content': '\n'.join(current_section)})
            current_h1 = line[2:].strip()
            current_section = [line]
        else: current_section.append(line)
    if current_h1 is not None: sections.append({'title': current_h1, 'content': '\n'.join(current_section)})
    return sections

# === Save as Markdown (.md) ===
md_parts = []
for note in notes:
    md_parts.append(f"## Date: {note['date']}\n\n{note['text']}")
full_markdown = "\n\n---\n\n".join(md_parts)
md_filename = f"{output_prefix}.md"
with open(md_filename, "w", encoding="utf-8") as f:
    f.write(full_markdown)

# === Save as TXT (plain text) ===
plain_text_notes = [f"Date: {note['date']}\n{markdown_to_plain_text(note['text'])}" for note in notes]
with open(f"{output_prefix}.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(plain_text_notes))

# === Save as LaTeX (.tex) ===
with open(f"{output_prefix}.tex", "w", encoding="utf-8") as f:
    f.write(r"\documentclass[a4paper,12pt]{article}\n\usepackage[utf8]{inputenc}\n\usepackage{hyperref}\n"
            r"\usepackage{url}\n\usepackage{lipsum}\n\usepackage{titlesec}\n\usepackage{tocloft}\n"
            r"\usepackage{fancyhdr}\n\pagestyle{fancy}\n\fancyhf{}\n\rhead{\thepage}\n\begin{document}\n\n")
    f.write(r"\begin{titlepage}\n\centering\n\vspace*{5cm}\n{\Huge\bfseries The Journal \par}\n"
            r"\vspace{1cm}\n{\Large by MJB \par}\n\vfill\n\end{titlepage}\n\n")
    f.write(r"\tableofcontents\n\newpage\n\n")
    for note in notes:
        f.write(f"\\textbf{{Date: {note['date']}}} {markdown_to_latex(note['text'])}\n\n\\vspace{{1em}}\n\n")
    f.write("\\end{document}")

# === Save as DOCX (.docx) ===
doc = Document()
doc.add_heading("Collected Notes", level=1)
for note in notes:
    doc.add_paragraph(f"Date: {note['date']}")
    add_markdown_to_docx(doc, note['text'])
    doc.add_paragraph()
docx_filename = f"{output_prefix}.docx"
doc.save(docx_filename)

# === Convert DOCX to PDF (.pdf) ===
try:
    convert(docx_filename, f"{output_prefix}.pdf")
    print(f"✅ PDF saved as: {output_prefix}.pdf")
except Exception as e:
    print(f"[!] PDF conversion failed: {e}")

# === Save as EPUB (.epub) ===
book = epub.EpubBook()
book.set_identifier('id123456'); book.set_title('Collected Notes'); book.set_language('en')
if os.path.exists("cover.jpg"):
    with open("cover.jpg", 'rb') as cover_file: book.set_cover("cover.jpg", cover_file.read())
    print("✅ Cover image added to EPUB")
else: print("⚠️ Cover image (cover.jpg) not found - EPUB will be created without cover")
chapters, toc_entries, chapter_counter = [], [], 1
h1_sections = [{'date': note['date'], 'title': s['title'], 'content': s['content']} for note in notes for s in split_content_by_h1(note['text'])]
if h1_sections:
    for section in h1_sections:
        chapter_filename = f'chap_{chapter_counter:02d}.xhtml'
        chapter = epub.EpubHtml(title=section['title'], file_name=chapter_filename, lang='en')
        chapter.content = f"<p><strong>Date: {section['date']}</strong></p>\n{markdown_to_html(section['content'])}"
        book.add_item(chapter); chapters.append(chapter)
        toc_entries.append(epub.Link(chapter_filename, section['title'], f'chap{chapter_counter}'))
        chapter_counter += 1
else:
    for i, note in enumerate(notes):
        chapter_filename, chapter_title = f'chap_{i+1:02d}.xhtml', f"Entry {note['date']}"
        chapter = epub.EpubHtml(title=chapter_title, file_name=chapter_filename, lang='en')
        chapter.content = f"<h1>{chapter_title}</h1>\n{markdown_to_html(note['text'])}"
        book.add_item(chapter); chapters.append(chapter)
        toc_entries.append(epub.Link(chapter_filename, chapter_title, f'chap{i+1}'))
book.toc = tuple(toc_entries)
book.add_item(epub.EpubNcx()); book.add_item(epub.EpubNav()); book.spine = ['nav'] + chapters
epub_filename = f"{output_prefix}.epub"
epub.write_epub(epub_filename, book)

# === Final Summary ===
print("\n✅ All files generated in folder:", folder_name)
print(f"- {os.path.basename(md_filename)} (Consolidated Markdown)")
print(f"- {os.path.basename(output_prefix)}.txt (Plain Text)")
print(f"- {os.path.basename(output_prefix)}.tex (LaTeX)")
print(f"- {os.path.basename(output_prefix)}.docx (Word)")
print(f"- {os.path.basename(output_prefix)}.pdf (PDF)")
print(f"- {os.path.basename(epub_filename)} (EPUB)")

if h1_sections:
    print(f"\n📖 EPUB contains {len(h1_sections)} chapters based on H1 headings:")
    for section in h1_sections: print(f"  - {section['title']} (from {section['date']})")
else:
    print(f"\n📖 EPUB contains {len(notes)} chapters based on dates (no H1 headings found):")
    for note in notes: print(f"  - Entry {note['date']}")