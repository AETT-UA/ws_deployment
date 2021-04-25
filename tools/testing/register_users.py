from locust import HttpUser, task, TaskSet, between
import random
import string
import time
import os

user_pool_size = int(os.getenv("num_users_register")) 
user_file = open("user_data.tsv", "a+")
num_curr_users = 0

class RegisterNewUsers(HttpUser):
    wait_time = between(0.9,1)

    @task
    class Register(TaskSet):
        wait_time = between(0.9,1)
        def on_start(self):
            """ 
            on_start is called when a Locust start before any task is scheduled
            """
            global num_curr_users
            global user_pool_size
            global user_file

            # open file to record the user ccredeentials
            # self.user_file = open("user_data.tsv", "a+")

            # register new user
            self.register_new_user()
            
            num_curr_users +=1
            

        def register_new_user(self):
            # generate new  user data
            m_first_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5, 10))
            m_last_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5, 10))
            m_password = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            m_email = f"{m_first_name}{m_last_name}@ua.pt"
            
            # register new user
            response = self.client.post("/register",
                            json = {"first_name": m_first_name,
                            "last_name" : m_last_name,
                            "email": m_email,
                            "password": m_password})

            if response.status_code == 200:
                print(f"[Registered new user] Email:{m_email}, Password:{m_password}")
                # write data to file
                user_file.write(f"{m_email}\t{m_password}\n")
                #user_file.flush()
            
        @task
        def leave(self):
            # wait for all the users to be registered and leave
            if num_curr_users == user_pool_size:
                user_file.close()
                exit(0)
