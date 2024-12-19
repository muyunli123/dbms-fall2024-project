"""
Flask CLI Command Extensions
"""
from flask import current_app as app  # Import Flask application
from service.models import db, Customer, Company, CarType, BranchLocation, Reservation, Account
from datetime import datetime


######################################################################
# Command to force tables to be rebuilt
# Usage:
#   flask db-create
######################################################################
@app.cli.command("db-create")
def db_create():
    """
    Recreates a local database. You probably should not use this on
    production. ;-)
    """
    db.drop_all()
    db.create_all()

    # sample data

    customer1 = Customer(
        MemberId=1,
        FirstName="John",
        LastName="Doe",
        DoB=datetime.strptime("1990-01-01", "%Y-%m-%d").date(),  # Convert string to date
        SSN="123-45-6789",
        DriverLicense="D1234567",
        Age=33
    )

    customer2 = Customer(
        MemberId=2,
        FirstName="Jane",
        LastName="Smith",
        DoB=datetime.strptime("1985-05-15", "%Y-%m-%d").date(),  # Convert string to date
        SSN="987-65-4321",
        DriverLicense="S7654321",
        Age=38
    )

    #customer1 = Customer(MemberId=1, FirstName="John", LastName="Doe", DoB="1990-01-01", SSN="123-45-6789", DriverLicense="D1234567", Age=33)
    #customer2 = Customer(MemberId=2, FirstName="Jane", LastName="Smith", DoB="1985-05-15", SSN="987-65-4321", DriverLicense="S7654321", Age=38)

    company1 = Company(MemberId=3, Code="ACME", Name="ACME Corporation")
    company2 = Company(MemberId=4, Code="GLOBEX", Name="Globex Corporation")

    account1 = Account(Id=1, Type="Customer", EmailAddress="john.doe@example.com", PhoneNumber="555-1234", MemberId=1)
    account2 = Account(Id=2, Type="Customer", EmailAddress="jane.smith@example.com", PhoneNumber="555-5678", MemberId=2)
    account3 = Account(Id=3, Type="Company", EmailAddress="contact@acme.com", PhoneNumber="555-8765", MemberId=3)
    account4 = Account(Id=4, Type="Company", EmailAddress="support@globex.com", PhoneNumber="555-4321", MemberId=4)


    car_type1 = CarType(TypeId=1, Brand="Toyota", Model="Camry", Seats=5, Speed=120, Luggage=3, Price=50.00, Door=4, Auto=True, CompetitivePrice=48.00)
    car_type2 = CarType(TypeId=2, Brand="Honda", Model="Civic", Seats=5, Speed=115, Luggage=2, Price=45.00, Door=4, Auto=True, CompetitivePrice=42.50)

    branch1 = BranchLocation(Id=1, Street="123 Main St", City="New York", State="NY", ZipCode="10001", Country="USA")
    branch2 = BranchLocation(Id=2, Street="456 Elm St", City="Los Angeles", State="CA", ZipCode="90001", Country="USA")

    reservation1 = Reservation(
        Id=1,
        AccountId=1,
        CarTypeId=1,
        PickUpTime=datetime.strptime("2024-12-20 09:00:00", "%Y-%m-%d %H:%M:%S"),  # Convert string to datetime
        DropOffTime=datetime.strptime("2024-12-25 09:00:00", "%Y-%m-%d %H:%M:%S"),  # Convert string to datetime
        PickUpLocationId=1,
        DropOffLocationId=2,
        RentalPricePerDay=50.00,
        InsurancePlanPricePerDay=5.00,
        TotalPrice=275.00,
    )

    reservation2 = Reservation(
        Id=2,
        AccountId=2,
        CarTypeId=2,
        PickUpTime=datetime.strptime("2024-12-22 10:00:00", "%Y-%m-%d %H:%M:%S"),  # Convert string to datetime
        DropOffTime=datetime.strptime("2024-12-27 10:00:00", "%Y-%m-%d %H:%M:%S"),  # Convert string to datetime
        PickUpLocationId=2,
        DropOffLocationId=1,
        RentalPricePerDay=45.00,
        InsurancePlanPricePerDay=4.00,
        TotalPrice=245.00,
    )

    db.session.add_all([customer1, customer2, company1, company2, 
                        account1, account2, account3, account4, 
                        car_type1, car_type2, branch1, branch2, 
                        reservation1, reservation2])

    db.session.commit()
