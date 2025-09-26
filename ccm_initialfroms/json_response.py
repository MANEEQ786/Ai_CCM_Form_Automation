import traceback
from datetime import datetime
import logging
from ccm_initialfroms.utils.custom_exception import ApplicationException
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
    def init_prompt(data):
        try:
            prompt=f"""You working as a Primary Care Physician. You are running a Chronic Care Management program, for that you are generating an initial assessment questionnaire including Care Plan goals and interventions by reviewing their past 3 encounter notes, to get an update on their current health conditions according to the Centers for Medicare and Medicaid Services program guidelines.
                Input:
                    Encounter No 1:
                        ENCOUNTER DATE:
                            08/12/2024
                        ALLERGIES:
                            Sulfa (Sulfonamide Antibiotics) ,Severe ,Anaphylaxis
                            Penicillins ,Severe ,Anaphylaxis
                        DIAGNOSIS (ICDS):
                            R45.2, Unhappiness Diagnosis Date: 08/12/2024
                            D50.8, Other iron deficiency anemias Diagnosis Date: 10/20/2020
                            D69.59, Other secondary thrombocytopenia Diagnosis Date: 09/25/2023
                            K75.81, Nonalcoholic steatohepatitis (nash) Diagnosis Date: 02/21/2023
                            J30.2, Other seasonal allergic rhinitis Diagnosis Date: 05/24/2021
                            Z95.1, Presence of aortocoronary bypass graft Diagnosis Date: 10/20/2020
                            I10, Essential (primary) hypertension Diagnosis Date: 10/20/2020
                            E11.9, Type 2 diabetes mellitus without complications Diagnosis Date: 10/20/2020
                            E78.79, Other disorders of bile acid and cholesterol metabolism Diagnosis Date: 10/20/2020
                            Z68.33, Body mass index [BMI] 33.0-33.9, adult Diagnosis Date: 10/20/2020
                        MEDICATIONS:
                            ALBUTEROL HFA (PROAIR) INHALER, inhale 2 puffs by mouth every 12 hours , Qty: 8.5, Prescribe Date:02/24/2023,Reconciliation Date: 08/12/2024
                            Tresiba FlexTouch U-200 insulin 200 unit/mL (3 mL) subcutaneous pen, 32 units QPM , Start Date: 06/21/2024, Prescribe Date:06/21/2024,Reconciliation Date: 08/12/2024
                            omeprazole 40 mg capsule,delayed release, 1 cap by mouth daily , Start Date: 06/21/2024, Prescribe Date:06/21/2024,Reconciliation Date: 08/12/2024
                            ferrous sulfate 325 mg (65 mg iron) tablet, 1 cap by mouth daily , Start Date: 06/21/2024, Prescribe Date:06/21/2024,Reconciliation Date: 08/12/2024
                            FIASP F/P 100U/ML PEN, using SSC (4 to 12 units) with TID with meals , Prescribe Date: 12/19/2023,Reconciliation Date:08/12/2024
                            REPATHA SURE 140MG/ML INJ, null , Prescribe Date: 12/19/2023,Reconciliation Date: 08/12/2024
                            carvedilol 3.125 mg tablet, take 1 tablet(3.125MG) by oral route BID , Prescribe Date: 09/26/2022,Reconciliation Date:08/12/2024
                        IMMUNIZATIONS:
                            Administred:
                                Influenza, High Dose, Administered, 09/18/2023
                                influenza, recombinant, injectable, preservative free, Administered, 09/26/2022
                                Tdap, Administered, 09/26/2022
                                influenza, injectable, quadrivalent, preservative free, Administered, 09/27/2021
                            Historical:
                                Pneumococcal, (PPSV), Historical, 12/19/2023
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 04/08/2021
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 03/11/2021
                                Shingles Vaccine-SHINGRIX, Historical,
                            Refusal:
                                not provided
                        HISTORY:
                            Social Hx:
                                not provided
                            Past Medical Hx:
                                CABG 2015
                            Risk assessment
                                Exercise: 2-5 Time/Week
                                Seatbelts: Sometimes
                                Exposure: Hepatitis
                                Feels Safe at Home: Yes
                            Past Surgical History:
                                surgery on left eye
                        PREVENTIVE SCREENING:
                            pneumococcal polysaccharide vaccine, 23 valent
                            Shingles Vaccine-SHINGRIX
                            Seasonal, trivalent, recombinant, injectable influenza vaccine, preservative free
                            tetanus toxoid, reduced diphtheria toxoid, and acellular pertussis vaccine, adsorbed
                            influenza, high dose seasonal, preservative-free
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            Influenza, injectable, quadrivalent, preservative free
                            Tdap
                            Pneumococcal, (PPSV)
                            Influenza, High Dose
                            influenza, recombinant, injectable, preservative free
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose 	
                            Mammogram
                            Mammogram W/ultrasound
                        CHIEF COMPLAINT:
                            renal insufficiency, anemia, uncontrolled DM, hypercholesterlemia
                        HISTORY OF PRESENT ILLNESS:
                            The patient is a 65-year-old female who presents for a follow-up visit. She has a history of type 2 diabetes mellitus,
                            hypertension, hyperlipidemia, iron deficiency anemia, and nonalcoholic steatohepatitis (NASH). She is currently
                            taking insulin, repatha, omeprazole She reports that her blood sugar control has been unstable, with episodes of
                            both high and low blood sugars. She also reports feeling tired, having difficulty sleeping, and experiencing low
                            mood. She has noticed some bloating and discomfort after eating certain foods. She was recently hospitalized in
                            Canada She has been having difficulty managing her blood sugars since her return and has been experiencing
                            frequent episodes of hypoglycemia. She is also concerned about her fatigue and low mood, which she believes
                            may be related to her diabetes and recent hospitalization.
                        VITAL SIGNS:
                            Height: 4 ft 10 in
                            Weight: 157 lb
                            BMI: 32.81 Obesity   
                            BP: 123/78 mmHg Position:Sitting 
                            SpO2: 98 % Flowrate: Room Air Source: On room air 
                            HR: 69  bpm	
                        
                        PROCEDURES (CPTS):
                            99214 - Office o/p est mod 30 min
                            G8417 - BMI is documented above normal parameters and a follow-up plan is documented
                            G8427 - Eligible clinician attests to documenting in the medical record they obtained, updated, or reviewed the
                            patients current medications
                            G9903 - Patient screened for tobacco use and identified as a tobacco non-user
                            G8950 - ELEVATED OR HYPERTENSIVE BLOOD PRESSURE READING DOCUMENTED, AND THE
                            INDICATED FOLLOW-UP IS DOCUMENTED
                        PLAN OF CARE:
                            E11.9 :
                            The patient will continue to monitor her blood sugars closely and adjust her insulin doses as needed. She will also meet
                            with her endocrinologist to discuss her blood sugar control and medication regimen.
                            patient has a continuous blood glucose monitor Trend will be reviewed and Medicine adjusted by the endocrinologist
                            I10 :
                            The patient will continue to take her antihypertensive medications as prescribed.
                            blood pressure is stable
                            E78.79 :
                            The patient will continue to take her repatha as prescribed.
                            lipid panel results will be obtained from the cardiologist
                            She has an appointment to see a hepatologist to discuss her NASH and liver function.
                            K75.81 :
                            The patient will continue to follow a healthy diet and exercise regularly. She will also be referred to a hepatologist to
                            discuss her NASH and liver function.
                            continue to take omeprazole
                            increase activity
                            Z68.33 :
                            The patient will be encouraged to lose weight and maintain a healthy weight. She will be referred to a dietitian to discuss
                            her diet and exercise plan.
                            R45.2
                            patient will be referred to behavioral therapy
                        CARE TEAM:
                           Name:  "" , Relation: "" , Contact#: "", Email:""
                           Name:  "" , Relation: "" , Contact#: "", Email:""
                           Name:  "" , Relation: "" , Contact#: "", Email:""
                    Encounter No 2:
                        ENCOUNTER DATE:
                            06/21/2024 
                        ALLERGIES
                            Sulfa (Sulfonamide Antibiotics) ,Severe ,Anaphylaxis
                            Penicillins ,Severe ,Anaphylaxis
                        DIAGNOSIS (ICDS): 
                            D50.8, Other iron deficiency anemias Diagnosis Date: 10/20/2020
                            D69.59, Other secondary thrombocytopenia Diagnosis Date: 09/25/2023
                            K75.81, Nonalcoholic steatohepatitis (nash) Diagnosis Date: 02/21/2023
                            J30.2, Other seasonal allergic rhinitis Diagnosis Date: 05/24/2021
                            Z95.1, Presence of aortocoronary bypass graft Diagnosis Date: 10/20/2020
                            I10, Essential (primary) hypertension Diagnosis Date: 10/20/2020
                            E11.9, Type 2 diabetes mellitus without complications Diagnosis Date: 10/20/2020
                            E78.79, Other disorders of bile acid and cholesterol metabolism Diagnosis Date: 10/20/2020
                            Z68.33, Body mass index [BMI] 33.0-33.9, adult Diagnosis Date: 10/20/2020
                        MEDICATIONS:
                            ALBUTEROL HFA (PROAIR) INHALER, inhale 2 puffs by mouth every 12 hours , Qty: 8.5, Prescribe Date:/24/2023,Reconciliation Date: 06/06/2024
                            Tresiba FlexTouch U-200 insulin 200 unit/mL (3 mL) subcutaneous pen, 26 units QPM , Start Date: 06/21/2024, Prescribe Date:06/21/2024
                            omeprazole 40 mg capsule,delayed release, 1 cap by mouth daily , Start Date: 06/21/2024, Prescribe Date: 06/21/2024
                            ferrous sulfate 325 mg (65 mg iron) tablet, 1 cap by mouth daily , Start Date: 06/21/2024, Prescribe Date: 06/21/2024
                            FIASP F/P 100U/ML PEN, using SSC (4 to 12 units) with TID with meals , Prescribe Date: 12/19/2023,Reconciliation Date:06/21/2024
                            REPATHA SURE 140MG/ML INJ, null , Prescribe Date: 12/19/2023,Reconciliation Date: 06/06/2024
                            carvedilol 3.125 mg tablet, take 1 tablet(3.125MG) by oral route BID , Prescribe Date: 09/26/2022,Reconciliation Date:06/21/2024
                        IMMUNIZATIONS:
                            Administred:
                                Influenza, High Dose, Administered, 09/18/2023
                                influenza, recombinant, injectable, preservative free, Administered, 09/26/2022
                                Tdap, Administered, 09/26/2022
                                influenza, injectable, quadrivalent, preservative free, Administered, 09/27/2021
                            Historical:
                                Pneumococcal, (PPSV), Historical, 12/19/2023
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 04/08/2021
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 03/11/2021
                                Shingles Vaccine-SHINGRIX, Historical,
                            Refusal:
                                not provided
                        HISTORY:
                            Social Hx:
                                not provided
                            Risk Assessemnt
                                Exercise: 2-5 Time/Week
                                Seatbelts: Sometimes
                                Exposure: Hepatitis
                                Feels Safe at Home: Yes
                            Past Medical Hx:
                                CABG 2015
                            Past Surgical History:
                                surgery on left eye
                        PREVENTIVE SCREENING:
                            pneumococcal polysaccharide vaccine, 23 valent
                            Shingles Vaccine-SHINGRIX
                            Seasonal, trivalent, recombinant, injectable influenza vaccine, preservative free
                            tetanus toxoid, reduced diphtheria toxoid, and acellular pertussis vaccine, adsorbed
                            influenza, high dose seasonal, preservative-free
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            Influenza, injectable, quadrivalent, preservative free
                            Tdap
                            Pneumococcal, (PPSV)
                            Influenza, High Dose
                            influenza, recombinant, injectable, preservative free
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose 	
                            Mammogram
                            Mammogram W/ultrasound
                        CHIEF COMPLAINT:
                            Transitional Care Management
                        HISTORY OF PRESENT ILLNESS:
                            A 65 years old female came for follow up on hospital admission. Patient was admitted in the hospital of Canada while she
                            was visiting her mother from 6/8-6/11/2024 for diagnosis of hypertension, iron deficiency anemia (hb on admission was
                            8.6), hyperglycemia, and liver cirrhosis due to likely to have some form of infection.
                            her hypertension was corrected by IV fluids, sugar was fluctuating, she was seen by endocrinologist and other specialist
                            while in the hospital.
                            medications were adjusted including insulin, was given short-term therapy of Lasix as a diuretic as she was having fluid
                            collection in the abdomen.
                            hypertension was probably secondary to the blood pressure medication.
                            she returned to New Jersey for 2 days to follow with all her doctors as she's traveling back to Canada again tomorrow as
                            her mother is getting some cardiac surgery done.
                            she had consulted hematologist yesterday- And her hemoglobin was 9.6- done that she's waiting for oncologist office to
                            call today to determine whether or not she needs another IV infusion.
                            she had reached out to her endocrinologist as her blood sugar is fluctuating widely- she was instructed to consult their
                            nutrition is to guide her what to eat at this time. continue to take insulin.
                            she's also planning to call her GI and hepatology soon.
                            currently she is doing well, her energy level is getting better gradually. his monitoring her blood pressure and blood sugar
                            at home. she was instructed to repeat her liver function on discharge.
                        VITAL SIGNS:
                            Height: 4 ft 10 in
                            Weight: 153 lb 2 oz
                            BMI: 32 Obesity 
                            BP: 116/62 mmHg Position: Sitting 
                            SpO2: 97 % Flowrate: Room Air Source: On room air 
                            HR: 74 bpm	
                            Pain Socre:0
                        PROCEDURES (CPTS):
                            3008F - Body mass index docd
                            3074F - Syst bp lt 130 mm hg
                            3078F - Diast bp <80 mm hg
                            36415 - ROUTINE VENIPUNCTURE
                            99495 - Transj care mgmt mod f2f 14d
                            1111F - Dschrg med/current med merge
                        PLAN OF CARE:
                            D508- repeat CBC. Airport was also done by hematologist yesterday- pending results. Patient is waiting for them
                            to call as they will decide whether or not she needs another iron infusion are not.
                            on oral iron supple.
                            K7581- LFTS and CMP Done
                            E119- she already consulted endocrinologist. repeat A1C today.
                            in the hospital her A1C was 8%.
                            I10- continue coreg 3.125mg QAM and in evening if BP is >110.
                            omeprazole for gerd like sx
                        CARE TEAM:                            
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                    Encounter No 3:
                        ENCOUNTER DATE:
                            12/19/2023
                        ALLERGIES
                            Sulfa (Sulfonamide Antibiotics) ,Severe ,Anaphylaxis
                            Penicillins ,Severe ,Anaphylaxis
                        DIAGNOSIS (ICDS):
                            K75.81, Nonalcoholic steatohepatitis (nash) Diagnosis Date: 02/21/2023
                            J30.2, Other seasonal allergic rhinitis Diagnosis Date: 05/24/2021
                            Z95.1, Presence of aortocoronary bypass graft Diagnosis Date: 10/20/2020
                            D50.8, Other iron deficiency anemias Diagnosis Date: 10/20/2020
                            E11.9, Type 2 diabetes mellitus without complications Diagnosis Date: 10/20/2020
                            I10, Essential (primary) hypertension Diagnosis Date: 10/20/2020
                            E78.79, Other disorders of bile acid and cholesterol metabolism Diagnosis Date: 10/20/2020
                            Z68.33, Body mass index [BMI] 33.0-33.9, adult Diagnosis Date: 10/20/2020
                            D69.59, Other secondary thrombocytopenia Diagnosis Date: 09/25/2023
                        MEDICATIONS:
                            ALBUTEROL HFA (PROAIR) INHALER, inhale 2 puffs by mouth every 12 hours , Qty: 8.5, Prescribe Date:/24/2023,Reconciliation Date: 12/19/2023
                            TRESIBA FLEX 100U/ML PEN, null , Prescribe Date: 12/19/2023,Reconciliation Date: 12/19/2023
                            FIASP F/P 100U/ML PEN, null , Prescribe Date: 12/19/2023,Reconciliation Date: 12/19/2023
                            REPATHA SURE 140MG/ML INJ, null , Prescribe Date: 12/19/2023,Reconciliation Date: 12/19/2023
                            Levemir FlexPen 100 unit/mL (3 mL) solution subcutaneous insulin pen, 14 ml morninign and evening , Prescribe Date:09/18/2023,Reconciliation Date: 12/19/2023
                            NOVOLOG 100 UNIT/ML FLEXPEN, SSC , Prescribe Date: 05/22/2023,Reconciliation Date: 12/19/2023
                            Prilosec OTC 20 mg tablet,delayed release, One Tablet Daily Daily, Start Date: 02/06/2023, Prescribe Date:02/21/2023,Reconciliation Date: 12/19/2023
                            carvedilol 3.125 mg tablet, take 1 tablet(3.125MG) by oral route plus 6.25 qday , Prescribe Date: 09/26/2022,ReconciliationDate: 12/19/2023
                            carvedilol 6.25 mg tablet, 1 plus 3,25 qday , Prescribe Date: 09/26/2022,Reconciliation Date: 12/19/2023
                            losartan 25 mg tablet, take 1 tablet(25MG) by oral route Qd , Prescribe Date: 06/08/2021,Reconciliation Date: 12/19/2023
                        IMMUNIZATIONS:
                            Administred:
                                Influenza, High Dose, Administered, 09/18/2023
                                influenza, recombinant, injectable, preservative free, Administered, 09/26/2022
                                Tdap, Administered, 09/26/2022
                                influenza, injectable, quadrivalent, preservative free, Administered, 09/27/2021
                            Historical:
                                Pneumococcal, (PPSV), Historical, 12/19/2023
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 04/08/2021
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 03/11/2021
                                Shingles Vaccine-SHINGRIX, Historical,
                            Refusal:
                                not provided
                        HISTORY:
                            Social Hx:
                                Tobacco status: Never smoker (CDC-4)
                                Drug use: Never
                                Marital status: Married
                                Industry: 7490 - Other professional, scientific, and technical services
                            Risk Assessment:
                                Exercise: 2-5 Time/Week
                                Seatbelts: Always
                                Exposure: None
                                Feels Safe at Home: Yes
                            Past Medical Hx:
                                CABG 2015
                            Past Surgical History:
                                surgery on left eye
                        PREVENTIVE SCREENING:
                            pneumococcal polysaccharide vaccine, 23 valent
                            Shingles Vaccine-SHINGRIX
                            Seasonal, trivalent, recombinant, injectable influenza vaccine, preservative free
                            tetanus toxoid, reduced diphtheria toxoid, and acellular pertussis vaccine, adsorbed
                            influenza, high dose seasonal, preservative-free
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            Influenza, injectable, quadrivalent, preservative free
                            Tdap
                            Pneumococcal, (PPSV)
                            Influenza, High Dose
                            influenza, recombinant, injectable, preservative free
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose 	
                            Mammogram
                            Mammogram W/ultrasound
                        CHIEF COMPLAINT:
                            surgery on left eye
                        HISTORY OF PRESENT ILLNESS:
                            Patient presents today for routine evaluation and examination.
                            She reports no changes in appetite , sleep , weight , mood , bowel habits and urinary habits.
                            Last pap smear- could not tolerate pap smear due to pain around covid. patient needs to go for MRI
                            difficult to do pap smear - but haven't went back to see the gynecologist
                            Last eye exam- 3 months ago
                            Last mammogram- last year
                            Last colonoscopy- 3 months ago
                            Last dexa scan- due
                            shingles vaccine- finished 2 shots in 2022
                            last month she had blood work done- A1c= 9.7%- she went to see her endocrinologist for follow up after who have
                            changed both of her insulin to tresiba and Fiasp- which patient haven't started yet as she was told to finish the old insulin 1
                            and start new 1.
                            she's complaining of on and off cramps in both legs, sometimes together sometimes separate, mainly in early morning.
                            currently not on any multivitamin
                            patient is currently seeing GI, hepatologist, cardiologist, Hematologist and endocrinologist
                        VITAL SIGNS:
                            Height: 4 ft 10 in
                            Weight: 153 lb 2 oz 
                            BMI: 32 Obesity
                            BP: 124/79 mmHg Position:Sitting
                            SpO2: 99 % Flowrate: Room Air Source: On room air 
                            HR: 66 bpm	
                        PROCEDURES (CPTS):
                            99396 - Well Visit
                            36415 - Routine venipuncture
                            3074F - Syst bp lt 130 mm hg
                            3078F - Diast bp <80 mm hg
                            3008F - Body mass index docd
                            3046F - Hemoglobin a1c level >9.0%
                            1159F - Med list docd in rcrd
                            1160F - Rvw meds by rx/dr in rcrd
                        PLAN OF CARE:
                            up to date with age appropriate vaccination
                            EKG done and reviewed the findings- (could not save the results to the chart ).seeing cardiologist regularly
                            Influenza vaccine, routine eye and dental examination on an annual basis.
                            Choose a nutritious and balanced diet which is low in animal fat and sodium, and rich in fiber such as fruits, vegetables,
                            whole grains and beans.
                            Do regular exercises: Walk for 30 minutes everyday.
                            Maintain a healthy weight.
                            patient is recommended to follow up with gynecologist for Pap smear
                            continue on medications
                        CARE TEAM:
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                            Name:  "" , Relation: "" , Contact#: "", Email:""         
                Output:
                The output must strictly follow the exact sequence of questions provided without any changes in order. Each item in the questionnaire must appear exactly in the sequence as listed below. Do not reorder, add, or omit any items, and ensure the structure is preserved.No deviations from the order above are allowed. The sequence in the output must be identical to the sequence provided here.      
                    {{
                        "response": [
                            {{
                                "title": "<strong>Communication & Follow-Up Preferences</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                "title": "What is your preferred language for monthly assessment?",
                                "type": "Single Choice",
                                "options": ["English","Spanish"]
                            }},
                            {{
                                "title": "What is your preferred method of contact for monthly follow-ups?",
                                "type": "Single Choice",
                                "options": [,"Text message","Phone call","Email","No preference"]
                            }},
                            {{
                                "title": "What is your preferred time for us to call you for monthly follow-ups?",
                                "type": "Single Choice",
                                "options": ["Morning (9 AM – 12 PM)","Afternoon (12 PM – 4 PM)","No preference"]
                            }},
                            
                            {{
                                "title": "<strong>Diagnosis review</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                    "title": "<p><strong>Diagnosis:</strong></p><ul><li>I10 - Essential (primary) hypertension</li><li>E11.9 - Type 2 Diabetes Mellitus without complications</li></ul>",
                                    "type": "Text Box"
                            }},
                            {{
                                "title": "<strong>Care team review</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                "title": "Care Team",
                                "type": "Care Team"
                            }},
                            {{
                                "title": "Do you have any new care team members (e.g., doctor, nurse, therapist) you'd like us to add to your records?",
                                "type": "Single Choice",
                                "options": ["Yes","No"]
                            }},
                            {{
                                "title": "If yes, please provide their name, specialty, and contact number (if available):",
                                "type": "Text"
                            }},
                            {{
                                "title": "<strong>Allergies history review</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                "title": "Allergies",
                                "type": "Allergies"
                                
                            }},
                            {{
                                "title": "Do you have any new allergies you'd like us to add to your record?",
                                "type": "Single Choice",
                                "options": ["No, I have no new allergies","Yes, I have new allergies (please list below)"]
                                
                            }},
                            {{
                                "title": "New allergy/allergies:",
                                "type": "Text"
                            }},

                            {{
                                "title": "<strong>Medication Review & Compliance</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                    "title": "The following medications are listed in your health record. Please check the medications you are currently taking as prescribed:",
                                    "type": "Multiple Choice",
                                    "options": ['Escitalopram 5 mg tablet , 1 tab by mouth daily',
                                                'Docusate sodium 100 mg capsule , 1 cap by mouth 2 times per day',
                                                'Lisinopril 20 mg tablet , 1 tab by mouth daily',
                                                'Miralax 17 gram oral powder packet , 1 packet by mouth dissolved in fluid daily constipation',
                                                'Alendronate 70 mg tablet , 1 tab by mouth every week']
                            }},
                            {{
                                "title": "If you are no longer taking a medication or have changes (e.g., new medications, dosage changes), please list them below:",
                                "type": "Text"
                            }},
                            {{
                                    "title": "Here is a list of your current medications. Please check any that you need refilled:",
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
                                "title": "You are due for your mammogram. Would you like assistance scheduling an appointment?",
                                "type": "Single Choice",
                                "options": ["Yes","No"]
                            }},
                            {{
                                "title": "You are also due for your routine eye exam. Would you like assistance scheduling an appointment?",
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
                                            <p><strong>Initial goals and interventions:</strong></p>
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
                                    "title": "Do you have any personal health goals you would like to work on?",
                                    "type": "Text"
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
                        {data['pt_age']}
                    Patient Gender:
                        {data['pt_gender']}
                    Patient Language:
                        {data['pt_language']}
                    Encounter No 1:
                        ENCOUNTER DATE:
                            {data['et1_visit_Date']}
                        ALLERGIES
                            {data['et1_alg']}
                        DIAGNOSIS (ICDS):
                            {data['et1_icds']}
                        MEDICATIONS:
                            {data['et1_med']}
                        IMMUNIZATIONS:
                            Administred:
                                {data['et1_imz_adm']}
                            Historical:
                                {data['et1_imz_hist']}
                            Refusal:
                                {data['et1_imz_ref']}
                        HISTORY:
                            Social Hx: 
                                {data['et1_history_sx']}
                            Past Medical Hx:
                                {data['et1_history_pmh']}
                            Risk assessment
                                {data['et1_history_risk']}
                            Past Surgical History:
                                {data['et1_history_psh']}
                        PREVENTIVE SCREENING:
                            {data['et_screening']}
                        CHIEF COMPLAINT:
                            {data['et1_cheifComplaint']}
                        HISTORY OF PRESENT ILLNESS:
                            {data['et1_hpi']}
                        VITAL SIGNS:
                            {data['et1_vitals']}
                        PROCEDURES (CPTS):
                            {data['et1_cpts']}
                        PLAN OF CARE:
                            {data['et1_poc']}
                        CARE TEAM:
                            {data['care_team']}
                    Encounter No 2:
                        ENCOUNTER DATE:
                            {data['et2_visit_Date']}
                        ALLERGIES
                            {data['et2_alg']}
                        DIAGNOSIS (ICDS):
                            {data['et2_icds']}
                        MEDICATIONS:
                            {data['et2_med']}
                        IMMUNIZATIONS:
                            Administred:
                                {data['et2_imz_adm']}
                            Historical:
                                {data['et2_imz_hist']}
                            Refusal:
                                {data['et2_imz_ref']}
                        HISTORY:
                            Social Hx: 
                                {data['et2_history_sx']}
                            Past Medical Hx:
                                {data['et2_history_pmh']}
                            Risk assessment
                                {data['et2_history_risk']}
                            Past Surgical History:
                                {data['et2_history_psh']}
                        PREVENTIVE SCREENING:
                            {data['et_screening']}
                        CHIEF COMPLAINT:
                            {data['et2_cheifComplaint']}
                        HISTORY OF PRESENT ILLNESS:
                            {data['et2_hpi']}
                        VITAL SIGNS:
                            {data['et2_vitals']}
                        PROCEDURES (CPTS):
                            {data['et2_cpts']}
                        PLAN OF CARE:
                            {data['et2_poc']}
                        CARE TEAM:
                            {data['care_team']}
                    Encounter No 3:
                        ENCOUNTER DATE:
                            {data['et3_visit_Date']}
                        ALLERGIES
                            {data['et3_alg']}
                        DIAGNOSIS (ICDS):
                            {data['et3_icds']}
                        MEDICATIONS:
                            {data['et3_med']}
                        IMMUNIZATIONS:
                            Administred:
                                {data['et3_imz_adm']}
                            Historical:
                                {data['et3_imz_hist']}
                            Refusal:
                                {data['et3_imz_ref']}
                        HISTORY:
                            Social Hx: 
                                {data['et3_history_sx']}
                            Past Medical Hx:
                                {data['et3_history_pmh']}
                            Risk assessment
                                {data['et3_history_risk']}
                            Past Surgical History:
                                {data['et3_history_psh']}
                        PREVENTIVE SCREENING:
                            {data['et_screening']}
                        CHIEF COMPLAINT:
                            {data['et3_cheifComplaint']}
                        HISTORY OF PRESENT ILLNESS:
                            {data['et3_hpi']}
                        VITAL SIGNS:
                            {data['et3_vitals']}
                        PROCEDURES (CPTS):
                            {data['et3_cpts']}
                        PLAN OF CARE:
                            {data['et3_poc']}
                        CARE TEAM:
                            {data['care_team']}

                Based on the provided patient encounter data, create an initial assessment questionnaire with the following considerations, and ensure to follow all provided rules and format structure.
                Instructions:
                 
                    0.Preferred Language generation: generate the entire output questionnaire in the patient’s preferred **{data['pt_language']}** .(default to English if not provided), but always list medications in English exactly as in the encounter data with no additions( Medication Language Requirement: Medications must always be presented in English regardless of the patient's preferred language; do not translate medication names (e.g., if the preferred language is Spanish, medication names remain in English). )
                    1.The output must strictly follow the exact sequence of questions provided without any changes in order.    
                    2.Strictly follow the json format given in example output.
                    3.Age and Gender: Tailor the questions according to the patients age and gender.
                    4.CareTeam: Include the care team information from the latest encounter only.Latest Encounter is Encounter NO 1. if no care team information is available then please ask the patient to provide care team information.question Please provide their name, specialty and a contact number. type: text.
                    4.Diagnosis: Identify at all chronic conditions (ICD codes) from the  provided input encounters.Add these ICDS into the questionnaire in Diagnosis section. {data['et1_icds']}, {data['et2_icds']}, {data['et3_icds']}  add in diagnosis section.
                    5.Allergies: Very important section - check if patient has allergies from encounter data {data['et1_alg']}, {data['et2_alg']}, {data['et3_alg']}
                    6.Medication: Pick Medications from encounter MEDICATIONS: please list the medications from the below encounters in the questionnaire.(only pick from below latest encounter medications)
                    {data['et1_med']}
                    🚨 CRITICAL MEDICATION REQUIREMENTS - NO EXCEPTIONS:
                    
                    **MANDATORY MEDICATION INCLUSION RULES:**
                    1. **INCLUDE EVERY SINGLE MEDICATION** from the latest encounter (et1_med) - NO OMISSIONS ALLOWED
                    2. **DO NOT SKIP ANY MEDICATION** regardless of type (prescription, OTC, supplements, inhalers, injections)
                    3. **EXACT MEDICATION MATCHING** - Use the EXACT text from encounter data with NO modifications
                    4. **ALPHABETICAL ORDERING** - List all medications in alphabetical order by medication name
                    5. **COMPLETE MEDICATION LIST** - If encounter has 10 medications, questionnaire MUST have all 10
                    
                    **MEDICATION VALIDATION CHECKLIST:**
                    ✓ Count total medications in encounter: {data['et1_med']}
                    ✓ Verify every medication appears in questionnaire options
                    ✓ Confirm exact text matching (dosage, frequency, instructions)
                    ✓ Check alphabetical ordering is correct
                    ✓ Ensure NO medications are excluded or omitted
                    
                    **FAILURE TO INCLUDE ALL MEDICATIONS WILL CAUSE SYSTEM ERROR**
                    8.Preventive Care and Screening: Review the patient's preventive care and screening history. Apply the U.S. Preventive Services Task Force (USPSTF) guidelines to determine and list any due dates for preventive services.
                    9.Current month goals and interventions:
                    CRITICAL REQUIREMENT - Goals and Interventions for ALL Chronic Conditions:
                    **MANDATORY: You MUST generate goals and interventions for EVERY SINGLE chronic condition ICD code listed below. NO EXCEPTIONS. NO OMISSIONS.**
                    
                    **Source ICD Codes from ALL Encounters:**
                    - Encounter 1 ICDs: {data['et1_icds']}
                    - Encounter 2 ICDs: {data['et2_icds']} 
                    - Encounter 3 ICDs: {data['et3_icds']}
                    Include the goals and interventions for the current month, based on the patient's all chronic conditionsDIAGNOSIS (ICDS):
                            . Ensure that the goals are specific, measurable, achievable, relevant, and time-bound (SMART). The interventions should be evidence-based and tailored to the patient's needs. Also generate educational resources for each chronic condition, such as reputable links (e.g., MedlinePlus or CDC) to support patient self-management. For each chronic condition, provide:
                                - A clear goal statement that is measurable and time-bound.
                                - A list of interventions (medication adherence, lifestyle changes, monitoring, follow-up).
                                - An education & self-management section with a relevant patient-friendly link.
                    10.In the reminder, the appointment date should be **{data['appointment_Date']}**.If no Appoitment date then do not add *Appointments:* in reminder section.
                    10.Ensure that the questionnaire is comprehensive, follows the specified rules, and adheres to the format structure provided.
                    11.JSON Structure Compliance: Confirm that the output strictly adheres to the JSON format, including appropriate titles, types, and content organization according to the specified requirements.
                    12.Medications should be alphabetically ordered.
                    ERROR PREVENTION:
                    - No markdown formatting (```, **, etc.)
                    - No unescaped quotes in JSON strings
                    - No line breaks in JSON string values
                    
                    - Validate JSON structure before returning

                    OUTPUT ONLY THE JSON - NO OTHER TEXT:
                Output:
            """
            return prompt
        except Exception as e:
            error_logger.error(str(e))
            raise ApplicationException() 

    def init_prompt_v2(data):
        try:
            prompt=f"""You working as a Primary Care Physician. You are running a Chronic Care Management program, for that you are generating an initial assessment questionnaire including Care Plan goals and interventions by reviewing their past 3 encounter notes, to get an update on their current health conditions according to the Centers for Medicare and Medicaid Services program guidelines.
                Input:
                    Encounter No 1:
                        ENCOUNTER DATE:
                            08/12/2024
                        ALLERGIES:
                            Sulfa (Sulfonamide Antibiotics) ,Severe ,Anaphylaxis
                            Penicillins ,Severe ,Anaphylaxis
                        DIAGNOSIS (ICDS):
                            R45.2, Unhappiness Diagnosis Date: 08/12/2024
                            D50.8, Other iron deficiency anemias Diagnosis Date: 10/20/2020
                            D69.59, Other secondary thrombocytopenia Diagnosis Date: 09/25/2023
                            K75.81, Nonalcoholic steatohepatitis (nash) Diagnosis Date: 02/21/2023
                            J30.2, Other seasonal allergic rhinitis Diagnosis Date: 05/24/2021
                            Z95.1, Presence of aortocoronary bypass graft Diagnosis Date: 10/20/2020
                            I10, Essential (primary) hypertension Diagnosis Date: 10/20/2020
                            E11.9, Type 2 diabetes mellitus without complications Diagnosis Date: 10/20/2020
                            E78.79, Other disorders of bile acid and cholesterol metabolism Diagnosis Date: 10/20/2020
                            Z68.33, Body mass index [BMI] 33.0-33.9, adult Diagnosis Date: 10/20/2020
                        MEDICATIONS:
                            ALBUTEROL HFA (PROAIR) INHALER, inhale 2 puffs by mouth every 12 hours , Qty: 8.5, Prescribe Date:02/24/2023,Reconciliation Date: 08/12/2024
                            Tresiba FlexTouch U-200 insulin 200 unit/mL (3 mL) subcutaneous pen, 32 units QPM , Start Date: 06/21/2024, Prescribe Date:06/21/2024,Reconciliation Date: 08/12/2024
                            omeprazole 40 mg capsule,delayed release, 1 cap by mouth daily , Start Date: 06/21/2024, Prescribe Date:06/21/2024,Reconciliation Date: 08/12/2024
                            ferrous sulfate 325 mg (65 mg iron) tablet, 1 cap by mouth daily , Start Date: 06/21/2024, Prescribe Date:06/21/2024,Reconciliation Date: 08/12/2024
                            FIASP F/P 100U/ML PEN, using SSC (4 to 12 units) with TID with meals , Prescribe Date: 12/19/2023,Reconciliation Date:08/12/2024
                            REPATHA SURE 140MG/ML INJ, null , Prescribe Date: 12/19/2023,Reconciliation Date: 08/12/2024
                            carvedilol 3.125 mg tablet, take 1 tablet(3.125MG) by oral route BID , Prescribe Date: 09/26/2022,Reconciliation Date:08/12/2024
                        IMMUNIZATIONS:
                            Administred:
                                Influenza, High Dose, Administered, 09/18/2023
                                influenza, recombinant, injectable, preservative free, Administered, 09/26/2022
                                Tdap, Administered, 09/26/2022
                                influenza, injectable, quadrivalent, preservative free, Administered, 09/27/2021
                            Historical:
                                Pneumococcal, (PPSV), Historical, 12/19/2023
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 04/08/2021
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 03/11/2021
                                Shingles Vaccine-SHINGRIX, Historical,
                            Refusal:
                                not provided
                        HISTORY:
                            Social Hx:
                                not provided
                            Past Medical Hx:
                                CABG 2015
                            Risk assessment
                                Exercise: 2-5 Time/Week
                                Seatbelts: Sometimes
                                Exposure: Hepatitis
                                Feels Safe at Home: Yes
                            Past Surgical History:
                                surgery on left eye
                        PREVENTIVE SCREENING:
                            pneumococcal polysaccharide vaccine, 23 valent
                            Shingles Vaccine-SHINGRIX
                            Seasonal, trivalent, recombinant, injectable influenza vaccine, preservative free
                            tetanus toxoid, reduced diphtheria toxoid, and acellular pertussis vaccine, adsorbed
                            influenza, high dose seasonal, preservative-free
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            Influenza, injectable, quadrivalent, preservative free
                            Tdap
                            Pneumococcal, (PPSV)
                            Influenza, High Dose
                            influenza, recombinant, injectable, preservative free
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose 	
                            Mammogram
                            Mammogram W/ultrasound
                        CHIEF COMPLAINT:
                            renal insufficiency, anemia, uncontrolled DM, hypercholesterlemia
                        HISTORY OF PRESENT ILLNESS:
                            The patient is a 65-year-old female who presents for a follow-up visit. She has a history of type 2 diabetes mellitus,
                            hypertension, hyperlipidemia, iron deficiency anemia, and nonalcoholic steatohepatitis (NASH). She is currently
                            taking insulin, repatha, omeprazole She reports that her blood sugar control has been unstable, with episodes of
                            both high and low blood sugars. She also reports feeling tired, having difficulty sleeping, and experiencing low
                            mood. She has noticed some bloating and discomfort after eating certain foods. She was recently hospitalized in
                            Canada She has been having difficulty managing her blood sugars since her return and has been experiencing
                            frequent episodes of hypoglycemia. She is also concerned about her fatigue and low mood, which she believes
                            may be related to her diabetes and recent hospitalization.
                        VITAL SIGNS:
                            Height: 4 ft 10 in
                            Weight: 157 lb
                            BMI: 32.81 Obesity   
                            BP: 123/78 mmHg Position:Sitting 
                            SpO2: 98 % Flowrate: Room Air Source: On room air 
                            HR: 69  bpm	
                        
                        PROCEDURES (CPTS):
                            99214 - Office o/p est mod 30 min
                            G8417 - BMI is documented above normal parameters and a follow-up plan is documented
                            G8427 - Eligible clinician attests to documenting in the medical record they obtained, updated, or reviewed the
                            patients current medications
                            G9903 - Patient screened for tobacco use and identified as a tobacco non-user
                            G8950 - ELEVATED OR HYPERTENSIVE BLOOD PRESSURE READING DOCUMENTED, AND THE
                            INDICATED FOLLOW-UP IS DOCUMENTED
                        PLAN OF CARE:
                            E11.9 :
                            The patient will continue to monitor her blood sugars closely and adjust her insulin doses as needed. She will also meet
                            with her endocrinologist to discuss her blood sugar control and medication regimen.
                            patient has a continuous blood glucose monitor Trend will be reviewed and Medicine adjusted by the endocrinologist
                            I10 :
                            The patient will continue to take her antihypertensive medications as prescribed.
                            blood pressure is stable
                            E78.79 :
                            The patient will continue to take her repatha as prescribed.
                            lipid panel results will be obtained from the cardiologist
                            She has an appointment to see a hepatologist to discuss her NASH and liver function.
                            K75.81 :
                            The patient will continue to follow a healthy diet and exercise regularly. She will also be referred to a hepatologist to
                            discuss her NASH and liver function.
                            continue to take omeprazole
                            increase activity
                            Z68.33 :
                            The patient will be encouraged to lose weight and maintain a healthy weight. She will be referred to a dietitian to discuss
                            her diet and exercise plan.
                            R45.2
                            patient will be referred to behavioral therapy
                        CARE TEAM:
                           Name:  "" , Relation: "" , Contact#: "", Email:""
                           Name:  "" , Relation: "" , Contact#: "", Email:""
                           Name:  "" , Relation: "" , Contact#: "", Email:""
                    Encounter No 2:
                        ENCOUNTER DATE:
                            06/21/2024 
                        ALLERGIES
                            Sulfa (Sulfonamide Antibiotics) ,Severe ,Anaphylaxis
                            Penicillins ,Severe ,Anaphylaxis
                        DIAGNOSIS (ICDS): 
                            D50.8, Other iron deficiency anemias Diagnosis Date: 10/20/2020
                            D69.59, Other secondary thrombocytopenia Diagnosis Date: 09/25/2023
                            K75.81, Nonalcoholic steatohepatitis (nash) Diagnosis Date: 02/21/2023
                            J30.2, Other seasonal allergic rhinitis Diagnosis Date: 05/24/2021
                            Z95.1, Presence of aortocoronary bypass graft Diagnosis Date: 10/20/2020
                            I10, Essential (primary) hypertension Diagnosis Date: 10/20/2020
                            E11.9, Type 2 diabetes mellitus without complications Diagnosis Date: 10/20/2020
                            E78.79, Other disorders of bile acid and cholesterol metabolism Diagnosis Date: 10/20/2020
                            Z68.33, Body mass index [BMI] 33.0-33.9, adult Diagnosis Date: 10/20/2020
                        MEDICATIONS:
                            ALBUTEROL HFA (PROAIR) INHALER, inhale 2 puffs by mouth every 12 hours , Qty: 8.5, Prescribe Date:/24/2023,Reconciliation Date: 06/06/2024
                            Tresiba FlexTouch U-200 insulin 200 unit/mL (3 mL) subcutaneous pen, 26 units QPM , Start Date: 06/21/2024, Prescribe Date:06/21/2024
                            omeprazole 40 mg capsule,delayed release, 1 cap by mouth daily , Start Date: 06/21/2024, Prescribe Date: 06/21/2024
                            ferrous sulfate 325 mg (65 mg iron) tablet, 1 cap by mouth daily , Start Date: 06/21/2024, Prescribe Date: 06/21/2024
                            FIASP F/P 100U/ML PEN, using SSC (4 to 12 units) with TID with meals , Prescribe Date: 12/19/2023,Reconciliation Date:06/21/2024
                            REPATHA SURE 140MG/ML INJ, null , Prescribe Date: 12/19/2023,Reconciliation Date: 06/06/2024
                            carvedilol 3.125 mg tablet, take 1 tablet(3.125MG) by oral route BID , Prescribe Date: 09/26/2022,Reconciliation Date:06/21/2024
                        IMMUNIZATIONS:
                            Administred:
                                Influenza, High Dose, Administered, 09/18/2023
                                influenza, recombinant, injectable, preservative free, Administered, 09/26/2022
                                Tdap, Administered, 09/26/2022
                                influenza, injectable, quadrivalent, preservative free, Administered, 09/27/2021
                            Historical:
                                Pneumococcal, (PPSV), Historical, 12/19/2023
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 04/08/2021
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 03/11/2021
                                Shingles Vaccine-SHINGRIX, Historical,
                            Refusal:
                                not provided
                        HISTORY:
                            Social Hx:
                                not provided
                            Risk Assessemnt
                                Exercise: 2-5 Time/Week
                                Seatbelts: Sometimes
                                Exposure: Hepatitis
                                Feels Safe at Home: Yes
                            Past Medical Hx:
                                CABG 2015
                            Past Surgical History:
                                surgery on left eye
                        PREVENTIVE SCREENING:
                            pneumococcal polysaccharide vaccine, 23 valent
                            Shingles Vaccine-SHINGRIX
                            Seasonal, trivalent, recombinant, injectable influenza vaccine, preservative free
                            tetanus toxoid, reduced diphtheria toxoid, and acellular pertussis vaccine, adsorbed
                            influenza, high dose seasonal, preservative-free
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            Influenza, injectable, quadrivalent, preservative free
                            Tdap
                            Pneumococcal, (PPSV)
                            Influenza, High Dose
                            influenza, recombinant, injectable, preservative free
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose 	
                            Mammogram
                            Mammogram W/ultrasound
                        CHIEF COMPLAINT:
                            Transitional Care Management
                        HISTORY OF PRESENT ILLNESS:
                            A 65 years old female came for follow up on hospital admission. Patient was admitted in the hospital of Canada while she
                            was visiting her mother from 6/8-6/11/2024 for diagnosis of hypertension, iron deficiency anemia (hb on admission was
                            8.6), hyperglycemia, and liver cirrhosis due to likely to have some form of infection.
                            her hypertension was corrected by IV fluids, sugar was fluctuating, she was seen by endocrinologist and other specialist
                            while in the hospital.
                            medications were adjusted including insulin, was given short-term therapy of Lasix as a diuretic as she was having fluid
                            collection in the abdomen.
                            hypertension was probably secondary to the blood pressure medication.
                            she returned to New Jersey for 2 days to follow with all her doctors as she's traveling back to Canada again tomorrow as
                            her mother is getting some cardiac surgery done.
                            she had consulted hematologist yesterday- And her hemoglobin was 9.6- done that she's waiting for oncologist office to
                            call today to determine whether or not she needs another IV infusion.
                            she had reached out to her endocrinologist as her blood sugar is fluctuating widely- she was instructed to consult their
                            nutrition is to guide her what to eat at this time. continue to take insulin.
                            she's also planning to call her GI and hepatology soon.
                            currently she is doing well, her energy level is getting better gradually. his monitoring her blood pressure and blood sugar
                            at home. she was instructed to repeat her liver function on discharge.
                        VITAL SIGNS:
                            Height: 4 ft 10 in
                            Weight: 153 lb 2 oz
                            BMI: 32 Obesity 
                            BP: 116/62 mmHg Position: Sitting 
                            SpO2: 97 % Flowrate: Room Air Source: On room air 
                            HR: 74 bpm	
                            Pain Socre:0
                        PROCEDURES (CPTS):
                            3008F - Body mass index docd
                            3074F - Syst bp lt 130 mm hg
                            3078F - Diast bp <80 mm hg
                            36415 - ROUTINE VENIPUNCTURE
                            99495 - Transj care mgmt mod f2f 14d
                            1111F - Dschrg med/current med merge
                        PLAN OF CARE:
                            D508- repeat CBC. Airport was also done by hematologist yesterday- pending results. Patient is waiting for them
                            to call as they will decide whether or not she needs another iron infusion are not.
                            on oral iron supple.
                            K7581- LFTS and CMP Done
                            E119- she already consulted endocrinologist. repeat A1C today.
                            in the hospital her A1C was 8%.
                            I10- continue coreg 3.125mg QAM and in evening if BP is >110.
                            omeprazole for gerd like sx
                        CARE TEAM:                            
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                    Encounter No 3:
                        ENCOUNTER DATE:
                            12/19/2023
                        ALLERGIES
                            Sulfa (Sulfonamide Antibiotics) ,Severe ,Anaphylaxis
                            Penicillins ,Severe ,Anaphylaxis
                        DIAGNOSIS (ICDS):
                            K75.81, Nonalcoholic steatohepatitis (nash) Diagnosis Date: 02/21/2023
                            J30.2, Other seasonal allergic rhinitis Diagnosis Date: 05/24/2021
                            Z95.1, Presence of aortocoronary bypass graft Diagnosis Date: 10/20/2020
                            D50.8, Other iron deficiency anemias Diagnosis Date: 10/20/2020
                            E11.9, Type 2 diabetes mellitus without complications Diagnosis Date: 10/20/2020
                            I10, Essential (primary) hypertension Diagnosis Date: 10/20/2020
                            E78.79, Other disorders of bile acid and cholesterol metabolism Diagnosis Date: 10/20/2020
                            Z68.33, Body mass index [BMI] 33.0-33.9, adult Diagnosis Date: 10/20/2020
                            D69.59, Other secondary thrombocytopenia Diagnosis Date: 09/25/2023
                        MEDICATIONS:
                            ALBUTEROL HFA (PROAIR) INHALER, inhale 2 puffs by mouth every 12 hours , Qty: 8.5, Prescribe Date:/24/2023,Reconciliation Date: 12/19/2023
                            TRESIBA FLEX 100U/ML PEN, null , Prescribe Date: 12/19/2023,Reconciliation Date: 12/19/2023
                            FIASP F/P 100U/ML PEN, null , Prescribe Date: 12/19/2023,Reconciliation Date: 12/19/2023
                            REPATHA SURE 140MG/ML INJ, null , Prescribe Date: 12/19/2023,Reconciliation Date: 12/19/2023
                            Levemir FlexPen 100 unit/mL (3 mL) solution subcutaneous insulin pen, 14 ml morninign and evening , Prescribe Date:09/18/2023,Reconciliation Date: 12/19/2023
                            NOVOLOG 100 UNIT/ML FLEXPEN, SSC , Prescribe Date: 05/22/2023,Reconciliation Date: 12/19/2023
                            Prilosec OTC 20 mg tablet,delayed release, One Tablet Daily Daily, Start Date: 02/06/2023, Prescribe Date:02/21/2023,Reconciliation Date: 12/19/2023
                            carvedilol 3.125 mg tablet, take 1 tablet(3.125MG) by oral route plus 6.25 qday , Prescribe Date: 09/26/2022,ReconciliationDate: 12/19/2023
                            carvedilol 6.25 mg tablet, 1 plus 3,25 qday , Prescribe Date: 09/26/2022,Reconciliation Date: 12/19/2023
                            losartan 25 mg tablet, take 1 tablet(25MG) by oral route Qd , Prescribe Date: 06/08/2021,Reconciliation Date: 12/19/2023
                        IMMUNIZATIONS:
                            Administred:
                                Influenza, High Dose, Administered, 09/18/2023
                                influenza, recombinant, injectable, preservative free, Administered, 09/26/2022
                                Tdap, Administered, 09/26/2022
                                influenza, injectable, quadrivalent, preservative free, Administered, 09/27/2021
                            Historical:
                                Pneumococcal, (PPSV), Historical, 12/19/2023
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 04/08/2021
                                COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose, Historical, 03/11/2021
                                Shingles Vaccine-SHINGRIX, Historical,
                            Refusal:
                                not provided
                        HISTORY:
                            Social Hx:
                                Tobacco status: Never smoker (CDC-4)
                                Drug use: Never
                                Marital status: Married
                                Industry: 7490 - Other professional, scientific, and technical services
                            Risk Assessment:
                                Exercise: 2-5 Time/Week
                                Seatbelts: Always
                                Exposure: None
                                Feels Safe at Home: Yes
                            Past Medical Hx:
                                CABG 2015
                            Past Surgical History:
                                surgery on left eye
                        PREVENTIVE SCREENING:
                            pneumococcal polysaccharide vaccine, 23 valent
                            Shingles Vaccine-SHINGRIX
                            Seasonal, trivalent, recombinant, injectable influenza vaccine, preservative free
                            tetanus toxoid, reduced diphtheria toxoid, and acellular pertussis vaccine, adsorbed
                            influenza, high dose seasonal, preservative-free
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            SARS-COV-2 (COVID-19) vaccine, mRNA, spike protein, LNP, preservative free, 100 mcg/0.5mL dose
                            Influenza, injectable, quadrivalent, preservative free
                            Tdap
                            Pneumococcal, (PPSV)
                            Influenza, High Dose
                            influenza, recombinant, injectable, preservative free
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose
                            COVID-19, mRNA, LNP-S, PF, 100 mcg/0.5 mL dose 	
                            Mammogram
                            Mammogram W/ultrasound
                        CHIEF COMPLAINT:
                            surgery on left eye
                        HISTORY OF PRESENT ILLNESS:
                            Patient presents today for routine evaluation and examination.
                            She reports no changes in appetite , sleep , weight , mood , bowel habits and urinary habits.
                            Last pap smear- could not tolerate pap smear due to pain around covid. patient needs to go for MRI
                            difficult to do pap smear - but haven't went back to see the gynecologist
                            Last eye exam- 3 months ago
                            Last mammogram- last year
                            Last colonoscopy- 3 months ago
                            Last dexa scan- due
                            shingles vaccine- finished 2 shots in 2022
                            last month she had blood work done- A1c= 9.7%- she went to see her endocrinologist for follow up after who have
                            changed both of her insulin to tresiba and Fiasp- which patient haven't started yet as she was told to finish the old insulin 1
                            and start new 1.
                            she's complaining of on and off cramps in both legs, sometimes together sometimes separate, mainly in early morning.
                            currently not on any multivitamin
                            patient is currently seeing GI, hepatologist, cardiologist, Hematologist and endocrinologist
                        VITAL SIGNS:
                            Height: 4 ft 10 in
                            Weight: 153 lb 2 oz 
                            BMI: 32 Obesity
                            BP: 124/79 mmHg Position:Sitting
                            SpO2: 99 % Flowrate: Room Air Source: On room air 
                            HR: 66 bpm	
                        PROCEDURES (CPTS):
                            99396 - Well Visit
                            36415 - Routine venipuncture
                            3074F - Syst bp lt 130 mm hg
                            3078F - Diast bp <80 mm hg
                            3008F - Body mass index docd
                            3046F - Hemoglobin a1c level >9.0%
                            1159F - Med list docd in rcrd
                            1160F - Rvw meds by rx/dr in rcrd
                        PLAN OF CARE:
                            up to date with age appropriate vaccination
                            EKG done and reviewed the findings- (could not save the results to the chart ).seeing cardiologist regularly
                            Influenza vaccine, routine eye and dental examination on an annual basis.
                            Choose a nutritious and balanced diet which is low in animal fat and sodium, and rich in fiber such as fruits, vegetables,
                            whole grains and beans.
                            Do regular exercises: Walk for 30 minutes everyday.
                            Maintain a healthy weight.
                            patient is recommended to follow up with gynecologist for Pap smear
                            continue on medications
                        CARE TEAM:
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                            Name:  "" , Relation: "" , Contact#: "", Email:""
                            Name:  "" , Relation: "" , Contact#: "", Email:""         
                Output:
                The output must strictly follow the exact sequence of questions provided without any changes in order. Each item in the questionnaire must appear exactly in the sequence as listed below. Do not reorder, add, or omit any items, and ensure the structure is preserved.No deviations from the order above are allowed. The sequence in the output must be identical to the sequence provided here.      
                    {{
                        "response": [
                            {{
                                "title": "<strong>Communication & Follow-Up Preferences</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                "title": "What is your preferred language for monthly assessment?",
                                "type": "Single Choice",
                                "options": ["English","Spanish"]
                            }},
                            {{
                                "title": "What is your preferred method of contact for monthly follow-ups?",
                                "type": "Single Choice",
                                "options": [,"Text message","Phone call","Email","No preference"]
                            }},
                            {{
                                "title": "What is your preferred time for us to call you for monthly follow-ups?",
                                "type": "Single Choice",
                                "options": ["Morning (9 AM – 12 PM)","Afternoon (12 PM – 4 PM)","No preference"]
                            }},
                            
                            {{
                                "title": "<strong>Diagnosis review</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                    "title": "<p><strong>Diagnosis:</strong></p><ul><li>I10 - Essential (primary) hypertension</li><li>E11.9 - Type 2 Diabetes Mellitus without complications</li></ul>",
                                    "type": "Text Box"
                            }},
                            {{
                                "title": "<strong>Care team review</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                "title": "Care Team",
                                "type": "Care Team"
                            }},
                            {{
                                "title": "Do you have any new care team members (e.g., doctor, nurse, therapist) you'd like us to add to your records?",
                                "type": "Single Choice",
                                "options": ["Yes","No"]
                            }},
                            {{
                                "title": "If yes, please provide their name, specialty, and contact number (if available):",
                                "type": "Text"
                            }},
                            {{
                                "title": "<strong>Allergies history review</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                "title": "Allergies",
                                "type": "Allergies"
                                
                            }},
                            {{
                                "title": "Do you have any new allergies you'd like us to add to your record?",
                                "type": "Single Choice",
                                "options": ["No, I have no new allergies","Yes, I have new allergies (please list below)"]
                                
                            }},
                            {{
                                "title": "New allergy/allergies:",
                                "type": "Text"
                            }},

                            {{
                                "title": "<strong>Medication Review & Compliance</strong>",
                                "type": "Text Box"
                            }},
                            {{
                                "title": "Sometimes it's easy to miss a dose. In the past week, have you forgotten to take any of your medications? ",
                                "type": "Single Choice",
                                "options": ["No, I took all medications as prescribed","Yes, I missed one or two doses","Yes, I missed several doses","Other"]
                            }},
                            {{
                                "title": "Other:",
                                "type": "Text"
                            }},
                            {{
                                    "title": "The following medications are listed in your health record. Please check the medications you are currently taking as prescribed:",
                                    "type": "Multiple Choice",
                                    "options": ['Escitalopram 5 mg tablet , 1 tab by mouth daily',
                                                'Docusate sodium 100 mg capsule , 1 cap by mouth 2 times per day',
                                                'Lisinopril 20 mg tablet , 1 tab by mouth daily',
                                                'Miralax 17 gram oral powder packet , 1 packet by mouth dissolved in fluid daily constipation',
                                                'Alendronate 70 mg tablet , 1 tab by mouth every week']
                            }},
                            {{
                                "title": "If you are no longer taking a medication or have changes (e.g., new medications, dosage changes), please list them below:",
                                "type": "Text"
                            }},
                            {{
                                    "title": "Here is a list of your current medications. Please check any that you need refilled:",
                                    "type": "Multiple Choice",
                                    "options": ['Escitalopram 5 mg tablet , 1 tab by mouth daily',
                                                'Docusate sodium 100 mg capsule , 1 cap by mouth 2 times per day',
                                                'Lisinopril 20 mg tablet , 1 tab by mouth daily',
                                                'Miralax 17 gram oral powder packet , 1 packet by mouth dissolved in fluid daily constipation',
                                                'Alendronate 70 mg tablet , 1 tab by mouth every week']
                            }},
                            {{
                                "title": "Do you feel stressed, anxious, or depressed often?",
                                "type": "Single Choice",
                                "options": ["Not at all","Several days","More than half the days","Nearly every day"]
                            }}, 
                            {{
                                "title": "Do you have any personal health goals you would like to work on?",
                                "type": "Text"
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
                                "title": "Do you use any assistive devices (e.g., cane, walker, oxygen)? (place it above fall question)?",
                                "type": "Single Choice",
                                "options": ["Yes","No"]
                            }},
                            {{
                                "title": "If yes, please describe:",
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
                                            <p><strong>Initial goals and interventions:</strong></p>
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
                                    "title": "<p><strong>Reminders:</strong></p><ul><li>You last visited doctor’s office on July,10 2025 at 11:45 AM, your next appointment is on September,10 2025 at 11:45 AM</li></ul>",
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
                        {data['pt_age']}
                    Patient Gender:
                        {data['pt_gender']}
                    Patient Language:
                        {data['pt_language']}
                    Encounter No 1:
                        ENCOUNTER DATE:
                            {data['et1_visit_Date']}
                        ALLERGIES
                            {data['et1_alg']}
                        DIAGNOSIS (ICDS):
                            {data['et1_icds']}
                        MEDICATIONS:
                            {data['et1_med']}
                        IMMUNIZATIONS:
                            Administred:
                                {data['et1_imz_adm']}
                            Historical:
                                {data['et1_imz_hist']}
                            Refusal:
                                {data['et1_imz_ref']}
                        HISTORY:
                            Social Hx: 
                                {data['et1_history_sx']}
                            Past Medical Hx:
                                {data['et1_history_pmh']}
                            Risk assessment
                                {data['et1_history_risk']}
                            Past Surgical History:
                                {data['et1_history_psh']}
                        PREVENTIVE SCREENING:
                            {data['et_screening']}
                        CHIEF COMPLAINT:
                            {data['et1_cheifComplaint']}
                        HISTORY OF PRESENT ILLNESS:
                            {data['et1_hpi']}
                        VITAL SIGNS:
                            {data['et1_vitals']}
                        PROCEDURES (CPTS):
                            {data['et1_cpts']}
                        PLAN OF CARE:
                            {data['et1_poc']}
                        CARE TEAM:
                            {data['care_team']}
                    Encounter No 2:
                        ENCOUNTER DATE:
                            {data['et2_visit_Date']}
                        ALLERGIES
                            {data['et2_alg']}
                        DIAGNOSIS (ICDS):
                            {data['et2_icds']}
                        MEDICATIONS:
                            {data['et2_med']}
                        IMMUNIZATIONS:
                            Administred:
                                {data['et2_imz_adm']}
                            Historical:
                                {data['et2_imz_hist']}
                            Refusal:
                                {data['et2_imz_ref']}
                        HISTORY:
                            Social Hx: 
                                {data['et2_history_sx']}
                            Past Medical Hx:
                                {data['et2_history_pmh']}
                            Risk assessment
                                {data['et2_history_risk']}
                            Past Surgical History:
                                {data['et2_history_psh']}
                        PREVENTIVE SCREENING:
                            {data['et_screening']}
                        CHIEF COMPLAINT:
                            {data['et2_cheifComplaint']}
                        HISTORY OF PRESENT ILLNESS:
                            {data['et2_hpi']}
                        VITAL SIGNS:
                            {data['et2_vitals']}
                        PROCEDURES (CPTS):
                            {data['et2_cpts']}
                        PLAN OF CARE:
                            {data['et2_poc']}
                        CARE TEAM:
                            {data['care_team']}
                    Encounter No 3:
                        ENCOUNTER DATE:
                            {data['et3_visit_Date']}
                        ALLERGIES
                            {data['et3_alg']}
                        DIAGNOSIS (ICDS):
                            {data['et3_icds']}
                        MEDICATIONS:
                            {data['et3_med']}
                        IMMUNIZATIONS:
                            Administred:
                                {data['et3_imz_adm']}
                            Historical:
                                {data['et3_imz_hist']}
                            Refusal:
                                {data['et3_imz_ref']}
                        HISTORY:
                            Social Hx: 
                                {data['et3_history_sx']}
                            Past Medical Hx:
                                {data['et3_history_pmh']}
                            Risk assessment
                                {data['et3_history_risk']}
                            Past Surgical History:
                                {data['et3_history_psh']}
                        PREVENTIVE SCREENING:
                            {data['et_screening']}
                        CHIEF COMPLAINT:
                            {data['et3_cheifComplaint']}
                        HISTORY OF PRESENT ILLNESS:
                            {data['et3_hpi']}
                        VITAL SIGNS:
                            {data['et3_vitals']}
                        PROCEDURES (CPTS):
                            {data['et3_cpts']}
                        PLAN OF CARE:
                            {data['et3_poc']}
                        CARE TEAM:
                            {data['care_team']}

                Based on the provided patient encounter data, create an initial assessment questionnaire with the following considerations, and ensure to follow all provided rules and format structure.
                Instructions:
                 
                    0.Preferred Language generation: generate the entire output questionnaire in the patient’s preferred **{data['pt_language']}** .(default to English if not provided), but always list medications in English exactly as in the encounter data with no additions( Medication Language Requirement: Medications must always be presented in English regardless of the patient's preferred language; do not translate medication names (e.g., if the preferred language is Spanish, medication names remain in English). )
                    1.The output must strictly follow the exact sequence of questions provided without any changes in order.    
                    2.Strictly follow the json format given in example output.
                    3.Age and Gender: Tailor the questions according to the patients age and gender.
                    4.CareTeam: Include the care team information from the latest encounter only.Latest Encounter is Encounter NO 1. if no care team information is available then please ask the patient to provide care team information.question Please provide their name, specialty and a contact number. type: text.
                    4.Diagnosis: Add all ICDS into the questionnaire in Diagnosis section from only {data['et1_icds']}.
                    5.Allergies: Very important section - check if patient has allergies from encounter data {data['et1_alg']}, {data['et2_alg']}, {data['et3_alg']}
                    6.Medication: Pick Medications from encounter MEDICATIONS: please list the medications from the below encounters in the questionnaire.(only pick from below latest encounter medications)
                    {data['et1_med']}
                    🚨 CRITICAL MEDICATION REQUIREMENTS - NO EXCEPTIONS:
                    
                    **MANDATORY MEDICATION INCLUSION RULES:**
                    1. **INCLUDE EVERY SINGLE MEDICATION** from the latest encounter (et1_med) - NO OMISSIONS ALLOWED
                    2. **DO NOT SKIP ANY MEDICATION** regardless of type (prescription, OTC, supplements, inhalers, injections)
                    3. **EXACT MEDICATION MATCHING** - Use the EXACT text from encounter data with NO modifications
                    4. **ALPHABETICAL ORDERING** - List all medications in alphabetical order by medication name
                    5. **COMPLETE MEDICATION LIST** - If encounter has 10 medications, questionnaire MUST have all 10
                    
                    **MEDICATION VALIDATION CHECKLIST:**
                    ✓ Count total medications in encounter: {data['et1_med']}
                    ✓ Verify every medication appears in questionnaire options
                    ✓ Confirm exact text matching (dosage, frequency, instructions)
                    ✓ Check alphabetical ordering is correct
                    ✓ Ensure NO medications are excluded or omitted
                    
                    **FAILURE TO INCLUDE ALL MEDICATIONS WILL CAUSE SYSTEM ERROR**
                    9.Current month goals and interventions:
                    CRITICAL REQUIREMENT - Goals and Interventions for ALL Chronic Conditions:
                    **MANDATORY: You MUST generate goals and interventions for EVERY SINGLE chronic condition ICD code listed below. NO EXCEPTIONS. NO OMISSIONS.**
                    
                    **Source ICD Codes from Latest Encounter:**
                    - Encounter 1 ICDs: {data['et1_icds']}
                    Include the goals and interventions for the current month, based on the patient's all chronic conditions DIAGNOSIS (ICDS):
                            . Ensure that the goals are specific, measurable, achievable, relevant, and time-bound (SMART). The interventions should be evidence-based and tailored to the patient's needs. Also generate educational resources for each chronic condition, such as reputable links (e.g., MedlinePlus or CDC) to support patient self-management. For each chronic condition, provide:
                                - A clear goal statement that is measurable and time-bound.
                                - A list of interventions (medication adherence, lifestyle changes, monitoring, follow-up). 🚨**You must never include medication name in Interventions**
                                - An education & self-management section with a relevant patient-friendly link.
                    10.In the reminder, the last appointment date should be **{data['last_appointment_date']}** and future appointment date is **{data['appointment_date']}**.🚨 If there is no "future appointment", do not show this section.
                    10.Ensure that the questionnaire is comprehensive, follows the specified rules, and adheres to the format structure provided.
                    11.JSON Structure Compliance: Confirm that the output strictly adheres to the JSON format, including appropriate titles, types, and content organization according to the specified requirements.
                    12.Medications should be alphabetically ordered.
                    ERROR PREVENTION:
                    - No markdown formatting (```, **, etc.)
                    - No unescaped quotes in JSON strings
                    - No line breaks in JSON string values
                    - Validate JSON structure before returning

                    OUTPUT ONLY THE JSON - NO OTHER TEXT:
                Output:
            """
            return prompt
        except Exception as e:
            print(e)
            error_logger.error(str(e))
            raise ApplicationException()            