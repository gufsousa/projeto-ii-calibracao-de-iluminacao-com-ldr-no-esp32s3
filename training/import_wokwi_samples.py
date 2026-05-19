from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "training" / "data"
ARTIFACTS_DIR = PROJECT_ROOT / "training" / "artifacts"
INPUT_CSV = DATA_DIR / "wokwi_samples.csv"
OUTPUT_CSV = ARTIFACTS_DIR / "wokwi_training_dataset.csv"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["adc_raw"] = result["adc_raw"].astype(float)
    result["lux_referencia"] = result["lux_referencia"].astype(float)
    result["percentual_adc"] = result["percentual_adc"].astype(float)
    result["lux_estimado"] = result["lux_estimado"].astype(float)
    result["ratio_feature"] = result["adc_raw"] / (4095.0 - result["adc_raw"].clip(upper=4094.0))
    result["log_inverse_ratio_feature"] = np.log(
        (4095.0 - result["adc_raw"].clip(lower=1.0, upper=4094.0))
        / result["adc_raw"].clip(lower=1.0, upper=4094.0)
    )
    result["log_lux_referencia"] = np.log1p(result["lux_referencia"])
    return result


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {INPUT_CSV}\n"
            "Copie training/data/wokwi_samples_template.csv para wokwi_samples.csv e cole suas amostras."
        )

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT_CSV)

    required_columns = {"lux_referencia", "adc_raw", "percentual_adc", "lux_estimado"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes em {INPUT_CSV.name}: {sorted(missing)}")

    dataset = build_features(df)
    dataset.to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)

    print("Dataset preparado para o notebook")
    print(f"entrada : {INPUT_CSV}")
    print(f"saida   : {OUTPUT_CSV}")
    print(f"amostras: {len(dataset)}")
    print("colunas :", ", ".join(dataset.columns))


if __name__ == "__main__":
    main()
