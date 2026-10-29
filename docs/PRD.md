# PRD: DocuChat

## Problem

Finding one fact in a long PDF means skimming or Ctrl+F guessing the right word. Chatbots that read PDFs answer confidently even when the document doesn't say, and rarely show where an answer came from.

## Goal

Ask a question in plain language and get an answer that points to the passage it came from, or an honest "the document doesn't cover this".

## Users

- **Reader:** a student, engineer or analyst working through papers, manuals, reports or policies

## User stories

| As a… | I want to… | So that… |
|---|---|---|
| reader | upload a PDF by dragging it in | I can start in seconds |
| reader | ask a question in plain language | I don't need the exact wording |
| reader | see which passages an answer came from | I can trust or check it |
| reader | click a citation and see it highlighted on the page | I can read the surrounding context |
| reader | be told when the document doesn't cover my question | I don't act on a made-up answer |
| reader | see how confident the match was | I know how much to trust it |
| reader | come back to a document and see earlier questions | I don't lose my work |

## Requirements

- PDF upload up to 20 MB / 300 pages; clear errors for non-PDFs, encrypted and scanned files
- Passage extraction with page coordinates; embeddings in ChromaDB, filtered per document
- Retrieval confidence threshold (configurable) that skips generation when nothing is close enough
- Answers with numbered citations; model instructed to decline when the excerpts don't contain the answer
- Page image with the cited passage highlighted
- Groq, OpenAI or Ollama selectable by environment variable
- Chat history per document; single-password login

## Non-goals (v1)

- OCR for scanned PDFs
- Questions across several documents at once
- Follow-up questions that depend on earlier turns
- Streaming answers token by token
- Other file types (Word, HTML)

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
