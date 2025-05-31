# Code Citations

## License: MIT
https://github.com/Etzer12/facebook_profanity/blob/87eac0129a61956b9a46f0c98a86a616b18115ee/WebpageParser.py

```python
# HTML text cleaning implementation adapted from WebpageParser.py
# Clean up whitespace from HTML text extraction
lines = (line.strip() for line in text.splitlines())
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
text = '\n'.join(chunk for chunk in chunks if chunk)
```

Used in: `app/knowledge/services/source_service.py` - `_extract_html_content` method for cleaning extracted HTML text content.

