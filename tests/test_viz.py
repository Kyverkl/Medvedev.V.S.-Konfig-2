"""Тесты визуализации."""

from depvis.viz import to_ascii_tree, to_mermaid


def test_mermaid() -> None:
    graph = {"A": ["B"], "B": []}
    text = to_mermaid(graph, "A")
    assert "graph TD" in text
    assert "A --> B" in text


def test_ascii() -> None:
    graph = {"A": ["B"], "B": []}
    text = to_ascii_tree(graph, "A")
    assert "A" in text
    assert "B" in text
