---
name: czech-ai-news
description: Fetch the latest Czech AI news summaries from Hospodářské Noviny (ai.hn.cz/strucne), group them by topic, and present to the user. No translation, no rewriting.
metadata:
  roles: all
  keywords: czech-ai-news,czech ai news,czech news,hospodarske noviny,hn news
  display-name: COG Czech AI News
---

# Czech AI News

## When to Invoke
- User says "czech-ai-news", "czech ai news", "czech news", "what's in HN today"
- User wants the latest Czech AI/business briefs from Hospodářské Noviny

## Process

1. Run the fetch script from this skill's directory:

   ```bash
   bash .agents/skills/czech-ai-news/scripts/fetch-news.sh
   ```

2. **Do NOT translate or rewrite.** Keep the Czech text verbatim.
3. Group the summaries by topic (e.g., business, technology, economy, politics) using the article titles as the grouping signal.
4. Present the grouped summaries to the user with each group's heading in English; story titles + bodies stay in Czech.

## Error Handling
- If the script returns no articles, report "No fresh stories from ai.hn.cz/strucne" — don't fabricate.
- If `curl` fails (network/site down), surface the error to the user and stop.
