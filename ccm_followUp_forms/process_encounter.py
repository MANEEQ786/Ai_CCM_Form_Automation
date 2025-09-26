import uuid
import pandas as pd
import logging
from ccm_followUp_forms.generate_response import GenerateResponse
from ccm_followUp_forms.prompt import JsonPrompts
from ccm_followUp_forms.utils.utils import clean_json_response
from utils import *
info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')


def get_encounters_details(data_frames):
        et_htmls = {
            'et1_html': ''
        }
        parm_dict = {}
        try:
            ######### Vitals/ HPI / CC ############
            et1_visit_Date = ''
            et1_vitals = ''
            et1_cheifComplaint = ''
            et1_hpi = ''
            et1_html = ''
            pt_age, pt_gender, patient_language = '', '', 'no language'
            pt_practice_code = 0
            patient_name=''

            data1 = data_frames[0]
            data1.columns = data1.columns.str.upper()
            if data1.shape[0] > 0:
                pt_age = str(data1[data1['ENCOUNTER_NO'] == 1]['DOB'].iat[0])
                pt_gender = data1[data1['ENCOUNTER_NO'] == 1]['GENDER'].iat[0]
                patient_language = data1[data1['ENCOUNTER_NO'] == 1]['PREFERRED_LANGUAGE'].iat[0]
                pt_practice_code = int(data1[data1['ENCOUNTER_NO'] == 1]['PRACTICE_CODE'].iat[0])
                patient_name = str(data1[data1['ENCOUNTER_NO'] == 1]['PATIENT_NAME'].iat[0])

                et1_visit_Date = str(data1[data1['ENCOUNTER_NO'] == 1]['VISIT_DATE'].iat[0])
                et1_vitals = data1[data1['ENCOUNTER_NO'] == 1]['VITALS'].iat[0]
                et1_cheifComplaint = data1[data1['ENCOUNTER_NO'] == 1]['CHEIFCOMPLAINT'].fillna('').iloc[0].strip()
                et1_hpi = data1[data1['ENCOUNTER_NO'] == 1]['HPI'].fillna('').iloc[0].strip()
                et1_html = data1[data1['ENCOUNTER_NO'] == 1]['NOTE_HTML'].iat[0]

            parm_dict['et1_visit_Date'] = et1_visit_Date
            parm_dict['et1_vitals'] = et1_vitals
            parm_dict['et1_cheifComplaint'] = et1_cheifComplaint
            parm_dict['et1_hpi'] = et1_hpi
            parm_dict['pt_age'] = pt_age
            parm_dict['pt_gender'] = pt_gender
            parm_dict['patient_name'] = patient_name

            if pd.isnull(patient_language) or patient_language.strip() == "":
                patient_language = "no language"
            parm_dict['pt_language'] = patient_language
            parm_dict['pt_practice_code'] = pt_practice_code
            et_htmls = {
                'et1_html': et1_html,
            }

            ########### CARE TEAM #######
            df_careteam = data_frames[1]
            df_careteam.columns = df_careteam.columns.str.upper()
            care_teams = ''
            if df_careteam.shape[0] > 0:
                for index, row in df_careteam.iterrows():
                    care_teams += 'Name: ' + str(row['DOC_NAME'])
                    care_teams += ', Relation: ' + str(row['RELATION'])
                    care_teams += ', Contact#: ' + str(row['PHONE'])
                    care_teams += ' Email: ' + str(row['EMAIL'])
                    care_teams += '\n'
            if care_teams.strip() == "":
                care_teams = "no Care Team"
            parm_dict['care_team'] = care_teams

            ########## ICDS ##########
            print('innnnnnnnnnnnnnn')
            df_icd = data_frames[2]
            df_icd.columns = df_icd.columns.str.upper()
            et1_icds = ''
            if df_icd.shape[0] > 0:
                et1_icds = "\n".join(map(str, df_icd[df_icd['ENCOUNTER_NO'] == 1]['ICDS'].tolist()))

            try:
                icds_list=df_icd[df_icd['ENCOUNTER_NO'] == 1]['ICD10_CODE'].tolist()
                print('before:',icds_list)
                prompt = JsonPrompts.predict_chronic_icds(icds_list)
                response = GenerateResponse.generate_response(prompt)
                info_logger.info(f'{uuid} | Gemini response: {response}')
                et1_icds = clean_json_response(response,uuid)
                print('after:',et1_icds)
            except Exception as e:
                error_logger.error(str(e))
                print(e)
            parm_dict['et1_icds'] = et1_icds
             

            ############### PLAN OF CARE #############
            df_poc = data_frames[3]
            df_poc.columns = df_poc.columns.str.upper()
            et1_poc = ''

            if df_poc.shape[0] > 0:
                filtered_df = df_poc[df_poc['ENCOUNTER_NO'] == 1]
                if not filtered_df.empty:
                    value = filtered_df['PATIENT_PLANOFCARE_COMMENTS_TEXT'].iat[0]
                    if isinstance(value, str):
                        et1_poc = value.strip()
                    else:
                        et1_poc = str(value) 
                    
            parm_dict['et1_poc'] = et1_poc

            ################ CPTS ################
            df_cpts = data_frames[4]
            df_cpts.columns = df_cpts.columns.str.upper()
            et1_cpts = ''
            if df_cpts.shape[0] > 0:
                et1_cpts = "\n".join(map(str, df_cpts[df_cpts['ENCOUNTER_NO'] == 1]['CPTS'].tolist()))

            parm_dict['et1_cpts'] = et1_cpts

            ############## IMMUNIZATION ##################
            df_imz = data_frames[5]
            df_imz.columns = df_imz.columns.str.upper()
            et1_imz_hist, et1_imz_adm, et1_imz_ref = '', '', ''

            if df_imz.shape[0] > 0:
                df_imz['IMMUNIZATION_TYPE'] = df_imz['IMMUNIZATION_TYPE'].astype(str).str.lower()
                et1_imz_ref = "\n".join(map(str, df_imz[(df_imz['ENCOUNTER_NO'] == 1) & (df_imz['IMMUNIZATION_TYPE'] == 'refusal')]['IMMUNIZATION'].tolist()))
                et1_imz_hist = "\n".join(map(str, df_imz[(df_imz['ENCOUNTER_NO'] == 1) & (df_imz['IMMUNIZATION_TYPE'] == 'historical')]['IMMUNIZATION'].tolist()))
                et1_imz_adm = "\n".join(map(str, df_imz[(df_imz['ENCOUNTER_NO'] == 1) & (df_imz['IMMUNIZATION_TYPE'] == 'administered')]['IMMUNIZATION'].tolist()))

            parm_dict['et1_imz_hist'] = et1_imz_hist
            parm_dict['et1_imz_adm'] = et1_imz_adm
            parm_dict['et1_imz_ref'] = et1_imz_ref

            ######### HISTORY ###########
            parm_dict['et1_history_sx'] = ""
            parm_dict['et1_history_pmh'] = ""
            parm_dict['et1_history_psh'] = ""
            parm_dict['et1_history_risk'] = ""

            ########## MEDICATIONS ################
            df_med = data_frames[7]
            df_med.columns = df_med.columns.str.upper()
            et1_med = 'No medications'
            if df_med.shape[0] > 0:
                et1_med = "\n".join(map(str, df_med[df_med['ENCOUNTER_NO'] == 1]['MED_RESULT'].tolist()))
            parm_dict['et1_med'] = et1_med

            ########## ALLERGY ################
            df_allergy = data_frames[8]
            df_allergy.columns = df_allergy.columns.str.upper()
            et1_alg = 'no allergies'
            if df_allergy.shape[0] > 0:
                et1_alg = "\n".join(map(str, df_allergy[df_allergy['ENCOUNTER_NO'] == 1]['ALLERGY_RESULT'].tolist()))
            parm_dict['et1_alg'] = et1_alg

            return parm_dict, et_htmls
        except Exception as e:
            error_logger.error(str(e))
            print(e)
