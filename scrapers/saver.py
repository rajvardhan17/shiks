import pandas as pd


def save_to_csv(records: list[dict[str, str]], output_file: str) -> None:
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
