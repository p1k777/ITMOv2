from pathlib import Path

from taskhub.storage import Storage
from taskhub.models import Task


def test_storage_add_list_done(tmp_path: Path):
    st = Storage(tmp_path)
    st.init()
    t = Task.new("Test task", tags=["x"])
    st.add_task(t)

    tasks = st.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Test task"
    assert tasks[0].status == "todo"

    st.mark_done(t.id)
    tasks = st.list_tasks(status="done")
    assert len(tasks) == 1
    assert tasks[0].status == "done"
