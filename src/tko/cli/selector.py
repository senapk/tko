def select_with_fzf(elements: list[tuple[str, str]], pattern: str | None = None, selected: str | None = None) -> str | None:
    from subprocess import run

    lines: list[str] = [
        f"{key}\t{text}"
        for key, text in elements
    ]

    args: list[str] = [
        "fzf",
        "--exact",
        "--with-nth=2..",
        "--delimiter=\t",
        "--layout=reverse",
        "--ansi",
        "--prompt=Select a task> ",
    ]
    if pattern is not None:
        args += [
            "--query",
            pattern,
        ]

    if selected is not None:
        index = next((i for i, (key, _) in enumerate(elements) if key == selected), None)
        if index is not None:
            args += [
                 f"--bind=load:pos({index + 1})",
            ]

    result = run(
        args,
        input="\n".join(lines),
        text=True,
        capture_output=True,
    )

    if result.returncode == 0:
        key = result.stdout.split("\t", 1)[0].strip()
        return key
    else:
        print(result.stderr)
    return None


def select_with_number(elements: list[tuple[str, str]], pattern: str | None = None) -> str | None:

    filtered_elements = [
        (key, text)
        for key, text in elements
        if pattern is None or pattern in text
    ]

    if not filtered_elements:
        print("No matching elements found.")
        return None

    print("Select an element by number:")
    for i, (_, text) in enumerate(filtered_elements):
        print(f"{i + 1:>3}. {text}")

    while True:
        try:
            choice = input("Enter the number of your choice (or 'q' to quit): ")
            if choice.lower() == 'q':
                return None
            index = int(choice) - 1
            if 0 <= index < len(filtered_elements):
                return filtered_elements[index][0]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")