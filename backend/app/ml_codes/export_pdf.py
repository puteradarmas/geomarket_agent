import markdown
from weasyprint import HTML

# 1. Your Markdown content
md_text = """
# Analysis Report

## Key Stats
- Population: **12,345**
- Growth Rate: *2.3%*

## Recommendation
We recommend focusing on the **northern zone** due to higher population density.
"""

# 2. Convert Markdown → HTML
html_content = markdown.markdown(md_text, extensions=['extra'])

# 3. Wrap HTML in full document format
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 2em;
            line-height: 1.6;
        }}
        h1, h2 {{
            color: #333;
        }}
        strong {{
            color: #111;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

# 4. Export HTML → PDF
HTML(string=html_template).write_pdf("report.pdf")

print("PDF generated: report.pdf")