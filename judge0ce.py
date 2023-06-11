import json
import requests

class Judge0CEClient:
    def __init__(self, token: str):
        self.token: str = token
        self.headers = {
            "X-RapidAPI-Key": self.token,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        }
        self.url = 'https://judge0-ce.p.rapidapi.com/'

    
    def create_submission(self, source_code: str, language_id: int, number_of_runs: int = 1):
        data = {
            'source_code': source_code,
            'language_id': language_id,
            'number_of_runs': number_of_runs
        }
        r = requests.post(self.url + 'submissions', json=data, headers=self.headers)
        return r.json()
    
    def get_submission(self, submission_id: int):
        r = requests.get(self.url + 'submissions/' + str(submission_id), headers=self.headers)
        return r.json()
    
    def get_submission_output(self, submission_id: int):
        r = requests.get(self.url + 'submissions/' + str(submission_id), headers=self.headers)
        return r.json()
    
    def run_code(self, source_code: str, language_id: int, number_of_runs: int = 1):
        submission = self.create_submission(source_code, language_id, number_of_runs)
        submission_id = submission['token']
        print(self.get_submission(submission_id))
        while True:
            submission = self.get_submission(submission_id)
            if submission['status']['id'] in [1, 2]:
                continue
            break

        output = self.get_submission_output(submission_id)
        return json.dumps(output, indent=4, sort_keys=True)
    
    