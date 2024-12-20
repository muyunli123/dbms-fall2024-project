from flask import Flask, request, jsonify
from flask import current_app as app 
from service.models import db, Reservation, Account, Company, Customer, CarType, BranchLocation
import joblib
from datetime import timedelta
from service.ml_model import RentalPriceEstimator


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
estimator = joblib.load('service/rental_price_model.pkl')

@app.route('/predict-price', methods=['POST'])
def predict_price():
    data = request.json
    try:
        estimated_price = estimator.predict(
            brand=data['Brand'],
            model=data['Model'],
            seats=data.get('Seats', 4),
            pickupcity=data['Location_City'],
            pick_up_day=data['Pick_Up_Day'],
            pick_up_month=data['Pick_Up_Month'],
            drop_off_day=data['Drop_Off_Day'],
            drop_off_month=data['Drop_Off_Month'],
            credit_score=data.get('Credit_Score', 700)  # Default credit score
        )
        return jsonify({"estimated_price": estimated_price}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
    account = Account.query.get(account_id)
    if account:
        if account.MemberId:
            customer = Customer.query.get(account.MemberId)
            if customer:
                return jsonify({"name": f"{customer.FirstName} {customer.LastName}"})
            company = Company.query.get(account.MemberId)
            if company:
                return jsonify({"name": company.Name})
    return jsonify({"error": "Account not found"}), 404

@app.route('/reservations/<int:reservation_id>/extend', methods=['PUT'])
def extend_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if reservation:
        reservation.DropOffTime += timedelta(weeks=1)
        db.session.commit()
        return jsonify({"message": "Reservation extended"}), 200
    return jsonify({"error": "Reservation not found"}), 404

@app.route('/car-types', methods=['GET'])
def list_car_types():
    """
    List all car types available in the database.
    """
    car_types = CarType.query.all()  
    if not car_types:
        return jsonify({"error": "No car types found"}), 404
    return jsonify([
        {"TypeId": car_type.TypeId, "Brand": car_type.Brand, "Model": car_type.Model}
        for car_type in car_types
    ]), 200


@app.route('/car-types/<int:type_id>', methods=['GET'])
def get_car_type_by_id(type_id):
    """Retrieve a car type by its ID."""
    car_type = CarType.query.get(type_id)
    if not car_type:
        return jsonify({"error": "Car type not found"}), 404
    return jsonify({"type": f"{car_type.Brand} {car_type.Model}"}), 200

@app.route('/locations', methods=['GET'])
def list_locations():
    """
    List all branch locations available in the database.
    """
    locations = BranchLocation.query.all()
    if not locations:
        return jsonify({"error": "No locations found"}), 404

    return jsonify([
        {"Id": location.Id, "Street": location.Street, "City": location.City, "State": location.State, "ZipCode": location.ZipCode, "Country": location.Country}
        for location in locations
    ]), 200

@app.route('/locations/<int:location_id>', methods=['GET'])
def get_location_by_id(location_id):
    """
    Retrieve a branch location by its ID.
    """
    location = BranchLocation.query.get(location_id)
    print(location)
    if not location:
        return jsonify({"error": "Location not found"}), 404
    return jsonify({
        "location": f"{location.Street}, {location.City}, {location.State} {location.ZipCode}"
    }), 200

