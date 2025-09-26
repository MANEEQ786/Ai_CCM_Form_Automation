import pymssql, datetime

from ccm_followUp_forms.utils.custom_exception import ApplicationException
from .DatabaseConnectionManager import DatabaseConnectionManager  

class FormDataFetcher:
    def __init__(self):
        self.wellness_db_manager = DatabaseConnectionManager(env="Talk")

    def get_form_data(self, uid, patient_account):

        query = f"""    

                    DECLARE @PATIENT_ACCOUNT VARCHAR(50) = 	{patient_account};
                    ------LAST FORM SENT TO PATIENT---------
                    DROP TABLE IF EXISTS #TEMP;
                    SELECT TOP 1 B.MRN, A.*
                    INTO #TEMP
                    FROM RPM_TBL_PATIENT_FORM_SENT AS A
                    JOIN RPM_TBL_PATIENT_V1 AS B
                    ON A.PATIENT_ID = B.PATIENT_ID
                    join RPM_TBL_PATIENT_FORM_SENT_FILLED as f on a.FORM_SENT_ID=f.FORM_SENT_ID
                    WHERE B.MRN = @PATIENT_ACCOUNT
                    AND ISNULL(A.DELETED, 0) = 0-- and A.FORM_STATUS = 'reviewed'
                    ORDER BY A.SENT_DATE DESC; 
                    -----------------------------
                    DROP TABLE IF EXISTS #TEMP2;
                    SELECT
                        FS.MRN AS PATIENT_ACCOUNT,
                        PF.FORM_BUILDER_ID,
                        FB.CONTROL_TYPE AS QUESTION_TYPE,
                        FB.TITLE AS QUESTION,
                        CASE
                            WHEN FB.CONTROL_TYPE in ('Multiple Choice','Single Choice') THEN (
                                RTRIM(
                                    CASE WHEN ISNULL(PF.VALUE_1, '') != ''  THEN ISNULL(FB.VALUE_2 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_2, '') != ''  THEN ISNULL(FB.VALUE_4 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_3, '') != ''  THEN ISNULL(FB.VALUE_6 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_4, '') != ''  THEN ISNULL(FB.VALUE_8 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_5, '') != ''  THEN ISNULL(FB.VALUE_10 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_6, '') != ''  THEN ISNULL(FB.VALUE_12 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_7, '') != ''  THEN ISNULL(FB.VALUE_14 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_8, '') != ''  THEN ISNULL(FB.VALUE_16 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_9, '') != ''  THEN ISNULL(FB.VALUE_19 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_10, '') != '' THEN ISNULL(FB.VALUE_20 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_11, '') != '' THEN ISNULL(FB.VALUE_22 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_12, '') != '' THEN ISNULL(FB.VALUE_24 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_13, '') != '' THEN ISNULL(FB.VALUE_26 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_14, '') != '' THEN ISNULL(FB.VALUE_28 + ', ','') ELSE '' END +
                                    CASE WHEN ISNULL(PF.VALUE_15, '') != '' THEN ISNULL(FB.VALUE_30 + ', ','') ELSE '' END
                                ) 
                            )
                            ELSE ISNULL(PF.VALUE_1, '') 
                        END AS Answer
                    into #temp2
                    FROM #TEMP FS WITH(NOLOCK)
                    JOIN RPM_TBL_PATIENT_FORM_SENT_FILLED PF WITH(NOLOCK)
                        ON FS.PATIENT_FORM_ID = PF.PATIENT_FORM_ID AND FS.FORM_SENT_ID = PF.FORM_SENT_ID
                        AND ISNULL(PF.DELETED, 0) = 0
                    JOIN RPM_TBL_PATIENT_FORM_BUILDER FB WITH(NOLOCK)
                        ON PF.PATIENT_FORM_ID = FB.PATIENT_FORM_ID AND PF.FORM_BUILDER_ID = FB.FORM_BUILDER_ID
                        AND ISNULL(FB.DELETED, 0) = 0
                    ORDER BY FB.SEQUENCE;
                    ----------------------------------------
                    SELECT QUESTION_TYPE,QUESTION,
                        CASE
                            WHEN ISNULL(LTRIM(RTRIM(ANSWER)),NULL) IN ('',NULL) THEN 'No Answer Provided'
                            WHEN RIGHT(ANSWER, 1) = ',' THEN LEFT(ANSWER, LEN(ANSWER) - 1)  
                            ELSE ANSWER  -- KEEP THE ORIGINAL ANSWER IF NO CONDITIONS MATCH
                        END AS ANSWER
                    FROM #TEMP2;
                        ------------------------------
                    """

        try:
            with self.wellness_db_manager as conn:
                with conn.cursor(as_dict=True) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()

            if not results:
                return []

            form_data = []
            return results

        except pymssql.DatabaseError as e:
            raise ApplicationException()

        except Exception as e:
            raise ApplicationException("Error getting Last month form data")
    
    def get_appointment_date(self, patient_account):
        query= f"""
                    SELECT  CONCAT(FORMAT(APT.APPOINTMENT_DATE_TIME, 'MMMM d, yyyy'), ' at ', APT.Time_From) AS  APPOINTMENT_DATE_TIME FROM APPOINTMENTS  AS APT WITH (NOLOCK)
                    LEFT JOIN APPOINTMENT_STATUS AS ST WITH (NOLOCK)
                    ON APT.APPOINTMENT_STATUS_ID=ST.APPOINTMENT_STATUS_ID
                    WHERE PATIENT_ACCOUNT={patient_account}
                    AND ISNULL(APT.DELETED,0)=0
                    AND ST.APPOINTMENT_STATUS_DESCRIPTION NOT IN('CANCELLED','COMPLETED')
                    AND APT.APPOINTMENT_DATE_TIME>GETDATE()
                    ORDER BY APT.APPOINTMENT_DATE_TIME ASC;
                    """
        try:   
            with self.wellness_db_manager as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    if result:
                        appointment_date = result[0][0]
                        # if isinstance(appointment_date, str):
                        #     appointment_date = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M:%S.%f")
                        return appointment_date#.strftime("%m-%d-%Y")   
                    else:
                        #print(f"No appointment Date found against patient: {patient_account}")
                        return "No appointment scheduled"
        except Exception as e :
            raise ApplicationException("Error getting future appointment")
        
    def get_last_appointment(self, patient_account):
            query2= f""" SELECT  top 1 CONCAT(FORMAT(APT.APPOINTMENT_DATE_TIME, 'MMMM d, yyyy'), ' at ', APT.Time_From) AS APPOINTMENT_DATE FROM APPOINTMENTS  AS APT WITH (NOLOCK)
                        LEFT JOIN APPOINTMENT_STATUS AS ST WITH (NOLOCK)
                        ON APT.APPOINTMENT_STATUS_ID=ST.APPOINTMENT_STATUS_ID
                        WHERE PATIENT_ACCOUNT={patient_account}
                        AND ISNULL(APT.DELETED,0)=0
                        AND ST.APPOINTMENT_STATUS_DESCRIPTION  IN('COMPLETED')
                        AND APT.APPOINTMENT_DATE_TIME<GETDATE()
                        ORDER BY APT.APPOINTMENT_DATE_TIME DESC """
            try:
                with self.wellness_db_manager as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query2)
                        result = cursor.fetchall()
                        if result:
                            last_appointment=result[0][0]
                            # if isinstance(last_appointment, str):
                            #     last_appointment = datetime.strptime(last_appointment, "%Y-%m-%d %H:%M:%S.%f")
                            return last_appointment#.strftime("%m-%d-%Y")    
                        else:
                            #print(f"No Appoitment Date found against patient: {patient_account}")
                            return "No appointment scheduled"
            except Exception as e :
                raise ApplicationException("Error getting last appointment")




