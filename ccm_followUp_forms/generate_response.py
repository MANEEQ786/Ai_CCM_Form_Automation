
import traceback
from config.config import *
from ccm_followUp_forms.utils.custom_exception import ApplicationException
from rest_framework.exceptions import APIException

import logging
info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')

class GenerateResponse:
    def __init__(self):
        pass
    @staticmethod
    def generate_response(prompt):
        try:
            response = model.generate_content(
                    prompt,
                    generation_config={
                        "max_output_tokens": 65000,
                        "temperature": 0.3,
                        "top_p": 0.95,                    },
                )
            res = response.text
            res=res.replace('**','')
            res=res.replace('```json','')
            res=res.replace('```','')
            info_logger.info(f"Generated response: {res}")
            return res
        except Exception as e:
            error_logger.error(str(e))
            if "429" in str(e):
                raise ApplicationException("The service is temporarily out of capacity. Please try again later.")
            else:
                raise ApplicationException()
