# Quickstart: Сортировка задач (backend)

**Date**: 2026-11-01
**Feature**: specs/001-tasks-sort-back/spec.md

## Предварительные требования

- Python 3.11+
- `pytest` установлен
- Репозиторий TaskHub доступен

## Настройка

```bash
cd /Users/igor/Documents/vibe/ITMOv2/practices/practice_04
export PYTHONPATH=src
python -m venv .venv
source .venv/bin/activate
pip install pytest typer
```

## Запуск тестов

```bash
pytest -q tests/test_storage.py
```

## Проверка через CLI

```bash
python -m taskhub.app init
python -m taskhub.app add "Покупка" --tag еда
python -m taskhub.app add "Работа" --tag работа
python -m taskhub.app list
```

## Проверка через GUI

```bash
python -m taskhub.gui
```

Откройте TaskHub, кликните на заголовке колонки — проверьте сортировку.

## Проверка через MCP

```bash
# Используйте инструменты MCP-сервера TaskHub
```

## Ожидаемые результаты

| Действие | Ожидаемый результат |
|----------|---------------------|
| `list` без сортировки | Порядок из файла |
| Клик "Название" в GUI | Задачи по алфавиту, стрелка ▲ |
| Клик "Название" снова | Обратный алфавиту, стрелка ▼ |
| Клик "Название" третий раз | Без сортировки, стрелка исчезла |
| Клик "Статус" | "todo" перед "done" |
| Применить фильтр | Сортировка сохраняется |
| Сбросить фильтры | Сортировка сохраняется |