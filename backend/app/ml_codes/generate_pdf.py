import markdown
import pdfkit

# Step 1: Read your markdown file
def generate_pdf(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Step 2: Convert markdown to HTML
    html = markdown.markdown(md_content, extensions=["extra", "codehilite", "tables"])

    # Optional: wrap in basic HTML template for styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
            }}
            pre code {{
                background-color: #f4f4f4;
                padding: 10px;
                display: block;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
    {html}
    </body>
    </html>
    """

    # Step 3: Convert HTML to PDF
    pdfkit.from_string(full_html,output_file)