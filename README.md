# BusterCall-AI

**BusterCall-AI** is a **FastAPI** web app with a **One Piece** theme — it evaluates the threat level and assigns bounties (in Berries) to pirate characters based on their Haki, Devil Fruit, and achievements, and simulates battles between them, all powered by a language model (LLM) via OpenRouter.

It ships with both a REST API and a retro-style One Piece web UI (Jinja2 templates).

## Features

- **Bounty Evaluation**: Submit a pirate's info (name, crew, devil fruit, haki, achievements) and let the AI determine the bounty (in Berries), threat level, and reasoning.
- **Battle Simulator**: Pit two pirate characters against each other in a chosen location — the AI referee produces a pre-match analysis, a 3-turn combat log with stamina tracking, and a winner.
- **Devil Fruit Lookup**: Query detailed information about a Devil Fruit from the One Piece API.
- **User Management**: Full CRUD for users (create, read, update fully/partially, delete, list), persisted with SQLAlchemy + SQLite.
- **Web UI**: A themed frontend (Home, Bounty Assessor, Battle Simulator, Encyclopedia, Crew Registry) served by Jinja2 templates.

## Architecture

| File | Description |
|------|-------------|
| `main.py` | FastAPI app definition, API endpoints, UI routes, and LLM client |
| `schemas.py` | Pydantic models (input/output validation) |
| `models.py` | SQLAlchemy ORM models (`User`) |
| `db.py` | SQLite connection setup, engine, and session |
| `bounty_evaluator_prompt.py` | System prompt for the AI bounty evaluator, following One Piece lore |
| `battle_simulator_prompt.py` | System prompt for the AI battle referee (JSON combat log output) |
| `fruit.py` | Script for exploring the Devil Fruit API |
| `templates/` | Jinja2 HTML templates for the web UI |
| `static/` | Static assets (CSS) for the web UI |

## Installation

Requirements: **Python >= 3.14** and [uv](https://docs.astral.sh/uv/).

```bash
# Clone the repo and install dependencies
uv sync

# Configure the API key
cp .env.example .env   # if present, or create your own .env file
```

In the `.env` file, set:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Running the server

```bash
uv run uvicorn main:app --reload
```

Then open:

- Web UI: http://localhost:8000
- Swagger UI docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

> Note: On startup, the database tables (`pirate.db`) are created automatically by `Base.metadata.create_all` in `main.py`.

## Web UI Pages

| Route | Page |
|-------|------|
| `/` | Home |
| `/bounty` | Bounty Assessor — form to evaluate a pirate's bounty |
| `/battle` | Battle Simulator — set up a clash between two characters |
| `/encyclopedia` | Devil Fruit encyclopedia lookup |
| `/crew` | Crew Registry — register & manage users (contacts) |

## API Endpoints

### 1. User management

**Create user**

`POST /api/users`

Body:
```json
{
  "user_name": "luffy",
  "email": "luffy@strawhat.com"
}
```

**Get user**

`GET /api/users/{id}`

**List all users**

`GET /api/users`

**Update user fully (PUT)**

`PUT /api/users/{id}`

Body:
```json
{
  "id": 1,
  "user_name": "luffy",
  "email": "luffy@strawhat.com"
}
```

**Update user partially (PATCH)**

`PATCH /api/users/{id}`

Body (only the fields to change):
```json
{
  "email": "monkey.luffy@strawhat.com"
}
```

**Delete user**

`DELETE /api/users/{id}`

### 2. Evaluate pirate bounty

`POST /api/v1/bounty/assess`

Body:
```json
{
  "name": "Monkey D. Luffy",
  "crew_name": "Straw Hat Pirates",
  "devil_fruit": "Hito Hito no Mi, Model: Nika",
  "observation_haki": true,
  "armament_haki": true,
  "conqueror_haki": true,
  "achievement": "Defeated Kaido and became Yonko."
}
```

Response:
```json
{
  "bounty": 3000000000,
  "threat_level": "SS",
  "reasoning": "Yonko-level threat with Conqueror Haki..."
}
```

- AI model used: `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` (free on OpenRouter).
- `threat_level` accepts: `D`, `A`, `B`, `C`, `S`, `SS`, `>` (max 3 characters).

### 3. Simulate a battle

`POST /api/v1/battle/simulate`

Body (two pirate profiles — same schema as the bounty assessor — plus a location):
```json
{
  "character_1": {
    "name": "Monkey D. Luffy",
    "crew_name": "Straw Hat Pirates",
    "devil_fruit": "Hito Hito no Mi, Model: Nika",
    "observation_haki": true,
    "armament_haki": true,
    "conqueror_haki": true,
    "achievement": "Defeated Kaido and became Yonko."
  },
  "character_2": {
    "name": "Charlotte Katakuri",
    "crew_name": "Big Mom Pirates",
    "devil_fruit": "Mochi Mochi no Mi",
    "observation_haki": true,
    "armament_haki": true,
    "conqueror_haki": false,
    "achievement": "Undefeated for decades in the Whole Cake Island territory."
  },
  "location": "Whole Cake Island"
}
```

Response (the AI referee's JSON):
```json
{
  "pre_match_analysis": {
    "character_a_advantages": ["Superior strength and durability", "Advanced Conqueror Haki"],
    "character_b_advantages": ["Advanced Observation Haki sees the future", "Awakened Paramecia powers"],
    "environmental_impact": "The homies and terrain of Whole Cake Island favor the defender..."
  },
  "combat_log": [
    {
      "turn": 1,
      "phase": "Opening Phase",
      "description": "The two clash head-on, shaking the island...",
      "character_a_stamina_left": 95,
      "character_b_stamina_left": 92
    }
  ],
  "result": {
    "winner": "Monkey D. Luffy",
    "winning_condition": "A Gear 5 finishing blow overwhelmed Katakuri's future sight...",
    "difficulty": "Extreme_Diff"
  }
}
```

### 4. Look up Devil Fruit

`POST /api/v1/encyclopedia/query`

Body:
```json
{
  "devil_fruit": "Gomu Gomu no Mi"
}
```

Returns the matching Devil Fruit info from [One Piece API](https://api-onepiece.com).

## Bounty evaluation criteria

According to `bounty_evaluator_prompt.py`, the AI estimates bounties based on:

- **East Blue rookie**: 1,000,000 – 30,000,000 Berries
- **Supernova level**: 100,000,000 – 400,000,000 Berries
- **Shichibukai / New World Veteran**: 800,000,000 – 1,500,000,000 Berries
- **Yonko level**: 3,000,000,000+ Berries
- **Bonuses**: Observation Haki (+50M–100M), Armament Haki (+100M–200M), Conqueror Haki (+500M–1B), Ancient/Mythical Zoan & Logia (+200M–500M).
- **Attacking Celestial Dragons / destroying Marine bases / knowing Void Century secrets**: massively inflates the bounty.

## Tech stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [Jinja2](https://jinja.palletsprojects.com/) templates + static CSS for the web UI
- [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite
- [Pydantic](https://docs.pydantic.dev/latest/)
- [OpenRouter API](https://openrouter.ai/) for the LLM
- [One Piece API](https://api-onepiece.com) for Devil Fruit data

## Author

- ducanhlee633-crypto — ducanhlee633@gmail.com