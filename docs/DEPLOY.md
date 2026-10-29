# Deploy

DocuChat is **not deployed yet**. This is the intended setup.

| Part | Platform |
|---|---|
| Frontend | Vercel (`frontend/`, build `npm run build`, output `dist`, SPA rewrite to `index.html`) |
| API | A service with a **persistent disk** (e.g. Render with a disk mounted at `DATA_DIR`) |
| Model | Groq |

Uploaded PDFs, Chroma's files and (by default) the SQLite database all live in `DATA_DIR`, so the API needs storage that survives restarts. A free instance with an ephemeral filesystem loses every document on restart. The embedding model needs roughly 300 MB of RAM on top of the app.

## Environment

On the API:

- `APP_PASSWORD` (strong) and `SESSION_SECRET` (long random)
- `LLM_PROVIDER=groq`, `LLM_API_KEY`
- `DATA_DIR=/var/data` (the mounted disk)
- `FRONTEND_URL=https://<frontend-host>`, `CROSS_SITE_COOKIES=true`

On the frontend: `VITE_API_URL=https://<api-host>`.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
