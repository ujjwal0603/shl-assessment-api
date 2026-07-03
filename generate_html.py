import markdown

with open('Approach_Document.md', 'r', encoding='utf-8') as f:
    md_text = f.read()

html = markdown.markdown(md_text)

full_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 40px;
        line-height: 1.6;
        color: #333;
    }}
    h1, h2, h3 {{ color: #111; }}
    code {{ background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: monospace; }}
</style>
</head>
<body>
{html}
</body>
</html>
"""

with open('Approach_Document.html', 'w', encoding='utf-8') as f:
    f.write(full_html)
