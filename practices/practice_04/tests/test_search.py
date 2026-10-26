import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from taskhub.app import app
from taskhub.models import Task
from taskhub.storage import Storage


@pytest.fixture
def catalog(tmp_path: Path):
    tasks = [
        Task.new("Сделать Практику", tags=["учеба"]),
        Task.new("Купить хлеб"),
        Task.new("Hello World"),
        Task.new("Other", tags=["hello"]),
        Task.new("Straße"),
        Task.new("A B"),
        Task.new("AB"),
        Task.new("[demo]"),
        Task.new("demo"),
        Task.new("\u0439"),
        Task.new("\u0438\u0306"),
        Task.new("ёлка"),
        Task.new("Практика первая", due_date="2026-10-26T00:00:00.000000Z",
                 tags=["учеба", "demo"]),
        Task.new("Практика готова", tags=["учеба"]),
        Task.new("Практика другая", tags=["работа"]),
        Task.new("Чтение", tags=["учеба"]),
    ]
    tasks[13].status = "done"
    st = Storage(tmp_path)
    st.save_tasks(tasks)
    return st, tasks


@pytest.mark.parametrize(("query", "indices"), [
    ("прак", [0, 12, 13, 14]),
    ("HELLO", [2]),
    ("STRASSE", [4]),
    (" ", [0, 1, 2, 5, 12, 13, 14]),
    ("[demo]", [7]),
    ("\u0439", [9]),
    ("\u0438\u0306", [10]),
    ("елка", []),
    ("praktika", []),
    ("несуществующее", []),
])
def test_storage_search(catalog, query, indices):
    st, tasks = catalog
    assert st.list_tasks(search=query) == [tasks[i] for i in indices]


def test_storage_search_combines_filters(catalog):
    st, tasks = catalog
    assert st.list_tasks("todo", "учеба", "практика") == [tasks[12]]
    assert st.list_tasks(search="ПРАК", status="todo", tag="учеба") == [
        tasks[0], tasks[12],
    ]


@pytest.mark.parametrize("filters", [{}, {"status": "todo", "tag": "учеба"}])
def test_storage_disabled_search_and_old_calls(catalog, filters):
    st, tasks = catalog
    expected = [tasks[0], tasks[12], tasks[15]] if filters else tasks
    assert st.list_tasks(**filters) == expected
    assert st.list_tasks(search=None, **filters) == expected
    assert st.list_tasks(search="", **filters) == expected
    assert st.list_tasks("todo", "учеба") == [tasks[0], tasks[12], tasks[15]]


def test_storage_search_empty_storage(tmp_path: Path):
    assert Storage(tmp_path).list_tasks(search="прак") == []


@pytest.mark.parametrize(("query", "indices"), [
    ("прак", [0, 12, 13, 14]),
    ("HELLO", [2]),
    ("STRASSE", [4]),
    ("\u0439", [9]),
    ("\u0438\u0306", [10]),
    ("несуществующее", []),
])
def test_cli_search(catalog, monkeypatch, query, indices):
    st, tasks = catalog
    monkeypatch.chdir(st.root)
    result = CliRunner().invoke(app, ["list", "--search", query])
    assert result.exit_code == 0
    assert result.stdout == "".join(
        f"{tasks[i].id} [{tasks[i].status}] {tasks[i].title} "
        f"(due={tasks[i].due_date or '-'} tags={','.join(tasks[i].tags)})\n"
        for i in indices
    )
    assert [line.split()[0] for line in result.stdout.splitlines()] == [
        task.id for task in st.list_tasks(search=query)
    ]


def test_cli_search_combines_filters(catalog, monkeypatch):
    st, tasks = catalog
    monkeypatch.chdir(st.root)
    result = CliRunner().invoke(app, [
        "list", "--search", "практика", "--status", "todo", "--tag", "учеба",
    ])
    assert result.exit_code == 0
    assert result.stdout == (
        f"{tasks[12].id} [todo] Практика первая "
        "(due=2026-10-26T00:00:00.000000Z tags=учеба,demo)\n"
    )
    assert [line.split()[0] for line in result.stdout.splitlines()] == [
        task.id for task in st.list_tasks(status="todo", tag="учеба", search="практика")
    ]


@pytest.mark.parametrize("options", [[], ["--status", "todo", "--tag", "учеба"]])
def test_cli_disabled_search(catalog, monkeypatch, options):
    st, _ = catalog
    monkeypatch.chdir(st.root)
    runner = CliRunner()
    baseline = runner.invoke(app, ["list", *options])
    empty = runner.invoke(app, ["list", *options, "--search", ""])
    assert baseline.exit_code == empty.exit_code == 0
    assert baseline.stdout == empty.stdout


def test_cli_search_missing_value(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(app, ["list", "--search"])
    assert result.exit_code != 0
    assert "requires an argument" in result.output
    assert not (tmp_path / "tasks.json").exists()


@pytest.mark.parametrize("initialized", [False, True])
def test_cli_search_empty_storage(tmp_path: Path, monkeypatch, initialized):
    monkeypatch.chdir(tmp_path)
    st = Storage(tmp_path)
    if initialized:
        st.init()
    result = CliRunner().invoke(app, ["list", "--search", "прак"])
    assert result.exit_code == 0
    assert result.stdout == ""
    assert json.loads(st.path.read_text(encoding="utf-8")) == {"version": 1, "tasks": []}
    assert not st.history_dir.exists()


def test_cli_list_help():
    result = CliRunner().invoke(app, ["list", "--help"], color=False)
    assert result.exit_code == 0
    assert "--search" in result.stdout


@pytest.mark.parametrize("query", ["прак", "", "несуществующее"])
@pytest.mark.parametrize("with_history", [False, True])
@pytest.mark.parametrize("interface", ["storage", "cli"])
def test_search_preserves_stored_state(catalog, monkeypatch, query, with_history, interface):
    st, tasks = catalog
    monkeypatch.chdir(st.root)
    if with_history:
        st.history_dir.mkdir(parents=True)
        for i in range(3):
            snapshot = {"version": 1, "tasks": [t.to_dict() for t in tasks[:i]]}
            (st.history_dir / f"{i}.json").write_text(
                json.dumps(snapshot, ensure_ascii=False), encoding="utf-8",
            )
    original = st.path.read_bytes()
    history = {p.name: p.read_bytes() for p in st.history_dir.glob("*.json")}
    if interface == "cli":
        result = CliRunner().invoke(app, ["list", "--search", query])
        assert result.exit_code == 0
    else:
        st.list_tasks(search=query)
    assert st.path.read_bytes() == original
    assert st.history_dir.exists() == with_history
    assert {p.name: p.read_bytes() for p in st.history_dir.glob("*.json")} == history
