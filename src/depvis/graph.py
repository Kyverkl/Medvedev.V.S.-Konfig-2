"""Построение графа зависимостей: итеративный DFS."""

from __future__ import annotations

from collections.abc import Callable


class GraphError(Exception):
    """Ошибка построения или обхода графа."""


WHITE = 0
GRAY = 1
BLACK = 2


def build_transitive_graph(
    root: str,
    get_deps: Callable[[str], list[str]],
) -> dict[str, list[str]]:
    """
    Строит граф зависимостей обходом DFS без рекурсии.

    get_deps(name) — прямые зависимости пакета.
    Циклические зависимости сохраняются как рёбра,
    повторный заход в серый узел не выполняется.
    """
    graph: dict[str, list[str]] = {}
    color: dict[str, int] = {root: GRAY}
    # стек кадров: (узел, индекс_следующего_ребёнка)
    stack: list[tuple[str, int]] = [(root, 0)]

    while stack:
        node, index = stack[-1]
        if node not in graph:
            graph[node] = _safe_deps(get_deps, node)

        deps = graph[node]
        if index < len(deps):
            child = deps[index]
            stack[-1] = (node, index + 1)
            state = color.get(child, WHITE)
            if state == WHITE:
                color[child] = GRAY
                stack.append((child, 0))
            # GRAY — цикл, BLACK — уже полностью обойдён
            continue

        color[node] = BLACK
        stack.pop()

    return graph


def _safe_deps(
    get_deps: Callable[[str], list[str]], name: str
) -> list[str]:
    """Вызов get_deps с защитой от ошибок источника."""
    try:
        return list(get_deps(name))
    except Exception:
        return []


def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Возвращает список найденных циклов."""
    cycles: list[list[str]] = []
    color = {node: WHITE for node in graph}
    parents: dict[str, str | None] = {}

    for start in graph:
        if color[start] != WHITE:
            continue
        stack: list[tuple[str, int]] = [(start, 0)]
        color[start] = GRAY
        parents[start] = None
        while stack:
            node, idx = stack[-1]
            deps = graph.get(node, [])
            if idx < len(deps):
                child = deps[idx]
                stack[-1] = (node, idx + 1)
                state = color.get(child, WHITE)
                if state == GRAY:
                    cycles.append(_cycle_path(parents, node, child))
                elif state == WHITE:
                    color[child] = GRAY
                    parents[child] = node
                    stack.append((child, 0))
                continue
            color[node] = BLACK
            stack.pop()
    return cycles


def _cycle_path(
    parents: dict[str, str | None], node: str, back: str
) -> list[str]:
    """Восстанавливает путь цикла node -> ... -> back -> node."""
    path = [back]
    cur: str | None = node
    while cur is not None and cur != back:
        path.append(cur)
        cur = parents.get(cur)
    path.append(back)
    path.reverse()
    return path


def reverse_dependencies(
    graph: dict[str, list[str]], target: str
) -> list[str]:
    """
    Пакеты, зависящие от target (транзитивно).
    Итеративный DFS по обратному графу.
    """
    reverse: dict[str, list[str]] = {}
    for src, deps in graph.items():
        reverse.setdefault(src, [])
        for dep in deps:
            reverse.setdefault(dep, []).append(src)

    result: list[str] = []
    seen: set[str] = {target}
    stack: list[str] = [target]
    while stack:
        node = stack.pop()
        for parent in reverse.get(node, []):
            if parent in seen:
                continue
            seen.add(parent)
            result.append(parent)
            stack.append(parent)
    result.sort()
    return result
