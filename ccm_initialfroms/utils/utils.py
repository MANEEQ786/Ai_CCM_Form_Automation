import logging
info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')


def clean_json_response(response: str, uid: str):
    import re
    import json
    try:
        # Extract the first JSON object or array
        json_regex = r'(\{.*\}|\[.*\])'
        matches = re.findall(json_regex, response, re.DOTALL)
        if not matches:
            raise ValueError("No valid JSON object found in the response.")
        cleaned_response = matches[0].strip()
        # Try to load directly
        return json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        error_logger.error('error', uid, f"JSONDecodeError: {e}")
        return None
    except ValueError as ve:
        error_logger.error('error', uid, f"ValueError: {ve}")
        return None
    except Exception as e:
        error_logger.error('error', uid, f"Unexpected error: {e}")
        return None