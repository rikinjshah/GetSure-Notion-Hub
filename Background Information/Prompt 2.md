
You’ve already created the basic Notion hub via Python. Now we need a **follow‑up version** that significantly upgrades the **sales call content**, adds visual formatting, and outputs everything into separate content files for Claude to use.

---

## 🎯 Goals

1. **Sales-call training pages** must include:
   - A mix of **long-form paragraphs**, **bulleted lists**, **callouts**, **tables**, and **emphasis blocks**.  
   - Not just bullets—give context, mindset insights, examples, emotional guidance, and mini storytelling.

2. **Everything** (FAQs, sales‑call pages, objections, scripts) should live in separate JSON or markdown files:
   - `faqs.json`
   - `sales_call_pages.md` (multiple individual markdown files, one per phase)
   - `objections.json`
   - `scripts.json`

3. The final Python script (`build_training_hub.py`) reads these files, then:
   - Builds Notion pages + databases with gallery view
   - Applies covers, icons, thumbnails
   - Inserts richly formatted blocks into Notion using its API

---

## 🔍 Example Content (for “Introduction & Rapport Building”)

Here's a **full content example** in mixed formatting (in markdown style) for one sales-call phase. Claude should mimic this style in its other pages:

```markdown
---
slug: introduction-rapport.md
title: "1. Introduction & Rapport Building"
icon: "🤝"
cover_image: "https://source.unsplash.com/collection/rapport-building-123"
---

🎯 **Purpose of this phase**  
Establish trust within the first 30 seconds and set the tone that this call is about **helping**, not selling. Make the client feel heard and respected.

💭 **What the prospect might be thinking**  
They might wonder: “Is this just another sales call?” or “Will this take too much time?”  
Adults in this stage are often cautious, so your tone must be calm and empathetic.

🧠 **Why it matters**  
Building rapport early reduces resistance later—and increases the chance they'll engage with the rest of the call.

> **Callout**: Use their name at least twice, **mirror their tone**, and **confirm availability** before proceeding.

**Suggested Phrases**  
- “Hi [Name], it’s [Agent] from [Company]. How are you doing today?”  
- “I saw you requested info on final expense—can I have 5 minutes of your time right now?”

**Further Coaching Tips**  
- Speak *slightly slower* than normal—project calm.  
- Notice their energy level and match it: if they speak softly, do the same.  
- Ask one question, then *pause*—true listening builds trust.

📌 **Quick table: Tone vs Comment Example**

| Prospect Tone | Agent Match Strategy      | Example Response                                  |
|---------------|---------------------------|---------------------------------------------------|
| Fast talker   | Use brisk pacing           | “Great! I’ll keep this quick—need just 5 min.”  |
| Hesitant      | Slow and reassuring        | “No rush at all—whenever you’re ready is fine.” |

---

Your content for the other 5 call phases should replicate this format: **introduction paragraph**, **prospect mindset**, **agent goals**, **callouts**, **bullets**, and a **small table** or **emphasis block** for visual clarity.

---

## 🛠️ Instructions for Claude

1. **Generate four content files**:
   - `faqs.json`
   - `sales_call_pages/intro_rapport.md` (example shown)
   - `sales_call_pages/…` (other five phases with same rich format)
   - `objections.json`
   - `scripts.json`

2. **Generate `build_training_hub.py`** to:
   - Read those files
   - Use Notion API to build or update pages & databases
   - Apply **covers**, **icons**, and **thumbnails**
   - Insert richly formatted blocks as specified in each markdown/JSON file
   - Ensure idempotency and logging

---

## ✅ Requirements Recap

- **Rich formatting**: paragraphs + bullets + callouts + tables—not just bullets
- **Separate files** for each content domain
- **Example provided** for Claude to replicate
- Python script reads and builds from content

---

Please output:

1. The content files with the example and template structure
2. The Python script scaffolding that reads them and builds the hub

Ready when you are—this will make the hub feel polished, visually structured, and high-impact for agents.
````
