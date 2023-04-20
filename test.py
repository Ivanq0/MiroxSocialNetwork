from requests import get, post, put, delete

print(get('http://localhost:5000/api/user/3').json())