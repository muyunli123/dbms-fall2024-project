from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = "CUSTOMER"
    MemberId = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    DoB = db.Column(db.Date)
    SSN = db.Column(db.String(11))
    DriverLicense = db.Column(db.String(20))
    Age = db.Column(db.Integer)

class Company(db.Model):
    __tablename__ = "COMPANY"
    MemberId = db.Column(db.Integer, primary_key=True)
    Code = db.Column(db.String(10))
    Name = db.Column(db.String(100))

class Account(db.Model):
    __tablename__ = "ACCOUNT"
    Id = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String(20))
    EmailAddress = db.Column(db.String(100))
    PhoneNumber = db.Column(db.String(20))
    MemberId = db.Column(db.Integer, db.ForeignKey("CUSTOMER.MemberId"))

class PaymentAccount(db.Model):
    __tablename__ = "PAYMENT_ACCOUNT"
    Id = db.Column(db.Integer, primary_key=True)
    CardNumber = db.Column(db.String(16))
    ExpirationDate = db.Column(db.Date)
    CardHolderFirstName = db.Column(db.String(50))
    CardHolderLastName = db.Column(db.String(50))
    CardSecurityCode = db.Column(db.String(5))

class Employee(db.Model):
    __tablename__ = "EMPLOYEE"
    EmployeeId = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    SSN = db.Column(db.String(11))
    PhoneNumber = db.Column(db.String(20))
    EmailAddress = db.Column(db.String(100))
    ManagerId = db.Column(db.Integer, db.ForeignKey("EMPLOYEE.EmployeeId"))
    PositionType = db.Column(db.String(20))

class CarType(db.Model):
    __tablename__ = "CAR_TYPE"
    TypeId = db.Column(db.Integer, primary_key=True)
    Brand = db.Column(db.String(50))
    Model = db.Column(db.String(50))
    Seats = db.Column(db.Integer)
    Speed = db.Column(db.Integer)
    Luggage = db.Column(db.Integer)
    Price = db.Column(db.Numeric(10, 2))
    Door = db.Column(db.Integer)
    Auto = db.Column(db.Boolean)
    CompetitivePrice = db.Column(db.Numeric(10, 2))

class Car(db.Model):
    __tablename__ = "CAR"
    LicensePlateNumber = db.Column(db.String(20), primary_key=True)
    CarTypeId = db.Column(db.Integer, db.ForeignKey("CAR_TYPE.TypeId"))
    Status = db.Column(db.String(20))
    BranchId = db.Column(db.Integer, db.ForeignKey("BRANCH_LOCATION.Id"))

class BranchLocation(db.Model):
    __tablename__ = "BRANCH_LOCATION"
    Id = db.Column(db.Integer, primary_key=True)
    Street = db.Column(db.String(100))
    City = db.Column(db.String(50))
    State = db.Column(db.String(50))
    ZipCode = db.Column(db.String(10))
    Country = db.Column(db.String(50))

class Discount(db.Model):
    __tablename__ = "DISCOUNT"
    Code = db.Column(db.String(10), primary_key=True)
    Amount = db.Column(db.Numeric(5, 2))
    StartDate = db.Column(db.Date)
    EndDate = db.Column(db.Date)

class Reservation(db.Model):
    __tablename__ = "RESERVATION"
    Id = db.Column(db.Integer, primary_key=True)
    Time = db.Column(db.DateTime)
    AccountId = db.Column(db.Integer, db.ForeignKey("ACCOUNT.Id"))
    PaymentAccountId = db.Column(db.Integer, db.ForeignKey("PAYMENT_ACCOUNT.Id"))
    SalesId = db.Column(db.Integer, db.ForeignKey("EMPLOYEE.EmployeeId"))
    CarTypeId = db.Column(db.Integer, db.ForeignKey("CAR_TYPE.TypeId"))
    CarPlateNumber = db.Column(db.String(20), db.ForeignKey("CAR.LicensePlateNumber"))
    PickUpTime = db.Column(db.DateTime)
    DropOffTime = db.Column(db.DateTime)
    Duration = db.Column(db.Integer)  # Derived attribute
    PickUpLocationId = db.Column(db.Integer, db.ForeignKey("BRANCH_LOCATION.Id"))
    DropOffLocationId = db.Column(db.Integer, db.ForeignKey("BRANCH_LOCATION.Id"))
    RentalPricePerDay = db.Column(db.Numeric(10, 2))
    DiscountCode = db.Column(db.String(10), db.ForeignKey("DISCOUNT.Code"))
    InsurancePlanPricePerDay = db.Column(db.Numeric(10, 2))
    TotalPrice = db.Column(db.Numeric(15, 2))  # Derived attribute

    # CRUD Methods for Reservation
    @classmethod
    def create_reservation(cls, data):
        """Create a new reservation."""
        new_reservation = cls(
            Time=data.get("Time"),
            AccountId=data.get("AccountId"),
            PaymentAccountId=data.get("PaymentAccountId"),
            SalesId=data.get("SalesId"),
            CarTypeId=data.get("CarTypeId"),
            CarPlateNumber=data.get("CarPlateNumber"),
            PickUpTime=data.get("PickUpTime"),
            DropOffTime=data.get("DropOffTime"),
            Duration=data.get("Duration"),
            PickUpLocationId=data.get("PickUpLocationId"),
            DropOffLocationId=data.get("DropOffLocationId"),
            RentalPricePerDay=data.get("RentalPricePerDay"),
            DiscountCode=data.get("DiscountCode"),
            InsurancePlanPricePerDay=data.get("InsurancePlanPricePerDay"),
            TotalPrice=data.get("TotalPrice"),
        )
        db.session.add(new_reservation)
        db.session.commit()
        return new_reservation

    @classmethod
    def read_reservation(cls, reservation_id):
        """Retrieve a reservation by ID."""
        return cls.query.get(reservation_id)

    @classmethod
    def update_reservation(cls, reservation_id, updates):
        """Update an existing reservation."""
        reservation = cls.query.get(reservation_id)
        if not reservation:
            return None
        for key, value in updates.items():
            setattr(reservation, key, value)
        db.session.commit()
        return reservation

    @classmethod
    def delete_reservation(cls, reservation_id):
        """Delete a reservation by ID."""
        reservation = cls.query.get(reservation_id)
        if not reservation:
            return None
        db.session.delete(reservation)
        db.session.commit()
        return reservation

    # Serialize the model to a dictionary
    def serialize(self):
        """Convert a Reservation object into a JSON-compatible dictionary."""
        return {
            "Id": self.Id,
            "Time": self.Time.isoformat() if self.Time else None,
            "AccountId": self.AccountId,
            "PaymentAccountId": self.PaymentAccountId,
            "SalesId": self.SalesId,
            "CarTypeId": self.CarTypeId,
            "CarPlateNumber": self.CarPlateNumber,
            "PickUpTime": self.PickUpTime.isoformat() if self.PickUpTime else None,
            "DropOffTime": self.DropOffTime.isoformat() if self.DropOffTime else None,
            "Duration": self.Duration,
            "PickUpLocationId": self.PickUpLocationId,
            "DropOffLocationId": self.DropOffLocationId,
            "RentalPricePerDay": float(self.RentalPricePerDay) if self.RentalPricePerDay else None,
            "DiscountCode": self.DiscountCode,
            "InsurancePlanPricePerDay": float(self.InsurancePlanPricePerDay) if self.InsurancePlanPricePerDay else None,
            "TotalPrice": float(self.TotalPrice) if self.TotalPrice else None,
        }

    # Deserialize a dictionary into a Reservation object
    @classmethod
    def deserialize(cls, data):
        """Create or update a Reservation object from a dictionary."""
        return cls(
            Time=data.get("Time"),
            AccountId=data.get("AccountId"),
            PaymentAccountId=data.get("PaymentAccountId"),
            SalesId=data.get("SalesId"),
            CarTypeId=data.get("CarTypeId"),
            CarPlateNumber=data.get("CarPlateNumber"),
            PickUpTime=data.get("PickUpTime"),
            DropOffTime=data.get("DropOffTime"),
            Duration=data.get("Duration"),
            PickUpLocationId=data.get("PickUpLocationId"),
            DropOffLocationId=data.get("DropOffLocationId"),
            RentalPricePerDay=data.get("RentalPricePerDay"),
            DiscountCode=data.get("DiscountCode"),
            InsurancePlanPricePerDay=data.get("InsurancePlanPricePerDay"),
            TotalPrice=data.get("TotalPrice"),
        )

    @classmethod
    def list_by_account_id(cls, account_id):
        """List all reservations for a given AccountId."""
        return cls.query.filter_by(AccountId=account_id).all()
    