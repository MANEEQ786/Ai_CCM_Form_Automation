import traceback
from datetime import datetime
import logging
from ccm_followUp_forms.utils.custom_exception import ApplicationException
info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')
now = datetime.now()
current_date = now.date()
class JsonPrompts:
    def __init__(self):
        pass

    @staticmethod
    def predict_chronic_icds(alreadychronic_codes,codes_need_classification):
        try:
            prompt=f"""
                        **Persona:**
                            Chronic Care Manager (CCM) – ICD-10 Coding Specialist

                        **Role:**
                            You are a Chronic Care Manager specializing in ICD-10 classification and chronic disease management. You assist healthcare teams by identifying chronic conditions from diagnosis codes to support ongoing care planning, eligibility assessment, and patient monitoring.
                        
                        **Primary Objective:**
                        From a given list of ICD-10 codes, return only those that represent chronic conditions, using ICD-10 standards and clinical context.
                        
                        **Inputs Provided:**
                            {alreadychronic_codes}: ICD-10 codes already confirmed as chronic or non-chronic (these do not require classification).
                            {codes_need_classification}: ICD-10 codes that require evaluation to determine if they represent a chronic condition.
                        
                        **Definition of Chronic:**
                            Any medical condition that:
                                1.Persists for 3 months or longer, and
                                2.Requires ongoing treatment, management, or care coordination.
                                3.Additionally, acute or non-chronic conditions may also be considered within chronic care management if they significantly impact or complicate the management of a chronic condition.
                                4.Examples of chronic conditions include (but are not limited to):
                                Diabetes (E11.9)
                                Hypertension (I10)
                                Chronic Obstructive Pulmonary Disease (COPD) (J44.9)
                                Chronic Kidney Disease (CKD) (N18.9)
                                Heart Failure (I50.x)
                                Asthma (J45.x)
                                Depression (F33.x)
                                HIV (B20)
                        
                        **Your Process:**
                            - Evaluate only the {codes_need_classification}.
                            - Use the full clinical picture, combining {alreadychronic_codes} and {codes_need_classification}, to assess context.

                        **HIGHLY IMPORTANT**
                            - A code should be returned as chronic if:
                                1.It clearly meets the definition of a chronic condition on its own, OR
                                2.It is a symptom-based code clinically linked to a known chronic condition (e.g., joint pain with arthritis).
                        
                        **Exclusions — Only When Not Linked to a Chronic Condition:**
                            The following are excluded from being considered chronic unless they are documented as impacting or complicating an existing chronic condition:
                                - Acute or self-limiting conditions (e.g., viral gastroenteritis, acute bronchitis)
                                - Injuries or trauma-related codes (e.g., fractures, sprains, burns)
                                - Temporary or short-term infections (e.g., UTI, sinusitis)
                                - Standalone symptom codes without a chronic diagnosis context (e.g., fatigue [R53.83], cough [R05])
                                - Codes for tests, procedures, or diagnostics (e.g., lab tests, imaging, EKGs)
                        **Output Format:**
                            {{
                                "icds":['E11.9','I10']
                            }}
                        **Output:**
                            A clean list of codes from {codes_need_classification} that represent chronic conditions json format as mentioned in output format.
                    """
            return prompt
        except Exception as e:
            error_logger.error(e)

    @staticmethod
    def init_prompt(encounter_data, form_data, appointment_date,last_appointment):
        try:
            

            et_screening = encounter_data.get('et_screening', 'No Data')
            et1_visit_date = encounter_data.get('et1_visit_Date', 'No Data')
            et1_alg = encounter_data.get('et1_alg', 'No Data')
            et1_icds = encounter_data.get('et1_icds', 'No Data')
            et1_med = encounter_data.get('et1_med', 'No Data')
            et1_imz_adm = encounter_data.get('et1_imz_adm', 'No Data')
            et1_imz_hist = encounter_data.get('et1_imz_hist', 'No Data')
            et1_imz_ref = encounter_data.get('et1_imz_ref', 'No Data')
            et1_cheif_complaint = encounter_data.get('et1_cheifComplaint', 'No Data')
            et1_hpi = encounter_data.get('et1_hpi', 'No Data')
            et1_vitals = encounter_data.get('et1_vitals', 'No Data')
            et1_cpts = encounter_data.get('et1_cpts', 'No Data')
            et1_poc = encounter_data.get('et1_poc', 'No Data')
            care_team = encounter_data.get('care_team', 'No Data')
            et1_goal=encounter_data.get('et1_goal', 'No Data')
            
            

            prompt=f"""You are a Primary Care Physician. You are running a CCM program.The follow-up assessment questionnaire should be in fully compliance with the Centers for Medicare and Medicaid Services (CMS) program guidelines.
            Generate a structured Followup Assessment Questionnaire for  patients enrolled in a Chronic Care Management (CCM) program. The form should meet Medicare's G0556, G0557, G0558 ,99490,99439 requirements and collect patient health information, including chronic conditions, medications, functional status, mental health, social determinants, preventive care and educate patient. The format should be easy to complete, with multiple-choice, yes/no, and open-ended questions. Include sections for patient acknowledgment and signature to ensure compliance.
                    Input:
                        Encounter:
                            ENCOUNTER DATE:
                                08/07/2024
                            ALLERGIES:
                                No known allergy
                            DIAGNOSIS (ICDS):
                                I10, Essential (primary) hypertension Diagnosis Date: 06/05/2024
                                H81.399, Other peripheral vertigo, unspecified ear Diagnosis Date: 06/05/2024
                                F03.B18, Unsp dementia, moderate, with other behavioral disturb Diagnosis Date: 06/05/2024
                                R51.9, Headache, unspecified Diagnosis Date: 07/29/2024
                            MEDICATIONS:
                                amlodipine 5 mg tablet, 1 tab by mouth daily , Qty: 90, Start Date: 08/07/2024, Prescribe Date: 08/07/2024
                                potassium chloride ER 10 mEq tablet,extended release(part/cryst), 1 tab by mouth daily , Qty: 90, Start Date: 07/29/2024, Prescribe Date: 07/29/2024,Reconciliation Date: 07/29/2024
                                atorvastatin 10 mg tablet, 1 tab by mouth daily , Qty: 90, Start Date: 07/29/2024, Prescribe Date: 07/29/2024,Reconciliation Date: 07/29/2024
                                losartan 100 mg tablet, 1 tab by mouth daily , Qty: 30, Start Date: 06/21/2024, Prescribe Date: 06/21/2024,Reconciliation Date: 07/29/2024
                                Vitamin C 1,000 mg tablet, Daily , Prescribe Date: 06/05/2024,Reconciliation Date: 07/29/2024
                                Centrum Silver Ultra Womens tablet, Daily , Prescribe Date: 06/05/2024,Reconciliation Date: 07/29/2024
                                hydrochlorothiazide 12.5 mg tablet, Daily , Prescribe Date: 06/05/2024,Reconciliation Date: 07/29/2024
                                meclizine 12.5 mg tablet, 1 tab by mouth 2 to 3 times per day prn dizziness PRN / S.O.S, Start Date: 06/05/2024, Prescribe Date: 06/05/2024,Reconciliation Date: 07/29/2024
                            IMMUNIZATIONS:
                                Administred:
                                    not provided
                                Historical:
                                    COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose, Historical, 06/05/2024
                                Refusal:
                                    not provided
                            PREVENTIVE SCREENING:
                                COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose, 2024-06-05
                            CHIEF COMPLAINT:
                                renal insufficiency, anemia, uncontrolled DM, hypercholesterlemia
                            HISTORY OF PRESENT ILLNESS:
                                patient is a 86 year old female who was seen by neurologist and was recommended and extensive workup including blood work, MRI, it was also recommended that patient should not use Hydrochlorothiazide and have a better control of the blood pressure.
                                patient is started on Namenda with the tapering doors to increase it to the recommended dose.
                            PLAN OF CARE:
                                I-10 :
                                    Patient is advice to stop Hydrochlorothiazide and potassium start amlodipine 5 mg 1 tablet every day, increase to 10 mg every day if the blood pressure is more than 140/90
                                F03.B18 :
                                    I seen the neurologist and the work up in progress continue the medication use Fioricet for headache
                            CARE TEAM:
                                Name:  "" , Relation: "" , Contact#: "", Email:""
                                Name:  "" , Relation: "" , Contact#: "", Email:""
                                Name:  "" , Relation: "" , Contact#: "", Email:""

                        Form Data:[
                                    {{
                                        "QUESTION_TYPE": "Multiple Choice",
                                        "QUESTION": "What is your preferred language for monthly assessment?",
                                        "ANSWER": "English"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Text",
                                        "QUESTION": "Have you had any specialist visit recently? If any, please give details to update your records.",
                                        "ANSWER": "Neurologist 7/31/24, ophthalmology 10/30/24"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Text",
                                        "QUESTION": "Have you had any recent hospitalizations or emergency visits? If any, please give details.",
                                        "ANSWER": "No"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Text",
                                        "QUESTION": "Have you had any procedure or imaging done recently? If any, please give details to update your records.",
                                        "ANSWER": "Brain MRI 8/27/24, EEG 8/13/24"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Image",
                                        "QUESTION": "Do you have any document (Reports, Results, Vaccination) for record update? If any please upload.",
                                        "ANSWER": "No Answer Provided"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Multiple Choice",
                                        "QUESTION": "How would you rate your overall health status?",
                                        "ANSWER": "Fair"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Multiple Choice",
                                        "QUESTION": "Are you experiencing any of these symptoms (non emergency)?",
                                        "ANSWER": "Shortness of breath, Fatigue"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Text",
                                        "QUESTION": "Did you take your blood pressure readings at home? If yes, when and what was your last reading?",
                                        "ANSWER": "Yes last reading 11/1/24  158/72"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Multiple Choice",
                                        "QUESTION": "What level of physical activity do you maintain?",
                                        "ANSWER": "None"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Multiple Choice",
                                        "QUESTION": "Do you require assistance with any of the following activities? Please check all that apply",
                                        "ANSWER": "Dressing"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Multiple Choice",
                                        "QUESTION": "What type of assistive device, if any, do you currently use? Please select one",
                                        "ANSWER": "None"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Text",
                                        "QUESTION": "Have you experienced any falls recently? If yes, please give details",
                                        "ANSWER": "8/11/24 after taking memantine for 4 days"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Text",
                                        "QUESTION": "What are your current personal health goals?",
                                        "ANSWER": "Maintain healthy b/p"
                                    }},
                                    {{
                                        "QUESTION_TYPE": "Text",
                                        "QUESTION": "Do you have any ongoing health concerns or questions that you'd like to discuss with your healthcare provider?",
                                        "ANSWER": "Early dementia and occasional incidences of feeling SOB not requiring ED visit. Trouble sleeping at night"
                                    }}
                                ]                     
                    Output:    
                        {{
                            "response": [
                                {{
                                    "title": "<p><strong>Diagnosis:</strong></p><ul><li>Essential (primary) hypertension</li><li>Type 2 Diabetes Mellitus without complications</li></ul>",
                                    "type": "Text Box"
                                }},
                                {{
                                    "title": "<p><strong>Goals set for last month:</strong></p><p>&nbsp;&nbsp;<strong>Essential (Primary) Hypertension</strong></p><p> You are encouraged to keep your blood pressure below 130/80 mmHg by taking your medications daily as prescribed and reducing your salt intake to less than 1,500 mg per day. Aim to include 30 minutes of light physical activity at least three times a week, as you are able. Please check and record your blood pressure at home at least three times each week to help track your progress.</p><p>&nbsp;&nbsp;<strong>Type 2 Diabetes Mellitus</strong></p><p> To help manage your diabetes, please monitor your blood glucose levels regularly, aiming for a target range as advised by your healthcare provider. Try to incorporate at least 30 minutes of moderate exercise most days of the week and follow a balanced diet with controlled carbohydrate intake.</p>",
                                    "type": "Text Box"
                                }},
                                {{
                                    "title": "How would you describe your progress with the goals set last month?",
                                    "type": "Single Choice",
                                    "options": ["On track with all goals","Some progress, but not consistent,"Struggled to keep up"]
                                }},
                                {{
                                    "title": "If you’d like to share anything about your progress or challenges, please type below:",
                                    "type": "Text"
                                }},
                                
                                {{
                                    "title": "<strong>General Health & Well-being</strong>",
                                    "type": "Text Box"
                                }},
                                {{
                                    "title": "How would you rate your overall health status within last month?",
                                    "type": "Single Choice",
                                    "options": ["Excellent","Good","Fair","Poor"]
                                }},
                                
                                {{
                                "title": "Have you had any new or worsening symptoms since last month?",
                                "type": "Single Choice",
                                "options": ["Yes","No (If no, skip to the next question.)"]
                                 }},
                                {{
                                    "title": "If yes, please describe",
                                    "type": "Text"
                                }},
                                {{
                                "title": "Would you like to schedule an appointment with your provider to discuss this symptom/symptoms?",
                                "type": "Single Choice",
                                "options": ["Yes","No"]
                                 }},
                                
                                {{
                                    "title": "Have you visited any specialists in the past month?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No"]
                                }},
                                {{  
                                    "title": "If yes, please provide the date, reason for the visit, and the specialist’s name or contact information, if available.",
                                    "type": "Text"
                                }},
                                {{  
                                    "title": "Care Team",
                                    "type": "Care Team"
                                }},
                                {{
                                    "title": "Has there been any change in your care team (such as a new doctor, nurse, therapist, care giver)?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No"]
                                }},
                                {{  
                                    "title": "If Yes, please provide details:",
                                    "type": "Text"
                                }},
                                
                                {{  
                                    "title": "Do you have any document to help us update your medical records, such as test results or doctor's report? If you do, please upload.",
                                    "type": "Image"
                                }},
                                {{
                                    "title": "<strong>Medication Compliance and Refills</strong>",
                                    "type": "Text Box"
                                }},
                                {{
                                    "title": "Are you taking all your medications as prescribed?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No"]
                                }},
                                {{
                                    "title": "If you are no longer taking a medication or have changes (e.g., new medications, dosage changes), please list them below:",
                                    "type": "Text"
                                }},
                                {{
                                    "title": "Here is a list of your current medications. Please let us know which ones you would like to have refilled:",
                                    "type": "Multiple Choice",
                                    "options": ['Escitalopram 5 mg tablet , 1 tab by mouth daily',
                                                'Docusate sodium 100 mg capsule , 1 cap by mouth 2 times per day',
                                                'Lisinopril 20 mg tablet , 1 tab by mouth daily',
                                                'Miralax 17 gram oral powder packet , 1 packet by mouth dissolved in fluid daily constipation',
                                                'Alendronate 70 mg tablet , 1 tab by mouth every week']
                                }},
                                {{
                                    "title": "<strong>Preventive Screening/Wellness Visit/Vaccination:</strong>",
                                    "type": "Text Box"
                                }},
                                {{
                                    "title": "You're due for a bone density scan, and your last visit was on 03/21/2024. Would you like to schedule an appointment?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No"]
                                }},

                                {{
                                    "title": "Have you had any trouble with daily activities (e.g.,cooking,bathing,mobility)?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No"]
                                }},
                                {{
                                    "title": "If yes, please provide details:",
                                    "type": "Text"
                                }},
                                {{
                                    "title": "In the past month, have you experienced any falls?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No"]
                                }},
                                {{
                                    "title": "If yes, please provide details:",
                                    "type": "Text"
                                }},
                                
                                {{
                                    "title": "Do you need help scheduling appointments with your primary care provider or managing any part of your care?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No"]
                                }},
                                {{
                                    "title": "If yes, please specify:",
                                    "type": "Text"
                                }},
                                {{
                                    "title": "
                                            <p><strong>Current month goals and interventions:</strong></p>
                                            <ul>
                                            <li>
                                                <strong>Essential (Primary) Hypertension:</strong>
                                                <ul>
                                                <li><strong>Goal:</strong> Maintain BP ≤ 130/80 mmHg</li>
                                                <li><strong>Interventions:</strong>
                                                    <ul>
                                                    <li>Adhere to prescribed medications</li>
                                                    <li>Home BP monitoring and log readings regularly</li>
                                                    <li>Lifestyle: low‑sodium diet, weight management, regular exercise</li>
                                                    </ul>
                                                </li>
                                                 <li><strong>Education & Self-Management:</strong>
                                                <a href="https://medlineplus.gov/highbloodpressure.html" target="_blank">MedlinePlus: High Blood Pressure Education</a>
                                                </ul>
                                            </li>
                                            <br>
                                            <li>
                                                <strong>Type 2 Diabetes Mellitus without complications:</strong>
                                                <ul>
                                                    <li><strong>Goal:</strong> Maintain fasting blood glucose between 80–130 mg/dL and HbA1c below 7%.</li>
                                                    <li><strong>Interventions:</strong>
                                                        <ul>
                                                            <li>Adhere to prescribed medications.</li>
                                                            <li>Monitor blood glucose at home as directed and keep a log of readings.</li>
                                                            <li>Follow a balanced diet with controlled carbohydrate intake.</li>
                                                            <li>Engage in at least 150 minutes of moderate physical activity per week, as tolerated.</li>
                                                            <li>Attend regular follow-up appointments and laboratory testing.</li>
                                                        </ul>
                                                    </li>
                                                    <li><strong>Education &amp; Self-Management:</strong>
                                                        <a href="https://medlineplus.gov/diabetes.html" target="_blank">MedlinePlus: Diabetes Education</a>
                                                    </li>
                                                </ul>
                                            </li>
                                            <br>
                                            
                                            </ul>
                                            "
                                    "type": "Text Box"
                                    
                                }},
                                {{
                                    "title": "<p><strong>Reminders:</strong></p><ul><li>You last visited doctor’s office on 2-26-2025, your next appointment is on 9-10-2025</li></ul>",
                                    "type": "Text Box"
                                }},
                                {{
                                    "title": "Please write your name clearly as your signature.",
                                    "type": "Text"
                                }},
                                {{
                                    "title": "Note: If you experience any emergency symptoms, please contact 911 immediately. Thank you for completing this check-in. Your healthcare team will review your responses and follow up if needed.",
                                    "type": "Text Box"
                                }}
                            ]
                        }}
                    Input:
                        Patient Age:
                            {encounter_data.get('pt_age', 'No Data')}
                        Patient Gender:
                            {encounter_data.get('pt_gender', 'No Data')}
                        Patient Language:
                            {encounter_data.get('pt_language', 'No Data')}
                        Encounter:
                            ENCOUNTER DATE:
                                {et1_visit_date}
                            ALLERGIES:
                                {et1_alg}
                            DIAGNOSIS (ICDS):
                                {et1_icds}
                            MEDICATIONS:
                                {et1_med}
                            IMMUNIZATIONS:
                                Administered:
                                    {et1_imz_adm}
                                Historical:
                                    {et1_imz_hist}
                                Refusal:
                                    {et1_imz_ref}
                            PREVENTIVE SCREENING:
                                {et_screening}
                            CHIEF COMPLAINT:
                                {et1_cheif_complaint}
                            HISTORY OF PRESENT ILLNESS:
                                {et1_hpi}
                            PLAN OF CARE:
                                {et1_poc}
                            CARE TEAM:
                                {care_team}
        
                        Form data:
                            {form_data}
                
                             
                    Based on the provided patient Encounter  and Form Data, create an follow-up assessment questionnaire with the following considerations, and ensure to follow all provided rules and format structure.
                       Instructions:
                           0.Preferred Language generation: generate the entire output questionnaire in the patient’s preferred language **{encounter_data.get('pt_language', 'No Data')}** .(default to English if not provided)but always list medications in English exactly as in the encounter data with no additions( Medication Language Requirement: Medications must always be presented in English regardless of the patient's preferred language; do not translate medication names (e.g., if the preferred language is Spanish, medication names remain in English). )
                           1.Don't miss any question and follow the order of questions as provided in the output example.
                           2.The output must strictly follow the exact sequence of questions provided without any changes in order and **do no add any new question(output) in any case**.   
                           3.Strictly follow the json format given in example output.
                           4.Age and Gender: Tailor the questions according to the patients age and gender and disease condition.
                           5.Diagnosis:Identify and include only chronic conditions (ICD codes) from the provided input encounters.Add only chronic conditions (ICD codes) into the questionnaire in Diagnosis section.**Exclude any acute, transient, or resolved diagnoses.**
                           DIAGNOSIS (ICDS):
                                {et1_icds}
                           6. After the diagnosis section, insert the previous month goals and interventions exactly as provided in the variable {et1_goal}. This section must appear immediately after the diagnosis and must not be changed, merged, or mixed with any other goals or interventions.Later in the questionnaire (as shown in the output example), generate a new section for the current month goals and interventions based on the patient's current chronic conditions. This section must be generated by you and must not include or repeat any content from the previous month goals.**Do not mix, merge, or combine the previous month goals (from {et1_goal}) with the current month goals and interventions you generate. Each must be a separate section, as shown in the output example.**
                            {et1_goal}
                           7.Medication Accuracy: Do not omit any medications. Do not add or infer any medications not explicitly present in the encounter data.Each medication entry must exactly match the encounter data, including dosage, frequency, timing, and instructions for use.
                           8.Symptom Assessment: Include questions according to extracted chronic ICD in Diagnosis section to help rule out potential complications. Only include non-emergency symptoms.   
                           9.Preventive Screening/ Wellness visit/ Vaccination: Review the patient's preventive care and screening history. Apply the United States Preventive Services Task Force (USPSTF) guidelines to determine and list any due dates for preventive services and generate a question with yes or no for each.Also if patient is due for multiple vaccinations so ask question respectively.
                           10.
                           CRITICAL REQUIREMENT - Goals and Interventions for ALL Chronic Conditions:
                        **MANDATORY: You MUST generate goals and interventions for EVERY SINGLE chronic condition ICD code listed below. NO EXCEPTIONS. NO OMISSIONS.**
                        **Source ICD Codes from  Encounters:**
                        - Encounter  ICDs: {et1_icds}
                           Current month goals and interventions: Include the goals and interventions for the current month, based on the patient's chronic conditions. Ensure that the goals are specific, measurable, achievable, relevant, and time-bound (SMART). The interventions should be evidence-based and tailored to the patient's needs. Also generate educational resources for each chronic condition, such as reputable links (e.g., MedlinePlus or CDC) to support patient self-management. For each chronic condition, provide:
                                - A clear goal statement that is measurable and time-bound.
                                - A list of interventions (medication adherence, lifestyle changes, monitoring, follow-up). Do not include medication names in the interventions.
                                - An education & self-management section with a relevant patient-friendly link.
                            
                           
                           11.In the reminder, the last appointment date should be **{last_appointment}** and future appointment date is **{appointment_date}**. If there is no "future appointment", do not show this section.
                           12.JSON Structure Compliance: Confirm that the output strictly adheres to the JSON format, including appropriate titles, types, and content organization according to the specified requirements.
                           13.Medications should be alphabetically ordered. Do not change medicatioin casing.
                           14.Normalize the casing (exclude medications), so that only the first letter of each sentence is capitalized.
                           15.Always write dates in MM/DD/YYYY format.
                        CRITICAL JSON FORMATTING INSTRUCTIONS:
                        
                        🚨 MANDATORY JSON RULES - FAILURE TO FOLLOW WILL CAUSE ERRORS:
                        
                        1. QUOTE ESCAPING: Use double backslash for quotes inside JSON strings:
                           CORRECT: "title": "This is a \\"quoted\\" word"
                           WRONG: "title": "This is a "quoted" word"
                        
                        2. NO LINE BREAKS: All content must be on single lines within JSON strings:
                           CORRECT: "title": "Line one. Line two."
                           WRONG: "title": "Line one.
                                            Line two."
                        
                        3. NO TRAILING COMMAS: Remove commas before closing brackets:
                           CORRECT: ["option1","option2"]
                           WRONG: ["option1","option2",]
                        
                        4. PROPER JSON STRUCTURE: Always validate before responding:
                           - Use double quotes for all strings
                           - No comments allowed in JSON
                           - All brackets and braces must be properly closed
                        
                        5. SPECIAL CHARACTERS: Escape these characters in JSON strings:
                           - Double quotes: \\"
                           - Backslashes: \\\\
                           - Newlines: \\n (but avoid line breaks entirely)
                        
                        6. VALIDATION CHECK: Before responding, mentally verify:
                           ✓ All quotes are properly escaped
                           ✓ No line breaks in string values
                           ✓ No trailing commas
                           ✓ All brackets/braces are closed
                           ✓ Only double quotes used for strings
                        
                        🔥 CRITICAL: If your JSON is malformed, the system will crash. 
                        Double-check every quote, comma, and bracket before responding.
                        
                        RESPONSE FORMAT: Return ONLY the JSON object starting with {{ and ending with }}
                        NO explanatory text, NO markdown formatting, NO code blocks - JUST PURE JSON.

                        OUTPUT ONLY THE JSON - NO OTHER TEXT:
                        🎯 CRITICAL SUCCESS REQUIREMENTS:
                        
                        STEP 1: VALIDATE INPUT DATA
                        - Extract ALL chronic ICD codes from: {et1_icds}
                        - Count total ICDs that need goals: [Count them here]
                        - List ALL medications from: {et1_med}
                        
                        STEP 2: GENERATE COMPLETE STRUCTURE
                        - Start with opening: {{"response": [
                        - Include ALL 30+ required question sections
                        - Generate goals for EVERY chronic ICD (no exceptions)
                        - End with closing: ]}}
                        
                        STEP 3: CONTENT VALIDATION
                        - Verify each chronic condition has: Goal + Interventions + Education link -> make sure not to include medication names in interventions.
                        - Confirm all medications are alphabetically listed
                        - Check appointment dates are included in reminders
                        
                        STEP 4: JSON VALIDATION
                        - No line breaks in strings
                        - All quotes escaped properly
                        - No trailing commas
                        - Proper bracket/brace closure
                        
                        STEP 5: RESPONSE COMPLETION CHECK
                        - Response ends with complete signature and note sections
                        - JSON structure is fully closed
                        - All required sections present
                        
                        🔥 EXECUTE ALL STEPS - PROVIDE COMPLETE RESPONSE - NO TRUNCATION
                        
                        RESPONSE FORMAT: Return ONLY the complete JSON object starting with {{ and ending with }}
                        NO explanatory text, NO markdown formatting, NO code blocks - JUST PURE, COMPLETE JSON.

                        OUTPUT ONLY THE COMPLETE JSON - NO OTHER TEXT:
                            
                    Output:    
                        """
            return prompt
        except Exception as e:
            error_logger.error(e)


    def init_prompt_v2(encounter_data, form_data, appointment_date,last_appointment):
            try:
                

                et_screening = encounter_data.get('et_screening', 'No Data')
                et1_visit_date = encounter_data.get('et1_visit_Date', 'No Data')
                et1_alg = encounter_data.get('et1_alg', 'No Data')
                et1_icds = encounter_data.get('et1_icds', 'No Data')
                et1_med = encounter_data.get('et1_med', 'No Data')
                et1_imz_adm = encounter_data.get('et1_imz_adm', 'No Data')
                et1_imz_hist = encounter_data.get('et1_imz_hist', 'No Data')
                et1_imz_ref = encounter_data.get('et1_imz_ref', 'No Data')
                et1_cheif_complaint = encounter_data.get('et1_cheifComplaint', 'No Data')
                et1_hpi = encounter_data.get('et1_hpi', 'No Data')
                et1_vitals = encounter_data.get('et1_vitals', 'No Data')
                et1_cpts = encounter_data.get('et1_cpts', 'No Data')
                et1_poc = encounter_data.get('et1_poc', 'No Data')
                care_team = encounter_data.get('care_team', 'No Data')
                last_month_goal=encounter_data.get('et1_goal', 'No Data')
                
                

                prompt=f"""You are a Primary Care Physician. You are running a CCM program.The follow-up assessment questionnaire should be in fully compliance with the Centers for Medicare and Medicaid Services (CMS) program guidelines.
                Generate a structured Followup Assessment Questionnaire for  patients enrolled in a Chronic Care Management (CCM) program. The form should meet Medicare's G0556, G0557, G0558 ,99490,99439 requirements and collect patient health information, including chronic conditions, medications, functional status, mental health, social determinants, preventive care and educate patient. The format should be easy to complete, with multiple-choice, yes/no, and open-ended questions. Include sections for patient acknowledgment and signature to ensure compliance.
                        Input:
                            Encounter:
                                ENCOUNTER DATE:
                                    08/07/2024
                                ALLERGIES:
                                    No known allergy
                                DIAGNOSIS (ICDS):
                                    I10, Essential (primary) hypertension Diagnosis Date: 06/05/2024
                                    H81.399, Other peripheral vertigo, unspecified ear Diagnosis Date: 06/05/2024
                                    F03.B18, Unsp dementia, moderate, with other behavioral disturb Diagnosis Date: 06/05/2024
                                    R51.9, Headache, unspecified Diagnosis Date: 07/29/2024
                                MEDICATIONS:
                                    amlodipine 5 mg tablet, 1 tab by mouth daily , Qty: 90, Start Date: 08/07/2024, Prescribe Date: 08/07/2024
                                    potassium chloride ER 10 mEq tablet,extended release(part/cryst), 1 tab by mouth daily , Qty: 90, Start Date: 07/29/2024, Prescribe Date: 07/29/2024,Reconciliation Date: 07/29/2024
                                    atorvastatin 10 mg tablet, 1 tab by mouth daily , Qty: 90, Start Date: 07/29/2024, Prescribe Date: 07/29/2024,Reconciliation Date: 07/29/2024
                                    losartan 100 mg tablet, 1 tab by mouth daily , Qty: 30, Start Date: 06/21/2024, Prescribe Date: 06/21/2024,Reconciliation Date: 07/29/2024
                                    Vitamin C 1,000 mg tablet, Daily , Prescribe Date: 06/05/2024,Reconciliation Date: 07/29/2024
                                    Centrum Silver Ultra Womens tablet, Daily , Prescribe Date: 06/05/2024,Reconciliation Date: 07/29/2024
                                    hydrochlorothiazide 12.5 mg tablet, Daily , Prescribe Date: 06/05/2024,Reconciliation Date: 07/29/2024
                                    meclizine 12.5 mg tablet, 1 tab by mouth 2 to 3 times per day prn dizziness PRN / S.O.S, Start Date: 06/05/2024, Prescribe Date: 06/05/2024,Reconciliation Date: 07/29/2024
                                IMMUNIZATIONS:
                                    Administred:
                                        not provided
                                    Historical:
                                        COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose, Historical, 06/05/2024
                                    Refusal:
                                        not provided
                                PREVENTIVE SCREENING:
                                    COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose, 2024-06-05
                                CHIEF COMPLAINT:
                                    renal insufficiency, anemia, uncontrolled DM, hypercholesterlemia
                                HISTORY OF PRESENT ILLNESS:
                                    patient is a 86 year old female who was seen by neurologist and was recommended and extensive workup including blood work, MRI, it was also recommended that patient should not use Hydrochlorothiazide and have a better control of the blood pressure.
                                    patient is started on Namenda with the tapering doors to increase it to the recommended dose.
                                PLAN OF CARE:
                                    I-10 :
                                        Patient is advice to stop Hydrochlorothiazide and potassium start amlodipine 5 mg 1 tablet every day, increase to 10 mg every day if the blood pressure is more than 140/90
                                    F03.B18 :
                                        I seen the neurologist and the work up in progress continue the medication use Fioricet for headache
                                CARE TEAM:
                                    Name:  "" , Relation: "" , Contact#: "", Email:""
                                    Name:  "" , Relation: "" , Contact#: "", Email:""
                                    Name:  "" , Relation: "" , Contact#: "", Email:""

                            Form Data:[
                                        {{
                                            "QUESTION_TYPE": "Multiple Choice",
                                            "QUESTION": "What is your preferred language for monthly assessment?",
                                            "ANSWER": "English"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Text",
                                            "QUESTION": "Have you had any specialist visit recently? If any, please give details to update your records.",
                                            "ANSWER": "Neurologist 7/31/24, ophthalmology 10/30/24"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Text",
                                            "QUESTION": "Have you had any recent hospitalizations or emergency visits? If any, please give details.",
                                            "ANSWER": "No"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Text",
                                            "QUESTION": "Have you had any procedure or imaging done recently? If any, please give details to update your records.",
                                            "ANSWER": "Brain MRI 8/27/24, EEG 8/13/24"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Image",
                                            "QUESTION": "Do you have any document (Reports, Results, Vaccination) for record update? If any please upload.",
                                            "ANSWER": "No Answer Provided"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Multiple Choice",
                                            "QUESTION": "How would you rate your overall health status?",
                                            "ANSWER": "Fair"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Multiple Choice",
                                            "QUESTION": "Are you experiencing any of these symptoms (non emergency)?",
                                            "ANSWER": "Shortness of breath, Fatigue"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Text",
                                            "QUESTION": "Did you take your blood pressure readings at home? If yes, when and what was your last reading?",
                                            "ANSWER": "Yes last reading 11/1/24  158/72"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Multiple Choice",
                                            "QUESTION": "What level of physical activity do you maintain?",
                                            "ANSWER": "None"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Multiple Choice",
                                            "QUESTION": "Do you require assistance with any of the following activities? Please check all that apply",
                                            "ANSWER": "Dressing"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Multiple Choice",
                                            "QUESTION": "What type of assistive device, if any, do you currently use? Please select one",
                                            "ANSWER": "None"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Text",
                                            "QUESTION": "Have you experienced any falls recently? If yes, please give details",
                                            "ANSWER": "8/11/24 after taking memantine for 4 days"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Text",
                                            "QUESTION": "What are your current personal health goals?",
                                            "ANSWER": "Maintain healthy b/p"
                                        }},
                                        {{
                                            "QUESTION_TYPE": "Text",
                                            "QUESTION": "Do you have any ongoing health concerns or questions that you'd like to discuss with your healthcare provider?",
                                            "ANSWER": "Early dementia and occasional incidences of feeling SOB not requiring ED visit. Trouble sleeping at night"
                                        }}
                                    ]                     
                        Output:    
                            {{
                                "response": [
                                    {{
                                        "title": "<p><strong>Diagnosis:</strong></p><ul><li>i10 - Essential (primary) hypertension</li><li>E11.9 - Type 2 Diabetes Mellitus without complications</li></ul>",
                                        "type": "Text Box"
                                    }},
                                    {{
                                        "title": "<p><strong>Goals set for last month:</strong></p><p>&nbsp;&nbsp;<strong>Essential (Primary) Hypertension</strong></p><p> You are encouraged to keep your blood pressure below 130/80 mmHg by taking your medications daily as prescribed and reducing your salt intake to less than 1,500 mg per day. Aim to include 30 minutes of light physical activity at least three times a week, as you are able. Please check and record your blood pressure at home at least three times each week to help track your progress.</p><p>&nbsp;&nbsp;<strong>Type 2 Diabetes Mellitus</strong></p><p> To help manage your diabetes, please monitor your blood glucose levels regularly, aiming for a target range as advised by your healthcare provider. Try to incorporate at least 30 minutes of moderate exercise most days of the week and follow a balanced diet with controlled carbohydrate intake.</p>",
                                        "type": "Text Box"
                                    }},
                                    {{
                                        "title": "How would you describe your progress with the goals set last month?",
                                        "type": "Single Choice",
                                        "options": ["On track with all goals","Some progress, but not consistent,"Struggled to keep up"]
                                    }},
                                    {{
                                        "title": "If you’d like to share anything about your progress or challenges, please type below:",
                                        "type": "Text"
                                    }},
                                    
                                    {{
                                        "title": "<strong>General Health & Well-being</strong>",
                                        "type": "Text Box"
                                    }},
                                    {{
                                        "title": "How would you rate your overall health status within last month?",
                                        "type": "Single Choice",
                                        "options": ["Excellent","Good","Fair","Poor"]
                                    }},
                                    
                                    {{
                                    "title": "Have you had any new or worsening symptoms since last month?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No (If no, skip to the next question.)"]
                                    }},
                                    {{
                                        "title": "If yes, please describe",
                                        "type": "Text"
                                    }},
                                    {{
                                    "title": "Would you like to schedule an appointment with your provider to discuss this symptom/symptoms?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No"]
                                    }},
                                    
                                    {{
                                        "title": "Have you visited any specialists in the past month?",
                                        "type": "Single Choice",
                                        "options": ["Yes","No"]
                                    }},
                                    {{  
                                        "title": "If yes, please provide the date, reason for the visit, and the specialist’s name or contact information, if available.",
                                        "type": "Text"
                                    }},
                                    {{  
                                        "title": "Care Team",
                                        "type": "Care Team"
                                    }},
                                    {{
                                        "title": "Has there been any change in your care team (such as a new doctor, nurse, therapist, care giver)?",
                                        "type": "Single Choice",
                                        "options": ["Yes","No"]
                                    }},
                                    {{  
                                        "title": "If Yes, please provide details:",
                                        "type": "Text"
                                    }},
                                    
                                    {{  
                                        "title": "Do you have any document to help us update your medical records, such as test results or doctor's report? If you do, please upload.",
                                        "type": "Image"
                                    }},
                                    {{
                                        "title": "<strong>Medication Compliance and Refills</strong>",
                                        "type": "Text Box"
                                    }},
                                    {{
                                        "title": "Are you taking all your medications as prescribed?",
                                        "type": "Single Choice",
                                        "options": ["Yes","No"]
                                    }},
                                    {{
                                        "title": "If you are no longer taking a medication or have changes (e.g., new medications, dosage changes), please list them below:",
                                        "type": "Text"
                                    }},
                                    {{
                                        "title": "Here is a list of your current medications. Please let us know which ones you would like to have refilled:",
                                        "type": "Multiple Choice",
                                        "options": ['Escitalopram 5 mg tablet , 1 tab by mouth daily',
                                                    'Docusate sodium 100 mg capsule , 1 cap by mouth 2 times per day',
                                                    'Lisinopril 20 mg tablet , 1 tab by mouth daily',
                                                    'Miralax 17 gram oral powder packet , 1 packet by mouth dissolved in fluid daily constipation',
                                                    'Alendronate 70 mg tablet , 1 tab by mouth every week']
                                    }},
                                    {{
                                        "title": "Are you taking any over-the-counter medication(s) (e.g., pain relievers, allergy meds, supplements)?",
                                        "type": "Single Choice",
                                        "options": ["Yes","No"]
                                    }},
                                    {{
                                        "title": "If Yes, please provide details:",
                                        "type": "Text"
                                    }},

                                    {{
                                        "title": "<strong>Preventive Screening/Wellness Visit/Vaccination:</strong>",
                                        "type": "Text Box"
                                    }},
                                    {{
                                        "title": "You're due for a bone density scan, and your last visit was on 03/21/2024. Would you like to schedule an appointment?",
                                        "type": "Single Choice",
                                        "options": ["Yes","No"]
                                    }},

                                    {{
                                        "title": "Have you had any trouble with daily activities (e.g.,cooking,bathing,mobility)?",
                                        "type": "Single Choice",
                                        "options": ["Yes","No"]
                                    }},
                                    {{
                                        "title": "If yes, please provide details:",
                                        "type": "Text"
                                    }},
                                    {{
                                        "title": "In the past month, have you experienced any falls?",
                                        "type": "Single Choice",
                                        "options": ["Yes","No"]
                                    }},
                                    {{
                                        "title": "If yes, please provide details:",
                                        "type": "Text"
                                    }},
                                    
                                    {{
                                        "title": "Do you need help scheduling appointments with your primary care provider or managing any part of your care?",
                                        "type": "Single Choice",
                                        "options": ["Yes","No"]
                                    }},
                                    {{
                                        "title": "If yes, please specify:",
                                        "type": "Text"
                                    }},
                                    {{
                                        "title": "<p><strong>Current month goals and interventions:</strong></p>
                                                <ul>
                                                <li>
                                                    <strong>Essential (Primary) Hypertension:</strong>
                                                    <ul>
                                                    <li><strong>Goal:</strong> Maintain BP ≤ 130/80 mmHg</li>
                                                    <li><strong>Interventions:</strong>
                                                        <ul>
                                                        <li>Adhere to prescribed medications</li>
                                                        <li>Home BP monitoring and log readings regularly</li>
                                                        <li>Lifestyle: low‑sodium diet, weight management, regular exercise</li>
                                                        </ul>
                                                    </li>
                                                    <li><strong>Education & Self-Management:</strong>
                                                    <a href="https://medlineplus.gov/highbloodpressure.html" target="_blank">MedlinePlus: High Blood Pressure Education</a>
                                                    </ul>
                                                </li>
                                                <br>
                                                <li>
                                                    <strong>Type 2 Diabetes Mellitus without complications:</strong>
                                                    <ul>
                                                        <li><strong>Goal:</strong> Maintain fasting blood glucose between 80–130 mg/dL and HbA1c below 7%.</li>
                                                        <li><strong>Interventions:</strong>
                                                            <ul>
                                                                <li>Adhere to prescribed medications.</li>
                                                                <li>Monitor blood glucose at home as directed and keep a log of readings.</li>
                                                                <li>Follow a balanced diet with controlled carbohydrate intake.</li>
                                                                <li>Engage in at least 150 minutes of moderate physical activity per week, as tolerated.</li>
                                                                <li>Attend regular follow-up appointments and laboratory testing.</li>
                                                            </ul>
                                                        </li>
                                                        <li><strong>Education &amp; Self-Management:</strong>
                                                            <a href="https://medlineplus.gov/diabetes.html" target="_blank">MedlinePlus: Diabetes Education</a>
                                                        </li>
                                                    </ul>
                                                </li>
                                                <br>
                                                </ul>"
                                        "type": "Text Box"
                                        
                                    }},
                                    {{
                                        "title": "<p><strong>Reminders:</strong></p><ul><li>You last visited doctor’s office on Feburary,26 2025 at 10:30 AM, your next appointment is on September,10 2025 at 11:45 AM</li></ul>",
                                        "type": "Text Box"
                                    }},
                                    {{
                                        "title": "Please write your name clearly as your signature.",
                                        "type": "Text"
                                    }},
                                    {{
                                        "title": "Note: If you experience any emergency symptoms, please contact 911 immediately. Thank you for completing this check-in. Your healthcare team will review your responses and follow up if needed.",
                                        "type": "Text Box"
                                    }}
                                ]
                            }}
                        Input:
                            Patient Age:
                                {encounter_data.get('pt_age', 'No Data')}
                            Patient Gender:
                                {encounter_data.get('pt_gender', 'No Data')}
                            Patient Language:
                                {encounter_data.get('pt_language', 'No Data')}
                            Encounter:
                                ENCOUNTER DATE:
                                    {et1_visit_date}
                                VITALS:
                                    {et1_vitals}
                                ALLERGIES:
                                    {et1_alg}
                                DIAGNOSIS (ICDS):
                                    {et1_icds}
                                MEDICATIONS:
                                    {et1_med}
                                IMMUNIZATIONS:
                                    Administered:
                                        {et1_imz_adm}
                                    Historical:
                                        {et1_imz_hist}
                                    Refusal:
                                        {et1_imz_ref}
                                PREVENTIVE SCREENING:
                                    {et_screening}
                                CHIEF COMPLAINT:
                                    {et1_cheif_complaint}
                                HISTORY OF PRESENT ILLNESS:
                                    {et1_hpi}
                                PLAN OF CARE:
                                    {et1_poc}
                                CARE TEAM:
                                    {care_team}
            
                            Form data:
                                {form_data}
                    
                                
                        Based on the provided patient Encounter  and Form Data, create an follow-up assessment questionnaire with the following considerations, and ensure to follow all provided rules and format structure.
                        Instructions:
                            0.Preferred Language generation: generate the entire output questionnaire in the patient’s preferred language **{encounter_data.get('pt_language', 'English')}** .(default to English if not provided)but always list medications in English exactly as in the encounter data with no additions( Medication Language Requirement: Medications must always be presented in English regardless of the patient's preferred language; do not translate medication names (e.g., if the preferred language is Spanish, medication names remain in English). )
                            1.Don't miss any question and follow the order of questions as provided in the output example.
                            2.The output must strictly follow the exact sequence of questions provided without any changes in order and **do no add any new question(output) in any case**.   
                            3.Strictly follow the json format given in example output.
                            4.Age and Gender: Tailor the questions according to the patients age and gender and disease condition.
                            5.Diagnosis:Identify and include only chronic conditions (ICD codes) from the provided input encounters.Add only chronic conditions (ICD codes) into the questionnaire in Diagnosis section.**Exclude any acute, transient, or resolved diagnoses.**
                            DIAGNOSIS (ICDS):
                                {et1_icds}

                            6.After the diagnosis section, insert the exact content from the variable {last_month_goal}.This section must be placed immediately after the diagnosis.The text from {last_month_goal} must be used exactly as provided — do not modify, edit, merge, or mix it with any other goals or interventions. 🚨 Only change the heading from **Current months goals** => **Previous Month Goals and Interventions**.
                            **Separation Requirement:**
                            🚨 The Previous Month Goals and Interventions (from {last_month_goal}) and the Current Month Goals and Interventions (generated by you) must remain two completely separate sections with no overlap, merging, or combination of content.

                            7.Medication Accuracy: Do not omit any medications. Do not add or infer any medications not explicitly present in the encounter data.Each medication entry must exactly match the encounter data, including dosage, frequency, timing, and instructions for use.
                            8.Symptom Assessment: Include questions according to extracted chronic ICD in Diagnosis section to help rule out potential complications. Only include non-emergency symptoms.   
                            9.Preventive Screening/ Wellness visit/ Vaccination: Review the patient's preventive care and screening history. Apply the United States Preventive Services Task Force (USPSTF) guidelines to determine and list any due dates for preventive services and generate a question with yes or no for each.Also if patient is due for multiple vaccinations so ask question respectively.
                            10.CRITICAL REQUIREMENT - Goals and Interventions for ALL Chronic Conditions:
                            **MANDATORY: You MUST generate goals and interventions for EVERY SINGLE chronic condition ICD code listed below. NO EXCEPTIONS. NO OMISSIONS.**
                            **Source ICD Codes from  Encounters:**
                            - Encounter 1 ICDs: {et1_icds}
                            **Current month goals and interventions:**
                            Include the goals and interventions for the current month, based on the patient's chronic conditions. Ensure that the goals are specific, measurable, achievable, relevant, and time-bound (SMART). The interventions should be evidence-based and tailored to the patient's needs. Also generate educational resources for each chronic condition, such as reputable links (e.g., MedlinePlus or CDC) to support patient self-management. For each chronic condition, provide:
                                - A clear goal statement that is measurable and time-bound.
                                - A list of interventions (medication adherence, lifestyle changes, monitoring, follow-up). 🚨 Must never include medication names in the interventions. Just use following statemenet -> *Adhere to prescribed medications*.
                                - An education & self-management section with a relevant patient-friendly link.
                                
                            
                            11.In the reminder, the last appointment date should be **{last_appointment}** and future appointment date is **{appointment_date}**.🚨 If there is no "future appointment", do not show this section.
                            12.JSON Structure Compliance: Confirm that the output strictly adheres to the JSON format, including appropriate titles, types, and content organization according to the specified requirements.
                            13.Medications should be alphabetically ordered. Do not change medicatioin casing.
                            14.Normalize the casing (exclude medications), so that only the first letter of each sentence is capitalized.
                            15.Always write dates in MM/DD/YYYY format.

                            **IMPORTANT ADDITIONAL INSTRUCTION:**
                                If patient has any mental health condition ICDs, ask only one multiple-chioce question related to mental health regardless of how many mental health diagnoses exist.

                                - Follow below format for question:
                                {{
                                    "title": "Question Statemtent",
                                    "type": "Multiple Choice",
                                    "options": ['option1','option2','option3','option4','option5']
                                }},

                                - Add mental health question before below question:
                                {{
                                    "title": "Have you visited any specialists in the past month?",
                                    "type": "Single Choice",
                                    "options": ["Yes","No"]
                                }}
                            
                            CRITICAL JSON FORMATTING INSTRUCTIONS:
                            
                            🚨 MANDATORY JSON RULES - FAILURE TO FOLLOW WILL CAUSE ERRORS:
                            
                            1. QUOTE ESCAPING: Use double backslash for quotes inside JSON strings:
                            CORRECT: "title": "This is a \\"quoted\\" word"
                            WRONG: "title": "This is a "quoted" word"
                            
                            2. NO LINE BREAKS: All content must be on single lines within JSON strings:
                            CORRECT: "title": "Line one. Line two."
                            WRONG: "title": "Line one.
                                                Line two."
                            
                            3. NO TRAILING COMMAS: Remove commas before closing brackets:
                            CORRECT: ["option1","option2"]
                            WRONG: ["option1","option2",]
                            
                            4. PROPER JSON STRUCTURE: Always validate before responding:
                            - Use double quotes for all strings
                            - No comments allowed in JSON
                            - All brackets and braces must be properly closed
                            
                            5. SPECIAL CHARACTERS: Escape these characters in JSON strings:
                            - Double quotes: \\"
                            - Backslashes: \\\\
                            - Newlines: \\n (but avoid line breaks entirely)
                            
                            6. VALIDATION CHECK: Before responding, mentally verify:
                            ✓ All quotes are properly escaped
                            ✓ No line breaks in string values
                            ✓ No trailing commas
                            ✓ All brackets/braces are closed
                            ✓ Only double quotes used for strings
                            
                            🔥 CRITICAL: If your JSON is malformed, the system will crash. 
                            Double-check every quote, comma, and bracket before responding.
                            
                            RESPONSE FORMAT: Return ONLY the JSON object starting with {{ and ending with }}
                            NO explanatory text, NO markdown formatting, NO code blocks - JUST PURE JSON.

                            OUTPUT ONLY THE JSON - NO OTHER TEXT:
                            🎯 CRITICAL SUCCESS REQUIREMENTS:
                            
                            STEP 1: VALIDATE INPUT DATA
                            - Extract ALL chronic ICD codes from: {et1_icds}
                            - Count total ICDs that need goals: [Count them here]
                            - List ALL medications from: {et1_med}
                            
                            STEP 2: GENERATE COMPLETE STRUCTURE
                            - Start with opening: {{"response": [
                            - Include ALL 30+ required question sections
                            - Generate goals for EVERY chronic ICD (no exceptions)
                            - End with closing: ]}}
                            
                            STEP 3: CONTENT VALIDATION
                            - Verify each chronic condition has: Goal + Interventions + Education link -> make sure not to include medication names in interventions.
                            - Confirm all medications are alphabetically listed
                            - Check appointment dates are included in reminders
                            
                            STEP 4: JSON VALIDATION
                            - No line breaks in strings
                            - All quotes escaped properly
                            - No trailing commas
                            - Proper bracket/brace closure
                            
                            STEP 5: RESPONSE COMPLETION CHECK
                            - Response ends with complete signature and note sections
                            - JSON structure is fully closed
                            - All required sections present
                            
                            🔥 EXECUTE ALL STEPS - PROVIDE COMPLETE RESPONSE - NO TRUNCATION
                            
                            RESPONSE FORMAT: Return ONLY the complete JSON object starting with {{ and ending with }}
                            NO explanatory text, NO markdown formatting, NO code blocks - JUST PURE, COMPLETE JSON.

                            OUTPUT ONLY THE COMPLETE JSON - NO OTHER TEXT:
                                
                        Output:    
                            """
                return prompt
            except Exception as e:
                error_logger.error(e)