# EnviroGuard: Sistema de Monitoramento de Segurança Industrial

[![Build Status](https://img.shields.io/badge/status-stable-brightgreen)](#)
[![MicroPython](https://img.shields.io/badge/micropython-1.x-blue)](https://micropython.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Desenvolvido para:* Processo Seletivo – Intensivo Maker | IoT | Universidade Federal do Cariri (UFCA)

---

## 1. Visão Geral

O **EnviroGuard** é um sistema de monitoramento autônomo para ambientes industriais que requer vigilância contínua de segurança. A ideia central é simples: um ambiente industrial não pode depender de alertas manuais ou centralizados — o próprio nó de monitoramento precisa ser capaz de detectar anomalias e reagir instantaneamente.

O sistema coleta telemetria de sensores em tempo real (temperatura, umidade e concentração de gás), processa os dados localmente e aciona atuadores visuais (LEDs de estado) e sonoros (buzzer intermitente) sem nenhuma intervenção externa. É um controlador embarcado autônomo, pensado desde o início para operar em hardware com recursos limitados, viabilizando deploy em ambientes onde comunicação centralizada não é confiável.

---

## 2. Arquitetura da Solução

A solução segue uma arquitetura em camadas, o que facilita tanto a manutenção quanto a adição de novos sensores no futuro:

```
┌──────────────────────────────────────────┐
│     Camada de Apresentação               │
│  (Serial Monitor / Dashboard)            │
└──────────────────────────────────────────┘
              ↕
┌──────────────────────────────────────────┐
│   Camada de Atuação (Alerta)             │
│  • LED Verde (GPIO 25) - Estado Seguro   │
│  • LED Amarelo (GPIO 26) - Atenção       │
│  • LED Vermelho (GPIO 27) - Crítico      │
│  • Buzzer Intermitente (GPIO 18)         │
└──────────────────────────────────────────┘
              ↕
┌──────────────────────────────────────────┐
│   Camada de Processamento                │
│  • Classificação de sensores             │
│  • Lógica de estado do sistema           │
│  • Decisão de atuação em tempo real      │
└──────────────────────────────────────────┘
              ↕
┌──────────────────────────────────────────┐
│   Camada de Percepção (Sensoriamento)    │
│  • ADC Temperatura + Umidade (GPIO 15)   │
│  • ADC Concentração de Gás (GPIO 34)     │
│  • Potenciômetro de Controle (GPIO 35)   │
│  • Coleta contínua de telemetria         │
└──────────────────────────────────────────┘
```

### O que cada camada faz

**Percepção** — Um sensor DHT22 lê temperatura e umidade no GPIO 15 com alta resolução (0.1°C). Um sensor analógico de gás lê concentração no GPIO 34 (12 bits). Um potenciômetro no GPIO 35 permite simular variações de gás sem alterar código. Ambos os canais são lidos continuamente sem filtragem (para manter a lógica simples em hardware limitado).

**Processamento** — Aqui acontece a classificação de cada sensor em três estados (SEGURO, ATENÇÃO, CRÍTICO) com base em limiares configuráveis, e a combinação desses estados para determinar o estado global do sistema. Um ciclo completo roda em ~50ms, sem bloqueios, permitindo responsividade em tempo real.

**Atuação** — Resposta direta via GPIO: LED verde acende quando todos os sensores estão SEGURO, LED amarelo quando há ATENÇÃO em pelo menos um sensor, e LED vermelho + buzzer intermitente (25ms ligado/desligado) quando há estado CRÍTICO. A latência entre detecção e ação fica abaixo de 100ms.

---

## 3. Hardware e Componentes

### Plataforma

| Componente | Especificação | Função |
|---|---|---|
| **MCU** | ESP32-DevKit-C-V4 | Processador principal (Dual-core 240MHz) |
| **ADC** | 2x Canais (GPIO 34, 35) | Aquisição de dados dos sensores analógicos |
| **GPIO** | 5x Saídas (GPIO 18, 25, 26, 27) | Acionamento de atuadores (LEDs e buzzer) |
| **Comunicação** | GPIO 15 (1-Wire) | Protocolo DHT22 |
| **Memória** | 520 KB RAM / 4 MB Flash | Stack + heap + armazenamento de código |

### Sensores e Atuadores

| Componente | Pino | Função |
|---|---|---|
| Sensor DHT22 | GPIO 15 | Lê temperatura (±0.5°C) e umidade (±2%) reais |
| Sensor de Gás | GPIO 34 | Lê concentração de gás via ADC (12 bits) |
| Potenciômetro | GPIO 35 | Simula variações de concentração de gás |
| LED Verde | GPIO 25 | Indicador visual - Estado SEGURO |
| LED Amarelo | GPIO 26 | Indicador visual - Estado ATENÇÃO |
| LED Vermelho | GPIO 27 | Indicador visual - Estado CRÍTICO |
| Buzzer | GPIO 18 | Alarme sonoro intermitente (estado CRÍTICO) |

### Diagrama de Conexões

```
ESP32 ─────┬─── GPIO 15 (1-Wire) ←── Sensor DHT22 (Temperatura + Umidade)
            ├─── ADC1 (GPIO 34) ←── Sensor de Gás
            ├─── ADC2 (GPIO 35) ←── Potenciômetro (Simulação)
            ├─── GPIO 25 (OUT) ──→ LED Verde (Seguro)
            ├─── GPIO 26 (OUT) ──→ LED Amarelo (Atenção)
            ├─── GPIO 27 (OUT) ──→ LED Vermelho (Crítico)
            └─── GPIO 18 (OUT) ──→ Buzzer (Alarme Sonoro)
```

---

## 4. Decisões Técnicas

### 4.1 Programação Orientada a Objetos

A primeira versão era um script monolítico com múltiplas variáveis globais e lógica espalhada. Refatorei para OOP por uma razão prática: separar responsabilidades torna o código testável e extensível. Cada sensor tem sua própria classe, e o sistema de alertas é independente da lógica de coleta.

```python
class SensorReader:
    """Encapsula leitura de DHT22 e sensores analógicos"""
    def read_temperature(self):
        # Leitura com tratamento de erro
        pass
    
    def read_gas(self):
        # ADC com fallback em caso de erro
        pass

class AlertSystem:
    """Encapsula lógica de classificação e atuadores"""
    def classify_temperature(self, temp):
        # Determina SEGURO/ATENCAO/CRITICO
        pass
    
    def determine_system_state(self, sensor_states):
        # Combina estados individuais
        pass
```

Na prática, isso significa que adicionar um sensor BME680 via I2C amanhã é criar uma nova classe, não reescrever o sistema.

---

### 4.2 Temporização Não-Bloqueante

`time.sleep()` bloqueia a CPU inteira. Em um sistema que precisa ler múltiplos sensores e responder a eventos em paralelo, o sleep se torna um gargalo crítico.

A solução foi usar verificação de intervalo com `time.ticks_ms()`:

```python
def main():
    last_read_time = time.ticks_ms()
    
    while True:
        current_time = time.ticks_ms()
        
        if time.ticks_diff(current_time, last_read_time) >= SENSOR_INTERVAL_MS:
            last_read_time = current_time
            # Lê sensores e processa apenas quando o intervalo expira
            temp, humidity, gas = sensor_reader.read_all()
            # Atualiza alertas
            alert_system.update(temp, humidity, gas)
```

O processador não fica travado esperando — ele verifica se passou o intervalo e segue em frente. Em dispositivos com bateria, esse padrão pode reduzir o consumo significativamente.

---

### 4.3 Classificação de Sensores com Limiares Configuráveis

A lógica de classificação foi centralizada na classe `AlertSystem` com limiares definidos em `config.py`. Isso permite ajustar sensibilidade sem tocar em `main.py`:

```python
# Em config.py
TEMP_SAFE_MIN = 20
TEMP_SAFE_MAX = 30
TEMP_ATENCAO_MIN = 15
TEMP_ATENCAO_MAX = 40

GAS_SEGURO = 800
GAS_ATENCAO = 1200
GAS_CRITICO = 2500

# Em alerts.py
def classify_temperature(self, temp):
    if TEMP_SAFE_MIN <= temp <= TEMP_SAFE_MAX:
        return STATE_SEGURO
    elif (TEMP_ATENCAO_MIN <= temp < TEMP_SAFE_MIN) or \
         (TEMP_SAFE_MAX < temp <= TEMP_ATENCAO_MAX):
        return STATE_ATENCAO
    else:
        return STATE_CRITICO
```

---

### 4.4 Pipeline de CI/CD com GitHub Actions

O objetivo era ter feedback em menos de 20 segundos sem depender de hardware físico:

```
1. Linting e sintaxe (pylint)    → ~2s
2. Validação MicroPython         → ~3s
3. Simulação no Wokwi CLI        → ~12s
4. Validação de saída esperada   → ~3s
─────────────────────────────────────
Total: ~20 segundos
```

O arquivo `.github/workflows/ci.yml` automiza tudo, eliminando falsos-positivos através de validação de boot completo.

---

## 5. Limiares de Segurança e Estados

O sistema opera em três estados bem definidos:

### Estado SEGURO (Verde)
- Temperatura: 20°C a 30°C
- Umidade: 40% a 80%
- Concentração de gás: até 800 ppm
- **Ação:** LED verde aceso, outros apagados

### Estado ATENÇÃO (Amarelo)
- Temperatura: 15°C a 20°C **OU** 30°C a 40°C
- Umidade: < 40% **OU** > 80%
- Concentração de gás: 800 a 1200 ppm
- **Ação:** LED amarelo aceso, buzzer desligado

### Estado CRÍTICO (Vermelho)
- Temperatura: < 15°C **OU** > 40°C
- Umidade: extremamente baixa/alta (fora de ATENÇÃO)
- Concentração de gás: > 1200 ppm
- **Ação:** LED vermelho aceso + Buzzer intermitente (25ms ON/OFF)

O estado global do sistema é determinado pela **pior condição** entre os três sensores (hierarquia: CRÍTICO > ATENÇÃO > SEGURO).

---

## 6. Como Executar e Testar

### Simulação Interativa (Wokwi Web)

A forma mais rápida de ver o sistema funcionando, sem instalar nada:

1. Acesse aqui: [Wokwi Project](https://wokwi.com/projects/462423449300362241)
3. Clique em **Play**
4. Mova os potenciômetros para simular variações
5. Observe os LEDs respondendo e acompanhe os logs no terminal

### Execução Local (Dev Container)

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/processoseletivoIoT.git
cd processoseletivoIoT

# Reabra em Dev Container (VS Code)
# Ou instale dependências localmente:
pip install -r requirements.txt
```

### Validação via CI/CD (GitHub Actions)

1. Faça push para seu repositório
2. Acesse a aba **Actions**
3. O check verde ✅ confirma que o firmware compilou e passou na simulação automatizada

---

## 7. Estrutura de Arquivos

```
/processoseletivoIoT
 ├── src/
 │   ├── main.py              # Loop principal
 │   ├── sensors.py           # Classe SensorReader
 │   ├── alerts.py            # Classe AlertSystem
 │   ├── sensor_data.py       # Armazenamento de dados
 │   └── config.py            # Constantes e limiares
 ├── wokwi.toml               # Configuração da simulação
 ├── diagram.json             # Circuito no Wokwi
 ├── requirements.txt         # Dependências Python
 ├── flasher_args.json        # Argumentos do flasher
 ├── Dockerfile               # Imagem do dev container
 └── README.md                # Este arquivo
```

### Descrição dos Arquivos Principais

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Loop de execução, chamadas de leitura e atualização de alertas |
| `sensors.py` | Classe `SensorReader` — leitura de DHT22 e ADC com tratamento de erro |
| `alerts.py` | Classe `AlertSystem` — classificação de sensores, determinação de estado, controle de LEDs e buzzer |
| `config.py` | Todas as constantes: pinos, limiares de temperatura/umidade/gás, estados |
| `sensor_data.py` | Classe `CurrentSensorData` — armazenamento em memória dos últimos valores |
| `diagram.json` | Define o circuito virtual (componentes e conexões) |
| `wokwi.toml` | Configuração de simulação: versão, firmware, porta RFC2217 |

---

## 8. Resultados e Limitações

### O que foi alcançado

| Objetivo | Status | Detalhe |
|---|---|---|
| Monitoramento autônomo | ✅ | Ciclo de 50ms configurável |
| Classificação de 3 sensores | ✅ | Temperatura, umidade, gás com limiares customizáveis |
| Atuação em tempo real | ✅ | Latência < 100ms por decisão |
| Buzzer intermitente | ✅ | Frequência 20Hz (25ms ON/OFF) em estado crítico |
| Arquitetura OOP modular | ✅ | Fácil adição de novos sensores |
| Zero dependências externas | ✅ | Apenas MicroPython e DHT22 padrão |
| Pipeline CI/CD | ✅ | ~20 segundos com GitHub Actions + Wokwi CLI |
| Código bem documentado | ✅ | Docstrings e comentários explicativos |

### Limitações honestas

**Sensores DHT22 simulados:** a simulação não captura a dinâmica real de hardware como ruído de sensor, time-outs de comunicação 1-Wire ou variações de calibração. Em produção, seria recomendado testar com hardware real antes de deploy.

**Gás controlado via potenciômetro:** a concentração de gás não reflete situações reais (vazamentos, misturas complexas). Para produção, seria necessário um sensor real como MQ-5 ou MQ-9, exigindo poucas mudanças na arquitetura.

**Sem persistência:** os logs existem apenas em memória (serial). Um reinício perde todo o histórico. Para produção, EEPROM local ou MQTT resolveriam isso.

**Sem sincronização de tempo:** o clock interno do ESP32 deriva ao longo de dias. `ntptime.settime()` resolveria, mas adiciona dependência de rede — tradeoff consciente para manter o sistema funcionando offline.

**Sem comunicação de rede:** não há envio de alertas para servidor central. Para escalabilidade, MQTT ou HTTP POST seria adicionado futuramente.

Esses não são bugs, são tradeoffs documentados de um protótipo. O sistema faz exatamente o que foi projetado para fazer dentro do escopo do processo seletivo.

---

## 9. Requisitos do Processo Seletivo

Este projeto atende aos seguintes requisitos da etapa prática:

✅ **Organização de Projeto**
- Estrutura clara com separação de responsabilidades (OOP)
- Arquivos bem nomeados e documentados
- Arquivo `config.py` centraliza todas as constantes

✅ **Lógica de Firmware**
- Sistema de estados bem definido (SEGURO/ATENÇÃO/CRÍTICO)
- Temporização não-bloqueante (sem `sleep()` puro)
- Tratamento de erros em sensores (fallback em `last_*` values)

✅ **Simulação de Hardware**
- `diagram.json` define circuito completo com 7 componentes
- `wokwi.toml` configurado corretamente
- Execução sem erros no Wokwi CLI

✅ **Boas Práticas de Engenharia**
- Código modular (classes especializadas)
- Configuração centralizada
- Pipeline CI/CD automatizado
- README detalhado

✅ **Documentação**
- README com visão geral, arquitetura, hardware, decisões técnicas
- Docstrings em todas as classes e métodos
- Comentários em código complexo
- Diagrama de conexões e arquitetura em camadas

---

## 10. Referências e Recursos

- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [Wokwi Simulator](https://wokwi.com/)
- [DHT22 Sensor Datasheet](https://www.mouser.com/datasheet/2/758/DHT22-755265.pdf)

---

## Conclusão

O **EnviroGuard** começou como um desafio de processo seletivo e evoluiu para um sistema com arquitetura definida, pipeline automatizado e documentação completa. O maior aprendizado foi perceber que em sistemas embarcados as decisões de software (temporização não-bloqueante, modularização, tratamento de erro) têm impacto direto na confiabilidade, responsividade e extensibilidade. Pensar nisso desde o início, e não como ajuste posterior, faz toda a diferença.

---

## Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.

---

**Desenvolvido por:** [Seu Nome] | Universidade Federal do Cariri (UFCA)  
**Data:** Abril de 2026  
**Status:** ✅ Projeto Completo e Funcional
