from machine import Pin
import time

from config import (
    PIN_LED_VERDE, PIN_LED_AMARELO, PIN_LED_VERMELHO, PIN_BUZZER,
    STATE_SEGURO, STATE_ATENCAO, STATE_CRITICO,
    TEMP_SAFE_MIN, TEMP_SAFE_MAX, TEMP_ATENCAO_MIN, TEMP_ATENCAO_MAX,
    UMIDADE_SAFE_MIN, UMIDADE_SAFE_MAX,
    GAS_SEGURO, GAS_ATENCAO, GAS_CRITICO,
    BUZZER_ON_MS, BUZZER_OFF_MS
)


class AlertSystem:
    """Sistema de alertas e controle de LEDs e buzzer"""
    
    def __init__(self):
        """Inicializa pinos de LEDs e buzzer"""
        self.led_verde = Pin(PIN_LED_VERDE, Pin.OUT)
        self.led_amarelo = Pin(PIN_LED_AMARELO, Pin.OUT)
        self.led_vermelho = Pin(PIN_LED_VERMELHO, Pin.OUT)
        self.buzzer = Pin(PIN_BUZZER, Pin.OUT)
        
        # Estado anterior para controle de buzzer intermitente
        self.buzzer_state = False  # False = desligado, True = ligado
        self.buzzer_last_toggle = 0  # Timestamp do último toggle
        
        # Apaga todos os LEDs inicialmente
        self.led_verde.off()
        self.led_amarelo.off()
        self.led_vermelho.off()
        self.buzzer.off()
    
    def classify_sensor(self, value, safe_min, safe_max, atencao_min=None, atencao_max=None):
        """
        Classifica o valor de um sensor em SEGURO, ATENCAO ou CRITICO
        
        Args:
            value: Valor do sensor
            safe_min: Valor mínimo para estado seguro
            safe_max: Valor máximo para estado seguro
            atencao_min: Valor mínimo para estado atenção (opcional)
            atencao_max: Valor máximo para estado atenção (opcional)
        
        Returns:
            str: STATE_SEGURO, STATE_ATENCAO ou STATE_CRITICO
        """
        if safe_min <= value <= safe_max:
            return STATE_SEGURO
        
        if atencao_min is not None and atencao_max is not None:
            if atencao_min <= value <= atencao_max:
                return STATE_ATENCAO
        
        return STATE_CRITICO
    
    def classify_temperature(self, temp):
        """Classifica temperatura em SEGURO/ATENCAO/CRITICO"""
        if TEMP_SAFE_MIN <= temp <= TEMP_SAFE_MAX:
            return STATE_SEGURO
        elif (TEMP_ATENCAO_MIN <= temp < TEMP_SAFE_MIN) or (TEMP_SAFE_MAX < temp <= TEMP_ATENCAO_MAX):
            return STATE_ATENCAO
        else:
            return STATE_CRITICO
    
    def classify_humidity(self, humidity):
        """Classifica umidade em SEGURO/ATENCAO/CRITICO"""
        if UMIDADE_SAFE_MIN <= humidity <= UMIDADE_SAFE_MAX:
            return STATE_SEGURO
        else:
            return STATE_ATENCAO
    
    def classify_gas(self, gas):
        """Classifica concentração de gás em SEGURO/ATENCAO/CRITICO"""
        if gas <= GAS_SEGURO:
            return STATE_SEGURO
        elif gas <= GAS_ATENCAO:
            return STATE_ATENCAO
        else:
            return STATE_CRITICO
    
    def classify_all_sensors(self, temp, humidity, gas):
        """
        Classifica todos os sensores
        
        Args:
            temp: Temperatura em °C
            humidity: Umidade em %
            gas: Concentração de gás
        
        Returns:
            dict: {"temperatura": estado, "umidade": estado, "gas": estado}
        """
        return {
            "temperatura": self.classify_temperature(temp),
            "umidade": self.classify_humidity(humidity),
            "gas": self.classify_gas(gas)
        }
    
    def determine_system_state(self, sensor_states):
        """
        Determina o estado geral do sistema baseado nos estados individuais dos sensores
        
        Lógica:
        - Se qualquer sensor está em CRITICO → Sistema CRITICO
        - Se qualquer sensor está em ATENCAO → Sistema ATENCAO
        - Caso contrário → Sistema SEGURO
        
        Args:
            sensor_states: dict com estados de cada sensor
        
        Returns:
            str: Estado geral (STATE_SEGURO, STATE_ATENCAO ou STATE_CRITICO)
        """
        states = list(sensor_states.values())
        
        if STATE_CRITICO in states:
            return STATE_CRITICO
        elif STATE_ATENCAO in states:
            return STATE_ATENCAO
        else:
            return STATE_SEGURO
    
    def control_leds(self, system_state):
        """
        Controla os LEDs conforme o estado do sistema
        
        Args:
            system_state: Estado do sistema (STATE_SEGURO, STATE_ATENCAO ou STATE_CRITICO)
        """
        # Apaga todos os LEDs
        self.led_verde.off()
        self.led_amarelo.off()
        self.led_vermelho.off()
        
        # Liga o LED apropriado
        if system_state == STATE_SEGURO:
            self.led_verde.on()
        elif system_state == STATE_ATENCAO:
            self.led_amarelo.on()
        elif system_state == STATE_CRITICO:
            self.led_vermelho.on()
    
    def control_buzzer_intermitent(self, system_state):
        """
        Controla o buzzer com padrão intermitente apenas em estado CRITICO
        
        Buzzer pisca 500ms on / 500ms off em estado crítico
        
        Args:
            system_state: Estado do sistema
        """
        current_time = time.ticks_ms()
        
        if system_state == STATE_CRITICO:
            # Calcula tempo desde o último toggle
            time_since_toggle = time.ticks_diff(current_time, self.buzzer_last_toggle)
            
            # Determina o intervalo esperado
            interval = BUZZER_ON_MS if self.buzzer_state else BUZZER_OFF_MS
            
            # Toggle se chegou ao tempo
            if time_since_toggle >= interval:
                self.buzzer_state = not self.buzzer_state
                self.buzzer_last_toggle = current_time
                
                if self.buzzer_state:
                    self.buzzer.on()
                else:
                    self.buzzer.off()
        else:
            # Desliga buzzer em outros estados
            self.buzzer.off()
            self.buzzer_state = False
            self.buzzer_last_toggle = time.ticks_ms()
    
    def update_system(self, temp, humidity, gas):
        """
        Atualiza todo o sistema de alertas
        
        Args:
            temp: Temperatura em °C
            humidity: Umidade em %
            gas: Concentração de gás
        
        Returns:
            str: Estado geral do sistema
        """
        # Classifica sensores
        sensor_states = self.classify_all_sensors(temp, humidity, gas)
        
        # Determina estado geral
        system_state = self.determine_system_state(sensor_states)
        
        # Atualiza LEDs
        self.control_leds(system_state)
        
        # Atualiza buzzer
        self.control_buzzer_intermitent(system_state)
        
        return system_state
