#include <inttypes.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>

#include "esp_adc/adc_oneshot.h"
#include "esp_check.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "model_data.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/system_setup.h"
#include "tensorflow/lite/schema/schema_generated.h"

#define LDR_ADC_UNIT ADC_UNIT_1
#define LDR_ADC_CHANNEL ADC_CHANNEL_3
#define LDR_SAMPLE_COUNT 8

namespace {

constexpr float kAdcMax = 4095.0f;
constexpr int kTensorArenaSize = 4 * 1024;

alignas(16) uint8_t tensor_arena[kTensorArenaSize];

const tflite::Model *model = nullptr;
tflite::MicroInterpreter *interpreter = nullptr;
TfLiteTensor *input_tensor = nullptr;
TfLiteTensor *output_tensor = nullptr;

}  // namespace

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

static float build_feature_from_adc(int raw_value)
{
    float clamped_raw = (float)raw_value;

    if (clamped_raw < 1.0f) {
        clamped_raw = 1.0f;
    }
    if (clamped_raw > (kAdcMax - 1.0f)) {
        clamped_raw = kAdcMax - 1.0f;
    }

    float inverse_ratio = (kAdcMax - clamped_raw) / clamped_raw;
    return logf(fmaxf(inverse_ratio, 1e-6f));
}

static bool initialize_model(void)
{
    tflite::InitializeTarget();

    model = tflite::GetModel(g_ldr_model_data);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        printf(
            "Versao de schema TFLite invalida: modelo=%" PRIu32 " runtime=%d\n",
            model->version(),
            TFLITE_SCHEMA_VERSION);
        return false;
    }

    static tflite::MicroMutableOpResolver<1> resolver;
    if (resolver.AddFullyConnected() != kTfLiteOk) {
        printf("Falha ao registrar operador FullyConnected\n");
        return false;
    }

    static tflite::MicroInterpreter static_interpreter(
        model,
        resolver,
        tensor_arena,
        kTensorArenaSize);
    interpreter = &static_interpreter;

    if (interpreter->AllocateTensors() != kTfLiteOk) {
        printf("AllocateTensors() falhou\n");
        return false;
    }

    input_tensor = interpreter->input(0);
    output_tensor = interpreter->output(0);

    if (input_tensor->type != kTfLiteFloat32 || output_tensor->type != kTfLiteFloat32) {
        printf(
            "Tipos inesperados: input=%d output=%d\n",
            input_tensor->type,
            output_tensor->type);
        return false;
    }

    return true;
}

static float predict_lux_from_adc(int raw_value)
{
    float feature = build_feature_from_adc(raw_value);
    input_tensor->data.f[0] = feature;

    if (interpreter->Invoke() != kTfLiteOk) {
        printf("Falha na inferencia TFLite para ADC=%d\n", raw_value);
        return 0.0f;
    }

    float log_lux = output_tensor->data.f[0];
    return fmaxf(expf(log_lux), 0.0f);
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

extern "C" void app_main(void)
{
    if (!initialize_model()) {
        printf("Inicializacao do modelo TFLite falhou\n");
        return;
    }

    adc_oneshot_unit_handle_t adc1_handle;
    adc_oneshot_unit_init_cfg_t init_config = {};
    init_config.unit_id = LDR_ADC_UNIT;
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&init_config, &adc1_handle));

    adc_oneshot_chan_cfg_t config = {};
    config.atten = ADC_ATTEN_DB_12;
    config.bitwidth = ADC_BITWIDTH_12;
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc1_handle, LDR_ADC_CHANNEL, &config));

    printf("Inferencia TFLite Micro pronta. Modelo embarcado: %d bytes\n", g_ldr_model_data_len);

    while (1) {
        int raw_value = read_adc_average(adc1_handle);
        float normalized = (raw_value * 100.0f) / kAdcMax;
        float predicted_lux = predict_lux_from_adc(raw_value);
        const char *lighting_state = describe_lighting(predicted_lux);

        printf(
            "LDR raw=%4d | %.1f%% | lux estimado=%.2f | ambiente=%s\n",
            raw_value,
            normalized,
            predicted_lux,
            lighting_state);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
