"""
Script de teste para simular diferentes cenários de sensores
Testa 3 situações: SEGURO, ATENÇÃO e CRÍTICO
Respeita o intervalo de leitura de sensores (2 segundos)
"""

import time
import sys

# MicroPython compatibility layer for testing
if not hasattr(time, 'ticks_ms'):
    _start_time = time.time()
    
    def ticks_ms():
        """Return milliseconds since start (MicroPython compatible)"""
        return int((time.time() - _start_time) * 1000)
    
    def ticks_diff(ticks1, ticks2):
        """Calculate difference between two ticks values (MicroPython compatible)"""
        return ticks1 - ticks2
    
    # Add to time module
    time.ticks_ms = ticks_ms
    time.ticks_diff = ticks_diff

from alerts import AlertSystem
from config import SENSOR_INTERVAL_MS, ESTADO_TEXTO

# Cenários de teste com valores de sensores
test_scenarios = [
    {
        "nome": "Cenário 1: SEGURO",
        "tempo": 3,  # 3 segundos
        "valores": [
            {"temp": 25.0, "humidity": 60.0, "gas": 800},
            {"temp": 25.0, "humidity": 60.0, "gas": 800},
            {"temp": 25.0, "humidity": 60.0, "gas": 800},
            {"temp": 25.0, "humidity": 60.0, "gas": 800},
        ]
    },
    {
        "nome": "Cenário 2: ATENÇÃO",
        "tempo": 3,  # 3 segundos
        "valores": [
            {"temp": 15.0, "humidity": 60.0, "gas": 1200},
            {"temp": 15.0, "humidity": 60.0, "gas": 1200},
            {"temp": 15.0, "humidity": 60.0, "gas": 1200},
            {"temp": 15.0, "humidity": 60.0, "gas": 1200},
        ]
    },
    {
        "nome": "Cenário 3: CRÍTICO",
        "tempo": 4,  # 4 segundos (total: 10 segundos)
        "valores": [
            {"temp": 10.0, "humidity": 60.0, "gas": 1800},
            {"temp": 10.0, "humidity": 60.0, "gas": 1800},
            {"temp": 10.0, "humidity": 60.0, "gas": 1800},
            {"temp": 10.0, "humidity": 60.0, "gas": 1800},
        ]
    }
]


class MockSensorReader:
    """Mock do SensorReader para simular valores de sensores"""
    
    def __init__(self, valores):
        self.valores = valores
        self.index = 0
    
    def read_all(self):
        """Retorna o próximo valor da lista de simulação"""
        valor = self.valores[self.index % len(self.valores)]
        return valor["temp"], valor["humidity"], valor["gas"]


def run_test_scenario(scenario):
    """Executa um cenário de teste"""
    print(f"\n{'='*60}")
    print(f"{scenario['nome']}")
    print(f"{'='*60}\n")
    
    # Inicializa sistema de alertas
    alert_system = AlertSystem()
    sensor_reader = MockSensorReader(scenario['valores'])
    
    # Simula leituras a cada 2 segundos
    start_time = time.time()
    read_count = 0
    last_read_time = 0
    
    while time.time() - start_time < scenario['tempo']:
        current_time = time.time()
        
        # Lê sensores a cada 2 segundos (simula SENSOR_INTERVAL_MS)
        if current_time - last_read_time >= (SENSOR_INTERVAL_MS / 1000):
            last_read_time = current_time
            read_count += 1
            
            # Lê sensores
            temp, humidity, gas = sensor_reader.read_all()
            sensor_reader.index += 1
            
            # Atualiza sistema
            system_state = alert_system.update_system(temp, humidity, gas)
            
            # Exibe informações
            print(f"[Leitura {read_count}]")
            print(f"  Temp: {temp:.1f}°C | Umidade: {humidity:.1f}% | Gás: {gas} ppm")
            print(f"  Estado: {ESTADO_TEXTO[system_state]}")
            print(f"  LED Verde: {'ON' if alert_system.led_verde.value() else 'OFF'}")
            print(f"  LED Amarelo: {'ON' if alert_system.led_amarelo.value() else 'OFF'}")
            print(f"  LED Vermelho: {'ON' if alert_system.led_vermelho.value() else 'OFF'}")
            print(f"  Buzzer: {'ON' if alert_system.buzzer.value() else 'OFF'}\n")
        
        time.sleep(0.1)  # Sleep pequeno para não sobrecarregar
    
    print(f"Cenário concluído após {read_count} leituras\n")


def main():
    """Executa todos os cenários de teste"""
    print("\n" + "="*60)
    print("TESTE DO SISTEMA ENVIROGUARD - SIMULAÇÃO DE SENSORES")
    print("="*60)
    
    for scenario in test_scenarios:
        run_test_scenario(scenario)
    
    print("="*60)
    print("TESTES CONCLUÍDOS")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
