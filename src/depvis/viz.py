"""Визуализация графа: Mermaid и ASCII-дерево."""

from __future__ import annotations


def to_mermaid(graph: dict[str, list[str]], root: str) -> str:
    """Текстовое описание графа на языке Mermaid."""
    lines = ["```mermaid", "graph TD"]
    seen_edges: set[tuple[str, str]] = set()
    nodes = set(graph.keys())
    for src, deps in graph.items():
        nodes.add(src)
        for dep in deps:
            nodes.add(dep)
            edge = (src, dep)
            if edge in seen_edges:
                continue
            seen_edges.add(edge)
            lines.append(f"    {src} --> {dep}")
    if root in nodes and not any(
        src == root for src, _ in seen_edges
    ):
        lines.append(f"    {root}")
    lines.append("```")
    return "\n".join(lines)


def to_ascii_tree(
    graph: dict[str, list[str]], root: str
) -> str:
    """
    ASCII-дерево зависимостей от root.
    При повторном посещении узла ставится пометка (cycle).
    """
    lines: list[str] = []
    _walk(graph, root, prefix="", is_last=True, lines=lines, path=[])
    return "\n".join(lines)


def _walk(
    graph: dict[str, list[str]],
    node: str,
    prefix: str,
    is_last: bool,
    lines: list[str],
    path: list[str],
) -> None:
    """Рекурсивный вывод дерева (глубина графа обычно мала)."""
    connector = "`-- " if is_last else "|-- "
    if not path:
        lines.append(node)
    else:
        lines.append(prefix + connector + node)
    if node in path:
        lines[-1] += " (cycle)"
        return
    children = graph.get(node, [])
    if not children:
        return
    if not path:
        child_prefix = ""
    else:
        extension = "    " if is_last else "|   "
        child_prefix = prefix + extension
    new_path = path + [node]
    last_index = len(children) - 1
    for i, child in enumerate(children):
        _walk(
            graph,
            child,
            child_prefix,
            i == last_index,
            lines,
            new_path,
        )
