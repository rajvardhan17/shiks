from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, send_file, url_for

import main

ROOT = Path(__file__).resolve().parent
URLS_DIR = ROOT / "urls"
DATA_DIR = ROOT / "data"
URLS_FILE = URLS_DIR / "colleges.txt"
ALLOWED_OUTPUT_FILES = {
    "colleges.csv": DATA_DIR / "colleges.csv",
    "page_contents.csv": DATA_DIR / "page_contents.csv",
    "structured_facts.csv": DATA_DIR / "structured_facts.csv",
    "all_data.csv": DATA_DIR / "all_data.csv",
    "course_details.csv": DATA_DIR / "course_details.csv",
    "college_payloads.json": DATA_DIR / "college_payloads.json",
    "colleges.txt": URLS_FILE,
}

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

main.configure_logging()


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0

    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    return max(0, len(lines) - 1)


def load_current_urls() -> list[str]:
    if not URLS_FILE.exists():
        return []

    return main.load_urls(str(URLS_FILE))


@app.route("/", methods=["GET"])
def index() -> str:
    current_urls = load_current_urls()
    return render_template(
        "upload.html",
        current_urls=current_urls,
        current_count=len(current_urls),
        colleges_count=count_csv_rows(DATA_DIR / "colleges.csv"),
        page_contents_count=count_csv_rows(DATA_DIR / "page_contents.csv"),
        structured_count=count_csv_rows(DATA_DIR / "structured_facts.csv"),
        course_details_count=count_csv_rows(DATA_DIR / "course_details.csv"),
        message="",
        errors=[],
    )


@app.route("/upload", methods=["POST"])
def upload() -> str:
    uploaded_file = request.files.get("file")

    if uploaded_file is None or uploaded_file.filename == "":
        return render_template(
            "upload.html",
            current_urls=load_current_urls(),
            current_count=len(load_current_urls()),
            colleges_count=count_csv_rows(DATA_DIR / "colleges.csv"),
            page_contents_count=count_csv_rows(DATA_DIR / "page_contents.csv"),
            structured_count=count_csv_rows(DATA_DIR / "structured_facts.csv"),
            course_details_count=count_csv_rows(DATA_DIR / "course_details.csv"),
            message="",
            errors=["Please choose a text file containing one URL per line."],
        )

    raw_text = uploaded_file.stream.read().decode("utf-8", errors="replace")
    urls = [line.strip() for line in raw_text.splitlines() if line.strip()]
    errors = [url for url in urls if not is_valid_url(url)]

    if not urls:
        errors.append("The uploaded file does not contain any valid URLs.")

    if errors:
        return render_template(
            "upload.html",
            current_urls=load_current_urls(),
            current_count=len(load_current_urls()),
            colleges_count=count_csv_rows(DATA_DIR / "colleges.csv"),
            page_contents_count=count_csv_rows(DATA_DIR / "page_contents.csv"),
            structured_count=count_csv_rows(DATA_DIR / "structured_facts.csv"),
            course_details_count=count_csv_rows(DATA_DIR / "course_details.csv"),
            message="",
            errors=[
                "The following values are not valid HTTP or HTTPS URLs:",
                *errors,
            ],
        )

    URLS_DIR.mkdir(parents=True, exist_ok=True)
    URLS_FILE.write_text("\n".join(urls) + "\n", encoding="utf-8")

    main.scrape_colleges(
        urls_file=str(URLS_FILE),
        colleges_file=str(DATA_DIR / "colleges.csv"),
        page_contents_file=str(DATA_DIR / "page_contents.csv"),
        structured_file=str(DATA_DIR / "structured_facts.csv"),
        course_details_file=str(DATA_DIR / "course_details.csv"),
    )

    current_urls = load_current_urls()
    return render_template(
        "upload.html",
        current_urls=current_urls,
        current_count=len(current_urls),
        colleges_count=count_csv_rows(DATA_DIR / "colleges.csv"),
        page_contents_count=count_csv_rows(DATA_DIR / "page_contents.csv"),
        structured_count=count_csv_rows(DATA_DIR / "structured_facts.csv"),
        course_details_count=count_csv_rows(DATA_DIR / "course_details.csv"),
        message=f"Uploaded {len(urls)} URLs and scraped the data successfully.",
        errors=[],
    )


@app.route("/download/<filename>")
def download_output(filename: str):
    output_path = ALLOWED_OUTPUT_FILES.get(filename)

    if output_path is None or not output_path.exists():
        return "File not found", 404

    return send_file(output_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
