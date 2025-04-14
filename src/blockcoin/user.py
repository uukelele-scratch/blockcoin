from .utils import deep_merge, get_script_data
from .theme import Theme

class UserNotFound(Exception):
    pass

class User:
    def __init__(self, username, session, data=None):
        self.username = username
        self.session = session
        if data:
            self._update_from_dashboard_data(data)
        else:
            self.update()

    def update(self):
        res = self.session.get(f"https://blockcoin.vercel.app/profile/{self.username}", impersonate="chrome")
        data = get_script_data(res.text)
        self._update_from_data(data)

    def _update_from_data(self, data):
        self._data = data[1]
        if data[1] == None:
            raise UserNotFound(f"User {self.username} not found. NOTE: Usernames are case sensitive.")
        __data = self._data["data"]

        self.id = __data["id"]
        self.display_name = __data["display"]
        self.username = __data["user"]
        self.about = __data["about"]
        self.profile_picture = __data["profile-picture"]
        self.banner = __data["banner"]
        self.badges = __data["badges"]
        self.badge_count = len(self.badges)
        self.balance = round(__data["balance"], 1)
        self.followers = __data["followers"]
        if hasattr(self, "_posts_cache"):
            del self._posts_cache

    @property
    def posts(self):
        if hasattr(self, '_posts_cache'):
            return self._posts_cache
        from .post import Post
        self._posts_cache = [
            Post(id=post["data"]["id"], session=self.session, data=post)
            for post in self._data["data"]["posts"]
        ]
        return self._posts_cache


    def _update_from_dashboard_data(self, data):
        self._data = {}
        for d in data:
            deep_merge(self._data, d)
        del self._data["type"]
        __data = self._data["data"]
        __profile = __data["profile"]
        __stats = __data["dashboard"]["stats"]

        self.logged_in = __data["logged"]
        self.id = __data["user"]
        self.display_name = __profile["display"]
        self.username = __profile["user"]
        self.about = __profile["about"]
        self.profile_picture = __profile["profile-picture"]
        self.banner = __profile["banner"]
        self.badges = __profile["badges"]
        self.badge_count = len(self.badges)
        self.balance = round(__profile["balance"], 1)
        self.followers = __profile["followers"]
        self.theme = Theme(__data["theme"])
        self.likes = __stats["likes"]
        self.views = __stats["views"]
        if hasattr(self, "_posts_cache"):
            del self._posts_cache

    def __repr__(self):
        return f"<blockcoin.user.User object for {self.username}>"
    
    def __str__(self):
        return self.username