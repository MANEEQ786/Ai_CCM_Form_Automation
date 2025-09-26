from rest_framework.views import APIView
from rest_framework import viewsets
from django.template.loader import render_to_string

from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

from rest_framework.decorators import action
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
import secrets
from django.conf import settings

import json, os, zipfile
import time

from ccm_initialfroms.generate_response import GenerateResponse
from ccm_initialfroms.utils.custom_exception import ApplicationException
from ccm_initialfroms.encounter import Encounter

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import logging

info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')


# class Home(APIView):
#     def get(self, request, *args, **kwargs):
#         uid = secrets.token_hex(5)
#         info_logger.info(f'request uid:{uid}')
        
#         context = {
#             'response': '',
#             'prompt': '',
#             'et1_html': '<p></p>',
#             'et2_html': '<p></p>',
#             'et3_html': '<p></p>'
#         }
#         return render(request, 'index.html', context)


class Test(APIView):
    def get(self, request, format=None):
        return JsonResponse({"Response":"CCM Forms is working fine"})
    
class GetLogs(APIView):
    def get(self, request):
        try:
            uid = secrets.token_hex(5)
            method = request.method
            url = request.path
            headers = request.headers
            remote_address = request.META.get('REMOTE_ADDR')
            request_log = f"{method} on {url} from {remote_address} having headers: {headers}"
            info_logger.info(f'request uid:{uid}')
            info_logger.info(f"[{uid}] | {request_log}")
            DOWNLOAD_TOKEN = 'Ds@098765'
            token = request.GET.get('token')  # Get token from query parameters
            if token != DOWNLOAD_TOKEN:
                error_logger.error(f'{uid} | Unauthorized status=401')
                return HttpResponse('Unauthorized', status=401)
            path = 'API_LOGS'
            directory = os.path.join(settings.BASE_DIR, path)
            files_to_download = os.listdir(path)
            zip_filename = 'CCM-Logs.zip'
            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={zip_filename}'

            with zipfile.ZipFile(response, 'w') as zip_file:
                for file_name in files_to_download:
                    file_path = os.path.join(directory, file_name)
                    if os.path.exists(file_path):
                        zip_file.write(file_path, arcname=file_name)
            return response
        except Exception as e:
            error_logger.error(f'{uid} | {e}')
            raise ApplicationException()

class GetInitForms(APIView):
    def get(self,request):
        return Response({"status": "Failure", "message": "Get method Not ALLOWED"}, status=400)
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
            response = Encounter.process_ccm_form(patient_account,uid)
            info_logger.info(f'{uid} | response: {response}')
            return JsonResponse(response)
        except Exception as e:
            if not bad_request:
                error_logger.error(str(e))
                if "429" in str(e):
                    raise ApplicationException("The service is temporarily out of capacity. Please try again later.")
                raise ApplicationException()
            if bad_request:
                error_logger.error(f'{uid} | {e}')
                raise ApplicationException(str(e),400)