from ccm_followUp_forms.utils.custom_exception import ApplicationException
from .DatabaseConnectionManager import DatabaseConnectionManager
from .FormDataFetcher import FormDataFetcher
from .EncounterDataFetcher import EncounterDataFetcher
from .process_encounter import get_encounters_details


class DataProcessor:
    @staticmethod
    def process_encounters(uid, patient_account):
        try:
            form_data_fetcher = FormDataFetcher()
            encounter_data_fetcher = EncounterDataFetcher()
            form_data = form_data_fetcher.get_form_data(uid, patient_account)
            appointment_date = form_data_fetcher.get_appointment_date(patient_account)
            last_appointment = form_data_fetcher.get_last_appointment(patient_account)
            encounter_data = encounter_data_fetcher.get_encounter_data(uid, patient_account)
            if len(encounter_data)>0:
                if encounter_data[0].shape[0]>0:
                    encounters_sorted = encounter_data[0].sort_values(by='ENCOUNTER_NO', ascending=True)
                    for index,row in encounters_sorted.iterrows():
                        med=encounter_data_fetcher.get_encounter_med(patient_account,str(row['VISIT_DATE']),row['NOTE_ID'])
                        encounter_data.append(med)
            encounter, encounter_html = get_encounters_details(encounter_data,uid)
            return form_data, encounter, appointment_date,last_appointment
        except Exception as e:
            raise ApplicationException(str(e))
