URL = "http://localhost:11434/v1"

MODEL = "qwen3:32b"

PATIENT = {
    "temperature": 0.7,
    "stop": ["}"],
    "num_ctx": 16384,
}

INTERVIEWER = {
    "temperature": 0.3,
    "stop": ["}"],
    "num_ctx": 16384,
}
