import time
from locust import SequentialTaskSet, TaskSet, task, between
from locust.contrib.fasthttp import FastHttpUser
from utils.db_postgresql_connection import PostgreSqlDatabase
from locust.exception import StopUser
from test_data.data import USERS
import logging

class OnboardingWallet(SequentialTaskSet):
    wait_time = between(1, 5)

    phone_number_data = "NOT_FOUND"
    imei_data = "NOT_FOUND"
    document_number_data = "NOT_FOUND"
    document_city_data = "NOT_FOUND"
    date_of_birth_data = "NOT_FOUND"
    email_data = "NOT_FOUND"
    pin = "NOT_FOUND"   

    def on_start(self):
        print ('Step 1: Load Test Starts ...')

        if len(USERS) > 0:
            self.phone_number_data, self.imei_data, self.document_number_data, self.document_city_data, self.date_of_birth_data, self.email_data, self.pin = USERS.pop()

    @task
    def onboarding_flow(self):
        # OB-1 - Phone validator  
        print("TESTINGGGGG", self.imei_data)
        body_phone = {
            "phone_number":self.phone_number_data,
            "imei": self.imei_data
        }

        with self.client.post("/onboarding/phone-validator", data=body_phone, name="phone validator", catch_response=True) as response:
            try:
                if response.status_code == 200:
                    response.success()
                    self.opening_request_id = response.json().get("opening_request_id")
                    
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
        pin = db.select_from_database("SELECT pin FROM opening_requests WHERE id={}".format(self.opening_request_id))
        print("EL OTP", pin[0])
        #db.close_connection()
        
        # OB-2 - Pin validator  

        body_pin = {
            "opening_request_id": self.opening_request_id,
            "pin": pin[0],
            "imei": self.imei_data
        }

        with self.client.post("/onboarding/pin-validator", data=body_pin, name="pin validator", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(response.json())
        
        time.sleep(50)
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

        #print("El bodyyyy", body_signup)

        with self.client.post("/onboarding/signup", data=body_signup, name="open account request", catch_response=True) as response:
            try:
                if response.status_code == 200:
                    response.success()
                else :
                    logging.error('Status Code to signup endpoint: {}'.format(response.status_code))
                    response.failure(response.json())
            except AttributeError as error:
                response.failure('catch the error {}, {}'.format(error, response.json()))

        # #OB-4  - Validation foto

        # body_validation_foto = {
        #     "url":"https://4.bp.blogspot.com/-17l0DmOpH3k/V-5_ZG8pXVI/AAAAAAAEQhQ/BEGlb723dl0wOLv9zkeVbiTQ79zkpwQugCLcB/s1600/fotos-personas-vivas-y-famosas_06.jpeg"
        # }

        # with self.client.post("/onboarding/photo-validator", data=body_validation_foto, name="validation foto", catch_response=True) as response:
        #     if response.status_code == 200:
        #         response.success()
        #     else:
        #         response.failure(response.json())

        # # OB-5 - Validation image url
        
        # body_validation = {
        #     "urls":["https://4.bp.blogspot.com/-17l0DmOpH3k/V-5_ZG8pXVI/AAAAAAAEQhQ/BEGlb723dl0wOLv9zkeVbiTQ79zkpwQugCLcB/s1600/fotos-personas-vivas-y-famosas_06.jpeg"]
        # }

        # with self.client.post("/onboarding/%d/realtime-life-proofs"%(self.opening_request_id), json=body_validation, name="validation", catch_response=True) as response:
        #     if response.status_code == 200:
        #         response.success()
        #     else:
        #         response.failure(response.json())

        # # OB-6 - Create User 

        # body_create_user = {
        #     "opening_requests_id": self.opening_request_id,
        #     "pin": self.pin,
        #     "imei": "14daff629e5969a5",
        #     "os_info": "ANDROID",
        #     "type_code": 1
        # }

        # with self.client.post("/onboarding/finish-signup", data=body_create_user, name="create user", catch_response=True) as response:
        #     if response.status_code == 200:
        #         response.success()
        #     else:
        #         logging.error('El status code: {}'.format(response.status_code))
        #         response.failure(response.json())

        raise StopUser()



    # @task
    # def pin_validator(self):
    #     '''
    #         Query to DB
    #         getting the OTP

    #     '''
    #     db = PostgreSqlDatabase()
    #     db.connection_database()
    #     pin = db.select_from_database("SELECT pin FROM opening_requests WHERE id={}".format(self.opening_request_id))
    #     print("EL OTP", pin[0])
    #     db.close_connection()
        
    #     # OB-2 - Pin validator  

    #     body_pin = {
    #         "opening_request_id": self.opening_request_id,
    #         "pin": pin[0],
    #         "imei": self.imei_data
    #     }

    #     with self.client.post("/onboarding/pin-validator", data=body_pin, name="pin validator", catch_response=True) as response:
    #         if response.status_code == 200:
    #             response.success()
    #         else:
    #             response.failure(response.json())

    # @task
    # def signup (self):
    #     # OB-3 - Open Account Request  

    #     body_signup = {
    #         "document_number": self.document_number_data,
    #         "document_ext": "",
    #         "document_city": self.document_city_data,
    #         "phone_number": int(self.phone_number_data),
    #         "date_of_birth": self.date_of_birth_data,
    #         "email": self.email_data,
    #         "accept_tc":"true"
    #     }

    #     print("El bodyyyy", body_signup)

    #     with self.client.post("/onboarding/signup", data=body_signup, name="open account request", catch_response=True) as response:
    #         try:
    #             if response.status_code == 200:
    #                 response.success()
    #             else :
    #                 logging.error('Status Code to signup endpoint: {}'.format(response.status_code))
    #                 response.failure(response.json())
    #         except AttributeError as error:
    #             response.failure('catch the error {}, {}'.format(error, response.json()))
    #         # raise StopUser()

    # @task
    # def photo_validator(self):
    #     #OB-4  - Validation foto

    #     body_validation_foto = {
    #         "url":"https://4.bp.blogspot.com/-17l0DmOpH3k/V-5_ZG8pXVI/AAAAAAAEQhQ/BEGlb723dl0wOLv9zkeVbiTQ79zkpwQugCLcB/s1600/fotos-personas-vivas-y-famosas_06.jpeg"
    #     }

    #     with self.client.post("/onboarding/photo-validator", data=body_validation_foto, name="validation foto", catch_response=True) as response:
    #         if response.status_code == 200:
    #             response.success()
    #         else:
    #             response.failure(response.json())

    # @task
    # def realtime_life_proofs(self):
    #      # OB-5 - Validation image url
            
    #     body_validation = {
    #         "urls":["https://4.bp.blogspot.com/-17l0DmOpH3k/V-5_ZG8pXVI/AAAAAAAEQhQ/BEGlb723dl0wOLv9zkeVbiTQ79zkpwQugCLcB/s1600/fotos-personas-vivas-y-famosas_06.jpeg"]
    #     }

    #     with self.client.post("/onboarding/%d/realtime-life-proofs"%(self.opening_request_id), json=body_validation, name="validation", catch_response=True) as response:
    #         if response.status_code == 200:
    #             response.success()
    #         else:
    #             response.failure(response.json())

    # @task
    # def finish_signup(self):
    #     # OB-6 - Create User 

    #     body_create_user = {
    #         "opening_requests_id": self.opening_request_id,
    #         "pin": self.pin,
    #         "imei": "14daff629e5969a5",
    #         "os_info": "ANDROID",
    #         "type_code": 1
    #     }

    #     with self.client.post("/onboarding/finish-signup", data=body_create_user, name="create user", catch_response=True) as response:
    #         if response.status_code == 200:
    #             response.success()
    #         else:
    #             logging.error('El status code: {}'.format(response.status_code))
    #             response.failure(response.json())

    def on_stop(self):
        print ('Step 2: Load Test Ends ...')

class User(FastHttpUser):
    tasks = [OnboardingWallet]