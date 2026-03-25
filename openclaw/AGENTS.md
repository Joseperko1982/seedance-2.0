# Seedance 2.0 — OpenClaw Multi-Agent Team

> Configuration: [`openclaw.json`](./openclaw.json) | Workflow: [`workflows/production-pipeline.yaml`](./workflows/production-pipeline.yaml)

## Architecture

Each agent has its own **isolated workspace**, **persistent memory**, and **session store**. Messages are routed via **Telegram threads** — one thread per agent in a single Telegram group with topics enabled.

```
~/.openclaw/
├── workspace-seedance/
│   ├── director/          # Director's workspace (SOUL.md, MEMORY.md, USER.md)
│   ├── promptsmith/       # Promptsmith's workspace
│   ├── cinematographer/   # Cinematographer's workspace
│   ├── casting/           # Casting's workspace
│   ├── mistake/           # Mistake's workspace (+ assets gallery)
│   ├── sound-designer/    # Sound Designer's workspace
│   └── producer/          # Producer's workspace
├── agents/
│   ├── director/agent/    # Director's auth & config state
│   ├── director/sessions/ # Director's chat history
│   ├── promptsmith/...
│   └── ...
```

## Agents

| Agent | Model | Role | Telegram Thread | Tools |
|---|---|---|---|---|
| **Director** | Opus 4.6 | Creative lead & orchestrator | `#director` | read, write, exec |
| **Promptsmith** | Sonnet 4.6 | Prompt engineering & anti-slop | `#promptsmith` | read, write |
| **Cinematographer** | Sonnet 4.6 | Camera, lighting, VFX | `#cinematographer` | read |
| **Casting** | Sonnet 4.6 | Characters, motion, style | `#casting` | read |
| **Mistake** | Sonnet 4.6 | QA, copyright, assets gallery | `#mistake` | read, write, exec |
| **Sound Designer** | Sonnet 4.6 | Audio, lip-sync, SFX | `#sound-designer` | read |
| **Producer** | Sonnet 4.6 | API execution, pipeline | `#producer` | read, write, exec |

## Per-Agent Isolation

Each agent maintains:
- **SOUL.md** — Persona, skills, responsibilities, output format
- **MEMORY.md** — Persistent memory across sessions (patterns, preferences, logs)
- **USER.md** — User profile (Director only — shared context)
- **Isolated sessions** — Chat history at `~/.openclaw/agents/<id>/sessions`
- **Scoped tools** — Only the tools each agent needs (least privilege)

## Telegram Thread Routing

Set up a Telegram group with **topics enabled**, then create 7 threads:

| Thread | Agent | Purpose |
|---|---|---|
| Director | `director` | Creative interviews, project kickoff |
| Promptsmith | `promptsmith` | Prompt review, compilation, anti-slop |
| Cinematographer | `cinematographer` | Camera plans, lighting, VFX |
| Casting | `casting` | Character sheets, @Tag assignments |
| Mistake | `mistake` | QA reviews, asset gallery, copyright |
| Sound Designer | `sound-designer` | Audio design, lip-sync config |
| Producer | `producer` | API jobs, status, pipeline |

**Routing rules** (in priority order):
1. Message in a named thread → routes to the matching agent
2. Unthreaded message → routes to Director (default)
3. Director can delegate by mentioning `@agentname` in the pipeline

### Setup

1. Create a Telegram bot via `@BotFather`
2. Create a group, enable topics, add the bot as admin
3. Create 7 topic threads (one per agent)
4. Copy thread IDs to `.env` (see `.env.example`)
5. Run `openclaw start` with the config

## Pipeline Flow

```
User message (any thread)
    ↓
Director (interview & brief)
    ↓
┌───────────────────────────────────────┐
│  Parallel Specialist Phase            │
│  ┌─────────────┐ ┌─────────────────┐  │
│  │ Promptsmith  │ │ Cinematographer │  │
│  └─────────────┘ └─────────────────┘  │
│  ┌─────────────┐ ┌─────────────────┐  │
│  │ Casting      │ │ Sound Designer  │  │
│  └─────────────┘ └─────────────────┘  │
└───────────────────────────────────────┘
    ↓
Promptsmith (assembly)
    ↓
Mistake (QA gate — MUST PASS)
    ↓
Producer (API submission)
    ↓
Output video + gallery registration
```

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/Emily2040/seedance-2.0
cd seedance-2.0/openclaw

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys and thread IDs

# 3. Start the multi-agent team
openclaw start --config openclaw.json

# 4. Send a message in your Telegram group's Director thread
# The team takes it from there!
```
