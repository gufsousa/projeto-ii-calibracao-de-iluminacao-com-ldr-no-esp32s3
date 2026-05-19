# Ambiente de Treino - Projeto II

Esta pasta concentra o ambiente de treino e exportacao do modelo para o projeto:

`Projeto II - Estimativa Reacional Regressiva Perceptiva Aplicada Sobre Iluminacao Residencial Dinamica`

## Estrutura

- `requirements.txt`: dependencias do ambiente Python para treino e notebook.
- `setup_env.ps1`: cria uma virtualenv local em `training/.venv-tf`.
- `import_wokwi_samples.py`: converte amostras coletadas no terminal em CSV pronto para treino.
- `train_from_wokwi.py`: treina um modelo TensorFlow, converte para TFLite float32 e gera o array C do firmware.
- `notebooks/projeto_ii_lux_regression.ipynb`: notebook base para exploracao e ajuste.
- `data/wokwi_samples_template.csv`: modelo para colar as medicoes do Wokwi.
- `artifacts/`: saidas do treino, metricas e pesos exportados.

## Como usar

No PowerShell, a partir da raiz do projeto:

```powershell
.\training\setup_env.ps1
.\training\.venv-tf\Scripts\Activate.ps1
jupyter notebook .\training\notebooks\projeto_ii_lux_regression.ipynb
```

## Coleta real do Wokwi para CSV

1. Rode o firmware, ajuste o slider do Wokwi e anote o valor `raw` mostrado no terminal para cada `lux_referencia`.
2. Preencha `training/data/wokwi_samples.csv` com o mesmo formato do arquivo template.
3. Converta para dataset do notebook:

```powershell
python .\training\import_wokwi_samples.py
```

O arquivo final sera salvo em `training/artifacts/wokwi_training_dataset.csv`.

## Regerar parametros do firmware com dados reais

Depois de importar as amostras:

```powershell
python .\training\train_from_wokwi.py
```

Isso atualiza:

- `training/artifacts/projeto_ii_wokwi_model.json`
- `training/artifacts/ldr_lux_model.tflite`
- `main/model_data.h`
- `main/model_data.cc`

## O que este fluxo entrega

- Um modelo TFLite Micro float32 orientado ao ADC do LDR.
- Exportacao automatica do flatbuffer `.tflite` e do array C do firmware.
- Artefatos em JSON para inspecao e reproducao do treino.

## Bibliotecas

Para esta implementacao:

- No firmware ESP-IDF: o componente `espressif/esp-tflite-micro` e baixado automaticamente pelo `idf.py`.
- No treino Python: `tensorflow-cpu`, `numpy`, `pandas`, `matplotlib`, `jupyter`.
