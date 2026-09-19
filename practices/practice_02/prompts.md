# Журнал экспериментов Практики 2

- Выбранный слабый артефакт Практики 1:
practices/practice_01/project_management.md
- Что в нём нужно улучшить:
неполнота правил (нет QA-1/OBS-1/SCOPE-1), непроверяемые проверки, неясные зависимости, нереалистичная диаграмма, некорректная ссылка на prompts
- Как поймём, что изменение полезно:
есть трассировка на SEC-1/API-1/REL-1/OUT-1/QA-1/OBS-1, проверки измеримы (unit/integration/e2e/contract с условиями и исходами), диаграмма согласована с зависимостями, ссылка на строку техники в prompts.md согласована

| Техника | Файл эксперимента | Изменённый файл Практики 1 | Конкретное изменение | Проверка | Что отклонили |
|---|---|---|---|---|---|
| Few-shot | [`few_shot/experiment.md`](few_shot/experiment.md) | [`practice_02/few_shot/project_management_fixed.md`](few_shot/project_management_fixed.md) | Трассировка на SEC-1/API-1/REL-1/OUT-1/QA-1/OBS-1; измеримые проверки; согласованные зависимости и Гант; корректный раздел AI | Проверки (unit/integration/e2e/contract) сформулированы и трассируются к правилам; диаграмма соответствует зависимостям | Нефокусные улучшения вне первого сценария |
| R.C.T.F. | [`rctf/experiment.md`](rctf/experiment.md) | [`practice_02/rctf/project_management_fixed.md`](rctf/project_management_fixed.md) | Трассировка на SEC-1/API-1/REL-1/OUT-1/QA-1/OBS-1; измеримые проверки; согласованные зависимости и Гант; корректный раздел AI | Проверки (unit/integration/e2e/contract) сформулированы и трассируются к правилам; диаграмма/Гант соответствуют зависимостям | Нефокусные улучшения вне первого сценария |
| Chain of Verification | [`chain_of_verification/experiment.md`](chain_of_verification/experiment.md) | [`practice_02/chain_of_verification/project_management_fixed.md`](chain_of_verification/project_management_fixed.md) | Конкретизация инкрементов, проверок и зависимостей под SEC-1/API-1/REL-1/OUT-1/QA-1/OBS-1; обновление Ганта и AI-раздела | Контрактные/интеграционные тесты сформулированы; критерии приёмки соответствуют OUT-1/REL-1/SEC-1/API-1 | Отклонены нефокусные улучшения вне первого сценария |
| Tree of Thoughts | [`tree_of_thoughts/experiment.md`](tree_of_thoughts/experiment.md) | [`practice_02/tree_of_thoughts/project_management_fixed.md`](tree_of_thoughts/project_management_fixed.md) | Трассировка на SEC-1/API-1/REL-1/OUT-1/QA-1/OBS-1/SCOPE-1; измеримые проверки; согласованные зависимости и Гант; корректный раздел AI (Tree of Thoughts) | Проверки (unit/integration/e2e/contract) сформулированы и трассируются к правилам; диаграмма/Гант соответствуют зависимостям | Нефокусные улучшения вне первого сценария |
| RAG | [`rag/experiment.md`](rag/experiment.md) | [`practice_02/rag/project_management_fixed.md`](rag/project_management_fixed.md) | Трассировка на SEC-1/API-1/REL-1/OUT-1/QA-1/OBS-1; измеримые проверки; согласованные зависимости и Гант; корректный раздел AI | Проверки (unit/integration/e2e/contract) сформулированы и трассируются к правилам; цитирование `[FILE:lines]`; диаграмма соответствует зависимостям | Нефокусные улучшения вне первого сценария; предположения вне `CASE.md`/`CONTEXT.md` без подтверждения |
| ReAct | [`react/experiment.md`](react/experiment.md) | [`practice_02/react/project_management_fixed.md`](react/project_management_fixed.md) | Трассировка на SEC-1/API-1/REL-1/OUT-1/QA-1/OBS-1/SCOPE-1; измеримые проверки; согласованные зависимости и Гант; корректный раздел AI (ReAct) | Проверки (unit/integration/e2e/contract) сформулированы и трассируются к правилам; диаграмма/Гант соответствуют зависимостям | Нефокусные улучшения вне первого сценария |

## Независимое ревью

| Замечание другой команды | Где исправили | Evidence |
|---|---|---|
| Двусмысленность |  |  |
| Непроверяемое требование |  |  |
| Пропущенный риск или источник |  |  |
