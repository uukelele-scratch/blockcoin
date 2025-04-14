# BlockCoin API Wrapper

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/uukelele-scratch/blockcoin/publish.yml)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/uukelele-scratch/blockcoin)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/uukelele-scratch/blockcoin)
![PyPI - License](https://img.shields.io/pypi/l/blockcoin)
![GitHub Repo stars](https://img.shields.io/github/stars/uukelele-scratch/blockcoin)
![PyPI - Version](https://img.shields.io/pypi/v/blockcoin)




BlockCoin is a Python library that provides an easy-to-use wrapper for interacting with the BlockCoin API. The library uses [curl_cffi](https://pypi.org/project/curl-cffi/) with Chrome impersonation to mimic browser behavior and bypass certain anti-bot measures. It gives you convenient access to login, register, fetch user data, create posts, and more.

> **Note:** This library is currently in early development. Some features (like registration) are still a work-in-progress (WIP) and may change soon.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Authentication](#authentication)
  - [Working with Sessions](#working-with-sessions)
  - [Creating and Fetching Posts](#creating-and-fetching-posts)
  - [Working with Users and Themes](#working-with-users-and-themes)
- [API Documentation](#api-documentation)
  - [Session Class](#session-class)
  - [Post Class](#post-class)
  - [User Class](#user-class)
  - [Theme Class](#theme-class)
  - [Utility Functions](#utility-functions)
- [Modules Overview](#modules-overview)
- [Contributing](#contributing)
- [License](#license)

## Installation

BlockCoin depends on only one external package: [`curl_cffi==0.7.4`](https://pypi.org/project/curl-cffi/). Other modules used are Python's standard library (`re`, `json`, `datetime`, etc.).

To install the package, use pip:

```bash
pip install blockcoin
```

## Usage

### Authentication

To start working with BlockCoin, you need to log in. The library exposes a `login` function from the module's main package (`blockcoin/__init__.py`). This function creates a `Session` object after a successful login.

```python
from blockcoin import login

# Log in with your BlockCoin credentials
session = login("your_username", "your_password")

# Check out your session details
print(session)
```

### Working with Sessions

The `Session` class (in `session.py`) handles the authentication flow and maintains the session state. It automatically parses the server's responses, handles errors, and sets up the session for subsequent API calls.

```python
# Update session data (e.g., after posting or making changes)
session.update()

# Retrieve your user profile from the session
print("Logged in as:", session.user.username)
```

If an error occurs during login, a `LoginError` or `RegisterError` is raised with a descriptive message.

### Creating and Fetching Posts

The `Session` class provides methods for creating posts and fetching existing posts.

```python
from blockcoin.post import Post

# Create a new post
new_post = session.create_post("Hello BlockCoin!", price=10)
print("New post created with ID:", new_post.id)

# Fetch an existing post by its ID
fetched_post = session.fetch_post("some_post_id")
print("Post:", fetched_post.body)

# Repost the existing post
reposted_post = session.create_post(
    "This is a repost!",
    price=50,
    repost=fetched_post
)
print("Reposted original post. Reposted post ID:", reposted_post.id)
```

The `Post` class (in `post.py`) parses the server response and stores properties like body, likes, price, etc., automatically converting timestamps into `datetime` objects.

### Working with Users and Themes

The `User` class (in `user.py`) fetches and updates user information including profile details and posts. The user's theme data is represented by the `Theme` class (in `theme.py`).

```python
# Retrieve user data for a specific username
user_profile = session.get_user("another_username")
print("User Profile:", user_profile)

# List posts' likes by the user
for post in user_profile.posts:
    print(post.likes)
    
# Print the user's theme name
print("Theme:", user_profile.theme)
```

## API Documentation

Below is an overview of the main classes, their public attributes, and methods with type hints where applicable.

### Session Class (session.py)

Represents an active session with the BlockCoin API.  
**Attributes:**
- `username: str` — The username used for login.
- `session` — The underlying `curl_cffi` session used to make HTTP requests.
- `user: User` — The logged-in user's profile information (an instance of `User`).

**Public Methods:**
- `update() -> None`  
  Refreshes session data (e.g., user profile, dashboard data).

- `create_post(body: str, price: int = 0, repost: Optional[Post] = None) -> Post`  
  **Arguments:**
  - `body (str)`: The content of the post.
  - `price (int, default=0)`: The price associated with the post.
  - `repost (Optional[Post], default=None)`: A post object to repost; if provided, its `id` is used.
  
  **Returns:**  
  A new `Post` object representing the created post.

- `fetch_post(id: str) -> Post`  
  **Arguments:**
  - `id (str)`: The identifier of the post to fetch.
  
  **Returns:**  
  A `Post` object corresponding to the given post ID.

- `get_user(username: str) -> User`  
  **Arguments:**
  - `username (str)`: The username of the profile to fetch.
  
  **Returns:**  
  A `User` object with the requested user's data.

**Exceptions:**
- `LoginError` — Raised if login fails.
- `RegisterError` — Raised during registration issues (WIP).

---

### Post Class (post.py)

Represents a BlockCoin post.  
**Attributes (after initialization via API response):**
- `id: str` — The unique identifier for the post.
- `boost_end` — Timestamp or value indicating post boost ending.
- `boost_multi` — Multiplier used during boosting.
- `buyer` — A `User` object representing the buyer (if any), or `None`.
- `body: str` — The textual content of the post.
- `date: datetime` — A datetime object representing the post creation time.
- `hashtags` — A list of hashtags associated with the post.
- `is_buyable` — Boolean flag indicating if the post can be bought.
- `likes: int` — Number of likes.
- `price: int` — The price of the post.
- `profanity` — Value denoting profanity flags (or related information).
- `repost: Optional[Post]` — If the post is a repost, contains a `Post` object; else `None`.
- `reposting` — Additional data on reposting, if applicable.
- `author: User` — The author of the post.
- `views: int` — View count of the post.
- `reposts_number: int` — Number of times reposted.
- `comments_number: int` — Number of comments.

**Properties:**
- `liked -> bool`  
  Returns `True` if the current session user has liked the post, else `False`.  
  Internally performs a POST request to `/post/liked`.

**Methods:**
- `like(exist_ok: bool = False) -> bool`  
  Likes the post.  
  - If the post is already liked and `exist_ok` is `False`, raises an exception.  
  - Returns `True` if the request succeeds.

- `unlike(exist_ok: bool = False) -> bool`  
  Unlikes the post.  
  - If the post is not liked and `exist_ok` is `False`, raises an exception.  
  - Returns `True` if the request succeeds.

- `__repr__()` and `__str__()` — Provide string representations of the post.

---

### User Class (user.py)

Represents a BlockCoin user profile.  
**Attributes:**
- `username: str` — The user's username (case-sensitive).
- `id: str` — The unique identifier for the user.
- `display_name: str` — The user’s display name.
- `about: str` — The "about" description.
- `profile_picture: str` — URL for the profile picture.
- `banner: str` — URL for the profile banner.
- `badges: list` — A list containing the user’s badges.
- `badge_count: int` — Count of badges.
- `balance: float` — User’s current BlockCoin balance.
- `followers: int` — Number of followers.
- `theme: Theme` — A `Theme` instance holding the user’s theme data.
  
**Properties:**
- `posts -> List[Post]`  
  Lazily loads and returns a list of `Post` objects created from the user's profile data. Results are cached until the profile is updated.

**Methods:**
- `update() -> None`  
  Fetches the latest user profile data from the API.
- Internal update methods (`_update_from_data` and `_update_from_dashboard_data`) are not publicly accessible.

**Exceptions:**
- `UserNotFound` — Raised when a user cannot be found.

---

### Theme Class (theme.py)

Handles the user's theme information.  
**Attributes:**
- `data: dict` — Parsed theme metadata from a JSON string.
  
**Methods:**
- `__str__() -> str`  
  Returns a string with the theme name and author.
- `__repr__() -> str`  
  Returns the theme key as a representation.

---

### Utility Functions (utils.py)

**Public Functions:**
- `extract_data_array(js_code: str, keyword: str = "data") -> str`  
  **Arguments:**
  - `js_code (str)`: The raw JavaScript code as a string.
  - `keyword (str, default="data")`: The variable name to search for in the code.
  
  **Returns:**  
  A substring containing the JavaScript array (without the trailing semicolon).

- `get_script_data(body: str, keyword: str = "data") -> list`  
  Parses the JavaScript from an HTML body into Python objects.
  
- `get_error(url: str) -> Optional[str]`  
  **Arguments:**
  - `url (str)`: The URL which contains an error code.
  
  **Returns:**  
  A description for the error code if found; otherwise, returns `"Unknown Error"` or `None`.

- `login(username: str, password: str) -> "Session"`  
  **Arguments:**
  - `username (str)`: Your BlockCoin username.
  - `password (str)`: Your password.
  
  **Returns:**  
  A `Session` object after successful login.

- `_register(*args, **kwargs) -> "Session"`  
  *(Work in progress)* — Intended to handle account registration.

- `deep_merge(a: dict, b: dict) -> dict`  
  Recursively merges dictionary `b` into dictionary `a`.

---

## Modules Overview

- **`__init__.py`**  
  Exposes the library’s public API by exporting `login`.

- **`utils.py`**  
  Contains helper functions for parsing JavaScript data, error fetching, login, registration (WIP), and dictionary merging.

- **`session.py`**  
  Defines the `Session` class, managing user login, session updates, and API requests.

- **`post.py`**  
  Contains the `Post` class, parsing and representing post data from BlockCoin.

- **`user.py`**  
  Provides the `User` class for handling user profiles and caching their posts.

- **`theme.py`**  
  Defines the `Theme` class, which parses and represents theme data.

## Contributing

Contributions are welcome! Feel free to fork the repository, open issues, or submit pull requests. When submitting changes, please ensure your code follows the existing style guidelines and that tests pass locally.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
