"""Tests for iterative DFS graph builder."""

from depvis.graph import build_transitive_graph, find_cycles


def test_simple_tree() -> None:
    data = {"A": ["B", "C"], "B": ["D"], "C": [], "D": []}

    def get_deps(name: str) -> list[str]:
        return list(data.get(name, []))

    graph = build_transitive_graph("A", get_deps)
    assert set(graph["A"]) == {"B", "C"}
    assert graph["B"] == ["D"]
    assert "D" in graph


def test_cycle_detected() -> None:
    data = {"A": ["B"], "B": ["C"], "C": ["A"]}

    def get_deps(name: str) -> list[str]:
        return list(data.get(name, []))

    graph = build_transitive_graph("A", get_deps)
    cycles = find_cycles(graph)
    assert cycles
