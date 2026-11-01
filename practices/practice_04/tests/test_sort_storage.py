import pytest
from taskhub.storage import Storage
from taskhub.models import Task


def _make_task(
    title: str,
    status: str = "todo",
    due_date: str | None = None,
    tags: list[str] | None = None,
    created_at: str = "2026-01-01T00:00:00.000000Z",
) -> Task:
    t = Task.new(title, due_date=due_date, tags=tags)
    t.status = status
    t.created_at = created_at
    return t


@pytest.fixture
def storage(tmp_path):
    # Создаём набор задач с разными полями для сортировки
    tasks = [
        _make_task(
            "Alpha", status="todo", due_date=None, tags=[],
            created_at="2026-01-01T00:00:00.000000Z"
        ),
        _make_task(
            "Bravo", status="done",
            due_date="2026-02-01T00:00:00.000000Z",
            tags=["b"], created_at="2026-01-02T00:00:00.000000Z"
        ),
        _make_task(
            "charlie", status="todo",
            due_date="2026-01-15T00:00:00.000000Z",
            tags=["a"], created_at="2026-01-03T00:00:00.000000Z"
        ),
        _make_task(
            "Delta", status="done", due_date=None, tags=[],
            created_at="2026-01-04T00:00:00.000000Z"
        ),
        _make_task(
            "Эхо", status="todo",
            due_date="2026-01-10T00:00:00.000000Z",
            tags=["c"], created_at="2026-01-05T00:00:00.000000Z"
        ),
    ]
    st = Storage(tmp_path)
    st.init()
    st.save_tasks(tasks)
    return st


def _titles(tasks):
    return [t.title for t in tasks]


def test_sort_by_title_asc(storage):
    res = storage.list_tasks(sort_by="title", sort_order="asc")
    assert _titles(res) == ["Alpha", "Bravo", "charlie", "Delta", "Эхо"]


def test_sort_by_title_desc(storage):
    res = storage.list_tasks(sort_by="title", sort_order="desc")
    assert _titles(res) == ["Эхо", "Delta", "charlie", "Bravo", "Alpha"]


def test_sort_by_status_asc(storage):
    # todo before done, стабильный порядок внутри групп
    res = storage.list_tasks(sort_by="status", sort_order="asc")
    assert _titles(res) == ["Alpha", "charlie", "Эхо", "Bravo", "Delta"]


def test_sort_by_status_desc(storage):
    res = storage.list_tasks(sort_by="status", sort_order="desc")
    assert _titles(res) == ["Bravo", "Delta", "Alpha", "charlie", "Эхо"]


def test_sort_by_due_date_asc(storage):
    res = storage.list_tasks(sort_by="due_date", sort_order="asc")
    # задачи без due_date идут в конец
    assert _titles(res) == ["Эхо", "charlie", "Bravo", "Alpha", "Delta"]


def test_sort_by_due_date_desc(storage):
    res = storage.list_tasks(sort_by="due_date", sort_order="desc")
    # задачи без due_date идут в начало
    assert _titles(res) == ["Alpha", "Delta", "Bravo", "charlie", "Эхо"]


def test_sort_by_created_at_asc(storage):
    res = storage.list_tasks(sort_by="created_at", sort_order="asc")
    # оригинальный порядок уже по возрастанию created_at
    assert _titles(res) == ["Alpha", "Bravo", "charlie", "Delta", "Эхо"]


def test_sort_by_created_at_desc(storage):
    res = storage.list_tasks(sort_by="created_at", sort_order="desc")
    assert _titles(res) == ["Эхо", "Delta", "charlie", "Bravo", "Alpha"]


def test_sort_by_tags_asc(storage):
    res = storage.list_tasks(sort_by="tags", sort_order="asc")
    # без тегов в конец, сортировка по первому тегу case‑insensitive
    assert _titles(res) == ["charlie", "Bravo", "Эхо", "Alpha", "Delta"]


def test_sort_by_tags_desc(storage):
    res = storage.list_tasks(sort_by="tags", sort_order="desc")
    # без тегов в начале, потом теги в обратном порядке
    assert _titles(res) == ["Alpha", "Delta", "Эхо", "Bravo", "charlie"]


def test_sort_no_params_returns_original_order(storage):
    original = storage.list_tasks()
    sorted_res = storage.list_tasks(sort_by="title", sort_order="asc")
    # после сортировки оригинальный порядок не меняется
    assert storage.list_tasks() == original


def test_invalid_sort_by_raises(storage):
    with pytest.raises(ValueError):
        storage.list_tasks(sort_by="unknown")


def test_invalid_sort_order_raises(storage):
    with pytest.raises(ValueError):
        storage.list_tasks(sort_by="title", sort_order="up")
