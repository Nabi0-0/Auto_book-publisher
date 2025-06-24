import os
import shutil
REVIEWED_PATH = "outputs/chapter1_reviewed_v1.txt"
FINAL_PATH = "outputs/chapter1_final_v1.txt"
MANUAL_EDIT_PATH = "outputs/chapter1_reviewed_edit.txt"

def load_text(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def save_text(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def manual_edit(content):
    print("\n Manual Edit Mode")
    print("Enter your full updated version below. Finish input with a line containing only `END`.")
    print("-" * 60)
    new_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        new_lines.append(line)
    return "\n".join(new_lines)

def main():
    print("Loading reviewed chapter for human-in-the-loop review...")
    if not os.path.exists(REVIEWED_PATH):
        print("Reviewed file not found. Please run reviewer.py first.")
        return

    content = load_text(REVIEWED_PATH)
    print("\n Reviewed Chapter Preview:")
    print("-" * 60)
    print(content[:1000])  
    print("-" * 60)
    print("\nChoose an action:")
    print("[1] Approve and Save as Final")
    print("[2] Manually Edit and Save")
    print("[3] Request Rewrite (return to writer)")
    choice = input("Enter option number (1/2/3): ").strip()

    if choice == "1":
        shutil.copy(REVIEWED_PATH, FINAL_PATH)
        print(f"Chapter approved and saved as: {FINAL_PATH}")

    elif choice == "2":
        updated = manual_edit(content)
        save_text(MANUAL_EDIT_PATH, updated)
        print(f"Edited version saved to: {MANUAL_EDIT_PATH}")
        print("You can now rerun reviewer.py with this version if needed.")

    elif choice == "3":
        print("Send the original input again through writer.py with updated tone or config.")
        print("Tip: Update prompts or try different model settings in writer.py.")

    else:
        print("Invalid input. Exiting.")

if __name__ == "__main__":
    main()
