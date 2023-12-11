# Planetarium-API
### Django REST API for the Planetarium project.
![img.png](https://cdn-icons-png.flaticon.com/512/2133/2133008.png)


##   [⚡ Live DEMO](https://newspapersagency-w41c.onrender.com/)
- You can use following superuser (or create another one by yourself):
    - Login: ```FullAdmin```
    - Password: ```admin```

# ⚡️ Features


1. [x] JWT authentication
2. [x] Full CRUD
3. [x] Orders creation for tickets
4. [x] Pagination
5. [x] Filtering feature

# 🧠 DB Schema



![img.png](https://media.mate.academy/planetarium_diagram_7f452c3e1d.png)

## 👩 _Installation & Run in Docker_
<details>
  <summary>Click me</summary>

  ### 🧠 Set up the variables  
 In [.env](.env) file connect db:
```
POSTGRES_HOST=db
POSTGRES_DB=app
POSTGRES_USER=postgressql
POSTGRES_PASSWORD=superhardpassword
 ```
 
### 👯 Compose Up 
```
docker-compose build
docker-compose up
```
### 🤔 Login to Container
To get active containers
```
docker ps
```
Find our and copy id. Place it here and run:
```
docker exec -it "container_id" /bin/bash
```
### 📫 Install database fixture
```python
python manage.py loaddata data.json
```
</details>

## 👩‍💻 _Installation & Run in Venv_ 

<details>
  <summary>Click me</summary>

### Check which DB you use in [settings.py](planetarium_api%2Fsettings.py).

Set `DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}` if you want use sqlite3 DB.
### 🧠 Set up the environment 


 On Windows:
```python
python -m venv venv 
venv\Scripts\activate
 ```
 On macOS:
```python
python3 -m venv venv 
source venv/bin/activate
 ```
### 👯 Set up requirements 
```python
pip install -r requirements.txt
```
### 🤔 Migrate

```python
python manage.py migrate
```
### 📫 Install database fixture
```python
python manage.py loaddata data.json
```
</details>

## 😄 Go to site [http://127.0.0.1:8000/api/planetarium/](http://127.0.0.1:8000/api/planetarium/)
