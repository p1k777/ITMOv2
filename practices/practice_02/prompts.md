# Журнал экспериментов Практики 2

- Выбранный слабый артефакт Практики 1:
practices/practice_01/project_management.md
- Что в нём нужно улучшить:
неполнота правил (нет QA-1/OBS-1/SCOPE-1), непроверяемые проверки, неясные зависимости, нереалистичная диаграмма, некорректная ссылка на prompts
- Как поймём, что изменение полезно:
есть трассировка на SEC-1/API-1/REL-1/OUT-1/QA-1/OBS-1, проверки измеримы (unit/integration/e2e/contract с условиями и исходами), диаграмма согласована с зависимостями, ссылка P2-CoVe-01 согласована
- Идентификатор: P2-CoVe-01

| Техника | Файл эксперимента | Изменённый файл Практики 1 | Конкретное изменение | Проверка | Что отклонили |
|---|---|---|---|---|---|
| Few-shot | [`few_shot/experiment.md`](few_shot/experiment.md) |  |  |  |  |
| R.C.T.F. | [`rctf/experiment.md`](rctf/experiment.md) |  |  |  |  |
| Chain of Verification | [`chain_of_verification/experiment.md`](chain_of_verification/experiment.md) | [`practice_02/chain_of_verification/project_management_fixed.md`](chain_of_verification/project_management_fixed.md) | Конкретизация инкрементов, проверок и зависимостей под SEC-1/API-1/REL-1/OUT-1/QA-1/OBS-1; обновление Ганта и AI-раздела | Контрактные/интеграционные тесты сформулированы; критерии приёмки соответствуют OUT-1/REL-1/SEC-1/API-1 | Отклонены нефокусные улучшения вне первого сценария |
| Tree of Thoughts | [`tree_of_thoughts/experiment.md`](tree_of_thoughts/experiment.md) |  |  |  |  |
| RAG | [`rag/experiment.md`](rag/experiment.md) |  |  |  |  |
| ReAct | [`react/experiment.md`](react/experiment.md) |  |  |  |  |

## Независимое ревью

| Замечание другой команды | Где исправили | Evidence |
|---|---|---|
| Двусмысленность |  |  |
| Непроверяемое требование |  |  |
| Пропущенный риск или источник |  |  |
