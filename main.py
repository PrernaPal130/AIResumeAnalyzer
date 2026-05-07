"""Command-line entry point for AI Resume Analyzer."""

from __future__ import annotations

from pathlib import Path

from analyzer import analyze_resume, print_report, save_report_json
from utils import read_resume_file, read_text_file


def _read_multiline_input() -> str:
    """Read pasted job description text until the user enters END."""
    print("Paste the job description below. Type END on a new line when finished:")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def run_analysis(resume_path: str, job_description: str, save_json: bool = True) -> dict:
    """Run analysis from file path and job description text."""
    resume_text = read_resume_file(resume_path)
    result = analyze_resume(resume_text, job_description)
    print_report(result)

    if save_json:
        output_path = save_report_json(result)
        print(f"JSON report saved to: {output_path.resolve()}")

    return result


def menu() -> None:
    """Simple CLI menu."""
    while True:
        print("\nAI Resume Analyzer")
        print("1. Analyze resume")
        print("2. Run sample analysis")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                resume_path = input("Enter resume file path (.txt or .pdf): ").strip()
                jd_choice = input("Use job description from file? (y/n): ").strip().lower()

                if jd_choice == "y":
                    jd_path = input("Enter job description text file path: ").strip()
                    job_description = read_text_file(jd_path)
                else:
                    job_description = _read_multiline_input()

                run_analysis(resume_path, job_description)

            elif choice == "2":
                root = Path(__file__).parent
                resume_path = root / "sample_resume.txt"
                jd_path = root / "sample_jd.txt"
                run_analysis(str(resume_path), read_text_file(jd_path))

            elif choice == "3":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please select 1, 2, or 3.")

        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    menu()
