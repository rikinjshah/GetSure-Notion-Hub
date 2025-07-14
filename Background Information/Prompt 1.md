You are a senior full‑stack developer and life insurance expert crafting a **Python script** that, when run, uses the Notion API to build a **Life Insurance Agent Training Hub** workspace. This workspace has two main sections:

---

### 1. Final Expense Life Insurance 101

- Create a **Notion database** titled `Final Expense FAQs` with **exactly 20 pages/items**.
- Each item represents a “top FAQ” and includes:
  - **Title**: the FAQ question.
  - **Description**: a 1–2 sentence summary.
  - **Tags**: such as `underwriting`, `premium`, `beneficiary`, `approval`, etc.
  - **Thumbnail image**: relevant icon or picture.
- Database should display in **Gallery view** showing title, description, tags, and thumbnail.
- Each page’s **full content** should include:
  - The **question** as a heading.
  - The **answer** as:
    - A **callout** summarizing the core idea
    - A detailed 200-300 word answer that uses STRUCTURE to make its point crystal clear (sub-headings, bullets, and/or tables)
    - The answer should conclude with a list of "variations of this question"
- Use Notion icons and emojis to visually enhance readability.

✅ Use a mix of the following **real FAQ examples** from the attached spreadsheet:

1. **Title**: “How does final expense insurance work?”
   - **Description**: Covers funeral costs and other end-of-life expenses.
   - **Tags**: `overview`, `benefits`, `cost`
   - **Callout**: “Final expense is a small whole life policy meant to pay for funeral and related costs.”


2. **Title**: “Can I get coverage if I have health issues?”
   - **Description**: Yes—many policies are designed for people with health conditions.
   - **Tags**: `underwriting`, `health`, `approval`


3. **Title**: “What’s the difference between term and whole life insurance?”
   - **Description**: Term expires; whole life stays with you for life.
   - **Tags**: `term`, `whole life`, `coverage type`
  

(Include 17 more FAQs in a similar format using spreadsheet data and placeholders as needed.)

---

### 2. Sales Training Section

#### a) Sales Call Sequence Pages
- Create a **Notion page** (or nested pages) titled `Sales Call Training`.
- Include a page for each part of the call:
  1. Introduction
  2. Needs Discovery / Fact‑Find
  3. Product Presentation
  4. Pricing Discussion
  5. Closing / Next Steps
  6. Follow‑Up Cadence
- Each page must include:
  - A **callout** that frames the goal of the step.
  - A **bullet list** of:
    - Phrases to say
    - Common client reactions
    - Agent coaching notes
  - Use **tables** where applicable (e.g., sample dialogue).
  - Use icons and visual structure to aid scanning.

#### b) Objections Database
- Create a Notion **database** called `Common Objections`.
- At least 5 entries, each with:
  - **Title** (e.g., “It’s too expensive”)
  - **Description** (summary of the objection)
  - **Tags**: `price`, `trust`, `delay`, etc.
  - **Thumbnail**
- Each entry should show in gallery view and include:
  - Objection in H2
  - Callout: “What they’re really saying”
  - Bullet list of rebuttal strategies
  - Optional table: sample agent responses
  - Alternate ways this objection may be said

#### c) Scripts Database
- Create another Notion **database** titled `Scripts`:
  - Includes: `Call Script`, `Voicemail Script`, `SMS Script`
  - Each page shows in gallery view with:
    - Title
    - Description
    - Tags (`call`, `text`, etc.)
    - Thumbnail
  - Inside: 
    - Script formatted in blockquote or code style
    - Callout: when to use
    - Bullets: tips for adapting script

---

### 🔧 Implementation Requirements

- Use **Notion API** in Python (`notion-client` or similar)
- Your script should:
  1. Prompt for (or accept) a Notion API token and parent page ID.
     - Use:  
       - `parent_page_id = "230dfdef0e0a809ba2c5c506978fe342"`  
       - `token = "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"`
  2. Create or reuse a Notion workspace titled **"Life Insurance Agent Training Hub"**
  3. Add:
     - One FAQ database
     - One training module with sub-pages
     - Two additional databases (`Objections`, `Scripts`)
  4. Configure each database to **gallery view** with custom preview fields (title, description, tags, thumbnail)
  5. Insert content using structured Notion blocks (headings, callouts, bullets, tables, icons)
  6. Modular code—clearly commented sections and reusable functions

---

### ✅ Final Deliverable

- Fully working Python code that:
  - Creates hub in Notion
  - Populates all sections
  - Is maintainable and well-documented
- JSON, CSV, and/or md files for supporting content

---

### 🧠 Tone & Priorities

- Direct, clean, visual presentation
- Use icons and block types effectively
- All copy should reflect a **clear, confident, no-BS tone**
- Pull from PDFs and spreadsheet content to ensure authentic, useful agent guidance