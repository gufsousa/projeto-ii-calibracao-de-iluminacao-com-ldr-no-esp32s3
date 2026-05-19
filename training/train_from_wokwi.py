from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import tensorflow as tf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = PROJECT_ROOT / "training" / "artifacts"
INPUT_CSV = ARTIFACTS_DIR / "wokwi_training_dataset.csv"
TFLITE_MODEL_PATH = ARTIFACTS_DIR / "ldr_lux_model.tflite"
HEADER_PATH = PROJECT_ROOT / "main" / "model_data.h"
SOURCE_PATH = PROJECT_ROOT / "main" / "model_data.cc"
MODEL_JSON_PATH = ARTIFACTS_DIR / "projeto_ii_wokwi_model.json"

ADC_MAX = 4095.0
SEED = 7
EPOCHS = 1500


@dataclass
class ModelArtifacts:
    model_type: str
    epochs: int
    rmse: float
    mape_percent: float
    samples: int
    tflite_model_size_bytes: int
    input_dtype: str
    output_dtype: str
    source: str
    tflite_path: str


def build_feature(adc_values: np.ndarray) -> np.ndarray:
    clamped = np.clip(adc_values.astype(np.float32), 1.0, ADC_MAX - 1.0)
    return np.log((ADC_MAX - clamped) / clamped).reshape(-1, 1)


def build_model() -> tf.keras.Model:
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(1,)),
            tf.keras.layers.Dense(1),
        ]
    )
    model.compile(optimizer=tf.keras.optimizers.Adam(0.05), loss="mse")
    return model


def evaluate_predictions(predictions: np.ndarray, target: np.ndarray) -> tuple[float, float]:
    rmse = float(np.sqrt(np.mean((predictions - target) ** 2)))
    mape = float(np.mean(np.abs((predictions - target) / np.maximum(target, 1e-9))) * 100.0)
    return rmse, mape


def export_c_array(model_bytes: bytes) -> None:
    header = """#ifndef MODEL_DATA_H
#define MODEL_DATA_H

extern const unsigned char g_ldr_model_data[];
extern const int g_ldr_model_data_len;

#endif  // MODEL_DATA_H
"""
    HEADER_PATH.write_text(header, encoding="utf-8")

    byte_lines = []
    for index in range(0, len(model_bytes), 12):
        chunk = model_bytes[index:index + 12]
        byte_lines.append("    " + ", ".join(f"0x{byte:02x}" for byte in chunk))
    body = ",\n".join(byte_lines)

    source = f"""#include "model_data.h"

alignas(8) const unsigned char g_ldr_model_data[] = {{
{body}
}};

const int g_ldr_model_data_len = {len(model_bytes)};
"""
    SOURCE_PATH.write_text(source, encoding="utf-8")


def train_tflite_model(df: pd.DataFrame) -> tuple[ModelArtifacts, bytes]:
    tf.keras.utils.set_random_seed(SEED)

    adc = df["adc_raw"].to_numpy(dtype=np.float32)
    target = df["lux_referencia"].to_numpy(dtype=np.float32)
    feature = build_feature(adc)
    target_log = np.log(np.maximum(target, 1e-6)).reshape(-1, 1)

    model = build_model()
    model.fit(feature, target_log, epochs=EPOCHS, verbose=0)

    predictions = np.exp(model.predict(feature, verbose=0).reshape(-1))
    rmse, mape = evaluate_predictions(predictions, target)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()

    interpreter = tf.lite.Interpreter(model_content=tflite_model)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    artifacts = ModelArtifacts(
        model_type="tflite_micro_float32_dense",
        epochs=EPOCHS,
        rmse=rmse,
        mape_percent=mape,
        samples=len(df),
        tflite_model_size_bytes=len(tflite_model),
        input_dtype=str(input_details["dtype"].__name__),
        output_dtype=str(output_details["dtype"].__name__),
        source=str(INPUT_CSV),
        tflite_path=str(TFLITE_MODEL_PATH),
    )
    return artifacts, tflite_model


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {INPUT_CSV}\n"
            "Rode primeiro: python .\\training\\import_wokwi_samples.py"
        )

    df = pd.read_csv(INPUT_CSV)
    artifacts, tflite_model = train_tflite_model(df)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    TFLITE_MODEL_PATH.write_bytes(tflite_model)
    MODEL_JSON_PATH.write_text(json.dumps(asdict(artifacts), indent=2), encoding="utf-8")
    export_c_array(tflite_model)

    print("Treino TFLite Micro float32 a partir do CSV real do Wokwi concluido")
    print(f"amostras: {artifacts.samples}")
    print(f"rmse: {artifacts.rmse:.6f}")
    print(f"mape: {artifacts.mape_percent:.2f}%")
    print(f"tamanho   : {artifacts.tflite_model_size_bytes} bytes")
    print(f"json: {MODEL_JSON_PATH}")
    print(f"tflite: {TFLITE_MODEL_PATH}")
    print(f"header: {HEADER_PATH}")
    print(f"source: {SOURCE_PATH}")


if __name__ == "__main__":
    main()
