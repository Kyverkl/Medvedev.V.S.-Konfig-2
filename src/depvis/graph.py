"""Build dependency graph with iterative DFS."""

from __future__ import annotations

from collections.abc import Callable


class GraphError(Exception):
    """Graph construction or traversal error."""


WHITE = 0
GRAY = 1
BLACK = 2


def build_transitive_graph(
    root: str,
    get_deps: Callable[[str], list[str]],
) -> dict[str, list[str]]:
    """
    Build dependency graph via non-recursive DFS.

    Cyclic edges are kept; gray nodes are not re-entered.
    """
    graph: dict[str, list[str]] = {}
    color: dict[str, int] = {root: GRAY}
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
            continue

        color[node] = BLACK
        stack.pop()

    return graph


def _safe_deps(
    get_deps: Callable[[str], list[str]], name: str
) -> list[str]:
    """Call get_deps and return empty list on failure."""
    try:
        return list(get_deps(name))
    except Exception:
        return []


def find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Return list of detected cycles."""
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
                    cycles.append(
                        _cycle_path(parents, node, child)
                    )
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
    """Rebuild cycle path ending with back edge."""
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
    Packages that depend on target (transitively).

    Iterative DFS on the reversed edge list.
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
