# Explicacao do Notebook de Treino

## Objetivo

Este documento explica o papel do notebook de treino do projeto:

`training/notebooks/projeto_ii_lux_regression.ipynb`

O notebook foi criado para apoiar a etapa de analise e calibracao do sensor LDR. Ele permite visualizar os dados coletados, entender a relacao entre `adc_raw` e `lux_referencia` e validar a estrategia usada antes da exportacao do modelo para o firmware.

## Funcao do Notebook no Projeto

O notebook nao substitui o firmware e nem o script final de exportacao. Ele funciona como ambiente de exploracao.

Na pratica, ele serve para:

- inspecionar o dataset coletado no Wokwi
- verificar o comportamento do sensor
- testar a transformacao de entrada
- visualizar correlacoes e tendencias
- validar a escolha do modelo
- apoiar ajustes antes de exportar o `.tflite`

## Arquivo do Notebook

O notebook fica em:

`training/notebooks/projeto_ii_lux_regression.ipynb`

## Dados Utilizados

O fluxo de treino parte dos dados preenchidos manualmente em:

`training/data/wokwi_samples.csv`

Depois disso, o script:

`training/import_wokwi_samples.py`

gera o arquivo:

`training/artifacts/wokwi_training_dataset.csv`

Esse CSV processado e o principal insumo usado pelo notebook.

## Colunas Importantes do Dataset

O notebook trabalha com colunas como:

- `lux_referencia`: valor de iluminancia ajustado no slider do Wokwi
- `adc_raw`: leitura bruta do ADC do ESP32-S3
- `percentual_adc`: leitura normalizada em percentual
- `lux_estimado`: valor estimado no momento da coleta anterior
- `ratio_feature`: relacao auxiliar derivada do ADC
- `log_inverse_ratio_feature`: transformacao logaritmica usada pelo modelo
- `log_lux_referencia`: versao logaritmica do alvo

## Ideia Central do Treino

O LDR nao responde de forma linear direta quando relacionamos iluminancia e leitura analogica. Por isso, o notebook ajuda a mostrar que uma transformacao logaritmica representa melhor esse comportamento.

A ideia geral usada no projeto foi:

1. ler o `adc_raw`
2. transformar essa leitura em uma feature logaritmica
3. usar essa feature para prever `log(lux)`
4. aplicar a exponencial no resultado final

Isso equivale a dizer que o modelo aprende melhor em um espaco transformado, em vez de usar `adc_raw -> lux` de forma linear simples.

## Etapas que o Notebook Costuma Mostrar

Embora o notebook possa ser ajustado ao longo do projeto, a estrutura esperada e:

### 1. Carregamento dos dados

O notebook abre o CSV processado e mostra as primeiras linhas para verificar se o dataset esta correto.

### 2. Exploracao inicial

Nessa etapa normalmente sao observados:

- distribuicao dos valores de lux
- comportamento do ADC
- como a leitura cai ou sobe ao longo da escala de iluminacao

### 3. Visualizacao grafica

O notebook pode exibir graficos para comparar:

- `lux_referencia` vs `adc_raw`
- `adc_raw` vs `log_inverse_ratio_feature`
- `log_inverse_ratio_feature` vs `log_lux_referencia`

Esses graficos ajudam a justificar a escolha da transformacao logaritmica.

### 4. Ajuste do modelo

Depois da analise visual, o notebook ajuda a verificar se a regressao/modelo leve consegue representar bem os dados coletados.

No estado final do projeto, o modelo exportado foi gerado por TensorFlow e depois convertido para TensorFlow Lite Micro.

### 5. Validacao

O notebook tambem ajuda a comparar:

- valor real de lux
- valor previsto pelo modelo
- erro aproximado

Isso e util para decidir se o modelo esta bom o suficiente para ser embarcado.

## Relacao com o Script Final

O notebook e uma ferramenta de analise, enquanto o script:

`training/train_from_wokwi.py`

e a etapa automatizada de treino e exportacao.

Em resumo:

- notebook: exploracao, visualizacao, entendimento e validacao
- script Python: treino final e geracao do `.tflite` e do array C

## Como Executar o Notebook

Na raiz do projeto:

```powershell
.\training\setup_env.ps1
.\training\.venv-tf\Scripts\Activate.ps1
jupyter notebook .\training\notebooks\projeto_ii_lux_regression.ipynb
```

## O Que Observar no Notebook

Ao abrir o notebook, vale prestar atencao principalmente nestes pontos:

- se o dataset carregou corretamente
- se a relacao entre lux e ADC segue a tendencia esperada
- se a transformacao logaritmica melhora a linearidade visual
- se os valores previstos ficam proximos dos valores de referencia

## Resultado Esperado

Ao final da analise no notebook, espera-se concluir que:

- o comportamento do sensor foi corretamente amostrado
- a feature escolhida representa bem a curva do LDR
- o modelo consegue estimar lux com erro pequeno
- o fluxo esta pronto para exportacao embarcada

## Conclusao

O notebook de treino e importante porque documenta a parte analitica do projeto. Ele mostra como os dados coletados foram entendidos, transformados e validados antes de serem levados para o ESP32-S3.

Em outras palavras, ele funciona como a ponte entre:

- a coleta experimental no Wokwi
- e a inferencia embarcada no firmware final
