import json

from .utils import get_script_data
from .user import User
from datetime import datetime

class PostNotFound(Exception):
    pass

class Post:
    def __init__(self, id, session, data=None):
        self.id = id
        self.session = session
        if data:
            self._update_from_data({"post": data})
        else:
            res = session.get(f"{self.session.base_url}/post/{self.id}")
            data = get_script_data(res.text)
            if data[1] == None:
                raise PostNotFound(f"Post {id} not found.")
            post_data = data[1]["data"]
            self._update_from_data(post_data)

    def _update_from_data(self, data):
        self._data = data["post"]["data"]
        self.boost_end = self._data["boost_end"]
        self.boost_multi = self._data["boost_multi"]
        self.buyer = None if self._data["buyer"] == "None" else User(self._data["buyer"])
        self.body = self._data["data"]
        self.date = datetime.fromtimestamp(self._data["date"])
        self.hashtags = self._data["hashtags"]
        self.is_buyable = self._data["isBuyable"]
        self.likes = self._data["likes"]
        self.price = self._data["price"]
        self.profanity = self._data["profanity"]
        self.repost = None if not self._data.get("repost") else Post(self._data["repost"]["data"]["id"], self.session)
        self.reposting = self._data.get("reposting")
        self.author = User(data["post"]["profile"]["user"], session=self.session)
        self.views = self._data["views"]
        self.reposts_number = self._data["reposts_number"]
        self.comments_number = self._data["comments_number"]

    @property
    def liked(self):
        res = self.session.post(f"{self.session.base_url}/post/liked", headers={"Content-Type": "application/json"}, data=json.dumps({"post": self.id}), impersonate="chrome")
        return res.json()["liked"]
        

    def like(self, exist_ok=False):
        if self.liked and exist_ok == False:
            raise Exception("Cannot like post: Post already liked.")
        res = self.session.post(f"{self.session.base_url}/post/like", headers={"Content-Type": "application/json"}, data=json.dumps({"post": self.id}), impersonate="chrome")
        return res.status_code == 200
    
    def unlike(self, exist_ok=False):
        if not self.liked and exist_ok == False:
            raise Exception("Cannot unlike post: Post not liked.")
        res = self.session.post(f"{self.session.base_url}/post/like", headers={"Content-Type": "application/json"}, data=json.dumps({"post": self.id}), impersonate="chrome")
        return res.status_code == 200 

    def __repr__(self):
        return f"<blockcoin.post.Post object for post {self.id}>"
    
    def __str__(self):
        return f"Post {self.id} by {self.author.username}"