from flask import Flask, request, jsonify
from models import db, Reservation
import joblib

app = Flask(__name__)

# Initialize database and app context
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///your_database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Reservation API!"})

@app.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.json
    try:
        new_reservation = Reservation.deserialize(data)
        db.session.add(new_reservation)
        db.session.commit()
        return jsonify(new_reservation.serialize()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation(reservation_id):
    reservation = Reservation.read_reservation(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404
    return jsonify(reservation.serialize())

@app.route('/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id):
    data = request.json
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    for key, value in data.items():
        setattr(reservation, key, value)

    db.session.commit()
    return jsonify(reservation.serialize())

@app.route('/reservations/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    reservation = Reservation.delete_reservation(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404
    return jsonify({"message": "Reservation deleted successfully"})

@app.route('/reservations/account/<int:account_id>', methods=['GET'])
def list_reservations_by_account(account_id):
    reservations = Reservation.list_by_account_id(account_id)
    if not reservations:
        return jsonify({"message": "No reservations found for this account."}), 404

    # Serialize the list of reservations
    return jsonify([reservation.serialize() for reservation in reservations])


# Load the trained model
estimator = joblib.load('rental_price_model.pkl')

@app.route('/predict-price', methods=['POST'])
def predict_price():
    data = request.json
    try:
        estimated_price = estimator.estimate_price(
            car_brand=data['Car_Brand'],
            car_model=data['Car_Model'],
            seats=data['Seats'],
            location_city=data['Location_City'],
            pick_up_day=data['Pick_Up_Day'],
            pick_up_month=data['Pick_Up_Month'],
            drop_off_day=data['Drop_Off_Day'],
            drop_off_month=data['Drop_Off_Month'],
            credit_score=data.get('Credit_Score', 700)  # Default credit score
        )
        return jsonify({"estimated_price": estimated_price}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
