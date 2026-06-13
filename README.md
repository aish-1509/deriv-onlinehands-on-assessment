# Deriv Online Hands-on Assessment

Starter repository for the Deriv AI hands-on assessment using Python, FastAPI,
the Anthropic SDK, and a simple in-memory store.

## Pre-assessment setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create the local environment file:

   ```bash
   cp .env.example .env
   ```

4. Add a newly generated Anthropic API key to `.env`. Never commit `.env` or
   paste the key into source code, terminal recordings, chat, or screenshots.

5. Verify the development tools:

   ```bash
   claude --version
   python -c "import anthropic, fastapi, httpx, uvicorn, dotenv; print('Python dependencies ready')"
   git push
   ```

## 60-minute plan

| Time | Action |
| --- | --- |
| 0-5 min | Read the problem aloud, restate it, and describe the architecture. |
| 5-10 min | Use Claude Code to scaffold the project and explain the prompt. |
| 10-35 min | Build the core feature, reviewing each generated function aloud. |
| 35-45 min | Test normal and failure paths, then fix discovered issues. |
| 45-55 min | Finish the README: what it does, how to run it, and next steps. |
| 55-58 min | Commit and push the submission. |
| 58-60 min | Confirm the GitHub repository is live and submit its URL. |

## Narration prompts

- "I'm asking Claude to scaffold the API from the requirements."
- "It generated this structure; I'm checking whether the data flow and error
  handling match the prompt."
- "I'm testing the happy path first, then malformed input and upstream API
  failure."
- "This is deliberately in memory for the time box; I would add persistence,
  authentication, observability, and broader tests next."

## Relevant experience

- Built a local LLM chatbot with Ollama at Panasonic.
- Evaluated multi-agent and model workflows involving Wan 2.2, SlimInfer, and
  CODI.
- Built FastAPI and REST API services across multiple internships.
- GitHub: [aish-1509](https://github.com/aish-1509)

## Submission repository

https://github.com/aish-1509/deriv-onlinehands-on-assessment
