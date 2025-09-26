# import json
# import requests
# import uuid

# import logging

# info_logger = logging.getLogger('api_info')
# error_logger = logging.getLogger('api_error')


# class HistoryService:
#     """
#     Unified service for retrieving all patient history data in a single call
#     """
    
#     # API URLs
#     FAMILY_HISTORY_API_URL = 'https://mhealth.mtbc.com/SmartTALKPHR/api/Checkin/Familyhistory/GetFamilyHistory'
#     SOCIAL_HISTORY_API_URL = 'https://mhealth.mtbc.com/SmartTALKPHR/api/Checkin/SocialHistory/GetSocialHistory'
#     PAST_SURGICAL_HISTORY_API_URL = 'https://mhealth.mtbc.com/SmartTALKPHR/api/Checkin/SurgicalHistory/GetPastSurgicalHistory'
#     PAST_HOSPITALIZATION_API_URL = 'https://mhealth.mtbc.com/SmartTALKPHR/api/Checkin/PastHospitalization/GetPastHospitalization'
#     AUTH_API_URL = 'https://mhealth.mtbc.com/SmartTALKPHR/api/Auth/Login'

#     @staticmethod
#     def get_auth_token(uid: str) -> str:
#         """
#         Get authentication token for API requests
        
#         Args:
#             uid: Unique identifier for logging
            
#         Returns:
#             str: Access token for API authentication
#         """
#         payload = {
#             "CELLPHONE": "",
#             "DOB": "",
#             "LASTNAME": "",
#             "loginType": "user credentials",
#             "password": "2211ba1417311ee6a901f819a3116ab511386a5ca4d9c44d18cd2134634736cf3e23c9338171fa64aa9adc556be989cee970c35a5f95d35f08d856ff746b1aee",
#             "timezone": "",
#             "userName": "carecloud.mobile.team@gmail.com"
#         }
        
#         info_logger.debug(f'{uid} | AUTH API: Request payload: {json.dumps(payload, indent=4)}')
                
#         headers = {
#             'Content-Type': 'application/json-patch+json',
#             'accept': '*/*'
#         }
        
#         try:           
#             response = requests.post(
#                 HistoryService.AUTH_API_URL,
#                 headers=headers,
#                 json=payload,
#                 timeout=10
#             )
            
#             info_logger.info(f'{uid} | HISTORY AUTH API: Auth response status code: {response.status_code}')
#             response.raise_for_status()
#             auth_data = response.json()
        
#             token = None
            
#             if (auth_data.get('statusCode') == 200 and 
#                 'data' in auth_data and 
#                 'accessTokenResponse' in auth_data['data'] and 
#                 'accessToken' in auth_data['data']['accessTokenResponse']):
                
#                 token = auth_data['data']['accessTokenResponse']['accessToken']
                
#             else:
#                 error_logger.error(f'{uid} | HISTORY AUTH API: Could not find accessToken in expected location')
            
#             if not token:
#                 error_logger.error(f'{uid} | HISTORY AUTH API: Auth token not found in response')
#                 raise Exception(
#                     "Failed to retrieve auth token"
#                 )

#             info_logger.info(f'{uid} | HISTORY AUTH API: Successfully retrieved auth token')
#             return token
            
#         except requests.RequestException as e:
#             error_logger.error(f'{uid} | HISTORY AUTH API: Auth API call failed with status {getattr(e.response, "status_code", "No status")}')
#             error_logger.exception(f'{uid} | HISTORY AUTH API: Auth failure details: {str(e)}')
#             raise Exception(
#                 "Failed to authenticate with history API"
#             )

#     @staticmethod
#     def get_history(patient_account: str, practice_code: str, uid: str = None) -> dict:
#         """
#         Get all patient history data in a single consolidated response
        
#         Args:
#             patient_account: Patient's account number
#             practice_code: Practice code
#             uid: Unique identifier for logging
            
#         Returns:
#             dict: Dictionary containing all history data with keys:
#                 - FamilyHistory: List of family history entries
#                 - SocialHistory: Dictionary of social history data
#                 - PastSurgicalHistory: List of past surgical history entries
#                 - PastHospitalization: List of past hospitalization entries
#         """
        
#         # Generate UID if not provided
#         if not uid:
#             uid = str(uuid.uuid4())
        
#         # Input validation
#         if not patient_account:
#             error_logger.error(f'{uid} | HISTORY API: Missing PATIENT_ACCOUNT')
#             raise Exception(
#                 "Missing PATIENT_ACCOUNT"
#             )
#         if not practice_code:   
#             error_logger.error(f'{uid} | HISTORY API: Missing PRACTICE_CODE')
#             raise Exception(
#                 "Missing PRACTICE_CODE"
#             )

#         info_logger.info(f'{uid} | HISTORY API: Starting consolidated history retrieval for patient: {patient_account}')
        
#         # Initialize result dictionary
#         consolidated_history = {
#             'FamilyHistory': [],
#             'SocialHistory': {},
#             'PastSurgicalHistory': [],
#             'PastHospitalization': []
#         }
        
#         # Get authentication token once for all requests
#         try:
#             token = HistoryService.get_auth_token(uid)
#             headers = {'Authorization': f'Bearer {token}'}
#             params = {'PracticeCode': practice_code, 'PatientAccount': patient_account}
            
#             info_logger.debug(f'{uid} | HISTORY API: Using parameters: {json.dumps(params, indent=4)}')
            
#         except Exception as e:
#             error_logger.error(f'{uid} | HISTORY API: Failed to get auth token: {str(e)}')
#             raise Exception(
#                 "Failed to authenticate with history API"
#             )

#         # 1. GET FAMILY HISTORY
#         try:
#             info_logger.info(f'{uid} | HISTORY API: Fetching Family History...')
            
#             response = requests.get(
#                 HistoryService.FAMILY_HISTORY_API_URL,
#                 headers=headers,
#                 params=params,
#                 timeout=10
#             )
#             response.raise_for_status()
#             family_data = response.json()
            
#             if family_data and family_data.get('statusCode') == 200:
#                 family_history_list = family_data.get('data', {}).get('familyHistories', [])
                
#                 for fh in family_history_list:
#                     # Extract disease name from diagnosis description
#                     diagnosis_desc = fh.get('familyHistoryDiagnosisDescription', '')
#                     disease_name = ''
#                     if 'ICD9:' in diagnosis_desc:
#                         start_idx = diagnosis_desc.find('ICD9:') + 5
#                         end_idx = diagnosis_desc.find('Snomed:')
#                         if end_idx > start_idx:
#                             disease_name = diagnosis_desc[start_idx:end_idx].strip()
#                         else:
#                             disease_name = diagnosis_desc[start_idx:].strip()
                    
#                     # Map relationship codes to names
#                     relationship_mapping = {
#                         'F': 'Father', 'M': 'Mother', 'B': 'Brother', 'S': 'Sister', 
#                         'C': 'Child', 'G': 'Grandfather', 'GM': 'Grandmother', 
#                         'U': 'Uncle', 'A': 'Aunt'
#                     }
#                     relationship_code = fh.get('relationship', '')
#                     relationship_name = relationship_mapping.get(relationship_code, relationship_code)
                    
#                     consolidated_history['FamilyHistory'].append({
#                         'family_history_id': fh.get('familyHistoryId', ''),
#                         'disease_name': disease_name,
#                         'diagnosis_description': diagnosis_desc,
#                         'relationship': relationship_name,
#                         'relationship_code': relationship_code,
#                         'deceased': fh.get('isDeceased', ''),
#                         'age': fh.get('age', ''),
#                         'age_at_onset': fh.get('ageAtOnset', ''),
#                         'description': fh.get('description', ''),
#                         'name': fh.get('name', ''),
#                         'modified_date': fh.get('modifiedDate', '')
#                     })
                
#                 info_logger.info(f'{uid} | HISTORY API: Retrieved {len(consolidated_history["FamilyHistory"])} family history entries')
#             else:
#                 error_logger.warning(f'{uid} | HISTORY API: Family history API returned error: {family_data.get("message", "Unknown error")}')
                
#         except requests.RequestException as e:
#             error_logger.error(f'{uid} | HISTORY API: Family history request failed: {str(e)}')
#             # Continue with other requests even if this one fails
        
#         # 2. GET SOCIAL HISTORY
#         try:
#             info_logger.info(f'{uid} | HISTORY API: Fetching Social History...')
            
#             response = requests.get(
#                 HistoryService.SOCIAL_HISTORY_API_URL,
#                 headers=headers,
#                 params=params,
#                 timeout=10
#             )
#             response.raise_for_status()
#             social_data = response.json()
            
#             if social_data and social_data.get('statusCode') == 200:
#                 social_history_data = social_data.get('data', {}).get('socialHistory', {})
                
#                 consolidated_history['SocialHistory'] = {
#                     'socialhxId': social_history_data.get('socialhxId', ''),
#                     'education': social_history_data.get('education', ''),
#                     'industryCode': social_history_data.get('industryCode', ''),
#                     'tobaccoStatusIdPk': social_history_data.get('tobaccoStatusIdPk', ''),
#                     'industryStartDate': social_history_data.get('industryStartDate', ''),
#                     'industryEndDate': social_history_data.get('industryEndDate', ''),
#                     'tobaccoStatus': social_history_data.get('tobaccoStatus', ''),
#                     'alcoholDay': social_history_data.get('alcoholDay', ''),
#                     'tobaccoStartDate': social_history_data.get('tobaccoStartDate', ''),
#                     'tobaccoEndDate': social_history_data.get('tobaccoEndDate', ''),
#                     'riskAssessmentStructId': social_history_data.get('riskAssessmentStructId', ''),
#                     'exercise': social_history_data.get('exercise', ''),
#                     'seatbelts': social_history_data.get('seatbelts', ''),
#                     'exposure': social_history_data.get('exposure', ''),
#                     'suicideRisk': social_history_data.get('suicideRisk', ''),
#                     'feelsSafe': social_history_data.get('feelsSafe', ''),
#                     'drugUse': social_history_data.get('drugUse', ''),
#                     'notes': social_history_data.get('notes', ''),
#                     'caffineUsage': social_history_data.get('caffineUsage', ''),
#                     'caffineUsageFrequency': social_history_data.get('caffineUsageFrequency', ''),
#                     'drugUseDetails': social_history_data.get('drugUseDetails', ''),
#                     'isReconcile': social_history_data.get('isReconcile', '')
#                 }
                
#                 info_logger.info(f'{uid} | HISTORY API: Retrieved social history data')
#             else:
#                 error_logger.warning(f'{uid} | HISTORY API: Social history API returned error: {social_data.get("message", "Unknown error")}')
                
#         except requests.RequestException as e:
#             error_logger.error(f'{uid} | HISTORY API: Social history request failed: {str(e)}')
#             # Continue with other requests even if this one fails
        
#         # 3. GET PAST SURGICAL HISTORY
#         try:
#             info_logger.info(f'{uid} | HISTORY API: Fetching Past Surgical History...')
            
#             response = requests.get(
#                 HistoryService.PAST_SURGICAL_HISTORY_API_URL,
#                 headers=headers,
#                 params=params,
#                 timeout=10
#             )
#             response.raise_for_status()
#             surgical_data = response.json()
            
#             if surgical_data and surgical_data.get('statusCode') == 200:
#                 surgical_history_list = surgical_data.get('data', [])
                
#                 for sh in surgical_history_list:
#                     consolidated_history['PastSurgicalHistory'].append({
#                         'past_surgical_history_structure_id': sh.get('pasT_SURGICAL_HISTORY_STRUCTURE_ID', ''),
#                         'surgery_date': sh.get('surgerY_DATE', ''),
#                         'surgery_name': sh.get('surgerY_NAME', ''),
#                         'surgery_place': sh.get('surgerY_PLACE', ''),
#                         'post_surgery_complications': sh.get('posT_SURGERY_COMPLICATIONS', ''),
#                         'created_by': sh.get('createD_BY', ''),
#                         'created_date': sh.get('createD_DATE', ''),
#                         'modified_by': sh.get('modifieD_BY', ''),
#                         'modified_date': sh.get('modifieD_DATE', '')
#                     })
                
#                 info_logger.info(f'{uid} | HISTORY API: Retrieved {len(consolidated_history["PastSurgicalHistory"])} past surgical history entries')
#             else:
#                 error_logger.warning(f'{uid} | HISTORY API: Past surgical history API returned error: {surgical_data.get("message", "Unknown error")}')
                
#         except requests.RequestException as e:
#             error_logger.error(f'{uid} | HISTORY API: Past surgical history request failed: {str(e)}')
#             # Continue with other requests even if this one fails
        
#         # 4. GET PAST HOSPITALIZATION
#         try:
#             info_logger.info(f'{uid} | HISTORY API: Fetching Past Hospitalization...')
            
#             response = requests.get(
#                 HistoryService.PAST_HOSPITALIZATION_API_URL,
#                 headers=headers,
#                 params=params,
#                 timeout=10
#             )
#             response.raise_for_status()
#             hospitalization_data = response.json()
            
#             if hospitalization_data and hospitalization_data.get('statusCode') == 200:
#                 hospitalization_list = hospitalization_data.get('data', [])
                
#                 for hosp in hospitalization_list:
#                     consolidated_history['PastHospitalization'].append({
#                         'past_hosp_structure_id': hosp.get('pasT_HOSP_STRUCTURE_ID', ''),
#                         'hosp_date': hosp.get('hosP_DATE', ''),
#                         'reason': hosp.get('reason', ''),
#                         'duration': hosp.get('duration', ''),
#                         'comments': hosp.get('comments', ''),
#                         'created_by': hosp.get('createD_BY', ''),
#                         'created_date': hosp.get('createD_DATE', ''),
#                         'modified_by': hosp.get('modifieD_BY', ''),
#                         'modified_date': hosp.get('modifieD_DATE', '')
#                     })
                
#                 info_logger.info(f'{uid} | HISTORY API: Retrieved {len(consolidated_history["PastHospitalization"])} past hospitalization entries')
#             else:
#                 error_logger.warning(f'{uid} | HISTORY API: Past hospitalization API returned error: {hospitalization_data.get("message", "Unknown error")}')
                
#         except requests.RequestException as e:
#             error_logger.error(f'{uid} | HISTORY API: Past hospitalization request failed: {str(e)}')
#             # Continue with other requests even if this one fails
        
#         # Log final summary
#         total_family = len(consolidated_history['FamilyHistory'])
#         has_social = bool(any(consolidated_history['SocialHistory'].values()))
#         total_surgical = len(consolidated_history['PastSurgicalHistory'])
#         total_hospitalization = len(consolidated_history['PastHospitalization'])
        
#         info_logger.info(
#             f'{uid} | HISTORY API: Consolidated history retrieval completed. '
#             f'Family History: {total_family} entries, '
#             f'Social History: {"Available" if has_social else "Empty"}, '
#             f'Past Surgical: {total_surgical} entries, '
#             f'Past Hospitalization: {total_hospitalization} entries'
#         )
        
#         return consolidated_history
    
# # Example usage
# try:
#     # Call with UID
#     history_data = HistoryService.get_history(
#         patient_account="1011163565413278", 
#         practice_code="1011163", 
#         uid="custom-uid-123"
#     )
    
#     # Or call without UID (will auto-generate)
#     history_data = HistoryService.get_history(
#         patient_account="1011163565413278", 
#         practice_code="1011163"
#     )
    
#     # Access the data
#     family_history = history_data['FamilyHistory']
#     social_history = history_data['SocialHistory'] 
#     surgical_history = history_data['PastSurgicalHistory']
#     hospitalization_history = history_data['PastHospitalization']
#     print("Family History:", family_history)
#     print("Social History:", social_history)
#     print("Surgical History:", surgical_history)
#     print("Hospitalization History:", hospitalization_history)
# except Exception as e:
#     print(f"API Error: {e}")
# except Exception as e:
#     print(f"Unexpected error: {str(e)}")