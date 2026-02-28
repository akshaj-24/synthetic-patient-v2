import random
import faker

fake = faker.Faker()


def generateField(field, dependencies):
    
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
        
        case 'education':
            age = dependencies.get('age')
            return randomEducation(int(age))
        
        case 'occupation':
            edu = dependencies.get('education')
            return randomOccupation(edu)
        
        case 'disorder':
            return randomDisorder()
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
        
        
        case 'session_history':
            
            # IMPLEMENT IF FORM HAS TEXT INPUT FOR SESSION HISTORY THEN USE CALL LLM 
            return "No prior sessions with this patient."
        
        case __:
            return "Error autogenerating field"



def randomAge():
    return random.randint(18, 80)

def randomGender():
    return random.choice(['Male', 'Female', 'Non-binary', 'Transgender'])

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









