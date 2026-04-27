from machine import ADC, Pin
from dht import DHT22
import time

from config import PIN_GAS, PIN_DHT, PIN_POT, GAS_SEGURO, GAS_ATENCAO, GAS_CRITICO
from config import POT_SEGURO_MAX, POT_ATENCAO_MIN, POT_ATENCAO_MAX, POT_CRITICO_MIN, POT_CRITICO_MAX


class SensorReader:
    """Classe para leitura dos sensores de temperatura, umidade e gás"""
    
    def __init__(self):
        """Inicializa os sensores"""
        self.dht = DHT22(Pin(PIN_DHT))
        self.gas_adc = ADC(Pin(PIN_GAS))
        self.gas_adc.atten(ADC.ATTN_11DB)  # 0-3.6V range
        self.gas_adc.width(ADC.WIDTH_12BIT)  # 12-bit resolution (0-4095)
        
        # Inicializa potenciômetro
        self.pot_adc = ADC(Pin(PIN_POT))
        self.pot_adc.atten(ADC.ATTN_11DB)  # 0-3.6V range
        self.pot_adc.width(ADC.WIDTH_12BIT)  # 12-bit resolution (0-4095)
        
        # Valores anteriores para fallback em caso de erro
        self.last_temp = 25.0
        self.last_humidity = 50.0
        self.last_gas = 0
    
    def read_temperature(self):
        """
        Lê a temperatura do sensor DHT22
        
        Returns:
            float: Temperatura em graus Celsius
        """
        try:
            self.dht.measure()
            temp = self.dht.temperature()
            self.last_temp = temp
            return temp
        except Exception as e:
            print("Erro ao ler temperatura: {}".format(e))
            return self.last_temp
    
    def read_humidity(self):
        """
        Lê a umidade do sensor DHT22
        
        Returns:
            float: Umidade em porcentagem (0-100%)
        """
        try:
            self.dht.measure()
            humidity = self.dht.humidity()
            self.last_humidity = humidity
            return humidity
        except Exception as e:
            print("Erro ao ler umidade: {}".format(e))
            return self.last_humidity
    
    def read_gas(self):
        """
        Lê a concentração de gás do sensor analógico
        
        Returns:
            int: Valor ADC do sensor de gás (0-4095)
        """
        try:
            gas_value = self.gas_adc.read()
            self.last_gas = gas_value
            return gas_value
        except Exception as e:
            print("Erro ao ler gás: {}".format(e))
            return self.last_gas
    
    def read_all(self):
        """
        Lê todos os sensores de uma vez
        
        Returns:
            tuple: (temperatura, umidade, gás)
        """
        temp = self.read_temperature()
        humidity = self.read_humidity()
        gas = self.read_gas()
        return temp, humidity, gas
    
    def read_potentiometer(self):
        """
        Lê o valor bruto do potenciômetro (ADC)
        
        Returns:
            int: Valor ADC do potenciômetro (0-4095)
        """
        try:
            pot_value = self.pot_adc.read()
            return pot_value
        except Exception as e:
            print("Erro ao ler potenciômetro: {}".format(e))
            return 0
    
    def map_pot_to_gas(self, pot_value):
        """
        Mapeia o valor ADC do potenciômetro para um valor de gás conforme o estado
        Divide a faixa 0-4095 em 3 zonas: SEGURO, ATENÇÃO, CRÍTICO
        
        Args:
            pot_value: Valor ADC do potenciômetro (0-4095)
        
        Returns:
            int: Valor de gás (GAS_SEGURO, GAS_ATENCAO ou GAS_CRITICO)
        """
        if pot_value <= POT_SEGURO_MAX:
            return GAS_SEGURO
        elif pot_value <= POT_ATENCAO_MAX:
            return GAS_ATENCAO
        else:
            return GAS_CRITICO

