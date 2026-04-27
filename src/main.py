"""
EnviroGuard - Sistema de Monitoramento de Segurança Industrial (IoT)

Lê constantemente:
- Temperatura (DHT22)
- Umidade (DHT22)
- Concentração de gás (Sensor analógico)

Estados do sistema: SEGURO (verde), ATENÇÃO (amarelo), CRÍTICO (vermelho)
Buzzer toca intermitentemente apenas em estado CRÍTICO
Display LCD mostra estado e dados dos sensores
"""

import time
from sensors import SensorReader
from alerts import AlertSystem
from display import LCDDisplay
from config import SENSOR_INTERVAL_MS


def main():
    """Função principal - Loop de execução do EnviroGuard"""
    
    print("=== EnviroGuard - Iniciando ===")
    
    # Inicializa componentes
    print("Inicializando sensores...")
    sensor_reader = SensorReader()
    
    print("Inicializando sistema de alertas...")
    alert_system = AlertSystem()
    
    print("Inicializando display LCD...")
    lcd_display = LCDDisplay()
    
    # Exibe mensagem inicial no LCD
    lcd_display.display_message("EnviroGuard", "Iniciando...")
    time.sleep(2)
    
    print("Sistema pronto! Iniciando loop de monitoramento...\n")
    
    # Loop principal
    last_read_time = 0
    
    try:
        while True:
            current_time = time.ticks_ms()
            
            # Lê sensores a cada SENSOR_INTERVAL_MS (2000 ms = 2 segundos)
            if time.ticks_diff(current_time, last_read_time) >= SENSOR_INTERVAL_MS:
                last_read_time = current_time
                
                try:
                    # Lê todos os sensores
                    temp, humidity, gas = sensor_reader.read_all()
                    
                    # Atualiza sistema de alertas (classifica e controla hardware)
                    system_state = alert_system.update_system(temp, humidity, gas)
                    
                    # Atualiza display LCD
                    lcd_display.update_display(system_state, temp, humidity, gas)
                    
                    # Debug: Imprime valores no console
                    print(f"Temp: {temp:.1f}°C | Umidade: {humidity:.1f}% | Gás: {gas} | Estado: {system_state.upper()}")
                    
                except Exception as e:
                    print(f"Erro no ciclo de leitura: {e}")
                    lcd_display.display_message("Erro!", "Falha nos sensores")
            
            # Controla buzzer intermitente (não bloqueia loop)
            # O buzzer é controlado em update_system, mas precisamos manter responsividade
            time.sleep(50)  # Sleep pequeno para evitar busy-waiting
    
    except KeyboardInterrupt:
        print("\n\n=== Encerrando EnviroGuard ===")
        alert_system.buzzer.off()
        alert_system.led_verde.off()
        alert_system.led_amarelo.off()
        alert_system.led_vermelho.off()
        lcd_display.display_message("Sistema", "Desligado")
        print("Sistema desligado com segurança.")
    
    except Exception as e:
        print(f"Erro crítico: {e}")
        alert_system.buzzer.off()
        lcd_display.display_message("Erro Critico!", str(e)[:16])


if __name__ == "__main__":
    main()
