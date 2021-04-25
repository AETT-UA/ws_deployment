from locust import HttpUser, task, between, runners
import threading
import random
import string
import time
import os

user_credentials = []
user_index = 0
user_pool_size = int(os.getenv("num_users_register"))
num_curr_users = 0

# open file to record the user credentials
user_file = open("user_data.tsv")
for line in user_file:
    m_email, m_password = line.strip().split("\t")
    user_credentials.append((m_email, m_password))


class QuickstartUser(HttpUser):
    wait_time = between(0,1)

    # CONSTANTS

    # number of students per class
    NUM_STUDENTS = 50
    # number of students that will be registered by teacher
    NUM_STUDENTS_REGISTERED_BY_TEACHER = 10
    # the teacher has some minutes, beforee creating the attendance sheet
    MAX_LOGIN_TIME = 5 * 60
    # refresh time rate
    REFRESH_TIME_INTERVAL = 15
    # time during which the student will register himself
    REGISTRATION_STUDENT_TIME_LIMIT_SECONDS = 3*60
    # percentage of students to bee removed by the teacher
    DELETED_STUDENT_PERCENTAGE = 0.1
    # The teacher can consult an attendance sheet for some time
    ATTENDANCE_SHEET_CONSULTATION_DURATION_SECONDS = 2*60



    def on_start(self):        
        """ 
        on_start is called when a Locust start before any task is scheduled
        """
        m_email, m_password = self.get_user_credentials()

        # sleep a bit
        # authenticate the teacher 
        time.sleep(random.randint(0, self.MAX_LOGIN_TIME))
        self.log_user(m_email, m_password)

        # run class lifecycle
        self.lifecycle()


    def lifecycle(self): 
        """ 
        lifecycle of a class
        """   
        global num_curr_users
        global user_pool_size
        # the teacher creates an attendance sheet
        self.create_attendance_sheet()

        # the teacher starts refreshing the registered students for REGISTRATION_STUDENT_TIME_LIMIT_SECONDS seconds
        teacher_refreshing_attendances_table_thread = threading.Thread(target=self.refresh_students_table, args=(self.REGISTRATION_STUDENT_TIME_LIMIT_SECONDS,))
        teacher_refreshing_attendances_table_thread.start()

        # at the same time, the students start registering themselves on the attendance sheet
        student_registers_threads = []
        for _ in range(self.NUM_STUDENTS):
            tmp_thread = threading.Thread(target=self.student_executes_register, args=())
            tmp_thread.start()
            student_registers_threads.append(tmp_thread)
        
        # at the same time, some teachers will manually register some students.
        teacher_registers_threads = []
        if random.random() < 0.5:
            for _ in range(self.NUM_STUDENTS_REGISTERED_BY_TEACHER):
                tmp_thread = threading.Thread(target=self.teacher_manually_registers_a_student, args=())
                tmp_thread.start()
                teacher_registers_threads.append(tmp_thread)

        # students stop registering
        for tmp_thread in student_registers_threads:
            tmp_thread.join()

        # teacher stops registering students
        for tmp_thread in teacher_registers_threads:
            tmp_thread.join()
            
        # in the end, the teacher removes some students
        if random.random() < 0.1:
            self.teacher_manually_deletes_some_students()

        # the teacher closes the attendance sheet
        self.close_attendance_sheet()

        # teacher stops refreshing the attendance sheet
        teacher_refreshing_attendances_table_thread.join()

        # the teacher consults his attendances sheet
        self.consult_attendance_sheet()
        
        # the teacher starts refreshing the registered students for ATTENDANCE_SHEET_CONSULTATION_DURATION_SECONDS seconds
        teacher_refreshing_attendances_table_thread = threading.Thread(target=self.refresh_students_table, args=(self.ATTENDANCE_SHEET_CONSULTATION_DURATION_SECONDS,))
        teacher_refreshing_attendances_table_thread.start()
        #teacher stops refreshing the attendance sheet
        teacher_refreshing_attendances_table_thread.join()

        # End of cycle
        num_curr_users +=1    


    def get_user_credentials(self):
        global user_index
        global user_credentials   
        return user_credentials[user_index + 1 if user_index < len(user_credentials) - 2 else 0]


    def log_user(self, m_email, m_password):
        response = self.client.post("/login",
                         json = {"email": m_email,
                          "password": m_password})
        if response.status_code == 200:
            # save user auth token
            self.user_token = response.json()["token"]
            print("[Authenticate teacher] Sucess:", response.status_code == 200)
        

    def create_attendance_sheet(self):
        # get course units and choose one
        response = self.client.get("/course_units")
        self.cu = random.choice(response.json()["data"])
        # create attendance sheet for the course unit
        response = self.client.post("/attendance/sheet/new",
                         json = {"course_unit": self.cu["id"],
                          "is_active": True},
                          headers={"Authorization" : f"Token {self.user_token}"})
        if response.status_code == 200:                                              
            # save user auth token and the attendance sheet id
            response_json = response.json()
            self.user_token = response_json["token"]
            self.attendance_sheet_id = response_json["data"]["attendance_id"]
            # get the infos of the attendance sheet created
            response = self.client.get(f"/attendance/sheet/{self.attendance_sheet_id}",
                            headers={"Authorization" : f"Token {self.user_token}"})
            if response.status_code == 200:                          
                response_json = response.json()
                cu_name = response_json["data"]["course_unit_name"]
                teacher = response_json["data"]["creator_name"]
                timestamp = response_json["data"]["timestamp"]
                # save user auth token
                self.user_token = response_json["token"]
                # for debug
                print(f"[Created attendance sheet] Aula: {cu_name}, Professor: {teacher}, ID: {self.attendance_sheet_id}" )

        
    def refresh_students_table(self, durantion_sec):
        for _ in range(int(durantion_sec/self.REFRESH_TIME_INTERVAL)):
            # get students table
            response = self.client.get(f"/attendance/sheet/{self.attendance_sheet_id}/students",
                        headers={"Authorization" : f"Token {self.user_token}"})  
            if response.status_code == 200:   
                response_json = response.json()  
                #print(response.json()) 
                if len(response_json["data"])  > 0:
                    self.registered_students = response_json["data"]
                # save user auth token
                self.user_token = response_json["token"]
                print(f"[Alunos registados na folha de presença obtidos com sucesso] ID: {self.attendance_sheet_id}")
            # wait until next refresh
            time.sleep(self.REFRESH_TIME_INTERVAL) 


    def student_executes_register(self):
        # wait to register himself
        time.sleep(random.randint(0, self.REGISTRATION_STUDENT_TIME_LIMIT_SECONDS))
        # get the infos of the attendance sheet created
        response = self.client.get(f"/attendance/sheet/{self.attendance_sheet_id}")
        if response.status_code == 200:                          
            # register students in the class
            response = self.client.post(f"/attendance/sheet/{self.attendance_sheet_id}/student/registration",
                        json = {"nmec": random.randint(0, 50000), "name":  ''.join(random.choice(string.ascii_lowercase) for i in range(15)) })
            if response.status_code == 200:  
                print("Student registered in class")


    def teacher_manually_registers_a_student(self):
        # wait a bit
        time.sleep(random.randint(1, self.REGISTRATION_STUDENT_TIME_LIMIT_SECONDS))    
        # register students in the class
        response = self.client.post(f"/attendance/sheet/{self.attendance_sheet_id}/student/registration",
                        json = {"nmec": random.randint(0, 50000), "name":  ''.join(random.choice(string.ascii_lowercase) for i in range(15)) },
                        headers={"Authorization" : f"Token {self.user_token}"})  
        if response.status_code == 200:  
            # save user auth token
            self.user_token = response.json()["token"]
            print("Student registered in class, by teacher")


    def teacher_manually_deletes_some_students(self):
        # get some students to be deleted
        if self.registered_students:
            students_to_be_deleted = self.registered_students[:int(len(self.registered_students)*self.DELETED_STUDENT_PERCENTAGE)]
            response = self.client.delete(f"/attendance/sheet/{self.attendance_sheet_id}/student/deletion",
                            json = {"nmecs": [student["nmec"] for student in students_to_be_deleted]},
                            headers={"Authorization" : f"Token {self.user_token}"})  
            if response.status_code == 200:  
                # save user auth token
                self.user_token = response.json()["token"]
                print("Deleted some students")


    def close_attendance_sheet(self):
        response = self.client.post(f"/attendance/sheet/{self.attendance_sheet_id}/status",
                         json = {"status": False},
                         headers={"Authorization" : f"Token {self.user_token}"})  
        if response.status_code == 200:  
            # save user auth token
            self.user_token = response.json()["token"]
            print("Teacher cclosed the attendance sheet")


    def consult_attendance_sheet(self):
        # get the course units of a teacher
        response = self.client.get("/course_units/my",
                    headers={"Authorization" : f"Token {self.user_token}"})  
        if response.status_code == 200:   
            response_json = response.json()   
            self.teacher_cus = response_json["data"]
            # save user auth token
            self.user_token = response_json["token"]
            print(f"Obtiveram se as cadeiras de um prof")

            # get the schedules of the current cu
            response = self.client.get(f"/attendance/sheets/{self.cu['id']}",
                    headers={"Authorization" : f"Token {self.user_token}"})  
            if response.status_code == 200: 
                # save user auth token
                self.user_token = response_json["token"]
                # get the infos of the current attendance sheet
                response = self.client.get(f"/attendance/sheet/{self.attendance_sheet_id}",
                        headers={"Authorization" : f"Token {self.user_token}"})
                if response.status_code == 200:                          
                    # save user auth token
                    self.user_token = response.json()["token"]
                    # for debug
                    print("Consulted an attendance sheet")


    @task
    def simulate(self):
        global num_curr_users
        global user_pool_size
        if num_curr_users == user_pool_size:
            print("OVER")
            time.sleep(60*60*24)
            exit(0)