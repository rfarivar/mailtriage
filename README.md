# mailtriage

Local-LLM email triage for IMAP inboxes (Gmail/Yahoo/Office365), with safe defaults and optional auto-move.

## What It Does

- Connects to an IMAP mailbox and fetches recent messages.
- Extracts and normalizes email content (plain text preferred, HTML fallback).
- Sends structured classification requests to an Ollama model.
- Assigns each email to one bucket:
  - `needs_attention`
  - `transactional`
  - `security_alert`
  - `calendar_or_travel`
  - `newsletter_or_marketing`
  - `social_notification`
  - `spam_or_scams`
  - `uncertain`
- Applies deterministic move policy in code (not model-defined).
- Writes JSONL logs for every processed email.
- Supports optional two-pass verification with a secondary model before moving.

## Safety Model

- `--mode report` is read-only (recommended first).
- `--mode move` only moves when policy checks pass.
- `policy.dry_run: true` or `--dry-run` prevents moving, even if `mode` is set to `move`.
- `never_move_from_domains` and `never_move_from_senders` in the `config.yaml` file are hard blocks.
- Two-pass mode can require model agreement (`--two pass --secondary-model qwen3:8b`) 
- For two-pass mode, you can either require both models come up with the exact same bucket, or allow some wiggle room with the grouping mode (`--agree bucket|group`).

## Requirements

- Python 3.10+
- Ollama running locally or reachable by URL
- One IMAP account configured in `config.yaml`

If your system maps `python`/`pip` differently, use `python3`/`pip3` instead.


## Quick Start

1. Create and activate a virtual environment.

PowerShell in Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

bash/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Note**: In the rest of this document, I will simply use `python` in presented CLI commands. You should use the correct python invocation for your environment, which can be either `python` or `python3`. 

2. Install dependencies.


```
python -m pip install -r requirements.txt
```



3. Configure `config.yaml`.

- Set `ollama.base_url`, `ollama.model`, and policy values.
- Add at least one account under `accounts`.

4. Email Setup

For Exchange accounts, we use OATH2 path. As such, you can skip the next section (nothing to set in the .env). The first time you run the program, it will give you a link and token to enter. Open the link in your browser and enter the generated code and follow your usual login process. Once done, the program will continue automatically and fetch your emails. The resulting authentication token will be stored in `.msal_token_cache.bin` file. 

For gmail and Yahoo accounts, you currently need to setup an `App Password`, and put it in the .env file (next section). Follow the instructions for [gmail](https://support.google.com/mail/answer/185833?hl=en) or [Yahoo Mail](https://help.yahoo.com/kb/generate-password-sln15241.html). 
Also put each IMAP account username in `.env` and reference it from `config.yaml` using `auth.username_env`.

5. Put secrets in `.env` (or your shell environment).

There is a `env.example.txt` file included. First, make a `.env` using it as a template:
```
cp env.example.txt .env
```


Anything you put in this file will become an environment variable and the program picks it up that way. 

Examples:

```env
# IMAP app passwords
GMAIL_APP_PASSWORD=...
YAHOO_APP_PASSWORD=...

# IMAP usernames
GMAIL_IMAP_USERNAME=...
YAHOO_IMAP_USERNAME=...
UIUC_IMAP_USERNAME=...

# Optional Ollama overrides
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.1:8b
# OLLAMA_CONTEXT_LENGTH_TOKENS=4096

# Optional Microsoft 365 device-flow auth, do not change these
M365_CLIENT_ID=...
M365_TENANT=organizations
# optional cache file override
M365_TOKEN_CACHE=.msal_token_cache.bin
```

## Core Commands

### Ensure destination folders exist

The mailtriage program will move the emails to folders in your inbox such as AI/Promotions, AI/Social, etc. The first time you run the program, use the following command to setup the folders for you.

```
python mailtriage.py folders --account gmail
```

### Dry-run triage report (recommended first)


```
python mailtriage.py --config config.yaml triage --account gmail --limit 200 --unseen --mode report
```

### Move mode

```
python mailtriage.py --config config.yaml triage --account gmail --limit 200 --unseen --mode move
```


Add `--dry-run` to force no moves even in move mode.

```
python mailtriage.py --config config.yaml triage --account gmail --limit 200 --unseen --mode move
```

### Two-pass verification

By default, the application uses llama3.1:8b (configurable in the `config.yaml` file) to read the text of your email and classify it. To reduce any false positives, you can use the two-pass verification flow, where the email will be processed in a second pass by the qwen3:8b model, and the results will be used together to create a consensus. 

```
python mailtriage.py --config config.yaml triage --account gmail --mode report --two-pass --secondary-model qwen3:8b --shortlist-threshold 0.85 --agree bucket
```

`--agree group` compares destination intent (folder group) instead of exact bucket.

As a point of reference, I typically use the program as follows: 
```
python mailtriage.py triage --account uiuc --mode report --limit 10 --two-pass --secondary-model qwen3:8b --agree group
```

## Config Notes (`config.yaml`)

- `ollama.base_url`: API endpoint, typically `http://localhost:11434`
- `ollama.model`: primary model name
- `ollama.timeout_s`: request timeout
- `ollama.context_length_tokens`: context window used for `num_ctx`
- `policy.auto_move_threshold`: minimum confidence for non-spam moves
- `policy.spam_quarantine_threshold`: minimum confidence for spam quarantine
- `policy.folder_map`: bucket -> destination IMAP folder
- `accounts.<name>.auth.method`: `password` or `xoauth2`
- `accounts.<name>.auth.username_env`: env var for IMAP username
- `accounts.<name>.auth.password_env`: env var for password auth
- `accounts.<name>.auth.access_token_env`: env var for OAuth token

For `xoauth2`, if `access_token_env` is missing at runtime and M365 env vars are set, the app can obtain a token with device code flow.

## Output and Logs

Each run writes JSONL in `runs/` by default:

- Filename pattern: `<account>_<YYYYMMDD_HHMMSS>.jsonl`
- Includes:
  - email metadata (`from`, `subject`, `message_id`, etc.)
  - primary model result
  - secondary model result (if two-pass)
  - effective bucket/destination
  - `verified` and `move_ok`
  - timing/token counters from Ollama response

## Tests

Run non-integration tests.

```
pytest -q -m "not integration"
```

Run integration tests (requires Ollama + model).

```
$env:RUN_OLLAMA_INTEGRATION="1"
pytest -q -m integration
```

## Troubleshooting

- `Missing env var for IMAP password`:
  - Set the env var named by `auth.password_env`.
- `Missing env var for IMAP username`:
  - Set the env var named by `auth.username_env`.
- `XOAUTH2 auth failed`:
  - Verify token validity/scope and account settings.
- `Empty message.content` or schema parse errors:
  - Try a more reliable model, increase timeout/context, and keep `system.md` strict.
- Slow runs:
  - Reduce `--limit`, lower context size, or use a faster model.

## Security Notes

- Keep `.env`, token caches, and run logs out of version control.
- Review `policy.folder_map` and thresholds before enabling move mode.
- Start with report mode, then enable move mode only after validating JSONL outputs.
