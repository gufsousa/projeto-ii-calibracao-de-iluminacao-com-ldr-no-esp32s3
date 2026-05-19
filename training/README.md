# Ambiente de Treino - Projeto II

Esta pasta concentra o ambiente de treino e exportacao do modelo para o projeto:

`Projeto II - Estimativa Reacional Regressiva Perceptiva Aplicada Sobre Iluminacao Residencial Dinamica`

## Estrutura

- `requirements.txt`: dependencias do ambiente Python para treino e notebook.
- `setup_env.ps1`: cria uma virtualenv local em `training/.venv`.
- `export_model.py`: gera dataset sintetico, treina a regressao e exporta artefatos.
- `import_wokwi_samples.py`: converte amostras coletadas no terminal em CSV pronto para treino.
- `train_from_wokwi.py`: recalcula o modelo usando o CSV real coletado no Wokwi.
- `notebooks/projeto_ii_lux_regression.ipynb`: notebook base para exploracao e ajuste.
- `data/wokwi_samples_template.csv`: modelo para colar as medicoes do Wokwi.
- `artifacts/`: saidas do treino, metricas e pesos exportados.

## Como usar

No PowerShell, a partir da raiz do projeto:

```powershell
.\training\setup_env.ps1
.\training\.venv\Scripts\Activate.ps1
python .\training\export_model.py
jupyter notebook .\training\notebooks\projeto_ii_lux_regression.ipynb
```

## Coleta real do Wokwi para CSV

1. Rode o firmware e copie as linhas de coleta mostradas no terminal.
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
- `main/model_params.h`

## O que este fluxo entrega

- Um modelo de regressao simples orientado ao ADC do LDR.
- Exportacao automatica do header `main/model_params.h`.
- Artefatos em JSON para inspecao e reproducao do treino.

## Bibliotecas

Para esta implementacao:

- No firmware ESP-IDF: nao foi necessario instalar biblioteca extra de TinyML.
- No treino Python: `numpy`, `pandas`, `matplotlib`, `scikit-learn`, `jupyter`.

O documento em `docs/Projeto Final ESP32 TinyML Wokwi.pdf` descreve opcoes com TFLite Micro, mas para o Projeto II ele tambem permite abordagens leves como regressao estatistica condensada e perceptron simples. Aqui seguimos a trilha mais enxuta para o ESP32-S3.
