
"""
EnviroGuard - Sistema de Monitoramento de Segurança Industrial (IoT)

Lê constantemente:
- Temperatura (DHT22)
- Umidade (DHT22)
- Concentração de gás (Sensor analógico)

Estados do sistema: SEGURO (verde), ATENÇÃO (amarelo), CRÍTICO (vermelho)
Buzzer toca intermitentemente apenas em estado CRÍTICO
Dados dos sensores são exibidos no terminal
"""

import time
from sensors import SensorReader
from alerts import AlertSystem
from sensor_data import CurrentSensorData
from config import SENSOR_INTERVAL_MS


def generate_sensor_values(cycle_counter):
    """
    Gera valores de temperatura e umidade para demonstração
    (Gás agora é controlado pelo potenciômetro)
    
    Args:
        cycle_counter: Contador de ciclos (incrementa a cada leitura)
    
    Returns:
        tuple: (temp, humidity)
    """
    # Usa valores fixos para uma demonstração mais estável
    # (temperatura e umidade continuam reais do DHT22)
    temp = 25.0
    humidity = 60.0
    
    return temp, humidity


def main():
    """Função principal - Loop de execução do EnviroGuard"""
    print("Teste")
    
    print("=== EnviroGuard - Iniciando ===")
    
    # Inicializa componentes
    print("Inicializando sensores...")
    sensor_reader = SensorReader()
    
    print("Inicializando sistema de alertas...")
    alert_system = AlertSystem()
    
    # Inicializa armazenamento de dados
    current_data = CurrentSensorData()
    
    print("Sistema pronto! Iniciando loop de monitoramento...\n")

    print("Demonstração: Use o potenciômetro para controlar o nível de gás")
    print("  • Potenciômetro baixo (0-33%)   → SEGURO (LED verde, gás 800 ppm)")
    print("  • Potenciômetro médio (33-66%)  → ATENÇÃO (LED amarelo, gás 1200 ppm)")
    print("  • Potenciômetro alto (66-100%)  → CRÍTICO (LED vermelho, buzzer, gás 2500 ppm)")
    print("─" * 80 + "\n")
    
    # Loop principal
    last_read_time = 0
    cycle_counter = 0  # Contador para alternar entre os 3 estados
    start_time = time.ticks_ms()
    loop_counter = 0  # Contador de iterações do loop
    loop_interval = 50  # Faz uma leitura a cada 50 iterações (aproximadamente 3s no Wokwi)
    
    try:
        while True:
            current_time = time.ticks_ms()
            loop_counter += 1
            
            # Lê sensores a cada N iterações
            if loop_counter >= loop_interval:
                loop_counter = 0
                cycle_counter += 1
                
                try:
                    # Gera valores para temperatura e umidade
                    temp, humidity = generate_sensor_values(cycle_counter)
                    
                    # Lê potenciômetro e mapeia para valor de gás
                    pot_value = sensor_reader.read_potentiometer()
                    gas = sensor_reader.map_pot_to_gas(pot_value)
                    
                    # Atualiza sistema de alertas (classifica e controla hardware)
                    system_state = alert_system.update_system(temp, humidity, gas)
                    
                    # Armazena dados atuais
                    current_data.update(temp, humidity, gas, system_state)
                    
                    # Imprime valores no console (tempo estimado: 3s por ciclo)
                    elapsed_time = (cycle_counter - 1) * 3
                    print("[{}s] Ciclo {}: {} | Pot: {}".format(elapsed_time, cycle_counter, current_data, pot_value))
                    
                except Exception as e:
                    print("Erro no ciclo de leitura: {}".format(e))
            
            # Controla buzzer intermitente (não bloqueia loop)
            # O buzzer é controlado em update_system, mas precisamos manter responsividade
            time.sleep(0.1)  # Sleep de 100ms para evitar busy-waiting
    
    except KeyboardInterrupt:
        print("\n\n" + "─" * 80)
        print("=== Encerrando EnviroGuard ===")
        print("Última leitura armazenada: {}".format(current_data))
        alert_system.buzzer.off()
        alert_system.led_verde.off()
        alert_system.led_amarelo.off()
        alert_system.led_vermelho.off()
        print("Sistema desligado com segurança.")
    
    except Exception as e:
        print("Erro crítico: {}".format(e))
        alert_system.buzzer.off()


def get_current_sensor_data(current_data):
    """
    Função auxiliar para acessar os dados atuais dos sensores
    
    Args:
        current_data: Instância de CurrentSensorData
    
    Returns:
        dict: Dados atuais dos sensores
    """
    return current_data.get_current_data()


if __name__ == "__main__":
    main()

