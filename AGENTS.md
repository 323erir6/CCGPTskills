# Repository engineering rules / Правила разработки

## English

This is a CC:Tweaked Lua reference library for humans and automated coding tools.

1. Read the relevant documentation and existing implementation before modifying a file.
2. Verify built-in APIs against https://tweaked.cc/ and modded APIs against the installed mod version.
3. Never invent a peripheral method, return-field name, rotation convention or hardware range.
4. Prefer small, reusable programs with explicit startup validation and helpful error messages.
5. Keep Lua comments bilingual: `-- EN: ...` immediately followed by `-- RU: ...` for explanatory comments.
6. Maintain equivalent English and Russian documentation where a bilingual pair exists.
7. Clearly label samples requiring third-party mods, unsupported versions or manual integration.
8. Use timeouts, bounded loops, defensive network decoding and safe shutdown for outputs.
9. Never claim that code was executed in Minecraft without real execution evidence.
10. Do not add personal details, conversational text, credentials or private project state.

## Русский

Это справочная библиотека CC:Tweaked Lua для людей и автоматических инструментов разработки.

1. Перед изменениями изучайте соответствующую документацию и текущий код.
2. Проверяйте стандартные API через https://tweaked.cc/, а сторонние — по установленной версии мода.
3. Не выдумывайте методы периферии, поля результатов, соглашения о вращении и пределы приводов.
4. Пишите небольшие повторно используемые программы с проверками и понятными ошибками.
5. Поясняющие комментарии Lua дублируйте: `-- EN: ...` и следующей строкой `-- RU: ...`.
6. Поддерживайте эквивалентные английские и русские документы.
7. Отдельно отмечайте необходимость сторонних модов и ручной настройки.
8. Используйте тайм-ауты, ограниченные циклы, проверку сетевого ввода и безопасное отключение выходов.
9. Не объявляйте запуск в Minecraft успешным без реального подтверждения.
10. Не добавляйте персональные сведения, переписку, секреты или внутреннее состояние частных проектов.
