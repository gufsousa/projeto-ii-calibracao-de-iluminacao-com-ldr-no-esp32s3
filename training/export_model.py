from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "training" / "artifacts"
HEADER_PATH = PROJECT_ROOT / "main" / "model_params.h"
DATASET_PATH = ARTIFACTS_DIR / "synthetic_lux_dataset.csv"
JSON_PATH = ARTIFACTS_DIR / "projeto_ii_model.json"

ADC_MAX = 4095.0


@dataclass
class ModelArtifacts:
    weight: float
    bias: float
    rmse: float
    mape_percent: float
    samples: int


def generate_dataset(samples: int = 500) -> tuple[np.ndarray, np.ndarray]:
    lux = np.geomspace(0.2, 10000.0, samples)
    adc = np.clip(np.round(ADC_MAX * lux / (lux + 35.0)), 1, ADC_MAX - 1).astype(np.float32)
    return adc, lux.astype(np.float32)


def train_linear_regression(adc: np.ndarray, lux: np.ndarray) -> ModelArtifacts:
    feature = adc / (ADC_MAX - adc)
    design = np.column_stack([feature, np.ones(len(feature), dtype=np.float32)])
    params, _, _, _ = np.linalg.lstsq(design, lux, rcond=None)

    weight = float(params[0])
    bias = float(params[1])
    predictions = (weight * feature) + bias

    rmse = float(np.sqrt(np.mean((predictions - lux) ** 2)))
    mape = float(np.mean(np.abs((predictions - lux) / lux)) * 100.0)

    return ModelArtifacts(
        weight=weight,
        bias=bias,
        rmse=rmse,
        mape_percent=mape,
        samples=len(adc),
    )


def write_dataset_csv(adc: np.ndarray, lux: np.ndarray) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with DATASET_PATH.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["adc_raw", "lux"])
        for raw, lux_value in zip(adc, lux):
            writer.writerow([int(raw), f"{float(lux_value):.6f}"])


def write_model_json(artifacts: ModelArtifacts) -> None:
    with JSON_PATH.open("w", encoding="utf-8") as fp:
        json.dump(asdict(artifacts), fp, indent=2)


def write_header(artifacts: ModelArtifacts) -> None:
    header = f"""#ifndef MODEL_PARAMS_H
#define MODEL_PARAMS_H

// Projeto II: regressao linear simples sobre feature derivada do ADC.
// Arquivo gerado por training/export_model.py.
#define PROJ2_MODEL_ADC_MAX {ADC_MAX:.1f}f
#define PROJ2_MODEL_WEIGHT {artifacts.weight:.6f}f
#define PROJ2_MODEL_BIAS ({artifacts.bias:.6f}f)

#endif  // MODEL_PARAMS_H
"""
    HEADER_PATH.write_text(header, encoding="utf-8")


def main() -> None:
    adc, lux = generate_dataset()
    artifacts = train_linear_regression(adc, lux)

    write_dataset_csv(adc, lux)
    write_model_json(artifacts)
    write_header(artifacts)

    print("Projeto II - treino/exportacao concluido")
    print(f"amostras: {artifacts.samples}")
    print(f"peso: {artifacts.weight:.6f}")
    print(f"bias: {artifacts.bias:.6f}")
    print(f"rmse: {artifacts.rmse:.6f}")
    print(f"mape: {artifacts.mape_percent:.2f}%")
    print(f"dataset: {DATASET_PATH}")
    print(f"json: {JSON_PATH}")
    print(f"header: {HEADER_PATH}")


if __name__ == "__main__":
    main()
