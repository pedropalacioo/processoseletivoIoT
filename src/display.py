from machine import I2C, Pin
import time

from config import (
    PIN_LCD_SDA, PIN_LCD_SCL, LCD_ADDRESS, LCD_WIDTH, LCD_HEIGHT,
    ESTADO_TEXTO
)


class LCDDisplay:
    """Interface para controle do LCD i2c 1602"""
    
    def __init__(self):
        """Inicializa a comunicação i2c e o LCD"""
        try:
            self.i2c = I2C(0, scl=Pin(PIN_LCD_SCL), sda=Pin(PIN_LCD_SDA), freq=400000)
            
            # Importa biblioteca de LCD
            from lcd1602 import LCD1602
            self.lcd = LCD1602(self.i2c, LCD_ADDRESS, LCD_HEIGHT, LCD_WIDTH)
            
            # Inicializa display
            self.lcd.clear()
            self.lcd.display(True)
            self.lcd.cursor(False)
            
            print("LCD inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar LCD: {e}")
            self.lcd = None
    
    def format_sensor_data(self, temp, humidity, gas):
        """
        Formata os dados dos sensores para caber na linha 2 do LCD (16 chars)
        
        Formato: "T:25C H:60% G:15" (máximo 16 caracteres)
        
        Args:
            temp: Temperatura em °C
            humidity: Umidade em %
            gas: Concentração de gás
        
        Returns:
            str: String formatada com até 16 caracteres
        """
        # Formata: T=temperatura, H=umidade, G=gás (em escala 0-100)
        # Converte gás para escala de 0-100 (2000 ppm = 100%)
        gas_scaled = min(100, int(gas / 20))
        
        data_str = f"T:{int(temp)}C H:{int(humidity)}% G:{gas_scaled}"
        
        # Garante que não ultrapasse 16 caracteres
        return data_str[:LCD_WIDTH]
    
    def update_display(self, system_state, temp, humidity, gas):
        """
        Atualiza o LCD com o estado do sistema e dados dos sensores
        
        Linha 1: Estado (SEGURO/ATENCAO/CRITICO)
        Linha 2: Dados formatados (T:xxC H:xx% G:xx)
        
        Args:
            system_state: Estado do sistema
            temp: Temperatura em °C
            humidity: Umidade em %
            gas: Concentração de gás
        """
        if self.lcd is None:
            return
        
        try:
            # Linha 1: Estado
            estado_texto = ESTADO_TEXTO.get(system_state, "DESCONHECIDO")
            linha1 = estado_texto[:LCD_WIDTH].ljust(LCD_WIDTH)
            
            # Linha 2: Dados
            linha2 = self.format_sensor_data(temp, humidity, gas)
            linha2 = linha2.ljust(LCD_WIDTH)  # Preenche com espaços até 16 chars
            
            # Escreve no LCD
            self.lcd.clear()
            self.lcd.write(0, 0, linha1)
            self.lcd.write(1, 0, linha2)
            
        except Exception as e:
            print(f"Erro ao atualizar LCD: {e}")
    
    def display_message(self, line1, line2=""):
        """
        Exibe uma mensagem customizada no LCD
        
        Args:
            line1: Texto para linha 1 (até 16 caracteres)
            line2: Texto para linha 2 (até 16 caracteres)
        """
        if self.lcd is None:
            return
        
        try:
            linha1 = line1[:LCD_WIDTH].ljust(LCD_WIDTH)
            linha2 = line2[:LCD_WIDTH].ljust(LCD_WIDTH)
            
            self.lcd.clear()
            self.lcd.write(0, 0, linha1)
            self.lcd.write(1, 0, linha2)
            
        except Exception as e:
            print(f"Erro ao exibir mensagem: {e}")
    
    def clear(self):
        """Limpa o LCD"""
        if self.lcd is not None:
            try:
                self.lcd.clear()
            except Exception as e:
                print(f"Erro ao limpar LCD: {e}")
