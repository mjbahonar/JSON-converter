
# 📔 Universal Document & Journal Converter

A powerful Python script to convert your **Day One journal exports** or **standard Markdown files** into a multitude of beautiful, organized formats, ready for archiving or sharing.

![output_files](https://user-images.githubusercontent.com/12345/67890-example.png) <!-- TODO: Replace this with a screenshot of the beautiful HTML output! -->

## ✨ Features

*   **Beautiful HTML Output 🎨**: Generates a single, self-contained `.html` file with modern, built-in CSS for a clean and beautiful reading experience in any browser.
*   **Dual Input Support ✌️**: Works with both:
    *   **Day One `.json` exports**: The script's primary function.
    *   **Standard `.md` files**: For any of your other Markdown notes.
*   **Multiple Output Formats 📚**: Converts your content into a comprehensive set of formats:
    *   ✨ Styled HTML (`.html`)
    *   📝 Consolidated Markdown (`.md`)
    *   📄 Plain Text (`.txt`)
    *   ✒️ LaTeX (`.tex`)
    *   ✍️ Microsoft Word (`.docx`)
    *   📑 PDF (requires Word on Windows)
    *   📖 EPUB (`.epub`)
*   **Chronological Sorting 📅**: Automatically sorts your Day One journal entries by their creation date.
*   **Markdown Preservation 💅**: Keeps your Markdown formatting (headers, bold, italics) intact across all relevant formats.
*   **Smart EPUB Creation 🧠**:
    *   Generates a dynamic Table of Contents based on `# H1 titles` in your content.
    *   Allows you to add a custom book cover!
*   **Organized Output 📂**: Creates a dedicated folder for each input file, keeping all your converted documents tidy.

## 🚀 How to Use

### 1. Prerequisites

You need to have Python 3 installed. Then, install the required libraries using pip:

```bash
pip install python-docx docx2pdf EbookLib
```

> **Note on PDF Conversion**: The `docx2pdf` library requires **Microsoft Word** to be installed on a **Windows** machine. If you are on macOS or Linux, the script will simply skip the PDF conversion step without crashing.

### 2. Setup

1.  **Prepare Your File**: Get your Day One `.json` export or any `.md` file you want to convert.
2.  **Place Your Files**: Put the `.json` or `.md` file in the same directory as the Python script.
3.  **(Optional) Add a Cover**: For a custom EPUB cover, place an image named `cover.jpg` in the same directory.

Your folder structure might look like this:
```
.
├── Journal1.json        <-- Your Day One export
├── MyNotes.md           <-- OR your Markdown file
├── cover.jpg            <-- Your optional EPUB cover
└── journal_converter.py <-- This Python script
```

### 3. Configure the Script

Open the Python script and change the `input_filename` variable on line 111 to match your file.

```python
# === Configure Input File ===
input_filename = "Journal1.json" 
```

### 4. Run the Script!

Execute the script from your terminal:
```bash
python journal_converter.py
```

## 📂 What to Expect

The script will create a new folder named after your input file (e.g., `Journal1`). Inside, you will find all your converted documents.

### How it Works with Different File Types

*   **For Day One (`.json`) files**: The script reads all entries, sorts them by date, and processes them individually.
*   **For Markdown (`.md`) files**: The script treats the entire file as a **single entry**. The date for this entry is automatically set to the file's **"last modified"** date. The chapter generation based on `# H1 titles` works perfectly.

---

Enjoy your newly archived documents! 🎉
