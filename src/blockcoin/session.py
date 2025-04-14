from curl_cffi import requests
import re
import json
from .utils import get_script_data, deep_merge, get_error
from .theme import Theme
from .post import Post
from .user import User

class LoginError(Exception):
    pass

class RegisterError(Exception):
    pass

class Session:
    def __init__(self, username, password):
        self.session = requests.Session(headers={"Origin": "https://blockcoin.vercel.app", "Host": "blockcoin.vercel.app", "Content-Type": "application/x-www-form-urlencoded"})
        self.balance = 0.0
        self._login(username, password)

    def _login(self, username, password):
        self.username = username
        self.password = password
        res = self.session.post("https://blockcoin.vercel.app/login", impersonate="chrome", data={"username": username, "password": password}, headers={"Referer": "https://blockcoin.vercel.app/login"})
        try:
            self._data = get_script_data(res.text)
            if self._data[0]["data"]["logged"] == True:
                self.user = User(self.username, session=self.session, data=self._data)
            else:
                error = get_error(res.url)
                raise LoginError(f"Failed to login. {error}")
        except:
            if "Vercel Security Checkpoint" in res.text:
                raise LoginError("Vercel thinks you're a bot and hit you with the Security Checkpoint. Try changing your IP address, or trying again later.")
            else:
                raise
        
    def update(self):
        res = self.session.get("https://blockcoin.vercel.app/dashboard", impersonate="chrome")
        self._data = get_script_data(res.text)
        self.user = User(self.username, session=self.session, data=self._data)

    def __repr__(self):
        return f"<blockcoin.session.Session for {self.username} ({self.user_id})>"
    
    def __str__(self):
        return f"BlockCoin Session for {self.username}"
    
    def create_post(self, body: str, price: int=0, repost: Post=None) -> Post:
        if repost is None:
            repost = ""
        else:
            repost = repost.id
        
        res = self.session.post("https://blockcoin.vercel.app/post", impersonate="chrome", data={"post": body, "price": price, "repost": repost})
        data = get_script_data(res.text)
        return Post(id=data[1]["data"]["post"]["data"]["id"], session=self.session)
    
    def fetch_post(self, id: str) -> Post:
        return Post(id=id, session=self.session)
    
    def get_user(self, username: str) -> User:
        return User(username=username, session=self.session)
    
    @classmethod
    # WIP
    def _register(cls, username: str, email: str):
        self = object.__new__(cls)
        self.session = requests.Session(headers={"Origin": "https://blockcoin.vercel.app", "Host": "blockcoin.vercel.app", "Content-Type": "application/x-www-form-urlencoded"})
        self.session.get("https://blockcoin.vercel.app/", impersonate="chrome")
        res = self.session.post("https://blockcoin.vercel.app/register", impersonate="chrome")
        error = get_error(res.url)
        if error:
            raise RegisterError(f"Failed to register account. {error}")
        print(res.url)
        print(res.status_code)
        print(res.text)