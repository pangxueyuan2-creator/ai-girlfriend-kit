# AI Girlfriend Kit 💕

**Lightweight, local-first toolkit to build your own AI girlfriend.**

Includes ready-to-use personality templates, long-term memory system, bilingual prompts (English / 中文), and character cards. Designed for privacy — everything can run locally.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- **Personality Templates** — Soft, clingy, teasing, mature sister, cold beauty, etc.
- **Long-term Memory** — Simple file-based memory that actually persists across conversations
- **Bilingual Support** — Full English + 中文 prompts and examples
- **Character Cards** — Ready-to-import format for most frontend UIs
- **Privacy First** — No cloud required, works with local models (Ollama, LM Studio, etc.)
- **Easy to Customize** — Just edit markdown / JSON files

---

## 🚀 Quick Start

1. Clone this repo
2. Pick a personality from `/personalities`
3. Copy the system prompt into your preferred frontend (SillyTavern, OpenWebUI, Cursor, Claude, etc.)
4. Use the memory template in `/memory` to keep conversation history
5. Start chatting

---

## 📁 Project Structure

```
ai-girlfriend-kit/
├── personalities/          # Personality system prompts
│   ├── soft-clingy.md
│   ├── teasing-sister.md
│   ├── mature-gentle.md
│   └── cold-beauty.md
├── memory/                 # Memory system
│   ├── memory-template.md
│   └── how-to-use-memory.md
├── character-cards/        # Importable character cards
│   └── example-cards/
├── prompts/                # Extra useful prompts
│   ├── daily-checkin.md
│   └── emotional-support.md
└── README.md
```

---

## 💡 Recommended Personalities

| Name | Style | Best For |
|------|-------|----------|
| Soft Clingy | 软萌、粘人、会撒娇 | Daily companionship |
| Teasing Sister | 会欺负你、又宠你的姐姐 | Playful & slightly dominant |
| Mature Gentle | 温柔成熟、会哄人 | Emotional support |
| Cold Beauty | 表面冷淡、内心在意 | Slow-burn tension |

All personalities come in both **English** and **中文** versions.

---

## 🧠 Memory System

This kit uses a simple but effective long-term memory approach:

- Important facts about the user are stored in a structured markdown file
- The AI is instructed to read and update this file
- Works surprisingly well with most modern models

See `/memory/how-to-use-memory.md` for detailed instructions.

---

## 🛠️ Compatible With

- SillyTavern
- OpenWebUI
- LM Studio + any frontend
- Ollama
- Cursor / Claude Projects
- Most custom agent frameworks

---

## ❤️ Philosophy

This project is for people who want a **personal, private AI companion** without sending everything to the cloud.  
Customize her personality, keep your own memories, and make her truly yours.

---

## License

MIT — free to use, modify, and share.

---

Made with care. Enjoy your new companion.
