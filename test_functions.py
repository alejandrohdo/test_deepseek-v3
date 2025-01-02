from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def calculate_compound_interest(principal, rate, time, n):
    if rate > 1:  # Convertir porcentaje a decimal
        rate = rate / 100
    amount = principal * (1 + rate/n)**(n*time)
    return round(amount, 2)

def create_user_profile(name, age, email, is_premium=False):
    return {
        "name": name,
        "age": age,
        "email": email,
        "is_premium": is_premium
    }

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_compound_interest",
            "description": "Calcula el interés compuesto",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number"},
                    "rate": {"type": "number"},
                    "time": {"type": "number"},
                    "n": {"type": "number"}
                },
                "required": ["principal", "rate", "time", "n"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_user_profile",
            "description": "Crea un perfil de usuario",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"},
                    "email": {"type": "string"},
                    "is_premium": {"type": "boolean"}
                },
                "required": ["name", "age", "email"]
            }
        }
    }
]

class TestMetrics:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.response_times = []

    def add_test_result(self, passed):
        self.total_tests += 1
        self.passed_tests += 1 if passed else 0
        self.failed_tests += 0 if passed else 1

    def add_response_time(self, time):
        self.response_times.append(time)

    def get_success_rate(self):
        return self.passed_tests / self.total_tests if self.total_tests > 0 else 0

    def get_avg_response_time(self):
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0

def verify_results(expected, actual, tolerance=0.01):
    if isinstance(expected, dict) and isinstance(actual, dict):
        return all(verify_results(expected[k], actual[k], tolerance) for k in expected)
    elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(expected - actual) <= tolerance
    return expected == actual

def validate_parameters(tool_call):
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    required = ["principal", "rate", "time", "n"] if function_name == "calculate_compound_interest" else ["name", "age", "email"]
    missing = [param for param in required if param not in arguments]
    
    if missing:
        raise ValueError(f"Parámetros faltantes para {function_name}: {missing}")
    return True

def execute_function_call(tool_call):
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    if function_name == "calculate_compound_interest":
        return calculate_compound_interest(**arguments)
    elif function_name == "create_user_profile":
        return create_user_profile(**arguments)
    raise ValueError(f"Función desconocida: {function_name}")

def generate_report(metrics):
    return json.dumps({
        "Total Tests": metrics.total_tests,
        "Passed Tests": metrics.passed_tests,
        "Failed Tests": metrics.failed_tests,
        "Success Rate": f"{metrics.get_success_rate() * 100:.2f}%",
        "Average Response Time": f"{metrics.get_avg_response_time():.2f} seconds"
    }, indent=2)

def run_unit_tests():
    test_cases = [
        {
            "function": "calculate_compound_interest",
            "params": {"principal": 1000, "rate": 5, "time": 5, "n": 4},
            "expected": 1282.04
        },
        {
            "function": "create_user_profile",
            "params": {"name": "Juan", "age": 30, "email": "juan@test.com"},
            "expected": {"name": "Juan", "age": 30, "email": "juan@test.com", "is_premium": False}
        }
    ]

    for test in test_cases:
        result = calculate_compound_interest(**test["params"]) if test["function"] == "calculate_compound_interest" else create_user_profile(**test["params"])
        print(f"✅ {test['function']} pasó la prueba" if verify_results(test["expected"], result) else f"❌ {test['function']} falló la prueba. Esperado: {test['expected']}, Obtenido: {result}")

def main():
    metrics = TestMetrics()
    run_unit_tests()
    
    start_time = time.time()
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Eres un asistente inteligente que puede realizar cálculos financieros y crear perfiles de usuario."},
                {"role": "user", "content": "Calcula el interés compuesto para $1000 con una tasa del 5% durante 5 años, compuesto trimestralmente. Luego crea un perfil de usuario para Juan Pérez, 30 años, con email juan@example.com."}
            ],
            tools=tools,
            tool_choice="auto"
        )

        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            for tool_call in tool_calls:
                try:
                    if validate_parameters(tool_call):
                        function_response = execute_function_call(tool_call)
                        print(f"✅ {tool_call.function.name} ejecutada correctamente")
                        print(f"Resultado: {function_response}")
                        metrics.add_test_result(True)
                except ValueError as e:
                    print(f"❌ Error en validación: {str(e)}")
                    metrics.add_test_result(False)
    
    except Exception as e:
        print(f"❌ Error en la ejecución: {str(e)}")
        metrics.add_test_result(False)
    
    metrics.add_response_time(time.time() - start_time)
    print("\n📊 Reporte Final:")
    print(generate_report(metrics))

if __name__ == "__main__":
    main()
