import traceback
import json
import re
from config.config import *
from ccm_initialfroms.utils.custom_exception import ApplicationException
from rest_framework.exceptions import APIException

import logging
info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')

class GenerateResponse:
    def __init__(self):
        pass
    
    @staticmethod
    def clean_json_response(response_text):
        """Clean invalid control characters and format JSON properly"""
        try:
            # Remove invalid control characters (addresses the line 157 column 27 error)
            cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_text)
            
            # Fix common JSON formatting issues
            cleaned_text = cleaned_text.replace('\n', '\\n')
            cleaned_text = cleaned_text.replace('\t', '\\t')
            cleaned_text = cleaned_text.replace('\r', '\\r')
            cleaned_text = cleaned_text.replace('\b', '\\b')
            cleaned_text = cleaned_text.replace('\f', '\\f')
            
            # Remove markdown formatting
            cleaned_text = cleaned_text.replace('**', '')
            cleaned_text = cleaned_text.replace('```json', '')
            cleaned_text = cleaned_text.replace('```', '')
            
            # Validate JSON structure
            json.loads(cleaned_text)
            return cleaned_text
            
        except json.JSONDecodeError as e:
            error_logger.error(f"JSON parsing error: {e}")
            raise ApplicationException(f"Invalid JSON response format: {str(e)}")
        except Exception as e:
            error_logger.error(f"Error cleaning response: {e}")
            raise ApplicationException("Failed to process response")
    
    @staticmethod
    def generate_response(prompt):
        try:
            # Check if response object exists and has content
            response = model.generate_content(
                prompt,
                safety_settings=safety_config,
                generation_config={
                    "max_output_tokens": 65000,
                    "temperature": 0.3,
                    "top_p": 0.95,
                },
            )
            
            # Handle MAX_TOKENS and blocked content issues
            if not response.candidates:
                error_logger.error("No candidates in response")
                raise ApplicationException("No response generated. Please try with a shorter prompt.")
            
            candidate = response.candidates[0]
            
            # Check if content was blocked by safety filters
            if candidate.finish_reason == "SAFETY":
                error_logger.error("Content blocked by safety filters")
                raise ApplicationException("Content was blocked by safety filters. Please modify your request.")
            
            # Check if response hit max tokens
            if candidate.finish_reason == "MAX_TOKENS":
                error_logger.error("Response hit maximum token limit")
                raise ApplicationException("Response too long. Please try with a more concise prompt.")
            
            # Check if response has content
            if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                error_logger.error("Response candidate content has no parts")
                raise ApplicationException("Empty response received. Please try again.")
            
            # Get the response text
            if hasattr(response, 'text') and response.text:
                res = response.text
            else:
                error_logger.error("Cannot get response text")
                raise ApplicationException("Cannot extract response text. Please try again.")
            
            # Clean and validate the response
            cleaned_response = GenerateResponse.clean_json_response(res)

            info_logger.info(f"Response generated successfully: {cleaned_response}")
            return cleaned_response
            
        except ApplicationException:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            error_msg = f"Unexpected error in generate_response: {str(e)}"
            error_logger.error(error_msg)
            error_logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Handle specific error cases
            if "429" in str(e):
                raise ApplicationException("The service is temporarily out of capacity. Please try again later.")
            elif "quota" in str(e).lower():
                raise ApplicationException("API quota exceeded. Please try again later.")
            elif "timeout" in str(e).lower():
                raise ApplicationException("Request timeout. Please try again.")
            elif "connection" in str(e).lower():
                raise ApplicationException("Connection error. Please check your internet connection.")
            else:
                raise ApplicationException("Something went wrong. Please try again later.")