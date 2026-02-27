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
        
        # case 'marital_status':
        
        # case 'education':
        #     age = dependencies.get('age')
        #     return randomEducation(age)
        
        case 'session_history':
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