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

## Telegram Forum Topic Routing

Each agent is bound to a **Telegram forum topic** (thread) in a single supergroup. OpenClaw's native `groups.topics` config maps topic IDs directly to agents — each topic gets its own session key (`:topic:<threadId>`) for full memory isolation.

| Topic | Agent | Purpose |
|---|---|---|
| Director | `director` | Creative interviews, project kickoff |
| Promptsmith | `promptsmith` | Prompt review, compilation, anti-slop |
| Cinematographer | `cinematographer` | Camera plans, lighting, VFX |
| Casting | `casting` | Character sheets, @Tag assignments |
| Mistake | `mistake` | QA reviews, asset gallery, copyright |
| Sound Designer | `sound-designer` | Audio design, lip-sync config |
| Producer | `producer` | API jobs, status, pipeline |

**Routing rules** (OpenClaw priority):
1. Message in a forum topic → routes to the agent bound to that topic ID
2. Topic entries inherit group settings unless overridden (`requireMention`, `allowFrom`, `skills`)
3. DMs and unthreaded messages → fallback to Director (default agent)
4. Session keys are topic-scoped: `session:topic:5` ≠ `session:topic:7`

### Setup

1. Create a Telegram bot via `@BotFather` → get bot token
2. Create a **supergroup**, enable **Topics** (forum mode), add bot as admin
3. Create 7 topics (Director, Promptsmith, Cinematographer, Casting, Mistake, Sound, Producer)
4. Get IDs: add `@getidsbot` → forward a message from each topic to get its thread ID
5. Get group ID: the supergroup ID (format: `-100xxxxxxxxxx`)
6. Fill in `.env` (see `.env.example`) with bot token, group ID, and topic IDs
7. Run `openclaw start --config openclaw.json`

### Memory Model

Each agent maintains persistent memory across sessions:

| Layer | Location | Lifetime | Loaded |
|---|---|---|---|
| Session context | In-memory transcript | Resets daily (4 AM) | Always |
| Daily logs | `memory/YYYY-MM-DD.md` | Permanent | Today + yesterday |
| Long-term | `MEMORY.md` | Permanent | DM/private sessions |
| Semantic search | Vector index over memory files | Rebuilt on demand | On `memory_search` |

Before context compaction, OpenClaw triggers a **pre-compaction flush** — the agent writes important info to `MEMORY.md` before the window is compressed.

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
