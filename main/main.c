#include <math.h>
#include <stdio.h>
#include "esp_adc/adc_oneshot.h"
#include "esp_check.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "model_params.h"

#define LDR_ADC_UNIT ADC_UNIT_1
#define LDR_ADC_CHANNEL ADC_CHANNEL_3
#define LDR_SAMPLE_COUNT 8
#define DATA_COLLECTION_MODE 0

static int read_adc_average(adc_oneshot_unit_handle_t adc_handle)
{
    int sum = 0;

    for (int i = 0; i < LDR_SAMPLE_COUNT; ++i) {
        int sample = 0;
        ESP_ERROR_CHECK(adc_oneshot_read(adc_handle, LDR_ADC_CHANNEL, &sample));
        sum += sample;
    }

    return sum / LDR_SAMPLE_COUNT;
}

static float predict_lux_from_adc(int raw_value)
{
    float clamped_raw = (float)raw_value;
    if (clamped_raw < 0.0f) {
        clamped_raw = 0.0f;
    }
    if (clamped_raw > (PROJ2_MODEL_ADC_MAX - 1.0f)) {
        clamped_raw = PROJ2_MODEL_ADC_MAX - 1.0f;
    }

    // Modelo logaritmico ajustado a partir da curva real coletada no Wokwi.
    float inverse_ratio = (PROJ2_MODEL_ADC_MAX - clamped_raw) / clamped_raw;
    float log_inverse_ratio = logf(fmaxf(inverse_ratio, 1e-6f));
    float lux = expf((PROJ2_MODEL_WEIGHT * log_inverse_ratio) + PROJ2_MODEL_BIAS);

    return fmaxf(lux, 0.0f);
}

static const char *describe_lighting(float lux)
{
    if (lux < 50.0f) {
        return "escuro";
    }
    if (lux < 150.0f) {
        return "aconchegante";
    }
    if (lux < 500.0f) {
        return "funcional";
    }
    return "intenso";
}

void app_main(void)
{
    adc_oneshot_unit_handle_t adc1_handle;
    adc_oneshot_unit_init_cfg_t init_config = {
        .unit_id = LDR_ADC_UNIT,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config, &adc1_handle));

    // No ESP32-S3, o GPIO4 corresponde ao ADC1_CHANNEL_3.
    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_12,
        .atten = ADC_ATTEN_DB_12,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, LDR_ADC_CHANNEL, &config));

#if DATA_COLLECTION_MODE
    printf("Modo de coleta ativo.\n");
    printf("Use o valor do slider do Wokwi como referencia e monte linhas no formato:\n");
    printf("lux_referencia,adc_raw,percentual_adc,lux_estimado\n");
#endif

    while (1) {
        int raw_value = read_adc_average(adc1_handle);
        float normalized = (raw_value * 100.0f) / PROJ2_MODEL_ADC_MAX;
        float predicted_lux = predict_lux_from_adc(raw_value);
        const char *lighting_state = describe_lighting(predicted_lux);

#if DATA_COLLECTION_MODE
        printf(
            "coleta,?,%d,%.1f,%.2f\n",
            raw_value,
            normalized,
            predicted_lux);
#endif
        printf(
            "LDR raw=%4d | %.1f%% | lux estimado=%.2f | ambiente=%s\n",
            raw_value,
            normalized,
            predicted_lux,
            lighting_state);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
