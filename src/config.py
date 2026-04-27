# ===== PINOS =====
PIN_GAS = 34
PIN_DHT = 15
PIN_BUZZER = 18
PIN_LED_VERDE = 25
PIN_LED_AMARELO = 26
PIN_LED_VERMELHO = 27
PIN_POT = 35  # Potenciômetro para controlar leitura de gás

# ===== TEMPERATURA (°C) =====
TEMP_SAFE_MIN = 20
TEMP_SAFE_MAX = 30
TEMP_ATENCAO_MIN = 15
TEMP_ATENCAO_MAX = 40

# ===== UMIDADE (%) =====
UMIDADE_SAFE_MIN = 40
UMIDADE_SAFE_MAX = 80

# ===== GÁS (ppm) =====
GAS_SEGURO = 800
GAS_ATENCAO = 1200
GAS_CRITICO = 2500

# ===== POTENCIÔMETRO - MAPEAMENTO ADC PARA ESTADOS =====
# Divide a faixa 0-4095 em 3 zonas iguais para os 3 estados
POT_SEGURO_MAX = 1365      # Faixa baixa: 0-1365 → SEGURO (gás 800 ppm)
POT_ATENCAO_MIN = 1366     # Faixa média: 1366-2730 → ATENÇÃO (gás 1200 ppm)
POT_ATENCAO_MAX = 2730
POT_CRITICO_MIN = 2731     # Faixa alta: 2731-4095 → CRÍTICO (gás 2500 ppm)
POT_CRITICO_MAX = 4095

# ===== STATES =====
STATE_SEGURO = "seguro"
STATE_ATENCAO = "atencao"
STATE_CRITICO = "critico"

ESTADO_TEXTO = {
    STATE_SEGURO: "SEGURO",
    STATE_ATENCAO: "ATENCAO",
    STATE_CRITICO: "CRITICO"
}

# ===== CONTROLE =====
SENSOR_INTERVAL_MS = 50    # Teste: intervalo muito pequeno (0.5s no Wokwi se escala=10x)
BUZZER_ON_MS = 25         # Buzzer intermitente: 25ms ligado (escala Wokwi)
BUZZER_OFF_MS = 25        # Buzzer intermitente: 25ms desligado (escala Wokwi)