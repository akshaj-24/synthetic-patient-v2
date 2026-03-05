TOOL_LIST = [
    {
        "type": "function",
        "function": {
            "name": "get_childhood_history",
            "description": "Retrieve the patient's childhood history including early life experiences and upbringing. Use when the conversation involves childhood, family of origin, or early trauma.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_education_history",
            "description": "Retrieve the patient's education history. Use when the conversation involves school, academic experiences, or learning.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_occupation_history",
            "description": "Retrieve the patient's occupation history. Use when the conversation involves work, career, or employment.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_relationship_history",
            "description": "Retrieve the patient's relationship history including romantic, family, and social relationships. Use when the conversation involves relationships or interpersonal dynamics.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_medical_history",
            "description": "Retrieve the patient's medical history including past diagnoses, treatments, and medications. Use when the conversation involves physical health or medical conditions.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_personal_history",
            "description": "Retrieve the patient's personal history including lifestyle, habits, and personal experiences. Use when the conversation involves personal background or daily life.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_session_history",
            "description": "Retrieve the patient's past session notes and therapy history. Use when the conversation references previous sessions or ongoing treatment progress.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }
    },
]