<<<<<<< HEAD
# hospital-management-system-v2
=======


Hospital Management System V - 2

This project is a web-based hospital management system built using Flask. 
It allows users to book appointments, track activities, and manage health-related information.

- Python
- Flask
- SQLite
- HTML
- CSS
- Jinja2
- Celery
- Redis



1. Clone the repository or extract the ZIP file.

2. Create virtual environment
python3 -m venv venv

3. Activate virtual environment
source venv/bin/activate

4. Install dependencies
pip install -r requirements.txt

5. Run Redis server

6. Start Flask application
python app.py

7. Run Celery worker
celery -A celery_worker.celery worker --loglevel=info

8. Run Celery beat
celery -A celery_worker.celery beat --loglevel=info
9. Run Vue.js
npm run dev
>>>>>>> dbbf107 (Milestone-0 HMS-V2 Setup)
