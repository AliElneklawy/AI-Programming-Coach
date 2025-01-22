import cohere
from dotenv import load_dotenv
from constants import cohere_sys_msg

load_dotenv()

class PythonLearningBot:
    def __init__(self, cohere_api):
        self.co = cohere.ClientV2(cohere_api)

    def initial_assesment(self, questions): 
        score = 0       
        for q, weight in questions:
            ans = input(f'{q} ')
            message = f"Question: {q}. User Answer: {ans}"
            messages = [
            {"role": "system", "content": cohere_sys_msg},
            {"role": "user", "content": message},
            ]

            response = self.co.chat(model="command-r-plus-08-2024", messages=messages)
            #print(response.message.content[0].text)

            if int(response.message.content[0].text) == 1:
                score += weight

        if score <= 4:
            level = 'beginner'
        elif score > 4 and score <= 12:
            level = 'intermediate'
        else:
            level = 'advanced'
        
        #print(score)
        return level

