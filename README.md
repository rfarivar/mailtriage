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

### 1. Install Ollama 
  - Follow ([instructions here](https://github.com/ollama/ollama?tab=readme-ov-file#download)) to install Ollama.
  - Open a browser tab and go to [http://localhost:11434](http://localhost:11434). You should see the sentence `Ollama is running` in your browser. 
  - Pull the required LLM models. By default, the app is configured to use `llama3.1:8b`, so ensure to at least pull this model. 
  ```
  ollama pull llama3.1:8b
  ```
To experiment with other models or to try the two-pass mode, you need to install other models as well. 
  ```
  ollama pull qwen3:8b
  ollama pull llama3.2
  ```

### 2. Create and activate a Python virtual environment.

PowerShell in Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

bash/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies.

```
python -m pip install -r requirements.txt
```

### 4. Email setup

Email account configuration is managed in the `config.yaml` file. The file already includes placeholders for the following account types:

* Gmail
* Yahoo Mail
* Microsoft 365 Exchange

Your `username` and `password` are secrets and should not be stored in the `config.yaml`. Instead, Store all secrets in the `.env` file (or defined in your shell environment).

An `env.example.txt` file is provided as a template in the repo. Create your `.env` file by copying it:

```
cp env.example.txt .env
```

#### Gmail and Yahoo Mail

For Gmail and Yahoo accounts, you must generate an `App Password` (a one-time password dedicated to this application). Follow the official [Gmail](https://support.google.com/mail/answer/185833?hl=en) or [Yahoo Mail](https://help.yahoo.com/kb/generate-password-sln15241.html) instructions to create the App Password.

Once generated, open the .env file in your preferred editor and add:
* Username and App Password for Gmail and Yahoo accounts

Leave the fields for any unused accounts blank.
All values defined in the .env file are loaded as environment variables and automatically used by the application.


#### Microsoft 365 Exchange

For Microsoft 365 Exchange accounts, OAuth2 authentication is used. 

Open the .env file in your preferred editor and add:
* Client ID and Tenant ID for Microsoft 365 Exchange accounts
* Your username for the exchange account

The first time you run the program, it will provide a URL and a verification code in the console. Open the URL in your browser, enter the generated code, and complete the standard Microsoft login process.
After authentication is complete, the program will automatically resume and begin fetching your emails. The resulting authentication token will be saved to the `.msal_token_cache.bin` file for future use.

- There are many other customization options in `config.yaml` which you can customize later.

## Core Commands

### Ensure destination folders exist

The mailtriage program moves emails into folders such as AI/Promotions, AI/Social, etc.
Before running triage for the first time, create the required folders with:

```
python mailtriage.py folders --account gmail
```

### Dry-run triage report (recommended first)
Run a report-only triage to preview actions without moving any emails:

```
python mailtriage.py --config config.yaml triage --account gmail --limit 5 --unseen --mode report
```

### Move mode

To move emails based on the triage results:

```
python mailtriage.py triage --account gmail --limit 5 --mode move
```

To prevent any emails from being moved (even in move mode), add the `--dry-run` flag:

```
python mailtriage.py triage --account gmail --limit 5 --mode move --dry-run`
```

You can add the `--unseen` option to run the analysis only on unread emails:

```
python mailtriage.py triage --account gmail --limit 5 --unseen --mode move
```

### Two-pass verification

By default, the application uses llama3.1:8b (configurable in the `config.yaml` file) to read the text of your email and classify it. To reduce any false positives, you can use the two-pass verification flow, where the email will be processed in a second pass by the qwen3:8b model, and the results will be used together to create a consensus. 

```
python mailtriage.py --config config.yaml triage --account gmail --mode report --two-pass --secondary-model qwen3:8b --shortlist-threshold 0.85 --agree bucket
```

## How to run

I want to share some of my experiences in running the Mail Triage program.

1. Which model runs the best?

I have experimented with four models: llama3.1:8b, qwen3:8b, deepseek-r1:8b and llama3.2:3b. In my experience, Llama3.1:8b is the best model to run, as it consistently makes meaningful judgement, and generates JSON output the way it is instructed. It does take the longest to run. Next is Qwen3. It seems to make a deeper analysis which is good, and is a bit faster to run, but occasioanly exceeds the output token limit, in which case the program considers the output as invalid. Lama3.2:3b is much faster to run, but the quality of the results are not as good as LLama3.1:8b. It may be possible to get higher quality from it with better prompting. Finally, deepseek-r1 is good at thinking, however, it frequently creates output that does not match the requested JSON format, and as such, I have not focused on it so far. 

2. How fast are the models?

The following numbers are collected from a run with 20 emails. Context is set to 4096 tokens. (In general, the longer the context, the slower your performance. For the 3080 card, 4096 is the sweetspot, and should handle about 14 thousand charachter emails, which should be enough to make a decision on the nature of the email.) The following table shows the triage phase time for each email in a 20-run batch.

System specs: 
Desktop: Intel Core i7 12700K, 64GB RAM, NVIDIA 3080 GPU
Laptop: Macbook Pro M2 13" (2022), 24GB RAM

| Model | Performance on NVIDIA 3080 10GB | Performance on Macbook Pro M2 | Comments |
|:---|:---|:---|:---|
| LLama3.1:8b | 2.41 seconds | 17.65 seconds | The best quality and consistency for the model size |
| Qwen3:8b | 1.90 seconds | 21.13 | Good reasoning ability, but sometimes misses the output format |
| Deepseek-r1 | 1.95 seconds | 18.95 | Frequently misses the output format
| LLama3.2:8b | 1.47 seconds | 7.61 | Very fast, but the quality is not always great |
| gpt-oss:20b | 38 seconds| 25.93 | Much slower on the NVIDIA 3080 due to the model needing more VRAM, and therefore mixed use of GPU and CPU and the overhead of different layers moving in and out of the GPU VRAM, to the point that it runs slows on the desktop than the laptop, which can fit everything in the memory due to the unified memory architecture |

Note that each switching and reloading of a different model has a certain amount of overhead. This also happens to be the reason in the two-pass method, we run one batch of emails on one model, and then switch. Otherwise the overhead of switching can be as high as 150%!

3. What is the experience like On a laptop? Does it slow down my laptop?
While running the inference, the CPU of the (Macbook Pro M2) laptop is relatively untouched, with all the efficiency and performance cores mostly remaining free. The built-in GPU however runs at around 95% utilization and the laptop discharges at a rate of around 32 watts. So the OS remains snappy and doesn't feel slowed down thanks to offlaoding on the GPU, but it will impact the battery consumption. Once the work stops, the laptop goes back to 4~5 watts discharge rate.

Assuming you receive and process 10 new emails per hour, this processing may take about 3~5 minutes on an M2 laptop, so you can expect 5%~8% extra battery draining than your normal use, or remaining 92%~95% the same. From the point of view of slowing the system down, you would barely notice it running in the background, since the CPU is mostly not involved. You may notice that occasionaly your laptop fan starts working for a few minutes, and it may get a bit warmer. 

On a desktop PC with a GPU, you barely notice anything happening, and you could process over 1000 emails per hour!

4. How much RAM do you need?
If you have a GPU with VRAM, the following need to fit in the GPU memory: 
- Quantized model weights. For an 8-billion parameter class model (like llama3.1:8b or qwen3:8b), that's about 4 ~ 4.5GB.
- Context window. The exact value depends on the size of the hidden state of each model (4096 for Llama3.1), the number of transformer layers (e.g. 32 layers), the number of attention heads, and the type of attention heads (MHA, GQA, MQA). For the models we focus on here and for a 4096 token context, they typically require about 2 to 4 GB of additional VRAM. 


5. Two-pass run

You can make the program more conservative, to move only emails where two separate models have concensus on the nature of that email. Here, you can either be very strict and only move emails where both models tag exactly the same, or you can allow some room for approximate behavior using the group option.

`--agree group` compares destination intent (folder group) instead of exact bucket.

As a point of reference, I typically use the program as follows if I want it to be very conservative: 
```
python mailtriage.py triage --account uiuc --mode report --limit 10 --two-pass --secondary-model qwen3:8b --agree group
```

Hoever, in practice, LLama3.1:8b has proven itself to be almost always correct. 

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

Each run writes JSONL in `runs/` by default, which may be useful for debugging or seeing the full LLM reasoning for each email:

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
