# BusterCall-AI

**BusterCall-AI** is a **FastAPI** web API with a **One Piece** theme — it evaluates the threat level and assigns bounties (in Berries) to pirate characters based on their Haki, Devil Fruit, and achievements, powered by a language model (LLM) via OpenRouter.

## Features

- **Bounty Evaluation**: Submit a pirate's info (name, crew, devil fruit, haki, achievements) and let the AI determine the bounty (in Berries), threat level, and reasoning.
- **Devil Fruit Lookup**: Query detailed information about a Devil Fruit from the One Piece API.
- **User Management**: Create and fetch user information, persisted with SQLAlchemy + SQLite.

## Architecture

| File | Description |
|------|-------------|
| `main.py` | FastAPI app definition and API endpoints |
| `schemas.py` | Pydantic models (input/output validation) |
| `models.py` | SQLAlchemy ORM models (`User`) |
| `db.py` | SQLite connection setup, engine, and session |
| `bounty_evaluator_prompt.py` | System prompt for the AI bounty evaluator, following One Piece lore |
| `fruit.py` | Script for exploring the Devil Fruit API |

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

- Swagger UI docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

> Note: On startup, the database tables (`pirate.db`) are created automatically by `Base.metadata.create_all` in `main.py`.

## API Endpoints

### 1. Create user

`POST /api/users`

Body:
```json
{
  "user_name": "luffy",
  "email": "luffy@strawhat.com"
}
```

### 2. Get user

`GET /api/users/{id}`

### 3. Evaluate pirate bounty

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
- [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite
- [Pydantic](https://docs.pydantic.dev/latest/)
- [OpenRouter API](https://openrouter.ai/) for the LLM
- [One Piece API](https://api-onepiece.com) for Devil Fruit data

## Author

- ducanhlee633-crypto — ducanhlee633@gmail.com