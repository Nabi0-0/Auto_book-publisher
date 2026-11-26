
def manual_edit(content: str) -> str:
    print("\nManual Edit Mode")
    print("Enter your complete edited version.")
    print("Finish with a line containing only END.")
    print("-" * 60)

    lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        lines.append(line)

    updated_content = "\n".join(lines).strip()

    if not updated_content:
        raise ValueError("Edited chapter cannot be empty.")

    return updated_content


def get_human_decision(
    reviewed_text: str,
    allow_rewrite: bool = True,
) -> tuple[str, str]:
    if not isinstance(reviewed_text, str) or not reviewed_text.strip():
        raise ValueError("Reviewed chapter cannot be empty.")

    print("\n" + "-" * 60)
    print(reviewed_text[:1500])
    print("-" * 60)

    while True:
        print("[1] Approve chapter")
        print("[2] Manually edit chapter")
        if allow_rewrite:
            print("[3] Request rewrite")
        print("[4] Cancel")

        choice = input("Enter option number (1/2/3/4): ").strip()

        if choice == "1":
            return "approve", reviewed_text

        if choice == "2":
            return "edit", manual_edit(reviewed_text)

        if choice == "3" and allow_rewrite:
            return "rewrite", reviewed_text

        if choice == "4":
            return "cancel", reviewed_text

        print("Invalid choice. Please select 1, 2, 3, or 4.")
