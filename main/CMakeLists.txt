idf_component_register(
    SRCS "main.cc" "model_data.cc"
    INCLUDE_DIRS "."
    REQUIRES "esp_adc"
    PRIV_REQUIRES "spi_flash")
