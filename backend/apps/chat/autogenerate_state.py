import time


def response(field, state, settings=None):
    """
    Generate a state field (summary, notes, etc.) for the current interview.

    Args:
        field:    Name of the state field to generate.
        state:    InterviewState model instance.
        settings: Optional ChatSettings model instance.
                  Use it to read model/temperature for LLM calls.
    """
    print(f"[autogenerate_state.response] field={field!r}  "
          f"settings=(patient_model={getattr(settings, 'patient_model', None)!r}, "
          f"patient_temperature={getattr(settings, 'patient_temperature', None)!r})")

    # Example usage of settings when making an LLM call:
    # model       = settings.patient_model       if settings else 'qwen3:32b'
    # temperature = settings.patient_temperature if settings else 0.7
    # result = ollama_client.chat(model=model, options={'temperature': temperature}, ...)

    time.sleep(1)
    return f"Generated {field} at turn {state.turn_count} for patient {state.interview.patient.name}"