from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "training" / "artifacts"
INPUT_CSV = ARTIFACTS_DIR / "wokwi_training_dataset.csv"
HEADER_PATH = PROJECT_ROOT / "main" / "model_params.h"
MODEL_JSON_PATH = ARTIFACTS_DIR / "projeto_ii_wokwi_model.json"

ADC_MAX = 4095.0


@dataclass
class ModelArtifacts:
    weight: float
    bias: float
    rmse: float
    mape_percent: float
    samples: int
    source: str


def train_linear_regression(df: pd.DataFrame) -> ModelArtifacts:
    adc = df["adc_raw"].to_numpy(dtype=np.float64)
    target = df["lux_referencia"].to_numpy(dtype=np.float64)
    feature = np.log((ADC_MAX - adc) / np.maximum(adc, 1.0))
    target_log = np.log(np.maximum(target, 1e-9))

    design = np.column_stack([feature, np.ones(len(feature), dtype=np.float64)])
    params, _, _, _ = np.linalg.lstsq(design, target_log, rcond=None)

    weight = float(params[0])
    bias = float(params[1])
    predictions = np.exp((weight * feature) + bias)
    predictions = np.maximum(predictions, 0.0)

    rmse = float(np.sqrt(np.mean((predictions - target) ** 2)))
    mape = float(np.mean(np.abs((predictions - target) / np.maximum(target, 1e-9))) * 100.0)

    return ModelArtifacts(
        weight=weight,
        bias=bias,
        rmse=rmse,
        mape_percent=mape,
        samples=len(df),
        source=str(INPUT_CSV),
    )


def write_header(artifacts: ModelArtifacts) -> None:
    header = f"""#ifndef MODEL_PARAMS_H
#define MODEL_PARAMS_H

// Projeto II: regressao logaritmica sobre a curva real do LDR no Wokwi.
// Arquivo gerado por training/train_from_wokwi.py.
#define PROJ2_MODEL_ADC_MAX {ADC_MAX:.1f}f
#define PROJ2_MODEL_WEIGHT {artifacts.weight:.6f}f
#define PROJ2_MODEL_BIAS ({artifacts.bias:.6f}f)

#endif  // MODEL_PARAMS_H
"""
    HEADER_PATH.write_text(header, encoding="utf-8")


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {INPUT_CSV}\n"
            "Rode primeiro: python .\\training\\import_wokwi_samples.py"
        )

    df = pd.read_csv(INPUT_CSV)
    artifacts = train_linear_regression(df)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_JSON_PATH.write_text(json.dumps(asdict(artifacts), indent=2), encoding="utf-8")
    write_header(artifacts)

    print("Treino a partir do CSV real do Wokwi concluido")
    print(f"amostras: {artifacts.samples}")
    print(f"peso: {artifacts.weight:.6f}")
    print(f"bias: {artifacts.bias:.6f}")
    print(f"rmse: {artifacts.rmse:.6f}")
    print(f"mape: {artifacts.mape_percent:.2f}%")
    print(f"json: {MODEL_JSON_PATH}")
    print(f"header: {HEADER_PATH}")


if __name__ == "__main__":
    main()
