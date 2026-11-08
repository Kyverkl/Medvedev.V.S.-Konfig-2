# depvis — визуализация графа зависимостей (вариант 18)

CLI-инструмент для графа зависимостей пакетов Cargo (Rust).
Менеджеры пакетов и сторонние resolver'ы не используются.

## Этап 1

Конфигурация TOML и вывод параметров.

Параметры: `package`, `repository`, `test_mode`, `ascii_tree`.

```bash
bash run.sh -c config.example.toml
bash run.sh -c config.bad-missing.toml
```

## Тесты

```bash
PYTHONPATH=src py -3.15 -m pytest tests/ -v
```
