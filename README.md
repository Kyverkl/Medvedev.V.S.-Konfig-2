# depvis — визуализация графа зависимостей (вариант 18)

CLI-инструмент для построения и визуализации графа зависимостей
пакетов **Cargo (Rust)**. Готовые менеджеры пакетов и библиотеки
для получения зависимостей **не используются**: данные берутся
из HTTP API crates.io или из файла тестового репозитория.

## Возможности

- конфигурация в TOML;
- прямые и транзитивные зависимости (DFS без рекурсии);
- обработка циклов;
- обратные зависимости;
- вывод Mermaid и ASCII-дерева;
- тестовый режим на файлах-фикстурах.

## Установка и запуск

```bash
# из корня репозитория
./run.sh -c config.example.toml --dump-config
./run.sh -c config.example.toml --direct-only
./run.sh -c config.example.toml
./run.sh -c config.example.toml --reverse
```

Windows:

```bat
run.bat -c config.example.toml --dump-config
```

Либо:

```bash
PYTHONPATH=src python -m depvis -c config.example.toml
```

## Конфигурация (TOML)

| Параметр | Тип | Описание |
|----------|-----|----------|
| `package` | string | имя анализируемого пакета |
| `repository` | string | URL (crates.io) или путь к файлу теста |
| `test_mode` | bool | `true` — тестовый файл, `false` — crates.io |
| `ascii_tree` | bool | печатать ASCII-дерево |

Примеры: `config.example.toml`, `config.real.example.toml`.

## Режимы CLI

| Флаг | Назначение |
|------|------------|
| `--dump-config` | только параметры ключ-значение (этап 1) |
| `--direct-only` | только прямые зависимости (этап 2) |
| (без флагов) | полный граф, Mermaid, опционально ASCII |
| `--reverse` | обратные зависимости (этап 4) |

## Тестовый репозиторий

Файл `fixtures/*.txt`, формат:

```text
A: B C
B: D
C: D
D:
```

Имена — **заглавные** латинские буквы и цифры.

## Тесты

```bash
PYTHONPATH=src python -m pytest tests/ -v
```

## Структура

```text
src/depvis/     — исходный код
tests/          — unit-тесты
fixtures/       — тестовые графы
run.sh, run.bat — скрипты запуска
```

## Сравнение с cargo tree

Штатный `cargo tree` строит дерево по локальному `Cargo.lock`
и реестру crates.io с учётом feature-флагов и версий.
Наш инструмент:

- не вызывает `cargo`;
- для реального режима использует HTTP API crates.io
  (только runtime-зависимости latest-версии);
- в тестовом режиме работает по упрощённому графу без версий.

Расхождения возможны из-за feature-флагов, optional-зависимостей
и выбора версии. Для учебных фикстур результаты совпадают
с ожидаемой структурой рёбер.
