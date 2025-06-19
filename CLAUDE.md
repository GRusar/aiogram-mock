# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

aiogram_mock is a Python library for testing aiogram (Telegram Bot API framework) applications. It provides a mocking system that simulates Telegram bot interactions without requiring actual Telegram API calls.

## Development Setup

### Virtual Environment Setup
```bash
uv venv                        # Create virtual environment
source .venv/bin/activate      # Activate virtual environment (Linux/Mac)
# or .venv\Scripts\activate    # Activate virtual environment (Windows)
```

### Dependency Installation
```bash
uv pip install -e .           # Install package in development mode
uv pip install -r requirements.txt  # Install development dependencies
```

## Development Commands

### Testing
```bash
pytest examples/test_basic.py  # Run the basic example test
pytest                         # Run all tests
```

### Linting and Type Checking
```bash
make lint                      # Run all linting (flake8, isort, mypy)
make lint-flake8              # Run flake8 only
make lint-isort               # Run isort only
make lint-mypy                # Run mypy only
```

## Architecture

The library consists of three main components:

### 1. TgState (src/aiogram_mock/tg_state.py)
Central state management that tracks:
- Chat histories and messages
- User states and reply markups
- Callback query answers
- File uploads (photos, documents)
- Update IDs and message IDs

### 2. MockedSession (src/aiogram_mock/mocked_session.py)
Replaces aiogram's HTTP session to intercept and mock Telegram API calls:
- Handles SendMessage, SendPhoto, EditMessage operations
- Manages AnswerCallbackQuery responses
- Validates message constraints (e.g., callback_data length ≤ 64 chars)

### 3. TgControl (src/aiogram_mock/tg_control.py)
Provides the testing interface:
- `TgControl`: Base class for sending messages and simulating user interactions
- `PrivateChatTgControl`: Specialized for private chat testing with convenience methods

### 4. Facade Factory (src/aiogram_mock/facade_factory.py)
Context manager `private_chat_tg_control()` that:
- Creates mock users and chats
- Patches the bot's session with MockedSession
- Returns PrivateChatTgControl instance for testing

## Testing Patterns

The library supports testing bot handlers by:
1. Creating a bot and dispatcher with registered handlers
2. Using `private_chat_tg_control()` context manager
3. Sending messages with `tg_control.send()`
4. Checking responses via `tg_control.last_message`
5. Simulating button clicks with `tg_control.click()`

## Configuration

- Python 3.8+ required
- Dependencies: aiogram>=3.0.0b6
- Test dependencies: pytest, pytest-asyncio
- Development tools: mypy, flake8, isort