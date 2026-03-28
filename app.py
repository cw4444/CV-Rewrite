import os
import tempfile
from pathlib import Path

import anthropic
import openai
import pdfplumber
from docx import Document
from dotenv import load_dotenv, set_key
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

ENV_PATH = Path(__file__).parent / ".env"

# ── Available models ──────────────────────────────────────────────────────────

MODELS = {
    "anthropic": [
        {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4 (recommended)"},
        {"id": "claude-opus-4-20250514", "name": "Claude Opus 4 (best quality, slower)"},
        {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5 (fastest, cheapest)"},
    ],
    "openai": [
        {"id": "gpt-4o", "name": "GPT-4o (recommended)"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini (fastest, cheapest)"},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
    ],
}

# ── Helpers ───────────────────────────────────────────────────────────────────


def extract_text_from_pdf(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        with pdfplumber.open(tmp_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    finally:
        os.unlink(tmp_path)


def extract_text_from_docx(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        doc = Document(tmp_path)
        return "\n".join(p.text for p in doc.paragraphs)
    finally:
        os.unlink(tmp_path)


SYSTEM_PROMPT = """\
You are an expert CV/resume rewriter. Your job is to rewrite the candidate's CV \
so that the language, keywords, and emphasis align closely with the provided job \
advertisement — while keeping ALL facts, dates, qualifications, and experience \
completely truthful and accurate.

Rules:
1. NEVER invent experience, skills, or qualifications the candidate does not have.
2. Rephrase bullet points and descriptions to use the same terminology and \
   keywords found in the job ad.
3. Reorder or emphasise sections/skills that are most relevant to the role.
4. Keep the overall structure clean and professional.
5. Where the candidate has relevant experience, mirror the exact phrasing from \
   the job ad where natural.
6. Output the rewritten CV in clean Markdown format.
"""


def build_user_prompt(cv_text: str, job_ad: str) -> str:
    return (
        f"## Original CV\n\n{cv_text}\n\n"
        f"---\n\n"
        f"## Job Advertisement\n\n{job_ad}\n\n"
        f"---\n\n"
        f"Please rewrite the CV above so its language matches the job ad. "
        f"Keep all facts truthful."
    )


async def rewrite_anthropic(cv_text: str, job_ad: str, model: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(cv_text, job_ad)}],
    )
    return message.content[0].text


async def rewrite_openai(cv_text: str, job_ad: str, model: str, api_key: str) -> str:
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(cv_text, job_ad)},
        ],
    )
    return response.choices[0].message.content


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def index():
    return Path("static/index.html").read_text(encoding="utf-8")


@app.get("/api/models")
async def get_models():
    return MODELS


@app.get("/api/keys/status")
async def keys_status():
    """Return which providers have keys configured (never return the actual keys)."""
    return {
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/api/keys/save")
async def save_key(provider: str = Form(...), api_key: str = Form(...)):
    """Save an API key to .env (creates the file if needed)."""
    if provider not in ("anthropic", "openai"):
        return JSONResponse({"error": "Invalid provider"}, status_code=400)

    env_var = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"

    # Ensure .env exists
    if not ENV_PATH.exists():
        ENV_PATH.touch()

    set_key(str(ENV_PATH), env_var, api_key)
    os.environ[env_var] = api_key  # also update current process
    return {"ok": True}


@app.post("/api/rewrite")
async def rewrite(
    job_ad: str = Form(...),
    provider: str = Form(...),
    model: str = Form(...),
    cv_text: str = Form(default=""),
    cv_file: UploadFile | None = File(default=None),
):
    # ── Resolve CV text ───────────────────────────────────────────────────
    if cv_file and cv_file.filename:
        file_bytes = await cv_file.read()
        ext = Path(cv_file.filename).suffix.lower()
        if ext == ".pdf":
            cv_content = extract_text_from_pdf(file_bytes)
        elif ext in (".docx", ".doc"):
            cv_content = extract_text_from_docx(file_bytes)
        elif ext == ".txt":
            cv_content = file_bytes.decode("utf-8", errors="replace")
        else:
            return JSONResponse(
                {"error": f"Unsupported file type: {ext}. Use PDF, DOCX, or TXT."},
                status_code=400,
            )
    elif cv_text.strip():
        cv_content = cv_text.strip()
    else:
        return JSONResponse(
            {"error": "Please provide your CV — either upload a file or paste the text."},
            status_code=400,
        )

    # ── Resolve API key ───────────────────────────────────────────────────
    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
    else:
        return JSONResponse({"error": "Invalid provider"}, status_code=400)

    if not api_key:
        return JSONResponse(
            {"error": f"No API key configured for {provider}. Add one in Settings."},
            status_code=400,
        )

    # ── Call LLM ──────────────────────────────────────────────────────────
    try:
        if provider == "anthropic":
            result = await rewrite_anthropic(cv_content, job_ad, model, api_key)
        else:
            result = await rewrite_openai(cv_content, job_ad, model, api_key)
    except Exception as e:
        return JSONResponse({"error": f"API error: {e}"}, status_code=502)

    return {"rewritten_cv": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
