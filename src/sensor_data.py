from config import ESTADO_TEXTO


class CurrentSensorData:
    """Classe para armazenar e gerenciar dados atuais dos sensores"""
    
    def __init__(self):
        """Inicializa os dados dos sensores"""
        self.temperature = 0.0
        self.humidity = 0.0
        self.gas = 0
        self.system_state = "seguro"
    
    def update(self, temperature, humidity, gas, system_state):
        """
        Atualiza os dados dos sensores
        
        Args:
            temperature: Temperatura em °C
            humidity: Umidade em %
            gas: Concentração de gás (ppm)
            system_state: Estado do sistema (seguro, atencao, critico)
        """
        self.temperature = temperature
        self.humidity = humidity
        self.gas = gas
        self.system_state = system_state
    
    def get_current_data(self):
        """
        Retorna os dados atuais dos sensores
        
        Returns:
            dict: Dicionário com temperatura, umidade, gás e estado do sistema
        """
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "gas": self.gas,
            "system_state": self.system_state
        }
    
    def __str__(self):
        """Representação em string dos dados dos sensores"""
        state_text = ESTADO_TEXTO.get(self.system_state, self.system_state.upper())
        return (
            "Temp: {:.1f}°C | "
            "Umidade: {:.1f}% | "
            "Gás: {} ppm | "
            "Estado: {}".format(self.temperature, self.humidity, self.gas, state_text)
        )
    
    def __repr__(self):
        """Representação em string para debug"""
        return (
            "CurrentSensorData(temp={}, "
            "humidity={}, "
            "gas={}, "
            "state={})".format(self.temperature, self.humidity, self.gas, self.system_state)
        )
