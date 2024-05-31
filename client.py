import json
import logging
from time import sleep
from random import randrange
from requests import Session
from settings import (HEADERS, URL_REFRESH_TOKEN, URL_BALANCE, TOKEN_FILE, URL_ME,
                      URL_FARMING_CLAIM, URL_FARMING_START, URL_PLAY_START, 
                      URL_PLAY_CLAIM, URL_DAILY_REWARD)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s]    %(message)s")

def retry(func):
    def wrapper(self, *args, **kwargs):
        while True:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logging.error(f"Http session error: {e}")
                sleep(10)
    return wrapper

class ClickerClient(Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = HEADERS.copy()
        self.balance = None
        self.balance_data = None
        self.play_passes = None
        self.tasks = None
        self.auth_data = None
        self.name = None
        self.authenticate()
        self.me()

    @retry
    def request(self, *args, **kwargs):
        while True:
            result = super().request(*args, **kwargs)
            if result.status_code == 401:
                self.refresh_token()
            else:
                return result

    @property
    def estimate_time(self):
        default_est_time = 60
        if 'farming' in self.balance_data:
            est_time = (self.balance_data['farming']['endTime'] - self.balance_data['timestamp']) / 1000 + 1
            return max(est_time, default_est_time)
        return default_est_time

    def me(self):
        response = self.get(URL_ME)
        if response.status_code == 200:
            self.name = response.json().get('username')
        return response

    def authenticate(self):
        with open(TOKEN_FILE, 'r') as tok_file:
            self.auth_data = json.load(tok_file)
        self.headers['Authorization'] = f"Bearer {self.auth_data.get('access')}"
        if self.me().status_code == 401:
            self.refresh_token()

    def refresh_token(self):
        self.headers.pop('Authorization', None)
        response = self.post(URL_REFRESH_TOKEN, json={"refresh": self.auth_data.get("refresh")})
        if response.status_code == 200:
            self.auth_data = response.json()
            with open(TOKEN_FILE, 'w') as tok_file:
                json.dump(self.auth_data, tok_file)
            self.headers['Authorization'] = f"Bearer {self.auth_data.get('access')}"
        else:
            raise Exception("Can't get token")

    def update_balance(self):
        logging.info("Updating balance...")
        response = self.get(URL_BALANCE)
        if response.status_code == 200:
            self.balance_data = response.json()
            self.balance = self.balance_data.get('availableBalance')
            self.play_passes = self.balance_data.get('playPasses')
            logging.info(json.dumps(self.balance_data))

    def start_farming(self):
        if 'farming' not in self.balance_data:
            logging.info("Starting farming...")
            response = self.post(URL_FARMING_START)
            logging.info(f"{response.status_code}, {response.text}")
            self.update_balance()
        elif self.balance_data["timestamp"] >= self.balance_data["farming"]["endTime"]:
            logging.info("Claiming farming rewards...")
            response = self.post(URL_FARMING_CLAIM)
            logging.info(f"{response.status_code}, {response.text}")
        logging.info(f"Waiting for farming to complete in {self.estimate_time} seconds")
        sleep(self.estimate_time)

    def play_game(self):
        for _ in range(self.play_passes or 0):
            logging.info(f"Starting farming mini-game. (diamonds: {self.play_passes})")
            response = self.post(URL_PLAY_START)
            if response.status_code == 200:
                data = response.json()
                data['points'] = randrange(150, 250)
                sleep(23)
                while True:
                    logging.info(f"Submitting game result: {data['points']}")
                    result = self.post(URL_PLAY_CLAIM, json=data)
                    if result.status_code == 200:
                        break
                    sleep(1)
                self.update_balance()
                logging.info(result.text)

    def daily_reward(self):
        response = self.get(URL_DAILY_REWARD)
        if response.status_code == 200:
            self.post(URL_DAILY_REWARD)
            logging.info(f"Claimed daily reward! {response.text}")
