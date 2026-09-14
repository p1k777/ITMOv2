# Результат по master prompt

summary: В PR добавлен эндпоинт POST /api/reviews и метод ReviewService.review, который формирует prompt с полным diff и передаёт его во внешний LLM. Ответ возвращается как {"comment": string}. Нарушены правила SEC-1, OUT-1 и REL-1; отсутствует проверка API-1.

risks:
- file: app/review_service.py
  line: 20
  evidence: "prompt = f\"Review this pull request and find problems:\n{diff}\""
  risk: Отправка полного diff во внешний LLM без редактирования секретов (SEC-1)
  risk_level: High
- file: app/review_service.py
  line: 22
  evidence: "return {\"comment\": answer}"
  risk: Формат ответа не соответствует OUT-1 (нет summary/risks/checks, нет ограничений по числу рисков)
  risk_level: High
- file: app/review_service.py
  line: 21
  evidence: "answer = self.llm.generate(prompt)" без таймаута/обработки ошибок
  risk: Нет таймаута 10с и контролируемой обработки ошибок внешнего вызова (REL-1)
  risk_level: Medium

checks:
- Юнит: проверка редакции секретов (SEC-1) — вход с тестовым token/ключом, в сформированном prompt вместо значений только [REDACTED]
- Интеграция: симуляция таймаута LLM >10с — сервис возвращает контролируемый ответ без подвисания (REL-1)
- E2E: diff длиной 20500 символов — HTTP 413 (API-1); diff 19500 символов — 200
- Контракт: ответ строго соответствует OUT-1 — summary:string, risks<=3 с file/line/evidence/risk, checks:string[]
- Наблюдаемость: в логах только request_id, длительность, статус; отсутствуют содержимое diff и ответ модели (OBS-1)
