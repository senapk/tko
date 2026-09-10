from pathlib import Path
from types import SimpleNamespace

import pytest

from loguru import logger

from tko.game.game import Game
from tko.game.game_builder import GameBuilder
from tko.repository.remote import Source


def build_game(tmp_path: Path, content: str) -> GameBuilder:
    index = tmp_path / "README.md"
    index.write_text(content, encoding="utf-8")
    builder = GameBuilder(index, "base")
    builder.build_from("")
    return builder


def quest_tasks(builder: GameBuilder, key: str) -> list[str]:
    quest = builder.collect_quests()[f"base@{key}"]
    return [task.basic.key for task in quest.get_tasks()]


def test_duplicate_tasks_keep_only_first_occurrence(tmp_path: Path) -> None:
    builder = build_game(
        tmp_path,
        "# Course\n\n"
        "## First <!-- @first -->\n"
        "- [ ] `@same eval=none` [First occurrence](first/README.md)\n"
        "- [ ] `@same eval=none` [Same quest duplicate](duplicate/README.md)\n"
        "## Second <!-- @second -->\n"
        "- [ ] `@same eval=none` [Other quest duplicate](other/README.md)\n"
        "- [ ] `@unique eval=none` [Unique](unique/README.md)\n",
    )

    assert quest_tasks(builder, "first") == ["same"]
    assert quest_tasks(builder, "second") == ["unique"]
    assert list(builder.collect_tasks()) == ["base@same", "base@unique"]


def test_task_key_prevents_later_quest_and_keeps_current_quest(tmp_path: Path) -> None:
    builder = build_game(
        tmp_path,
        "# Course\n\n"
        "- [ ] `@shared eval=none` [Task before any quest](shared/README.md)\n"
        "## Rejected <!-- @shared -->\n"
        "- [ ] `@after eval=none` [Still in current quest](after/README.md)\n",
    )

    assert list(builder.collect_quests()) == ["base@_sem_quest"]
    assert quest_tasks(builder, "_sem_quest") == ["shared", "after"]


def test_quest_key_prevents_later_task(tmp_path: Path) -> None:
    builder = build_game(
        tmp_path,
        "# Course\n\n"
        "## Shared <!-- @shared -->\n"
        "- [ ] `@shared eval=none` [Rejected task](shared/README.md)\n"
        "- [ ] `@accepted eval=none` [Accepted task](accepted/README.md)\n",
    )

    assert quest_tasks(builder, "shared") == ["accepted"]
    assert list(builder.collect_tasks()) == ["base@accepted"]


def test_duplicate_quest_heading_does_not_change_current_quest(tmp_path: Path) -> None:
    builder = build_game(
        tmp_path,
        "# Course\n\n"
        "## First <!-- @first -->\n"
        "- [ ] `@one eval=none` [One](one/README.md)\n"
        "## Second <!-- @second -->\n"
        "- [ ] `@two eval=none` [Two](two/README.md)\n"
        "## Repeated first <!-- @first -->\n"
        "- [ ] `@three eval=none` [Three](three/README.md)\n",
    )

    assert quest_tasks(builder, "first") == ["one"]
    assert quest_tasks(builder, "second") == ["two", "three"]


def test_requirements_are_ignored_for_gameplay(tmp_path: Path) -> None:
    messages: list[str] = []
    sink_id = logger.add(messages.append, level="WARNING", format="{message}")
    try:
        builder = build_game(
            tmp_path,
            "# Course\n\n"
            "## Base <!-- @base -->\n"
            "- [ ] `@blocked eval=none` [This key blocks a quest](blocked/README.md)\n"
            "## Rejected <!-- @blocked -->\n"
            "## Dependent <!-- @dependent deps=@blocked,@base -->\n"
            "- [ ] `@work eval=none` [Work](work/README.md)\n",
        )
    finally:
        logger.remove(sink_id)

    quests = builder.collect_quests()
    dependent = quests["base@dependent"]
    assert not any("carregando sem esse requisito" in message for message in messages)


def test_first_occurrence_is_reserved_before_language_filtering(tmp_path: Path) -> None:
    builder = build_game(
        tmp_path,
        "# Course\n\n"
        "## Python first <!-- @shared lang=python -->\n"
        "- [ ] `@python_task eval=none` [Python](python/README.md)\n"
        "## C duplicate <!-- @shared lang=c -->\n"
        "- [ ] `@c_task eval=none` [C](c/README.md)\n",
    )

    builder.build_from("c")

    assert builder.collect_quests() == {}
    assert builder.collect_tasks() == {}


def test_same_item_key_is_allowed_in_different_sources(tmp_path: Path) -> None:
    first_index = tmp_path / "first.md"
    second_index = tmp_path / "second.md"
    content = (
        "# Course\n\n"
        "## Quest <!-- @quest -->\n"
        "- [ ] `@same eval=none` [Same](same/README.md)\n"
    )
    first_index.write_text(content, encoding="utf-8")
    second_index.write_text(content, encoding="utf-8")
    remotes = {
        "first": Source.from_local_file("first", first_index),
        "second": Source.from_local_file("second", second_index),
    }
    indexes = {"first": first_index, "second": second_index}
    resolver = SimpleNamespace(
        resolve_index_file=lambda remote, load_git: (indexes[remote.name], True)
    )
    game = Game().set_sources(remotes, "")

    game.build(resolver)  # type: ignore[arg-type]

    assert list(game.tasks) == ["first@same", "second@same"]


def test_quest_goal_uses_reference_task_xp(tmp_path: Path) -> None:
    builder = build_game(
        tmp_path,
        "---\nvar: [value]\nxp: \"value\"\n---\n\n# Course\n\n"
        "## Quest <!-- @quest -->\n"
        "- [x] `@reference value=6 eval=diff` [Reference](reference/README.md)\n"
        "- [ ] `@alternative value=20 eval=diff` [Alternative](alternative/README.md)\n"
        "- [x] `@material eval=none` [Material](material/README.md)\n",
    )

    quest = builder.collect_quests()["base@quest"]

    assert quest.game.goal_xp == 6.0


def test_quest_goal_uses_all_non_wiki_task_xp_without_references(tmp_path: Path) -> None:
    builder = build_game(
        tmp_path,
        "---\nvar: [value]\nxp: \"value\"\n---\n\n# Course\n\n"
        "## Quest <!-- @quest -->\n"
        "- [ ] `@first value=6 eval=diff` [First](first/README.md)\n"
        "- [ ] `@second value=8 eval=self` [Second](second/README.md)\n"
        "- [ ] `@material eval=none` [Material](material/README.md)\n",
    )

    quest = builder.collect_quests()["base@quest"]

    assert quest.game.goal_xp == 14.0


def test_each_source_uses_its_own_xp_formula(tmp_path: Path) -> None:
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text(
        "---\nvar: [value]\nxp: \"value\"\n---\n"
        "## Quest <!-- @quest -->\n"
        "- [ ] `@task value=3 eval=diff` [Task](task/README.md)\n",
        encoding="utf-8",
    )
    second.write_text(
        "---\nvar: [gain, depth]\nxp: \"gain * depth\"\n---\n"
        "## Quest <!-- @quest -->\n"
        "- [ ] `@task gain=3 depth=2 eval=diff` [Task](task/README.md)\n",
        encoding="utf-8",
    )
    sources = {"first": Source.from_local_file("first", first), "second": Source.from_local_file("second", second)}
    resolver = SimpleNamespace(resolve_index_file=lambda source, load_git: ({"first": first, "second": second}[source.name], True))

    game = Game().set_sources(sources, "")
    game.build(resolver)  # type: ignore[arg-type]

    assert game.tasks["first@task"].xp == 3.0
    assert game.tasks["second@task"].xp == 6.0
