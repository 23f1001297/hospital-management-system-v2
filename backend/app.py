from flask import Flask, request, jsonify
from database import db, Users, Appointments, Doctor
from flask_cors import CORS
from doctor import doctor_bp
from patient import patient_bp
from flask_caching import Cache




cache = Cache()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hms.db'
    app.config['SECRET_KEY'] = 'secret-key'
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
    cache.init_app(app)

    db.init_app(app)
    CORS(app)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)

    @app.route('/daily')
    @cache.cached(timeout=60)
    def daily():
        from tasks import get_daily
        return jsonify(get_daily())
        
    
    @app.route('/monthly')
    @cache.cached(timeout=60)
    def monthly():
        from tasks import get_monthly
        return jsonify(get_monthly())

    @app.route('/')
    def home():
        return jsonify({"message": "Hospital API is running"})
    
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        user = Users.query.filter_by(username=data.get('username')).first()
        if user and user.password == data.get('password'):
            if user.blacklist:
                return jsonify({"message": "User is blacklisted"}), 403
            return jsonify({
                "message": "Login successful",
                "role": user.role,
                "name": user.name,
                "id": user.id
            }), 200
        return jsonify({"message": "Invalid credentials"}), 401

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        if Users.query.filter_by(username=data.get('username')).first():
            return jsonify({"message": "Username already exists"}), 400
        new_users = Users(username=data.get('username'), password=data.get('password'), name=data.get('name'), role='patient')
        db.session.add(new_users)
        db.session.commit()
        return jsonify({"message": "Registration successful"}),  201
    
    @app.route('/profile/<int:user_id>', methods=['GET'])
    def profiles(user_id):
        user = Users.query.get(user_id)
        return jsonify({"username": user.username, "name": user.name, "mobile": user.mobile or "", "age": user.age or "", "gender": user.gender or "", "address": user.address or ""})

    @app.route('/profile/update/<int:user_id>', methods=['PUT'])
    def updatep(user_id):
        data = request.json
        user = Users.query.get(user_id)
        user.name = data.get('name')
        user.mobile = data.get('mobile')
        user.age = data.get('age')
        user.gender = data.get('gender')
        user.address = data.get('address')
        db.session.commit()
        return jsonify({"message": "Profile updated"})

    @app.route('/docs')
    def docs():
        doctors = db.session.query(Users, Doctor).join(Doctor, Doctor.user_id == Users.id).filter(Users.role == 'doctor').all()
        d_list = []
        for user, doc in doctors:
            d_list.append({"id": user.id, "name": user.name, "special": doc.special, "availability": doc.availability, "blacklist": user.blacklist})
        return jsonify(d_list)

    @app.route('/patient')
    def patients():
        patients = Users.query.filter_by(role='patient').all()
        p_list = []
        for p in patients:
            p_list.append({"id": p.id, "name": p.name, "blacklist": p.blacklist})
        return jsonify(p_list)

    @app.route('/appoints')
    def appoints():
        appointments = Appointments.query.all()
        a_list = []
        for ap in appointments:
            patient = Users.query.get(ap.p_id)
            doctor = Users.query.get(ap.d_id)
            a_list.append({"id": ap.id, "patient_name": patient.name if patient else "Unknown", "doctor_name": doctor.name  if doctor else "Unknown", "date": ap.date,"time": ap.time, "status": ap.status, "remarks": ap.remarks})
        return jsonify(a_list)

    @app.route('/a_stats')
    @cache.cached(timeout=60)
    def a_stats():
        return jsonify({"total_doc" : Users.query.filter_by(role="doctor").count(), "total_patient": Users.query.filter_by(role="patient").count(), "total_appointment": Appointments.query.count(), "booked": Appointments.query.filter_by(status="Booked").count(), "completed": Appointments.query.filter_by(status="Completed").count(), "cancelled": Appointments.query.filter_by(status="Cancelled").count()})

    @app.route('/search')
    def search():
        query = request.args.get('q')
        type_ = request.args.get('type')
        if type_ == 'doctor':
            docs = Users.query.filter(Users.role == "doctor", Users.name.ilike(f"%{query}%")).all()
            result = [{"id": d.id, "name": d.name} for d in docs]
            return jsonify(result)
        elif type_ == "patient":
            patient = Users.query.filter(Users.role == "patient", Users.name.ilike(f"%{query}%")).all()
            result = [{"id": p.id, "name": p.name} for p in patient]
            return jsonify(result)
        return jsonify({"message": "Invalid search type"}), 400

    @app.route('/add_doc', methods=['POST'])
    def add_doc():
        data = request.get_json()
        if Users.query.filter_by(username=data.get('username')).first():
            return jsonify({"message": "Username already  exist"}), 400
        new_user = Users(username=data.get('username'), password=data.get('password'), name=data.get('name'), role='doctor')
        db.session.add(new_user)
        db.session.commit()
        new_doctor = Doctor(user_id=new_user.id, special=data.get('special'), availability=data.get('availability'))
        db.session.add(new_doctor)
        db.session.commit()
        return jsonify({"message": "Doctor added successfully"}), 201

    @app.route('/edit_doc/<int:id>',  methods=['PUT'])
    def edit_doc(id):
        data = request.get_json()
        user = Users.query.get(id)
        doctor = Doctor.query.filter_by(user_id=id).first()
        if not user or not doctor:
            return jsonify({"message": "Doctor not found"}), 404
        user.name = data.get('name')
        doctor.special = data.get('special')
        doctor.availability = data.get('availability')
        db.session.commit()
        return jsonify({"message": "Doctor Updated"})

    @app.route('/delete_doc/<int:id>', methods=['DELETE'])
    def delete_doc(id):
        user = Users.query.get(id)
        if not user or user.role == 'admin':
            return jsonify({"message": "Invalid operations"}), 400
        doc = Doctor.query.filter_by(user_id=id).first()
        if doc:
            db.session.delete(doc)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Doctor deleted"})

    @app.route('/edit_patient/<int:id>', methods=['PUT'])
    def edit_p(id):
        user = Users.query.get(id)
        if not user:
            return jsonify({"message": "Patient not found"}), 404
        data  = request.get_json()
        user.name = data.get('name')
        db.session.commit()
        return jsonify({"message": "Patient updated"})
    
    @app.route('/delete_p/<int:id>', methods=['DELETE'])
    def delete_p(id):
        user = Users.query.get(id)
        if not user or user.role == 'admin':
            return jsonify({"message": "Invalid operation"}), 400
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Patient deleted"})
    
    @app.route('/blacklist/<int:id>', methods=['PUT'])
    def blacklist(id):
        user = Users.query.get(id)
        if not user:
            return  jsonify({"message": "User not found"}), 404
        user.blacklist = not user.blacklist
        db.session.commit()
        return jsonify({"message": "Status updated"})

    @app.route('/delete_ap/<int:id>', methods=['DELETE'])
    def delete_ap(id):
        appoint = Appointments.query.get(id)
        if not appoint:
            return jsonify({"message": "Appointment not found"}), 404
        db.session.delete(appoint)
        db.session.commit()
        return jsonify({"message": "Appointment deleted"})

    with app.app_context():
        db.create_all()
        if not Users.query.filter_by(role='admin').first():
            admin = Users(username="admin", password="admin123", name="Admin", role="admin")
            db.session.add(admin)
            db.session.commit()
            print("System Initialized: Admin Created")
    return app

    
app = create_app()

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)