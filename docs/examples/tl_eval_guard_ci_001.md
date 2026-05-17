# TL Eval Guard CI 001

Adds a dedicated GitHub Actions workflow for sanitized TL semantic evals.

## Scope

The workflow runs only `make tl-eval`.

## Triggers

- pull_request
- push on main

## Runtime

- GitHub Actions
- Ubuntu latest
- Python 3.11

## Exclusions

This guard must not start or depend on runtime app, frontend, Railway, Vercel, OpenAI, Ollama, database, SMF, specifications, images, or real codes.
