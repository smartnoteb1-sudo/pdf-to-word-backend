from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pdf2docx import Converter
import os
import uuid

app = Flask(__name__)
CORS(app)  # 🚨 Important: allows requests from your InfinityFree frontend

@app.route('/convert', methods=['POST'])
def convert_pdf_to_word():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pdf'):
        # Save uploaded PDF temporarily
        pdf_path = f"/tmp/{uuid.uuid4()}.pdf"
        file.save(pdf_path)
        
        # Output Word path
        word_path = pdf_path.replace('.pdf', '.docx')
        
        # Convert PDF to DOCX
        cv = Converter(pdf_path)
        cv.convert(word_path, start=0, end=None)
        cv.close()
        
        # Send back the Word file
        response = send_file(word_path, as_attachment=True, download_name="converted.docx")
        
        # Clean up temp files after sending
        @response.call_on_close
        def cleanup():
            os.remove(pdf_path)
            os.remove(word_path)
        
        return response
    else:
        return jsonify({"error": "Invalid file type, only PDFs allowed"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
