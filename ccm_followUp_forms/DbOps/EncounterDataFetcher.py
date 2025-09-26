import pymssql, json

from ccm_followUp_forms.utils.custom_exception import ApplicationException
from .DatabaseConnectionManager import DatabaseConnectionManager
import pandas as pd

class EncounterDataFetcher:
    def __init__(self):
        self.talk_db_manager = DatabaseConnectionManager(env="Talk")

    def get_encounter_med(self,patient_account,visit_Date,note_id,Is_Active=1):
        df=pd.DataFrame()
        try:
            with self.talk_db_manager as conn:
                with conn.cursor(as_dict=True) as cursor:
                    cursor.callproc('AF_PROC_GET_PATIENT_NOTE_MEDICATIONS', (patient_account,visit_Date,note_id, Is_Active))
                    if cursor.description:
                        columns = [column[0] for column in cursor.description]
                        rows = cursor.fetchall()
                        df = pd.DataFrame(rows, columns=columns)
            if df.shape[0]>0:
                df['MED_RESULT'] = df.apply(lambda row: f"{row['MEDICINE_TRADE']} , {row['SIG']}".lower().capitalize(), axis=1)
            return df
        except Exception as e:
           raise ApplicationException("Erro Getting Medications")    

    def get_encounter_data(self, uid, patient_account):

        query = f"""DROP TABLE IF EXISTS #TEMP;
                    SELECT 
                    TOP 1
                    ROW_NUMBER() OVER(ORDER BY PTN.VISIT_DATE DESC) AS ENCOUNTER_NO,
                    PTN.PATIENT_ACCOUNT,
                    PTN.NOTE_ID,CONVERT(DATE,PTN.VISIT_DATE) AS VISIT_DATE
                    ,PTN.CHECKOUT_NOTES,PTN.PATIENT_NOTE_RTF AS NOTE_HTML
                    --VITALS
                    ,CONCAT(VT.HEIGHT,' ft ',VT.INCHHEIGHT,' in') AS HEIGHT,VT.[WEIGHT],VT.BMI,
                    CONCAT(VT.BP_SYSTOLIC,'/',VT.BP_DIASTOLIC,'mmHG Position: ',VT.BP_MEASUREMENT_POSITION) AS BP
                    ,VT.HEART_RATE AS HR,vt.pain_score
                    ,concat(vt.oxygen_saturation,'%, Soure: ',vt.oxygen_source,', FlowRate: ',OXYGEN_FLOWRATE) as spo2
                    --CHEIF COMPLAINT
                    ,CC.CHEIFCOMPLAINT
                    ,cc.hpi
                    ,isnull(pt.Gender,'') as gender
					,convert(date,pt.Date_Of_Birth) as dob
                    ,isnull(pt.practice_code,0) as practice_code
                    ,case when pt.Patient_Account in(10092812297,10056510118,10056511087,100101100250,10092810874,10092810675,10092810970,10092810551,10056510628,10056510672,10092810469,10014349,10092810581,10056510336,10092811276,10056510493,10092810972,10056510379,100101101235,10056510087,10092910012,10053910125,10056510781,10092811472,10092810337)  then 'Spanish' when pt.patient_account=10092811217 then 'english' when isnull(pt.languages,'english') not like '%english%' and isnull(pt.languages,'english') not like '%spanish%'then 'english' else isnull(pt.languages,'english')  end as preferred_language
                    ,concat(pt.Last_Name,', ',pt.First_Name) as patient_name
                    into #temp
                    FROM MIS_DB.DBO.AF_TBL_PATIENT_NOTE  AS PTN with (nolock)
                    JOIN MIS_DB.DBO.PATIENT  AS PT with (nolock)
                    on ptn.PATIENT_ACCOUNT=pt.Patient_Account
                    LEFT JOIN MIS_DB.DBO.AF_TBL_PATIENT_VITALS AS VT with (nolock)
                    ON PTN.NOTE_ID=VT.ENCOUNTER_ID AND PTN.PATIENT_ACCOUNT=VT.PATIENT_ACCOUNT
                    AND ISNULL(VT.DELETED,0)=0
                    LEFT JOIN MIS_DB.DBO.PATIENT_CHEIFCOMPLAINTS AS CC with (nolock)
                    ON CC.PATIENT_ACCOUNT=PTN.PATIENT_ACCOUNT AND CC.CHART_ID=PTN.NOTE_ID AND ISNULL(CC.DELETED,0)=0
                    WHERE PTN.PATIENT_ACCOUNT= {patient_account}--100101101745
                    --and ptn.practice_code=(select top 1 practice_code from #temp)--100
                    AND ISNULL(PTN.DELETED,0)=0
                    ORDER BY PTN.VISIT_DATE DESC;

                    select *,concat('Height: ',HEIGHT,', Weight: ',[weight],', HR: ',hr,', BP: ',BP,', Pain Score: ',pain_score,', SPO2: ',spo2)as vitals from #temp;
                    -----------------care team---------------------------
                    SELECT
                    CONCAT(B.LASTNAME,' ',B.FIRSTNAME) AS DOC_NAME,
                    B.RELATION,
                    B.PHONE,B.EMAIL                  
                    FROM MIS_DB.DBO.WEBEHR_TBL_PATIENTCARETEAM B                        
                    WHERE PATIENT_ACCOUNT={patient_account} AND PRACTICE_CODE=(select top 1 practice_code from #temp)--100           
                    AND isnull(deleted,0)=0;
                    ------------------ICDS----------------------
                    select aa.*, case  when aa.DIAGNOSED_DAYS>90 then 1 else 0 END AS CHRONIC from
					(SELECT A.NOTE_ID,A.ENCOUNTER_NO,B.ICD10_CODE,B.ICD10_DESCRIPTION,B.ICD9_CODE,B.ICD9_DESCRIPTION,CONCAT(ICD10_CODE,' : ',ICD10_DESCRIPTION) AS ICDS,
					DATEDIFF(DAY,B.PROBLEM_DATE,GETDATE()) AS DIAGNOSED_DAYS
                    FROM #TEMP AS A
                    JOIN MIS_DB.DBO.AF_TBL_PATIENT_PROBLEMS AS B with (nolock)
                    ON A.PATIENT_ACCOUNT=B.PATIENT_ACCOUNT AND A.ENCOUNTER_NO=1
                    WHERE  CONVERT(DATE,B.PROBLEM_DATE)<=CONVERT(DATE,A.VISIT_DATE)
                    AND B.DIGNOSE_STATUS='ACTIVE' AND ISNULL(B.DELETED,0)=0
                    AND B.PRACTICE_CODE=(select top 1 practice_code from #temp) )
					as aa;

                    --------------------POC-----------
                    SELECT A.NOTE_ID,A.ENCOUNTER_NO,B.PATIENT_PLANOFCARE_COMMENTS_TEXT 
                    FROM #TEMP AS A
                    JOIN MIS_DB.DBO.AF_TBL_PATIENT_POC_NOTES AS B with (nolock)
                    ON A.PATIENT_ACCOUNT=B.PATIENT_ACCOUNT
                    AND A.NOTE_ID=B.NOTE_ID
                    AND B.DELETED=0;

                    ---------------------CPTS------------------------------
                    SELECT A.PATIENT_ACCOUNT,A.NOTE_ID,A.ENCOUNTER_NO,A.VISIT_DATE,
                    CONCAT(CPT.PROCEDURE_CODE,' - ',PR.PROC_DESCRIPTION) AS CPTS 
                    FROM #TEMP AS A
                    JOIN MIS_DB.DBO.AF_TBL_PATIENT_PROCEDURES AS CPT with (nolock)
                    ON CPT.PATIENT_ACCOUNT=A.PATIENT_ACCOUNT AND CPT.ENCOUNTER_ID=A.NOTE_ID
                    JOIN MIS_DB.DBO.PROCEDURES AS PR with (nolock)
                    ON CPT.PROCEDURE_CODE=PR.PROC_CODE
                    WHERE ISNULL(CPT.DELETED,0)=0
                    AND CPT.PRACTICE_CODE=(select top 1 practice_code from #temp)--100;

                    -----------------IMMUNIZATION-------------------
                    SELECT  
                    T.PATIENT_ACCOUNT,T.NOTE_ID,T.ENCOUNTER_NO,T.VISIT_DATE,
                    B.SHORT_DESCRIPTION,A.IMMUNIZATION_TYPE,A.REFUSAL_REASON,A.ADMINISTERED_DATE,
                    case 
						when a.IMMUNIZATION_TYPE in('Refusal') then concat(b.SHORT_DESCRIPTION,', Refusal Reason: ',a.REFUSAL_REASON,', ',a.ADMINISTERED_DATE)
						else concat(b.SHORT_DESCRIPTION,', ',a.IMMUNIZATION_TYPE,', ',a.ADMINISTERED_DATE)
					end as immunization
                    FROM #TEMP AS T
                    JOIN MIS_DB.DBO.AF_TBL_PATIENT_IMMUNIZATION AS A with (nolock)
                    ON T.PATIENT_ACCOUNT=A.PATIENT_ACCOUNT AND T.ENCOUNTER_NO=1
                    JOIN MIS_DB.DBO.VACCINES AS B with (nolock)
                    ON A.IMMUNIZATION_ID=B.VACCINE_ID
                    WHERE CONVERT(DATE,A.CREATED_DATE)<=CONVERT(DATE,T.VISIT_DATE)AND ISNULL(A.DELETED,0)=0
                    UNION ALL
                    SELECT  
                    T.PATIENT_ACCOUNT,T.NOTE_ID,T.ENCOUNTER_NO,T.VISIT_DATE,
                    B.SHORT_DESCRIPTION,A.IMMUNIZATION_TYPE,A.REFUSAL_REASON,A.ADMINISTERED_DATE,
                    case 
						when a.IMMUNIZATION_TYPE in('Refusal') then concat(b.SHORT_DESCRIPTION,', Refusal Reason: ',a.REFUSAL_REASON,', ',a.ADMINISTERED_DATE)
						else concat(b.SHORT_DESCRIPTION,', ',a.IMMUNIZATION_TYPE,', ',a.ADMINISTERED_DATE)
					end as immunization
                    FROM #TEMP AS T
                    JOIN MIS_DB.DBO.AF_TBL_PATIENT_IMMUNIZATION AS A with (nolock)
                    ON T.PATIENT_ACCOUNT=A.PATIENT_ACCOUNT AND T.ENCOUNTER_NO=2
                    JOIN MIS_DB.DBO.VACCINES AS B with (nolock)
                    ON A.IMMUNIZATION_ID=B.VACCINE_ID
                    WHERE CONVERT(DATE,A.CREATED_DATE)<=CONVERT(DATE,T.VISIT_DATE)AND ISNULL(A.DELETED,0)=0
                    UNION ALL
                    SELECT  
                    T.PATIENT_ACCOUNT,T.NOTE_ID,T.ENCOUNTER_NO,T.VISIT_DATE,
                    B.SHORT_DESCRIPTION,A.IMMUNIZATION_TYPE,A.REFUSAL_REASON,A.ADMINISTERED_DATE,
                    case 
						when a.IMMUNIZATION_TYPE in('Refusal') then concat(b.SHORT_DESCRIPTION,', Refusal Reason: ',a.REFUSAL_REASON,', ',a.ADMINISTERED_DATE)
						else concat(b.SHORT_DESCRIPTION,', ',a.IMMUNIZATION_TYPE,', ',a.ADMINISTERED_DATE)
					end as immunization
                    FROM #TEMP AS T
                    JOIN MIS_DB.DBO.AF_TBL_PATIENT_IMMUNIZATION AS A with (nolock)
                    ON T.PATIENT_ACCOUNT=A.PATIENT_ACCOUNT AND T.ENCOUNTER_NO=3
                    JOIN MIS_DB.DBO.VACCINES AS B with (nolock)
                    ON A.IMMUNIZATION_ID=B.VACCINE_ID
                    WHERE CONVERT(DATE,A.CREATED_DATE)<=CONVERT(DATE,T.VISIT_DATE)AND ISNULL(A.DELETED,0)=0;
                    ------------------SCREENING-----------------------
                    SELECT  concat(b.screening,', ',convert(date,last_screening)) as screening 
                    FROM DBO.RPM_TBL_PATIENT_PREVENTIVE_CARE AS B with (nolock)
                    where b.practice_code=(select top 1 practice_code from #temp)--100
                    and b.PATIENT_ID={patient_account}--10054410254
                    and isnull(b.deleted,0)=0
                    and [status]='Completed';
                    
                    -------------------allergies--------------------
                    -------------------et 1 allergy-----------------
                    DECLARE @TBL11 TABLE(note_id BIGINT);
                    INSERT INTO @TBL11         
                    SELECT distinct pn.note_id         
                    FROM MIS_DB.DBO.af_tbl_patient_note PN WITH(nolock)
                    join #temp as t on pn.patient_account=t.patient_account and t.encounter_no=1
                    JOIN MIS_DB.DBO.af_tbl_patient_allergy PP WITH(nolock) ON PP.chart_id = PN.note_id         
                    WHERE PN.deleted = 0         
                    AND PN.note_id <> t.note_id         
                    AND convert(date,pn.visit_Date) <= convert(date,pn.visit_Date);
                    -------------					  
                    DROP TABLE if exists #g1;         
                    SELECT
                    PA.chart_id,pa.patient_account,Isnull(PA.allergy_description, '') ALLERGY_DESCRIPTION,                 
                    allergy_status,SAS.snomed_allergy_severity,resolved_date,resolved,         
                    Max(AR.allergy_reaction_id) AS ALLERGY_REACTION_ID,t.VISIT_DATE,t.encounter_no
                    INTO #g1        
                    FROM MIS_DB.DBO.af_tbl_patient_allergy PA WITH(nolock)
                    join #temp as t on pa.patient_account=t.patient_account and t.ENCOUNTER_NO=1
                    LEFT JOIN MIS_DB.DBO.snomed_allergy_severity SAS WITH(nolock)         
                    ON PA.allergy_severity_id =SAS.snomed_allergy_severity_id         
                    LEFT JOIN MIS_DB.DBO.af_tbl_patient_allergy_reaction AR WITH(nolock)         
                    ON AR.patient_allergy_id = PA.patient_allergy_id         
                    AND AR.deleted = 0
                    WHERE   (
                            chart_id = t.note_id         
                            OR chart_id IN (SELECT note_id FROM  @TBL11)         
                            OR Isnull(CONVERT(DATE, PA.onset_date),         
                            CONVERT(DATE, PA.created_date))<= Cast(t.VISIT_DATE AS DATE) 
                            )         
                            AND isnull(pa.deleted,0)=0        
                    GROUP  BY PA.patient_allergy_id,         
                    PA.chart_id,pa.patient_account,code,pa.practice_code,         
                    PA.allergy_description,Isnull(allergy_concept_id, ''),allergy_status,resolved_date,resolved,         
                    SAS.snomed_allergy_severity,         
                    onset_date,isreconciled,t.visit_Date,t.encounter_no;         
                    ----------------------
                    drop table if exists #et1_ag
                    SELECT A.*,S.snomedct_description AS REACTION_DESCRIPTION         
                    INTO #et1_ag FROM  #g1 A
                    LEFT JOIN MIS_DB.DBO.snomed_adverse_reactions S ON S.snomedct_code = A.allergy_reaction_id AND Isnull(S.deleted, 0) <> 1;
                    ------------------------------------
                    SELECT chart_id,patient_account,allergy_description,snomed_allergy_severity,reaction_description,encounter_no,
                    concat(allergy_description,', ',snomed_allergy_severity,', ',reaction_description) as allergy_result    
                    FROM #et1_ag WHERE  allergy_status = 'ACTIVE';
                    ------------------ Previous Form Goals ------------------------------
                    DROP TABLE IF EXISTS #lastgoal1;
                    SELECT  TOP 1 a.* into #lastgoal1 FROM RPM_TBL_PATIENT_FORM_SENT as a WITH(NOLOCK,NOWAIT)
                    join RPM_TBL_PATIENT_V1 as b WITH(NOLOCK,NOWAIT)
                    on a.PATIENT_ID=b.PATIENT_ID and b.MRN='{patient_account}'
                    WHERE ISNULL(a.DELETED,0)=0 AND FORM_SENT_STATUS='SENT'
                    ORDER BY SENT_DATE DESC;
                                        
                    drop table if exists #lastgoal2;
                    SELECT B.TITLE AS LAST_FORM_GOALS 
                    into #lastgoal2 FROM #lastgoal1 AS A
                    JOIN RPM_TBL_PATIENT_FORM_BUILDER AS B WITH(NOLOCK,NOWAIT)
                    ON A.PATIENT_FORM_ID=B.PATIENT_FORM_ID AND ISNULL(B.DELETED,0)=0
                    AND B.CONTROL_TYPE='TEXT BOX';

                    select LAST_FORM_GOALS from #lastgoal2 
                    where 
                    LAST_FORM_GOALS LIKE '%Metas del mes actual%' OR
                    LAST_FORM_GOALS LIKE '%Metas e intervenciones del mes actual%' OR
                    LAST_FORM_GOALS LIKE '%Metas e intervenciones para el mes actual%' OR
                    LAST_FORM_GOALS LIKE '%Goals Set for Current Month%' OR
                    LAST_FORM_GOALS LIKE '%Current month goals%' OR
                    LAST_FORM_GOALS LIKE '%Current month goals and interventions%';
                """
        
        try:
            with self.talk_db_manager as conn:
                with conn.cursor(as_dict=True) as cursor:
                    cursor.execute(query)
                    data_frames = []
                    df_count = 1

                    while True:
                        rows = cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description]

                        if rows:
                            df = pd.DataFrame(rows, columns=columns)
                        else:
                            df = pd.DataFrame(columns=columns)
                        
                        data_frames.append(df) 
                        df_count += 1
                        if not cursor.nextset():
                            break
                    
                    return data_frames

        except pymssql.DatabaseError as e:
            raise ApplicationException()

        except Exception as e:
            raise ApplicationException("Error Processing Encounter Data")
