# DeepSeek API Integration

## Requisitos previos
- Python 3.9 o superior
- Librerías necesarias: `python-dotenv`, `openai`

## Instalación
1. Clona el repositorio
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración
1. Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
   ```env
   DEEPSEEK_API_KEY=tu_api_key_aquí
   DEEPSEEK_BASE_URL=https://api.deepseek.com
   ```
2. Obtén tu API key desde: https://platform.deepseek.com/api_keys

## Uso
Importa y utiliza el cliente de la siguiente manera:
```bash 
python main.py
```