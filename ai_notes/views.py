import warnings, os
warnings.filterwarnings("ignore")
import vertexai
from vertexai.preview.language_models import TextGenerationModel
from vertexai.preview.generative_models import GenerativeModel, Part

import traceback
import secrets
import json
import time
from datetime import datetime

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
from django.utils.decorators import method_decorator
from django.views import View

from ccm_followUp_forms.utils.custom_exception import ApplicationException
from ccm_followUp_forms.utils.utils import *

import logging
info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')

# Initialize Vertex AI
try:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/aiml-365220-b6aec5dba4a2.json"
    vertexai.init(project="aiml-365220", location="us-central1")
    model = GenerativeModel("gemini-2.0-flash")
    info_logger.info("Vertex AI initialized successfully")
except Exception as e:
    error_logger.error(f"Failed to initialize Vertex AI: {str(e)}")
    model = None

class GenerateAINotesResponse:
    def __init__(self):
        pass
    
    @staticmethod
    def generate_response(prompt):
        try:
            if model is None:
                raise ApplicationException("AI model not initialized")
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 8192,
                    "temperature": 0.3,
                    "top_p": 0.95,
                },
            )
            
            if not response or not response.text:
                raise ApplicationException("Empty response from AI model")
            
            res = response.text
            res = res.replace('**','')
            res = res.replace('```json','')
            res = res.replace('```','')
            res = res.replace('###','')
            
            info_logger.info(f"Generated AI Notes response successfully")
            return res
            
        except Exception as e:
            error_logger.error(f"AI generation error: {str(e)}")
            if "429" in str(e):
                raise ApplicationException("The service is temporarily out of capacity. Please try again later.")
            elif "quota" in str(e).lower():
                raise ApplicationException("API quota exceeded. Please try again later.")
            elif "permission" in str(e).lower():
                raise ApplicationException("Permission denied. Please check AI credentials.")
            else:
                raise ApplicationException(f"Failed to generate AI response: {str(e)}")

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
        return JsonResponse({"Response": "Ai_notes is working fine"})

class GetAiNotes(APIView):
    def post(self, request, format=None):
        bad_request = False
        uid = secrets.token_hex(5)
        method = request.method
        url = request.path
        headers = dict(request.headers)
        remote_address = request.META.get('REMOTE_ADDR')
        request_log = f"{method} on {url} from {remote_address}"
        info_logger.info(f'request uid:{uid}')
        info_logger.info(f"[{uid}] | {request_log}")

        try:
            # Parse and validate request data
            if not request.body:
                bad_request = True
                raise ApplicationException("Request body is required", 400)
            
            try:
                request_data = json.loads(request.body)
                info_logger.info(f'{uid} | Request data received successfully')
            except json.JSONDecodeError as je:
                bad_request = True
                error_logger.error(f'{uid} | JSON decode error: {str(je)}')
                raise ApplicationException("Invalid JSON format", 400)
            
            # Validate payload structure - only "data" field required
            if 'data' not in request_data:
                bad_request = True
                raise ApplicationException("'data' field is required in payload", 400)
            
            clinical_data = request_data.get('data', '')
            
            if not clinical_data or not isinstance(clinical_data, str):
                bad_request = True
                raise ApplicationException("'data' field cannot be empty and must be a string", 400)
            
            if len(clinical_data.strip()) == 0:
                bad_request = True
                raise ApplicationException("'data' field cannot be empty", 400)
            
            info_logger.info(f'{uid} | Processing clinical data for AI analysis, data length: {len(clinical_data)}')
            
            # Generate AI clinical summary prompt
            ai_prompt = self.create_clinical_analysis_prompt(clinical_data, uid)
            info_logger.info(f'{uid} | AI prompt prepared, prompt length: {len(ai_prompt)}')
            
            # Generate AI response
            ai_response = GenerateAINotesResponse.generate_response(ai_prompt)
            info_logger.info(f'{uid} | AI response generated successfully')
            
            # Format the final AI notes
            ai_notes = self.format_clinical_notes(ai_response, uid)
            
            # Prepare response - exactly as requested
            response_data = {
                "status": True,
                "ai_notes": ai_notes
            }
            
            info_logger.info(f'{uid} | AI notes generated successfully')
            return JsonResponse(response_data)
            
        except ApplicationException as ae:
            error_logger.error(f'{uid} | Application Exception: {str(ae)}')
            if bad_request:
                return JsonResponse({"message": str(ae)}, status=400)
            else:
                return JsonResponse({"message": str(ae)}, status=500)
            
        except Exception as e:
            error_logger.error(f'{uid} | Unexpected error: {str(e)}')
            error_logger.error(f'{uid} | Traceback: {traceback.format_exc()}')
            
            if "429" in str(e):
                return JsonResponse({"message": "The service is temporarily out of capacity. Please try again later."}, status=429)
            elif "quota" in str(e).lower():
                return JsonResponse({"message": "API quota exceeded. Please try again later."}, status=429)
            elif "permission" in str(e).lower():
                return JsonResponse({"message": "Permission denied. Please check configuration."}, status=403)
            else:
                return JsonResponse({"message": f"Internal server error: {str(e)}"}, status=500)
    
    def create_clinical_analysis_prompt(self, clinical_data, uid):
        """
        Create a comprehensive prompt for AI clinical analysis
        """
        info_logger.info(f'{uid} | Creating clinical analysis prompt')
        
        # Sanitize the clinical data
        sanitized_data = str(clinical_data).strip()
        if len(sanitized_data) > 50000:  # Limit input size
            sanitized_data = sanitized_data[:50000] + "... [truncated]"

        prompt = f"""You are a highly experienced clinical professional with 50+ years of expertise in patient care, clinical assessment, and healthcare decision-making. You have deep knowledge in hypertension management, chronic disease workflows, and remote patient monitoring (RPM). You are tasked with creating a monthly summary of blood pressure logs for clinician review.

            **CLINICAL DATA TO ANALYZE:**
            {sanitized_data}

            **TASK:**
            Deeply analyze the ENTIRE clinical data provided above and generate a CONCISE patient-specific summary in exactly 4-5 lines only. Focus on the most critical and actionable insights for this patient's care.

            **REQUIREMENTS:**
            - Deeply analyze all aspects of the clinical data including patterns, trends, and relationships
            - Identify key clinical patterns and trends specific to this patient
            - Highlight urgent/critical findings requiring immediate attention
            - Use precise medical terminology appropriate for clinical documentation
            - Keep summary to 4-5 lines maximum

            **CRITICAL INSTRUCTION:**
            Do NOT include any introductory phrases like "Here's a concise clinical summary" or "Based on the provided data". Start directly with the clinical findings specific to this patient.

            **OUTPUT FORMAT:**
            Provide only a brief, professional clinical summary (4-5 lines) that captures the essential clinical status, key findings, and immediate recommendations for this patient's healthcare team."""
        
        return prompt

    def format_clinical_notes(self, ai_response, uid):
        """
        Format and clean the AI response for clinical use
        """
        try:
            if not ai_response:
                return "AI analysis completed but no specific notes generated."
            
            # Basic cleaning
            formatted_notes = str(ai_response).strip()
            
            # Remove any remaining markdown artifacts
            formatted_notes = formatted_notes.replace('**', '')
            formatted_notes = formatted_notes.replace('```json', '')
            formatted_notes = formatted_notes.replace('```', '')
            formatted_notes = formatted_notes.replace('###', '')
            formatted_notes = formatted_notes.replace('##', '')
            
            # Clean up extra whitespace
            lines = formatted_notes.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            formatted_notes = '\n'.join(cleaned_lines)
            
            # Ensure proper formatting
            if not formatted_notes or len(formatted_notes.strip()) == 0:
                formatted_notes = "AI analysis completed but no specific notes generated."
            
            info_logger.info(f'{uid} | AI notes formatted successfully, final length: {len(formatted_notes)}')
            return formatted_notes
            
        except Exception as e:
            error_logger.error(f'{uid} | Error formatting AI notes: {str(e)}')
            return f"Clinical Analysis Completed - Raw Output: {str(ai_response) if ai_response else 'No response'}"