# CV Rewriter

A local tool that rewrites your CV to match a job ad's language and keywords — using your real experience, just phrased to fit the role. Paste in a job ad, upload your CV, hit rewrite.

---

## Getting Started (from scratch)

### 1. Install Python

You need Python installed on your computer. If you've never done this before:

1. Go to [python.org/downloads](https://www.python.org/downloads/) and click the big yellow **Download Python** button
2. Run the installer
3. **Important:** Tick the box that says **"Add Python to PATH"** before clicking Install Now — this is the one thing people miss

To check it worked, open **PowerShell** (search for it in the Start menu) and type:

```
python --version
```

You should see something like `Python 3.13.3`. If you get an error, restart your computer and try again.

### 2. Install Git (if you don't have it)

1. Go to [git-scm.com/downloads/win](https://git-scm.com/downloads/win) and download the installer
2. Run it — the default options are fine, just click Next through everything
3. Restart PowerShell after installing

### 3. Download this project

Open PowerShell and run these commands one at a time:

```powershell
cd ~\Desktop
git clone https://github.com/cw4444/CV-Rewrite.git
cd CV-Rewrite
```

This puts the project in a folder on your Desktop. You can use a different location if you prefer.

### 4. Install the dependencies

Still in PowerShell, in the CV-Rewrite folder:

```powershell
pip install -r requirements.txt
```

This downloads everything the app needs. It'll take a minute or two.

### 5. Get an API key

The app uses AI to do the rewriting. You need an API key from at least one of these providers:

- **Anthropic (Claude)** — recommended: [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
- **OpenAI (GPT)**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

You'll need to create an account and add a small amount of credit (a few pounds/dollars will last ages — a single CV rewrite costs fractions of a penny).

You don't need to set the key up in advance — the app has a Settings button where you can paste it in when you first open it.

### 6. Run the app

```powershell
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:8000
```

That's it. The app runs entirely on your machine — your CV and API key never go anywhere except directly to the AI provider.

### Closing and re-opening

When you're done, press `Ctrl+C` in PowerShell to stop the app. Next time you want to use it:

```powershell
cd ~\Desktop\CV-Rewrite
python app.py
```

---

## How to use it

1. **Upload or paste your CV** on the left (supports PDF, Word, or plain text)
2. **Paste the job ad** on the right
3. **Pick a provider and model** from the dropdowns (defaults are fine)
4. Click **Rewrite CV**
5. Copy the result

The tool rephrases your experience to match the job ad's language and keywords. It won't invent anything — just makes sure you're speaking the same language as the job spec.

---

## Models

| Provider | Model | Best for |
|----------|-------|----------|
| Anthropic | Claude Sonnet 4 | Best balance of quality and speed (default) |
| Anthropic | Claude Opus 4 | Highest quality, slower |
| Anthropic | Claude Haiku 4.5 | Fastest and cheapest |
| OpenAI | GPT-4o | Best balance (default for OpenAI) |
| OpenAI | GPT-4o Mini | Fastest and cheapest |
| OpenAI | GPT-4 Turbo | Alternative |

---

## Troubleshooting

**"python is not recognized"** — You probably didn't tick "Add to PATH" when installing Python. Reinstall it and make sure that box is ticked.

**"pip is not recognized"** — Try `python -m pip install -r requirements.txt` instead.

**API error** — Double-check your API key in Settings. Make sure you have credit on your account.

**Port already in use** — Something else is using port 8000. Close it or edit the port number at the bottom of `app.py`.

## License

This project is proprietary. You may not use, copy, modify, redistribute, deploy, or install it for commercial or client use without prior written permission.

Commercial licenses are available. For business use, professional installation, or deployment enquiries, contact: **cw4444@gmail.com**
