import os
import docx
import fitz  # PyMuPDF
import PIL.Image
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv() 
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
app = Flask(__name__)
CORS(app)

@app.route('/summarize', methods=['POST'])
def summarize_document():
    if 'document' not in request.files:
        return jsonify({"error": "No document part"}), 400

    file = request.files['document']
    output_language = request.form.get('output_language', 'English')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # --- NEW PROMPT TO GENERATE INTERACTIVE MARKDOWN ---
    prompt_parts = [
        f"""
        You are "Lexi," an expert AI document analyst with a talent for clear visual presentation.
        Your task is to create a visually appealing, easy-to-read summary of the provided document using Markdown formatting.

        **Core Instructions:**
        1.  **Output Language:** Your entire response MUST be in {output_language}.
        2.  **Formatting:** Use Markdown extensively.
            -   Create a main title for the summary using a heading (e.g., `# Document Summary`).
            -   Use bold (`**text**`) for all key terms, names, dates, and amounts.
            -   Use bullet points (`*`) for lists of obligations or points.
            -   Use emojis to make sections visually distinct and intuitive.
        3.  **Structure:** Translate the following English section titles into {output_language} and use them as bold subheadings with an emoji.

        **Section Titles & Emojis to Use:**
        -   📄 **Document Type:**
        -   👥 **Key People/Entities Involved:**
        -   📌 **Main Points & Obligations:**
        -   📅 **Important Dates to Watch:**

        Now, analyze the provided document and generate the structured, interactive summary in {output_language}.
        ---
        """
    ]

    file_extension = file.filename.lower().split('.')[-1]

    # (The rest of the file handling code remains the same as before)
    if file_extension == 'docx':
        doc = docx.Document(file)
        text_content = "\n".join([para.text for para in doc.paragraphs])
        prompt_parts.append(text_content)
    elif file_extension == 'txt':
        text_content = file.read().decode('utf-8', errors='ignore')
        prompt_parts.append(text_content)
    elif file_extension in ['png', 'jpg', 'jpeg', 'webp']:
        image = PIL.Image.open(file.stream)
        prompt_parts.append(image)
    elif file_extension == 'pdf':
        pdf_file = fitz.open(stream=file.read(), filetype="pdf")
        for page_num in range(len(pdf_file)):
            page = pdf_file.load_page(page_num)
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            image = PIL.Image.open(io.BytesIO(img_data))
            prompt_parts.append(image)
        prompt_parts.append("\nINSTRUCTION: The above images are pages from a single PDF document. Analyze them as a whole.")
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    try:
        response = model.generate_content(prompt_parts)
        return jsonify({"summary": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)