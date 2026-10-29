# Changelog

All notable changes to **DocuChat** are documented here.

---

## [Unreleased]

---

## [0.1.0] — 2026-10-29

### ✨ Added
- PDF upload with validation (type, size, page count, password, no-text) and passage extraction with page coordinates
- Local embeddings (fastembed `bge-small-en-v1.5`) in ChromaDB, searched per document
- Retrieval confidence gate that declines without calling the model, plus a model-side decline
- Cited answers through Groq, OpenAI or Ollama
- Page images with the cited passage highlighted
- Chat history per document; single-password login

### 🧪 Tests
- PDF parsing, heading-aware passages, rendering, retrieval scoping, the confidence gate and prompt contents with pytest (no model download or key)
- Citation parsing with Vitest

---

[Unreleased]: https://github.com/akshatgcodes/DocuChat/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/akshatgcodes/DocuChat/releases/tag/v0.1.0

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
