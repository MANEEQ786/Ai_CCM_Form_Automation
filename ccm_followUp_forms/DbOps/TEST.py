from FormDataFetcher import FormDataFetcher
from EncounterDataFetcher import EncounterDataFetcher
from process_encounter import get_encounters_details
import pandas as pd
import json

form_data_fetcher = FormDataFetcher()
encounter_data_fetcher = EncounterDataFetcher()

uid = "user_123"
patient_account = '101112154910629'

try:
    result = form_data_fetcher.get_form_data(uid, patient_account)
    encounter_data = encounter_data_fetcher.get_encounter_data(uid, patient_account)
    print(len(encounter_data))
    print(type(encounter_data[0]))
    
        # Check the number of objects in the list
    print(f"Number of objects: {len(encounter_data)}")

    # Create a single Excel file with multiple sheets
    excel_file_name = "encounter_data.xlsx"

    try:
        with pd.ExcelWriter(excel_file_name, engine='openpyxl') as writer:
            for idx, obj in enumerate(encounter_data):
                # Convert each object to a DataFrame
                df = pd.DataFrame(obj)
                
                # Save each DataFrame to a separate sheet
                sheet_name = f"Sheet{idx + 1}"
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"Data successfully saved to '{excel_file_name}' with {len(encounter_data)} sheets.")
    except Exception as e:
        print(f"Error occurred: {e}")

    encounter, encounter_html = get_encounters_details(encounter_data)

    print("Form Data: \n",result)

    print("Encounter Data: \n",json.dumps( encounter,indent=4))
except Exception as e:
    print(f"Error fetching form data: {e}")