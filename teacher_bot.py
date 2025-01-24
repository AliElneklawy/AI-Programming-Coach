import cohere
import os
from datetime import datetime
from dotenv import load_dotenv
from constants import cohere_sys_msg
from database import DataBaseOps

load_dotenv()

class PythonLearningBot:
    def __init__(self):
        self.co = cohere.ClientV2(os.getenv('COHERE_API'))
        self.db = DataBaseOps()

    def get_response(self, message, user_asks=0):
        if user_asks: # if this is a question from the user
            answer = res = self.co.chat(
            model="command-r-plus-08-2024",
            messages=[
                    {"role": "system", "content": "Your response must be concise and to the point."},
                    {
                        "role": "user",
                        "content": f"{message}",
                    }
                ],
            )
            return res.message.content[0].text
                
        messages = [
            {"role": "system", "content": cohere_sys_msg},
            {"role": "user", "content": message},
            ]
        
        response = self.co.chat(model="command-r-plus-08-2024", messages=messages)
        status = int(response.message.content[0].text.rstrip('.'))

        return status
    
    def initial_assesment(self, questions, user_id): 
        score = 0       
        for q, weight in questions:
            ans = input(f'{q} ')
            message = f"Question: {q}. User Answer: {ans}"
            status = self.get_response(message)
            
            if status == 1:
                score += weight
            
            self.db.insert_assesment(user_id, q, ans, status, datetime.now())

        if score <= 4:
            level = 'beginner'
        elif score > 4 and score <= 12:
            level = 'intermediate'
        else:
            level = 'advanced'
        
        #print(score)
        return level
    
    def daily_task(self):
        pass
