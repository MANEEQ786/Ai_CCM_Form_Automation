from dotenv import load_dotenv
import os, json
import pymssql
import pandas as pd
import logging,time
from config.config import *
from datetime import datetime, timedelta
from ccm_initialfroms.utils.custom_exception import ApplicationException

info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')

load_dotenv()

DB_HOST = os.getenv("WELLNESS_DB_HOST")
DB_USER = os.getenv("WELLNESS_DB_USER")
DB_NAME = os.getenv("WELLNESS_DB_NAME")
DB_PASSWORD = os.getenv("WELLNESS_DB_PWD")
WKEY = os.getenv("WKEY")
DB_PASSWORD = get_password(DB_PASSWORD,WKEY)


class DBConnection:    
    @staticmethod
    def live_db(db_name=None):
        if db_name:
            try:
                conn = pymssql.connect(
                    user = DB_USER,
                    password = DB_PASSWORD,
                    host = DB_HOST,
                    database = db_name,
                    autocommit = True,
                )
                cursor = conn.cursor()
                return conn, cursor
            except Exception as e:
                error_logger.error(str(e))
                raise ApplicationException()
        else:    
            try:
                conn = pymssql.connect(
                    user = DB_USER,
                    password = DB_PASSWORD,
                    host = DB_HOST,
                    database = DB_NAME,
                    autocommit = True,
                )
                cursor = conn.cursor()
                return conn, cursor
            except Exception as e:
                error_logger.error(str(e))
                raise ApplicationException()
    
    @staticmethod 
    def db_disconnect(conn, cursor):        
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except Exception as e:
            error_logger.error(str(e))
            raise ApplicationException()


class DumpToDB:
    @staticmethod
    def executeSP(param,conn,cursor):
        try:
            cursor.callproc('Web_GetMaxColumnID', (param,))
            result = cursor.fetchone()
            return result[0]
        except Exception as e:
            error_logger.error(str(e))
            raise ApplicationException()
            
    @staticmethod
    def init_form_settings(patient_account,gender,practice_code,patient_name):
        try:
            # import pdb
            # pdb.set_trace()
            conn, cursor = DBConnection.live_db()
            #### form settings
            PATIENT_FORM_ID=int(DumpToDB.executeSP('RPM_PATIENT_FORM_ID',conn,cursor))
            
            TITLE='CCM Initial Health Assessment Questionnaire'
            DESCRIPTION='The below information includes your health record for review. Please answer questions accordingly.'
            FORM_CREATION_TIME='00:10:00'
            PROVIDER_REVIEW_TIME='00:10:00'
            CREATED_BY='AI'
            NAME='AI Initial Form - '+str(patient_name)
            TYPE= 'Initial form'
            CREATED_DATE = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            insert_query = """
            INSERT INTO RPM_TBL_PATIENT_FORMS (PATIENT_FORM_ID, patient_account,TITLE, DESCRIPTION, FORM_CREATION_TIME, PROVIDER_REVIEW_TIME, CREATED_BY, NAME, TYPE,CREATED_DATE)
            VALUES (%d,%d, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (PATIENT_FORM_ID,patient_account, TITLE, DESCRIPTION, FORM_CREATION_TIME, PROVIDER_REVIEW_TIME, CREATED_BY, NAME, TYPE,CREATED_DATE))
            conn.commit()
            ####### gender
            FORM_GENDER_ID=int(DumpToDB.executeSP('RPM_PATIENT_FORM_GENDER_ID',conn,cursor))
            CREATED_BY='AI'
            GENDER=gender
            insert_query = """
            INSERT INTO RPM_TBL_PATIENT_FORM_GENDERS (FORM_GENDER_ID,PATIENT_FORM_ID, GENDER, CREATED_BY,CREATED_DATE)
            VALUES (%d, %d, %s, %s,%s)
            """
            cursor.execute(insert_query, (FORM_GENDER_ID, PATIENT_FORM_ID, GENDER,CREATED_BY,CREATED_DATE))
            conn.commit()
            ####### AGE
            FORM_AGE_ID=int(DumpToDB.executeSP('RPM_PATIENT_FORM_AGE_ID',conn,cursor))
            CREATED_BY='AI'
            MIN_AGE=65
            MIN_AGE_TYPE='YEAR'
            MAX_AGE=100
            MAX_AGE_TYPE='YEAR'
            insert_query = """
            INSERT INTO RPM_TBL_PATIENT_FORM_AGES (FORM_AGE_ID,PATIENT_FORM_ID, MIN_AGE,MIN_AGE_TYPE,MAX_AGE,MAX_AGE_TYPE,CREATED_BY,CREATED_DATE)
            VALUES (%d, %d, %d, %s,%d,%s,%s,%s)
            """
            cursor.execute(insert_query, (FORM_AGE_ID, PATIENT_FORM_ID, MIN_AGE, MIN_AGE_TYPE, MAX_AGE, MAX_AGE_TYPE, CREATED_BY,CREATED_DATE))
            conn.commit()
            ####### PRACTICE
            FORM_PRACTICE_ID=int(DumpToDB.executeSP('RPM_PATIENT_FORM_PRACTICE_ID',conn,cursor))
            CREATED_BY='AI'
            PRAC_CODE=practice_code
            insert_query = """
            INSERT INTO RPM_TBL_PATIENT_FORM_PRACTICES (FORM_PRACTICE_ID,PATIENT_FORM_ID,PRACTICE_CODE,CREATED_BY,CREATED_DATE)
            VALUES (%d, %d, %d, %s,%s)
            """
            cursor.execute(insert_query, (FORM_PRACTICE_ID, PATIENT_FORM_ID,PRAC_CODE, CREATED_BY,CREATED_DATE))
            conn.commit()
            return PATIENT_FORM_ID
        except Exception as e:
            error_logger.error(str(e))
            raise ApplicationException()
        finally:
            DBConnection.db_disconnect(conn,cursor)

    @staticmethod
    def insert_question(df,patient_account,gender,practice_code,uid,patient_name):
        if df.shape[0]>0:
            try:
                PATIENT_FORM_ID=DumpToDB.init_form_settings(patient_account,gender,practice_code,patient_name)
                df['PATIENT_FORM_ID']=PATIENT_FORM_ID
                df['FORM_BUILDER_ID']=None
                CREATED_DATE = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                df['CREATED_DATE']=CREATED_DATE
                # max_id=int(DumpToDB.get_max_id('RPM_PATIENT_FORM_BUILDER_ID',df.shape[0]))
                conn,cursor= DBConnection.live_db()
                for index, row in df.iterrows():
                    fbid = int(DumpToDB.executeSP('RPM_PATIENT_FORM_BUILDER_ID',conn,cursor))
                    df.at[index, 'FORM_BUILDER_ID'] = fbid
                    # max_id+=1
                try:
                    columns = df.columns.tolist()
                    placeholders = ', '.join(['%s'] * len(columns))
                    sql = f"INSERT INTO dbo.RPM_TBL_PATIENT_FORM_BUILDER ({', '.join(columns)}) VALUES ({placeholders})"
                    for index, row in df.iterrows():
                        cursor.execute(sql, tuple(row))
                    conn.commit()
                except Exception as e:
                    error_logger.error(str(e))
                    raise ApplicationException()
                finally:
                    DBConnection.db_disconnect(conn,cursor)
                    DumpToDB.ai_form_backup(df)
                return PATIENT_FORM_ID
            except Exception as e:
                error_logger.error(str(e))
                raise ApplicationException()

    @staticmethod
    def ai_form_backup(df):
        if df.shape[0]>0:
            try:
                conn,cursor= DBConnection.live_db(db_name='ai_db')
                try:
                    columns = df.columns.tolist()
                    placeholders = ', '.join(['%s'] * len(columns))
                    sql = f"INSERT INTO dbo.RPM_TBL_PATIENT_FORM_BUILDER ({', '.join(columns)}) VALUES ({placeholders})"
                    for index, row in df.iterrows():
                        cursor.execute(sql, tuple(row))
                    conn.commit()
                except Exception as e:
                    error_logger.error(str(e))
                    return False
                finally:
                    DBConnection.db_disconnect(conn,cursor)
                return True
            except Exception as e:
                error_logger.error(str(e))
                return False

    @staticmethod
    def parse_json(js,patient_account,gender,practice_code,uid,patient_name):
        df1=pd.DataFrame()
        if 'response' in js and len(js['response']) > 0:
            for idx,question in enumerate(js['response'],start=1):
                df=pd.DataFrame()
                df['CONTROL_TYPE']=[question['type']]
                df['TITLE']=[question['title']]
                df['SEQUENCE']=[idx]
                df['CREATED_BY']=['AI']
                df['SUPPORT_TEXT'] = [question.get('support_text', '')]
                first_keys = question.keys()
                key_list=list(first_keys)
                if 'options' in key_list:
                    seen=set()
                    col=1
                    for ix,i in enumerate(question['options'],start=1):
                        if ix>30:
                            break
                        i_upper=i.upper()
                        if i_upper not in seen:
                            seen.add(i_upper)
                            df['Value_'+str(col)]=['Option '+str(ix)]
                            col+=1
                            df['Value_'+str(col)]=[i]
                            col+=1
                df1 = pd.concat([df1, df], ignore_index=True)
                df1.fillna('',inplace=True)
            PATIENT_FORM_ID=DumpToDB.insert_question(df1,patient_account,gender,practice_code,uid,patient_name)
            return PATIENT_FORM_ID
        else:
            error_logger.error('Incorrect Json')
            raise ApplicationException()

    @staticmethod
    def get_max_id(col_name,counter):
        try:
            conn, cursor = DBConnection.live_db()
            sql_query = f"""
            BEGIN      
            SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;     
            DECLARE @counterValue BIGINT;      
            SET NOCOUNT ON;      
            BEGIN      
                UPDATE Maintenance_Counter      
                SET Col_Counter = Col_Counter + {counter},      
                    @counterValue = Col_Counter
                WHERE COL_NAME = '{col_name}';
            END      
            
            SELECT (CONVERT(VARCHAR, (SELECT office_id FROM Maintenance)) + '' + CONVERT(VARCHAR, @counterValue)) AS MaxID;      
            END
            """
            cursor.execute(sql_query)
            result = cursor.fetchone()
            max_id = result[0]
            DBConnection.db_disconnect(conn=conn,cursor=cursor)
            return max_id
        except Exception as e:
            error_logger.error(f'{uid} | {e}')
            raise ApplicationException()
    
    @staticmethod
    def check_form_status(patient_account, uid):
        try:
            query = f"""
            SELECT PATIENT_FORM_ID, ISNULL(REVIEWED, 0) AS REVIEWED, CREATED_DATE
            FROM RPM_TBL_PATIENT_FORMS with (nolock)
            WHERE PATIENT_ACCOUNT = {patient_account} and [TYPE]='initial form' and CREATED_BY = 'AI' and isnull(deleted,0)=0 order by created_date desc;
            """
            conn, cursor = DBConnection.live_db()  
            df = pd.read_sql(query, conn)

            if df.shape[0] == 0:
                info_logger.info(f"{uid} | No Form found for the given patient account {patient_account}")
                return True

            patient_form_id = df['PATIENT_FORM_ID'].iat[0]
            reviewed = df['REVIEWED'].iat[0]
            created_date = df['CREATED_DATE'].iat[0]

            created_date_dt = pd.to_datetime(created_date)
            one_month_ago = datetime.now() - timedelta(days=30)

            if reviewed == 1:
                if created_date_dt < one_month_ago:
                    info_logger.info(f"{uid} | Form status is REVIEWED and older than one month. Proceeding.")
                    return True
                else:
                    info_logger.info(f"{uid} | Form status is REVIEWED. You can proceed after one month of created date.")
                    return False
            if reviewed == 0: 
                delete_queries = f"""UPDATE RPM_TBL_PATIENT_FORMS SET DELETED=1 
                                    WHERE PATIENT_ACCOUNT={patient_account} AND ISNULL(REVIEWED,0)=0 and CREATED_BY='AI';"""
                cursor.execute(delete_queries)
                conn.commit()
                info_logger.info(f"{uid} | Deleted unreviewed forms created by AI for Patient account: {patient_account}")
                return True

        except Exception as e:
            error_logger.error(str(e))
            raise ApplicationException(e)
        finally:
            DBConnection.db_disconnect(conn, cursor)
            




