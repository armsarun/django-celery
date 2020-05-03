<p align="center">
  <h2>Fisdom Demo</h2> 
</p>
<hr>

### Local Development setup:

***step 1:***  Install [virutalenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) 

                ```mkvirtualenv myapp```
                
                > By default env will be activate if it's not use below command
                
                ``` workon myapp ```
                
 ***step 2:***  Install all packages
 
                ```pip install -r requirements.txt```
                
  ***step 3:*** Create New [Postgresql](https://www.postgresql.org/download/linux/)  Database. Install if is not available
                
  ***step 4:*** Install [redis](https://redis.io/download)     
  
  ***step 5:*** Create .env file in root folder and add below keys
  
            >DATABASE_NAME = ''
            >DATABASE_USER = ''
            >DATABASE_PASSWORD = ''
            >DATABASE_HOST = '127.0.0.1'
            >DATABASE_PORT = ''
            >SECRET= ''
            >CELERY_BROKER_URL = ''
            >CELERY_RESULT_BACKEND = ''
            >DEBUG = True
  
  ***step 6:*** Start your django app
            ```python manage.py runserver``` 
            
      
  ***step 7:*** Celery Scheduler start
            > start redis server first
            ```redis-server```
            > Run celery worker
            ``` celery -A core worker -l info -B```  
            ****Note:****
            ***Celery need to start after activating virtualenv and must run in core 
            folder location***
             
                  
