from rest_framework.views import APIView
from rest_framework import viewsets
from django.template.loader import render_to_string

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from rest_framework.decorators import action
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
import secrets

import json
import time

from ccm_followUp_forms.utils.custom_exception import ApplicationException
from ccm_followUp_forms.utils.utils import *
from ccm_followUp_forms.DbOps.DataProcessor import DataProcessor 
from ccm_followUp_forms.DbOps.dump2db import DBConnection, DumpToDB
from ccm_followUp_forms.prompt import JsonPrompts
from ccm_followUp_forms.generate_response import GenerateResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import logging

info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')
from django.views import View
class Home(APIView):
    def get(self, request, *args, **kwargs):
        uid = secrets.token_hex(5)
        info_logger.info(f'request uid:{uid}')
        
        context = {
            'response': '',
            'prompt': '',
            'et1_html': '<p></p>'
        }
        return render(request, 'index.html', context)


class Test(APIView):
    def get(self, request, format=None):
            return JsonResponse({"Response":"CCM Forms is working fine"})

class Predict_icd(APIView):
    def post(self, request, format=None):
        bad_request=False
        uid = secrets.token_hex(5)
        method = request.method
        url = request.path
        headers = request.headers
        remote_address = request.META.get('REMOTE_ADDR')
        request_log = f"{method} on {url} from {remote_address} having headers: {headers}"
        info_logger.info(f'request uid:{uid}')
        info_logger.info(f"[{uid}] | {request_log}")
        try :
            icds = request.data.get('icds')
            if not icds:
                bad_request=True
                raise ApplicationException(detail="bad request",code=400)
            
            info_logger.info(f'{uid}: {icds}')

            prompt = JsonPrompts.predict_chronic_icds(icds)
            response = GenerateResponse.generate_response(prompt)
            info_logger.info(f'{uid} | Gemini response: {response}')
            cleaned_response = clean_json_response(response,uid)
            
            info_logger.info(f'{uid} | response: {json.dumps(cleaned_response, indent= 4)}')
            response = {"status":True,"chronic_icds":cleaned_response}
            # print(response)
            return JsonResponse(response)
            # return JsonResponse(cleaned_response)
        except Exception as e:
            if not bad_request:
                error_logger.error(str(e))
                if "429" in str(e):
                    raise ApplicationException("The service is temporarily out of capacity. Please try again later.")
                raise ApplicationException()
            if bad_request:
                error_logger.error(f'{uid} | {e}')
                raise ApplicationException(str(e),400)

class GetFollowUpForm(APIView):
    def post(self, request, format=None):
        bad_request=False
        uid = secrets.token_hex(5)
        method = request.method
        url = request.path
        headers = request.headers
        remote_address = request.META.get('REMOTE_ADDR')
        request_log = f"{method} on {url} from {remote_address} having headers: {headers}"
        info_logger.info(f'request uid:{uid}')
        info_logger.info(f"[{uid}] | {request_log}")
        try :
            patient_account = request.data.get('patient_account')
            if not patient_account:
                bad_request=True
                raise ApplicationException(detail="bad request",code=400)
            try:
                patient_account=int(patient_account)
            except Exception as e:
                bad_request=True
                error_logger.error(f'{uid} | {e}')
                raise ApplicationException(detail="Patient account must be a Integer",code=400)
            info_logger.info(f'{uid}: {patient_account}')

            # if not DumpToDB.check_form_status(patient_account,uid):
            #     response= {"response":"Form status is REVIEWED. You can proceed after one month of created date.Can't be recreated.", "status":False,"PATIENT_FORM_ID":None}
            #     return JsonResponse(response)
                
            form_data, encounter_data, appointment_date,last_appointment = DataProcessor.process_encounters(uid, patient_account)
            def is_encounter_data_empty(encounter_data):
                
                empty_values = {
                    'et1_visit_Date': '',
                    'et1_vitals': '',
                    'et1_cheifComplaint': '',
                    'et1_hpi': '',
                    'pt_age': '',
                    'pt_gender': '',
                    'patient_name': '',
                    'pt_language': 'no language',
                    'pt_practice_code': 0,
                    'care_team': 'no Care Team',
                    'et1_icds': '',
                    'et1_poc': '',
                    'et1_cpts': '',
                    'et1_imz_hist': '',
                    'et1_imz_adm': '',
                    'et1_imz_ref': '',
                    'et1_history_sx': '',
                    'et1_history_pmh': '',
                    'et1_history_psh': '',
                    'et1_history_risk': '',
                    'et1_med': 'No medications',
                    'et1_alg': 'no allergies'
                }
                
                for key, value in encounter_data.items():
                    if value != empty_values.get(key, None):
                        return False  
                return True  

            if not form_data and is_encounter_data_empty(encounter_data):
                response = {"response": "not data found", "status": False, "PATIENT_FORM_ID": "null"}
                return JsonResponse(response)

            form_data = json.dumps(form_data, indent=4)
            info_logger.info(f'Encounter Data:{json.dumps(encounter_data, indent= 4)}')
            info_logger.info(f'Form Data:{form_data}')
            prompt = JsonPrompts.init_prompt_v2(encounter_data, form_data, appointment_date,last_appointment)
            response = GenerateResponse.generate_response(prompt)
            info_logger.info(f'{uid} | Gemini response: {response}')
            cleaned_response = clean_json_response(response,uid)
            PATIENT_FORM_ID=DumpToDB.parse_json(cleaned_response,patient_account,encounter_data['pt_gender'],encounter_data['pt_practice_code'],uid,encounter_data['patient_name'])
            info_logger.info(f'{uid} | response: {json.dumps(cleaned_response, indent= 4)}')
            response = {"response":"Form Created", "status":True,"PATIENT_FORM_ID":PATIENT_FORM_ID}
            return JsonResponse(response)
            # return JsonResponse(cleaned_response)
        except Exception as e:
            if not bad_request:
                error_logger.error(str(e))
                if "429" in str(e):
                    raise ApplicationException("The service is temporarily out of capacity. Please try again later.")
                raise ApplicationException(str(e))
            if bad_request:
                error_logger.error(f'{uid} | {e}')
                raise ApplicationException(str(e),400)