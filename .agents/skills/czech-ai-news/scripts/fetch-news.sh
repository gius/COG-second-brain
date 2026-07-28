#!/bin/bash
# Fetch and parse Czech news from ai.hn.cz/strucne
# Outputs ready-to-display markdown

URL="https://ai.hn.cz/strucne"

echo "# Hospodářské Noviny - Stručně"
echo ""
echo "**$(date +%Y-%m-%d)** | ai.hn.cz/strucne"
echo ""

curl -s "$URL" | awk '
BEGIN { in_article = 0; title = ""; content = "" }

/<div class="article-sum/ {
    in_article = 1
    title = ""
    content = ""
    next
}

in_article && /<p>/ {
    line = $0
    gsub(/^[ \t]+/, "", line)

    if (line ~ /href=/) {
        # Extract article title from link text
        gsub(/.*<a[^>]*>/, "", line)
        gsub(/<\/a>.*/, "", line)
        gsub(/&nbsp;/, " ", line)
        gsub(/&#34;/, "\"", line)
        gsub(/^[ \t]+|[ \t]+$/, "", line)
        title = line
    } else {
        # Content paragraph - convert <br> to newlines
        gsub(/<br>/, "\n", line)
        gsub(/<[^>]*>/, "", line)
        gsub(/&nbsp;/, " ", line)
        gsub(/&#34;/, "\"", line)
        gsub(/^[ \t]+|[ \t]+$/, "", line)
        content = line
    }
}

/<\/div>/ && in_article {
    if (title && content) {
        print "---"
        print ""
        print "## " title
        print ""
        print content
        print ""
    }
    in_article = 0
}
'
