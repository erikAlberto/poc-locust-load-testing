from locust import task, between
from locust.contrib.fasthttp import FastHttpUser
from requests import Response
from utils.db_postgresql_connection import PostgreSqlDatabase
from utils.csv_reader import CsvReader
from locust.exception import StopUser
import logging

class OnboardingWallet(FastHttpUser):
    wait_time = between(1, 5)

    phone_number_data = ""
    imei_data = ""
    document_number_data = ""
    date_of_birth_data = ""
    email_data = ""
    pin = ""   

    def on_start(self):
        print ('Step 1: Load Test Starts ...')
    
    @task
    def onboarding_flow(self):

        data_test = CsvReader()
        data_test.read_csv_file()
        print("LA TUPLA",tuple(data_test.read_csv_file()))
        for row in tuple(data_test.read_csv_file()):
            self.phone_number_data = row.get("phone_number")
            self.imei_data = row.get("imei")

            self.document_number_data = row.get("document_number")
            self.document_city_data = row.get("document_city")
            self.date_of_birth_data = row.get("date_of_birth")
            self.email_data = row.get("email")
            self.pin = row.get("pin")
            
            # OB-1 - Phone validator  

            body_phone = {
                "phone_number":self.phone_number_data,
                "imei": self.imei_data
            }
            
            # response = self.client.post("/onboarding/phone-validator", data=body_phone, name="phone validator")
            # opening_request_id = response.json().get("opening_request_id")

            with self.client.post("/onboarding/phone-validator", data=body_phone, name="phone validator", catch_response=True) as response:
                try:
                    if response.status_code == 200:
                        response.success()
                        opening_request_id = response.json().get("opening_request_id")
                        
                    else :
                        logging.error('Status code from Phone validar endpoint{}'.format(response.status_code))
                        response.failure(response.json())
                except AttributeError as error:
                    response.failure('catch the error {}, {}'.format(error, response.json()))


            '''
                Query to DB
                getting the OTP

            '''
            db = PostgreSqlDatabase()
            db.connection_database()
            pin = db.select_from_database("SELECT pin FROM opening_requests WHERE id={}".format(opening_request_id))
            print("EL OTP", pin[0])
            db.close_connection()
            
            # OB-2 - Pin validator  

            body_pin = {
                "opening_request_id": opening_request_id,
                "pin": pin[0],
                "imei": self.imei_data
            }

            #self.client.post("/onboarding/pin-validator", data=body_pin, name="pin validator")

            with self.client.post("/onboarding/pin-validator", data=body_pin, name="pin validator", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(response.json())

            # OB-3 - Open Account Request  

            body_signup = {
                "document_number": self.document_number_data,
                "document_ext": "",
                "document_city": self.document_city_data,
                "phone_number": int(self.phone_number_data),
                "date_of_birth": self.date_of_birth_data,
                "email": self.email_data,
                "accept_tc":"true"
            }

            print("El bodyyyy", body_signup)

            with self.client.post("/onboarding/signup", data=body_signup, name="open account request", catch_response=True) as response:
                try:
                    if response.status_code == 200:
                        response.success()
                    else :
                        logging.error('Status Code to signup endpoint: {}'.format(response.status_code))
                        response.failure(response.json())
                except AttributeError as error:
                    response.failure('catch the error {}, {}'.format(error, response.json()))
               # raise StopUser()

            #OB-4  - Validation foto

            body_validation_foto = {
                "url":"https://4.bp.blogspot.com/-17l0DmOpH3k/V-5_ZG8pXVI/AAAAAAAEQhQ/BEGlb723dl0wOLv9zkeVbiTQ79zkpwQugCLcB/s1600/fotos-personas-vivas-y-famosas_06.jpeg"
            }

            #self.client.post("/onboarding/photo-validator", data=body_validation_foto, name="validation foto")

            with self.client.post("/onboarding/photo-validator", data=body_validation_foto, name="validation foto", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(response.json())

            # OB-5 - Validation image url
            
            body_validation = {
                "urls":["https://4.bp.blogspot.com/-17l0DmOpH3k/V-5_ZG8pXVI/AAAAAAAEQhQ/BEGlb723dl0wOLv9zkeVbiTQ79zkpwQugCLcB/s1600/fotos-personas-vivas-y-famosas_06.jpeg"]
            }

            #self.client.post("/onboarding/%d/realtime-life-proofs"%(opening_request_id), json=body_validation, name="validation")

            with self.client.post("/onboarding/%d/realtime-life-proofs"%(opening_request_id), json=body_validation, name="validation", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(response.json())

            # OB-6 - Create User 

            body_create_user = {
                "opening_requests_id": opening_request_id,
                "pin": self.pin,
                "imei": "14daff629e5969a5",
                "os_info": "ANDROID",
                "type_code": 1
            }

            #self.client.post("/onboarding/finish-signup", data=body_create_user, name="create user")

            with self.client.post("/onboarding/finish-signup", data=body_create_user, name="create user", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    logging.error('El status code: {}'.format(response.status_code))
                    response.failure(response.json())
        
        raise StopUser()

    def on_stop(self):
        print ('Step 2: Load Test Ends ...')
