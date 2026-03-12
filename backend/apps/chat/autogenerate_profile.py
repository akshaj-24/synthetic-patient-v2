import random
import faker
import time
import json
import os
from langfuse import get_client, observe
from dotenv import load_dotenv
from .OllamaLLM import LLM_CALL as LLM

load_dotenv()
langfuse = get_client()

fake = faker.Faker()

_PSI_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'PSI_analysis', 'PSI_CM_data.json')
with open(_PSI_PATH, "r") as f:
    _PSI_PATIENTS = json.load(f)


def generateField(field, dependencies, instructions, request=None, settings=None):
    """
    Generate a single patient profile field.

    Args:
        field:        Name of the field to generate.
        dependencies: Dict of already-filled field values this field may depend on.
        settings:     Optional NewSessionSettings model instance.
                      Use it to read model/temperature for LLM calls.
    """
    print(f"[generateField] field={field!r}  "
          f"settings=(model={getattr(settings, 'model', None)!r}, "
          f"temperature={getattr(settings, 'temperature', None)!r})")

    # Example usage of settings when making an LLM call:
    # model       = settings.model       if settings else 'qwen3:32b'
    # temperature = settings.temperature if settings else 1.0
    # response = ollama_client.chat(model=model, options={'temperature': temperature}, ...)

    match field:
        case 'age':
            return randomAge()
        case 'gender':
            return randomGender()
        case 'ethnicity':
            return randomEthnicity()
        case 'name':
            gender = dependencies.get('gender')
            return randomName(gender)
        case 'marital_status':
            age = dependencies.get('age')
            return randomMaritalStatus(age)
        case 'children':
            age          = dependencies.get('age')
            marital_status = dependencies.get('marital_status')
            return randomChildren(age, marital_status)
        case 'grandchildren':
            age      = dependencies.get('age')
            children = dependencies.get('children')
            return randomGrandchildren(age, children)
        case 'education':
            age = dependencies.get('age')
            return randomEducation(int(age))
        case 'occupation':
            edu = dependencies.get('education')
            return randomOccupation(edu)
        case 'disorder':
            return randomDisorder()
        case 'type':
            return randomPatientType()
        case 'base_emotions':
            return randomPsiEmotions()
        case 'helpless_beliefs':
            return randomHelplessBeliefs()
        case 'unlovable_beliefs':
            return randomUnlovableBeliefs()
        case 'worthless_beliefs':
            return randomWorthlessBeliefs()
        
        case 'intermediate_belief':
            return intermediateBelief(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'impact':
            return impact(dependencies, instructions, request.user.id, request.user.username, settings)


        case 'trigger':
            return trigger(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'auto_thoughts':
            return auto_thoughts(dependencies, instructions, request.user.id, request.user.username, settings)
        case 'coping_strategies':
            return coping_strategies(dependencies, instructions, request.user.id, request.user.username, settings)
        case 'behavior':
            return behavior(dependencies, instructions, request.user.id, request.user.username, settings)
        case 'intake':
            return intake(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'childhood_history':
            return childhood_history(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'education_history':
            return education_history(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'occupation_history':
            return occupation_history(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'relationship_history':
            return relationship_history(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'medical_history':
            return medical_history(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'personal_history':
            return personal_history(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'family_tree':
            return family_tree(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'timeline':
            return timeline(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case "vignette":
            return vignette(dependencies, instructions, request.user.id, request.user.username, settings)
        
        case 'session_history':
            if instructions.strip() != "":
                return session_history(dependencies, instructions, request.user.id, request.user.username, settings)
            else:
                return "No prior sessions. This is the patient's first session."
        
        case 'profile_summary':
            return profile_summary(dependencies, instructions, request.user.id, request.user.username, settings)

        case __:
            return f"Not yet implemented {field}, INSTRUCTIONS: {instructions}"



def randomAge():
    return random.randint(18, 80)

def randomGender():
    genders = ['Male', 'Female', 'Non-binary', 'Transgender']
    weights = [0.48, 0.48, 0.02, 0.02]  # Approximate BC population distribution
    return random.choices(genders, weights=weights, k=1)[0]
def randomEthnicity():
    return random.choice(['White / Caucasian','Black / African American','Hispanic / Latino','East Asian','South Asian','Southeast Asian',
                          'Middle Eastern','Indigenous / First Nations','Mixed / Multiracial'])
    
def randomMaritalStatus(age):
    age = int(age)
    if age < 20:
        weights = {
            'Single':       0.25,
            'Relationship': 0.70,
            'Common-Law':   0.03,
            'Married':      0.01,
            'Divorced':     0.00,
            'Widowed':      0.00,
            'Separated':    0.01,
        }
    elif age < 25:
        weights = {
            'Single':       0.25,
            'Relationship': 0.65,
            'Common-Law':   0.06,
            'Married':      0.02,
            'Divorced':     0.00,
            'Widowed':      0.00,
            'Separated':    0.02,
        }
    elif age < 30:
        weights = {
            'Single':       0.30,
            'Relationship': 0.25,
            'Common-Law':   0.22,
            'Married':      0.18,
            'Divorced':     0.02,
            'Widowed':      0.00,
            'Separated':    0.03,
        }
    elif age < 35:
        weights = {
            'Single':       0.20,
            'Relationship': 0.15,
            'Common-Law':   0.22,
            'Married':      0.33,
            'Divorced':     0.05,
            'Widowed':      0.00,
            'Separated':    0.05,
        }
    elif age < 40:
        weights = {
            'Single':       0.14,
            'Relationship': 0.10,
            'Common-Law':   0.18,
            'Married':      0.44,
            'Divorced':     0.08,
            'Widowed':      0.01,
            'Separated':    0.05,
        }
    elif age < 45:
        weights = {
            'Single':       0.11,
            'Relationship': 0.08,
            'Common-Law':   0.16,
            'Married':      0.47,
            'Divorced':     0.11,
            'Widowed':      0.01,
            'Separated':    0.06,
        }
    elif age < 50:
        weights = {
            'Single':       0.09,
            'Relationship': 0.07,
            'Common-Law':   0.14,
            'Married':      0.49,
            'Divorced':     0.13,
            'Widowed':      0.02,
            'Separated':    0.06,
        }
    elif age < 55:
        weights = {
            'Single':       0.08,
            'Relationship': 0.06,
            'Common-Law':   0.12,
            'Married':      0.50,
            'Divorced':     0.14,
            'Widowed':      0.03,
            'Separated':    0.07,
        }
    elif age < 60:
        weights = {
            'Single':       0.07,
            'Relationship': 0.05,
            'Common-Law':   0.11,
            'Married':      0.52,
            'Divorced':     0.14,
            'Widowed':      0.05,
            'Separated':    0.06,
        }
    elif age < 65:
        weights = {
            'Single':       0.06,
            'Relationship': 0.04,
            'Common-Law':   0.10,
            'Married':      0.53,
            'Divorced':     0.14,
            'Widowed':      0.08,
            'Separated':    0.05,
        }
    elif age < 70:
        weights = {
            'Single':       0.05,
            'Relationship': 0.03,
            'Common-Law':   0.08,
            'Married':      0.54,
            'Divorced':     0.13,
            'Widowed':      0.13,
            'Separated':    0.04,
        }
    else:  # 70-80
        weights = {
            'Single':       0.04,
            'Relationship': 0.02,
            'Common-Law':   0.06,
            'Married':      0.50,
            'Divorced':     0.11,
            'Widowed':      0.24,
            'Separated':    0.03,
        }

    statuses      = list(weights.keys())
    probabilities = list(weights.values())
    return random.choices(statuses, weights=probabilities, k=1)[0]
    
def randomChildren(age, marital_status):
    age = int(age) if age else 30
    if age < 20:
        weights = [0.99, 0.01, 0.00, 0.00]
    elif age < 25:
        weights = [0.91, 0.08, 0.01, 0.00]
    elif age < 30:
        weights = [0.70, 0.25, 0.05, 0.00]
    elif age < 40:
        weights = [0.35, 0.35, 0.22, 0.08]
    elif age < 50:
        weights = [0.25, 0.38, 0.27, 0.10]
    elif age < 60:
        weights = [0.25, 0.35, 0.28, 0.12]
    else:
        weights = [0.22, 0.35, 0.30, 0.13]
    return random.choices([0, 1, 2, 3], weights=weights, k=1)[0]

def randomGrandchildren(age, children):
    age      = int(age)      if age      else 40
    children = int(children) if children else 0
    if age < 45 or children == 0:
        return 0
    if age < 55:
        weights = [0.88, 0.10, 0.02]
    elif age < 65:
        weights = [0.55, 0.32, 0.13]
    elif age < 75:
        weights = [0.30, 0.42, 0.28]
    else:
        weights = [0.18, 0.44, 0.38]
    return random.choices([0, 1, 2], weights=weights, k=1)[0]

def randomName(gender):
    name = ''
    
    if gender == 'Male':
        name += fake.first_name_male()
    elif gender == 'Female':
        name += fake.first_name_female()
    else:
        name += random.choice([fake.first_name_male(), fake.first_name_female()])
        
    name += ' ' 
    name += fake.last_name()
    return name

def randomEducation(age):
    if age < 20:
        weights = {
            'Some High School':          0.05,
            'High School Diploma':       0.60,
            'Some College / University': 0.34,
            'Trade / Vocational':        0.01,
            'College Diploma':           0.00,
            "Bachelor's Degree":         0.00,
            "Master's Degree":           0.00,
            'Doctoral Degree':           0.00,
            'Professional Degree':       0.00,
        }
    elif age < 23:
        weights = {
            'Some High School':          0.03,
            'High School Diploma':       0.20,
            'Some College / University': 0.50,
            'Trade / Vocational':        0.10,
            'College Diploma':           0.12,
            "Bachelor's Degree":         0.04,
            "Master's Degree":           0.00,
            'Doctoral Degree':           0.00,
            'Professional Degree':       0.01,
        }
    elif age < 27:
        weights = {
            'Some High School':          0.02,
            'High School Diploma':       0.08,
            'Some College / University': 0.12,
            'Trade / Vocational':        0.15,
            'College Diploma':           0.22,
            "Bachelor's Degree":         0.32,
            "Master's Degree":           0.07,
            'Doctoral Degree':           0.01,
            'Professional Degree':       0.01,
        }
    elif age < 35:
        weights = {
            'Some High School':          0.02,
            'High School Diploma':       0.07,
            'Some College / University': 0.08,
            'Trade / Vocational':        0.15,
            'College Diploma':           0.20,
            "Bachelor's Degree":         0.32,
            "Master's Degree":           0.12,
            'Doctoral Degree':           0.02,
            'Professional Degree':       0.02,
        }
    elif age < 45:
        weights = {
            'Some High School':          0.02,
            'High School Diploma':       0.07,
            'Some College / University': 0.07,
            'Trade / Vocational':        0.16,
            'College Diploma':           0.20,
            "Bachelor's Degree":         0.31,
            "Master's Degree":           0.12,
            'Doctoral Degree':           0.02,
            'Professional Degree':       0.03,
        }
    elif age < 55:
        weights = {
            'Some High School':          0.03,
            'High School Diploma':       0.08,
            'Some College / University': 0.07,
            'Trade / Vocational':        0.17,
            'College Diploma':           0.20,
            "Bachelor's Degree":         0.29,
            "Master's Degree":           0.11,
            'Doctoral Degree':           0.02,
            'Professional Degree':       0.03,
        }
    elif age < 65:
        weights = {
            'Some High School':          0.05,
            'High School Diploma':       0.09,
            'Some College / University': 0.07,
            'Trade / Vocational':        0.18,
            'College Diploma':           0.20,
            "Bachelor's Degree":         0.25,
            "Master's Degree":           0.11,
            'Doctoral Degree':           0.02,
            'Professional Degree':       0.03,
        }
    elif age < 75:
        weights = {
            'Some High School':          0.06,
            'High School Diploma':       0.10,
            'Some College / University': 0.07,
            'Trade / Vocational':        0.20,
            'College Diploma':           0.20,
            "Bachelor's Degree":         0.23,
            "Master's Degree":           0.10,
            'Doctoral Degree':           0.02,
            'Professional Degree':       0.02,
        }
    else:  # 75-80
        weights = {
            'Some High School':          0.08,
            'High School Diploma':       0.11,
            'Some College / University': 0.07,
            'Trade / Vocational':        0.22,
            'College Diploma':           0.20,
            "Bachelor's Degree":         0.19,
            "Master's Degree":           0.09,
            'Doctoral Degree':           0.02,
            'Professional Degree':       0.02,
        }

    levels        = list(weights.keys())
    probabilities = list(weights.values())
    return random.choices(levels, weights=probabilities, k=1)[0]

OCCUPATION_MAP = {
    'Some High School': [
        'Retail Sales Associate',
        'Food Service Worker',
        'Warehouse Worker',
        'Delivery Driver',
        'Cashier',
        'Landscaper',
        'Janitor / Custodian',
        'Construction Labourer',
        'Farm Worker',
        'Unemployed',
    ],
    'High School Diploma': [
        'Retail Sales Associate',
        'Administrative Assistant',
        'Customer Service Representative',
        'Delivery Driver',
        'Warehouse Supervisor',
        'Security Guard',
        'Food Service Supervisor',
        'Receptionist',
        'Data Entry Clerk',
        'Unemployed',
    ],
    'Some College / University': [
        'Administrative Assistant',
        'Sales Representative',
        'Customer Service Representative',
        'Retail Supervisor',
        'Office Coordinator',
        'Medical Office Assistant',
        'Bookkeeper',
        'Unemployed',
        'Student',
    ],
    'Trade / Vocational': [
        'Electrician',
        'Plumber',
        'Carpenter',
        'HVAC Technician',
        'Auto Mechanic',
        'Welder',
        'Heavy Equipment Operator',
        'Millwright',
        'Pipefitter',
        'Sheet Metal Worker',
        'Industrial Mechanic',
        'Building Inspector',
    ],
    'College Diploma': [
        'Registered Nurse (RN)',
        'Dental Hygienist',
        'Paramedic',
        'Early Childhood Educator',
        'Accounting Technician',
        'IT Support Technician',
        'Graphic Designer',
        'Marketing Coordinator',
        'Human Resources Coordinator',
        'Social Service Worker',
        'Civil Engineering Technician',
        'Business Analyst',
    ],
    "Bachelor's Degree": [
        'Software Developer',
        'Registered Nurse (BSN)',
        'Teacher',
        'Accountant',
        'Financial Analyst',
        'Marketing Manager',
        'Project Manager',
        'Human Resources Manager',
        'Civil Engineer',
        'Mechanical Engineer',
        'Journalist',
        'Psychologist (MA-level)',
        'Urban Planner',
        'Social Worker (BSW)',
        'Lab Technician',
        'Business Manager',
    ],
    "Master's Degree": [
        'Software Engineer (Senior)',
        'Data Scientist',
        'Clinical Psychologist',
        'University Lecturer',
        'Registered Nurse (NP)',
        'Financial Manager',
        'Senior Project Manager',
        'Operations Manager',
        'Economist',
        'Environmental Scientist',
        'Public Health Analyst',
        'Speech-Language Pathologist',
        'Occupational Therapist',
        'Social Worker (MSW)',
        'Research Scientist',
    ],
    'Doctoral Degree': [
        'University Professor',
        'Research Scientist',
        'Neuroscientist',
        'Physicist',
        'Chemist',
        'Biomedical Researcher',
        'Clinical Psychologist (PhD)',
        'Economist (PhD)',
        'Historian',
        'Pharmaceutical Scientist',
    ],
    'Professional Degree': [
        'Medical Doctor (MD)',
        'Dentist',
        'Lawyer',
        'Pharmacist',
        'Optometrist',
        'Veterinarian',
        'Psychiatrist',
        'Orthodontist',
        'Judge',
        'Notary Public',
    ],
}

def randomOccupation(education):
    options = OCCUPATION_MAP.get(education, ['Unknown'])
    return random.choice(options)

def randomDisorder():
    return random.choice(['Major Depressive Disorder (MDD)', 'Generalized Anxiety Disorder (GAD)', 'Paranoid Personality Disorder (PPD)'])


PATIENT_TYPE_CATEGORIES = {
    # How open/forthcoming the patient is
    "openness": [
        "Open",
        "Guarded",
        "Defensive",
        "Evasive",
        "Selective",
        "Overly Disclosing",
    ],
    # Emotional expression style
    "affect": [
        "Flat Affect",
        "Emotionally Expressive",
        "Labile",
        "Blunted Affect",
        "Constricted Affect",
        "Euphoric",
        "Dysphoric",
    ],
    # Attitude toward the clinician
    "engagement": [
        "Cooperative",
        "Resistant",
        "Passive",
        "Hostile",
        "Ambivalent",
        "Eager to Please",
        "Demanding",
        "Withdrawn",
    ],
    # Awareness of their condition
    "insight": [
        "Good Insight",
        "Limited Insight",
        "No Insight",
        "Partial Insight",
        "Intellectualised Insight",   # understands cognitively but not emotionally
    ],
    # Communication / presentation style
    "presentation": [
        "Dramatic",
        "Stoic",
        "Somatic",
        "Intellectualizing",
        "Tangential",
        "Circumstantial",
        "Concrete",
        "Verbose",
        "Monosyllabic",
    ],
    # Attitude toward help / treatment
    "motivation": [
        "Help-Seeking",
        "Help-Rejecting",
        "Ambivalent about Treatment",
        "Externally Motivated",       # e.g. sent by family / court
        "Intrinsically Motivated",
    ],
    # Trust in the clinician / system
    "trust": [
        "Trusting",
        "Suspicious",
        "Paranoid",
        "Mistrustful of System",
        "Overly Trusting",
    ],
}

OPTIONAL_CATEGORIES = {"presentation", "trust"}


def randomPatientType() -> str:
    """
    Returns a comma-separated string of patient type attributes,
    one sampled per category. Optional categories have a 40% chance
    of being excluded to add natural variety.
    """
    selected = []
    for category, options in PATIENT_TYPE_CATEGORIES.items():
        if category in OPTIONAL_CATEGORIES and random.random() < 0.4:
            continue
        selected.append(random.choice(options))
    return ", ".join(selected)

def randomPsiEmotions():
    patient = random.choice(_PSI_PATIENTS)
    
    # Split comma-separated emotion strings into individual tags
    emotions = []
    for emotion_str in patient.get("emotion", []):
        emotions += [e.strip() for e in emotion_str.split(",")]
          
    return ", ".join(emotions)  
    
def randomHelplessBeliefs():
    patient = random.choice(_PSI_PATIENTS)
    
    beliefs = patient.get("helpless_belief", [])
    print(beliefs)
    return ", ".join(beliefs) if beliefs else "No helpless beliefs in patient"

def randomUnlovableBeliefs():
    patient = random.choice(_PSI_PATIENTS)
    
    beliefs = patient.get("unlovable_belief", [])
    return ", ".join(beliefs) if beliefs else "No unlovable beliefs in patient"

@observe(name="intermediate_belief_generation", as_type="span")
def intermediateBelief(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/intermediate_belief", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/intermediate_belief", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

def randomWorthlessBeliefs():
    patient = random.choice(_PSI_PATIENTS)
    
    beliefs = patient.get("worthless_belief", [])
    return ", ".join(beliefs) if beliefs else "No worthless beliefs in patient"

@observe(name="trigger_generation", as_type="span")
def trigger(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    
    sys_args = {
        "age": dependencies.get("age"),
        "marital_status": dependencies.get("marital_status"),
        "education": dependencies.get("education"),
        "occupation": dependencies.get("occupation"),
        "disorder": dependencies.get("disorder"),
        "type": dependencies.get("type"),
    }
    
    sys = langfuse.get_prompt("profile/sys/trigger", label="production")
    sys = sys.compile(**sys_args)
    user = langfuse.get_prompt("profile/user/trigger", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="auto_thoughts", as_type="span")
def auto_thoughts(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/auto_thoughts", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/auto_thoughts", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="coping_strategies", as_type="span")
def coping_strategies(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/coping_strategies", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/coping_strategies", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="behavior", as_type="span")
def behavior(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/behavior", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/behavior", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="impact", as_type="span")
def impact(dependencies, instructions, user_id, user_name, settings):
    # args = dependencies
    # args["user_instructions"] = instructions
    # sys = langfuse.get_prompt("profile/sys/impact", label="production")
    # sys = sys.compile()
    # user = langfuse.get_prompt("profile/user/impact", label="production")
    # user = user.compile(**args)
    
    # langfuse.update_current_trace(metadata=args,
    #                               user_id=str(user_name))
    
    # return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content
    return "The patient's symptoms have led to significant impairment in social and occupational functioning."


@observe(name="intake", as_type="span")
def intake(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/intake", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/intake", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="childhood_history", as_type="span")
def childhood_history(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/history", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/history/childhood", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="education_history", as_type="span")
def education_history(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/history", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/history/education", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="occupation_history", as_type="span")
def occupation_history(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/history", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/history/occupation", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="relationship_history", as_type="span")
def relationship_history(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/history", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/history/relationship", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="medical_history", as_type="span")
def medical_history(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/history", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/history/medical", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="personal_history", as_type="span")
def personal_history(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/history", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/history/personal", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="family_tree", as_type="span")
def family_tree(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/history", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/history/family_tree", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    userObj = User.objects.get(id=user_id)
    userSettings = userObj.newSessionSettings
    temperature = 0.2
    model = userSettings.model
    max_tokens = userSettings.max_tokens
    
    settings = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="timeline", as_type="span")
def timeline(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/history", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/history/timeline", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    userObj = User.objects.get(id=user_id)
    userSettings = userObj.newSessionSettings
    temperature = 0.2
    model = userSettings.model
    max_tokens = userSettings.max_tokens
    
    settings = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="vignette", as_type="span")
def vignette(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/vignette", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/vignette", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="session_history", as_type="span")
def session_history(dependencies, instructions, user_id, user_name, settings):
    args = dependencies
    args["user_instructions"] = instructions
    sys = langfuse.get_prompt("profile/sys/history", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/history/session", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content

@observe(name="profile_summary", as_type="span")
def profile_summary(dependencies, instructions, user_id, user_name, settings):
    
    print(settings)
    
    args = {
        "vignette": settings,
    }
    
    sys = langfuse.get_prompt("profile/sys/summary", label="production")
    sys = sys.compile()
    user = langfuse.get_prompt("profile/user/summary", label="production")
    user = user.compile(**args)
    
    langfuse.update_current_trace(metadata=args,
                                  user_id=str(user_name))
    
    summary_settings = {
        "model": "qwen3:32b",  # Use a more powerful model for the summary step
        "temperature": 0.3,     # Lower temperature for more coherent summaries
        "max_tokens": 1000,    # Allow for longer summaries
    }
    
    return LLM.call("autogenerate", sys=sys, user=user, settings=summary_settings, interview_id=None, user_id=user_id, metadata=None, tools=False).content