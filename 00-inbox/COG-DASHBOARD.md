---
type: dashboard
created: 2026-02-25
tags: [cog, config]
---

# COG Command Center

> Live queries powered by Dataview. This page updates automatically.

---

## Pulse

```dataviewjs
const braindumps = dv.pages('"03-professional/braindumps" or "02-personal"').where(p => p.type === "braindump");
const unresolved = braindumps.where(p => p.status !== "resolved" && p.status !== "consolidated");
const projects = dv.pages('"04-projects"').where(p => p.type === "project-overview");
const activeProjects = projects.where(p => p.status === "active");
const bookmarks = dv.pages('"05-knowledge/booklets"').where(p => p.type === "url-bookmark" || p.type === "url-tool" || p.type === "url-article");
const toEval = bookmarks.where(p => p.status === "to-evaluate");
const frameworks = dv.pages('"05-knowledge/consolidated"').where(p => p.type === "consolidated-knowledge" && p.status === "active");
const briefs = dv.pages('"01-daily/briefs"').where(p => p.type === "daily-brief");

dv.paragraph(`**${activeProjects.length}** active projects · **${unresolved.length}** open braindumps · **${toEval.length}** tools to evaluate · **${frameworks.length}** active frameworks · **${briefs.length}** daily briefs generated`);
```

---

## Active Projects

```dataview
TABLE WITHOUT ID
  link(file.link, project) AS "Project",
  customer AS "Customer",
  status AS "Status",
  updated AS "Updated"
FROM "04-projects"
WHERE type = "project-overview"
SORT status ASC, updated DESC
```

---

## Braindump Inbox

> Braindumps not yet resolved or consolidated — raw ideas waiting to be processed.

```dataview
TABLE WITHOUT ID
  file.link AS "Braindump",
  date AS "Date",
  status AS "Status",
  join(themes, ", ") AS "Themes",
  confidence AS "Confidence"
FROM "03-professional/braindumps" OR "02-personal"
WHERE type = "braindump" AND status != "resolved" AND status != "consolidated"
SORT date DESC
```

### Recently Consolidated

```dataview
TABLE WITHOUT ID
  file.link AS "Braindump",
  date AS "Date",
  consolidated_in AS "Consolidated In",
  consolidated_date AS "When"
FROM "03-professional/braindumps" OR "02-personal"
WHERE type = "braindump" AND (status = "consolidated" OR consolidated_in)
SORT consolidated_date DESC
LIMIT 5
```

---

## Knowledge Pipeline

### Tools to Evaluate

```dataview
TABLE WITHOUT ID
  file.link AS "Tool",
  title AS "Name",
  license AS "License",
  relevance AS "Relevance",
  date_saved AS "Saved"
FROM "05-knowledge/booklets"
WHERE type = "url-tool" AND status = "to-evaluate"
SORT relevance DESC, date_saved DESC
```

### High-Value References

```dataview
TABLE WITHOUT ID
  file.link AS "Reference",
  title AS "Title",
  category AS "Category",
  relevance AS "Relevance"
FROM "05-knowledge/booklets"
WHERE (type = "url-bookmark" OR type = "url-article") AND (relevance = "high" OR relevance = "medium-high")
SORT date_saved DESC
LIMIT 10
```

### Articles to Read

```dataview
TABLE WITHOUT ID
  file.link AS "Article",
  title AS "Title",
  author AS "Author",
  date_saved AS "Saved"
FROM "05-knowledge/booklets/articles"
WHERE type = "url-article" AND status = "captured"
SORT date_saved DESC
```

---

## Active Frameworks

```dataview
TABLE WITHOUT ID
  file.link AS "Framework",
  framework AS "Name",
  last_updated AS "Last Updated",
  source_documents AS "Sources"
FROM "05-knowledge/consolidated"
WHERE type = "consolidated-knowledge" AND status = "active"
SORT last_updated DESC
```

---

## Recent Daily Briefs

```dataview
TABLE WITHOUT ID
  file.link AS "Brief",
  date AS "Date",
  items_count AS "Items",
  join(interests, ", ") AS "Topics",
  confidence AS "Confidence"
FROM "01-daily/briefs"
WHERE type = "daily-brief"
SORT date DESC
LIMIT 7
```

---

## Consolidation History

```dataview
TABLE WITHOUT ID
  file.link AS "Consolidation",
  consolidation_period AS "Period",
  sources_analyzed AS "Sources",
  patterns_identified AS "Patterns Found",
  join(frameworks_created, ", ") AS "New Frameworks"
FROM "05-knowledge/consolidated"
WHERE type = "knowledge-consolidation"
SORT date DESC
LIMIT 5
```

---

## Cross-Project Tag Cloud

```dataviewjs
// Count documents per major theme across all braindumps
const pages = dv.pages('"03-professional/braindumps"').where(p => p.themes);
const themeCounts = {};
for (const page of pages) {
  const themes = Array.isArray(page.themes) ? page.themes : [page.themes];
  for (const theme of themes) {
    if (theme) themeCounts[theme] = (themeCounts[theme] || 0) + 1;
  }
}
const sorted = Object.entries(themeCounts).sort((a, b) => b[1] - a[1]);
const lines = sorted.map(([theme, count]) => `**${theme}** (${count})`);
dv.paragraph(lines.join(" · "));
```

---

## Project-Braindump Map

> Which projects have the most thinking behind them?

```dataviewjs
const braindumps = dv.pages('"03-professional/braindumps" or "02-personal" or "04-projects"')
  .where(p => p.type === "braindump");

const projectFolders = {};
for (const bd of braindumps) {
  const folder = bd.file.folder;
  // Extract project context from folder path
  let project = "General";
  if (folder.includes("04-projects/")) {
    const parts = folder.replace("04-projects/", "").split("/");
    project = parts.slice(0, 2).join("/");
  } else if (folder.includes("03-professional")) {
    project = "Professional (general)";
  } else if (folder.includes("02-personal")) {
    project = "Personal";
  }
  projectFolders[project] = (projectFolders[project] || 0) + 1;
}

const sorted = Object.entries(projectFolders).sort((a, b) => b[1] - a[1]);
dv.table(
  ["Project Area", "Braindumps"],
  sorted.map(([proj, count]) => [proj, count])
);
```

---

## Customers at a Glance

```dataview
TABLE WITHOUT ID
  file.link AS "Customer",
  customer AS "Name",
  status AS "Status"
FROM "04-projects"
WHERE type = "customer-overview"
SORT status ASC, customer ASC
```

---

*Dashboard auto-updates on every page load. Last configured: 2026-02-25.*
