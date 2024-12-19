import pandas as pd
from models import db, Reservation, CarType, BranchLocation
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

class RentalPriceEstimator:
    def __init__(self):
        self.model = None

    def train_model(self, reservation_data, car_data, branch_data):
        # Merge datasets to prepare the training data
        df = reservation_data.merge(car_data, left_on='CarTypeId', right_on='TypeId')
        df = df.merge(branch_data, left_on='PickUpLocationId', right_on='Id', suffixes=('', '_PickUp'))
        df = df.rename(columns={'City': 'PickUpCity'})
        df = df.merge(branch_data, left_on='DropOffLocationId', right_on='Id', suffixes=('', '_DropOff'))
        df = df.rename(columns={'City': 'DropOffCity'})

        # Create derived columns
        df['Pick_Up_Day'] = df['PickUpTime'].dt.dayofweek  # Day of the week (0 = Monday)
        df['Pick_Up_Month'] = df['PickUpTime'].dt.month
        df['Drop_Off_Day'] = df['DropOffTime'].dt.dayofweek
        df['Drop_Off_Month'] = df['DropOffTime'].dt.month
        df['Price'] = (
            df['RentalPricePerDay'] * (df['DropOffTime'] - df['PickUpTime']).dt.days
            + df['InsurancePlanPricePerDay'] * (df['DropOffTime'] - df['PickUpTime']).dt.days
        )

        # Select features and target
        data = df[['Brand', 'Model', 'Seats', 'PickUpCity', 'Pick_Up_Day', 'Pick_Up_Month',
                   'Drop_Off_Day', 'Drop_Off_Month', 'CreditScore', 'Price']]
        data = data.rename(columns={
            'Brand': 'Car_Brand',
            'Model': 'Car_Model',
            'PickUpCity': 'Location_City',
            'CreditScore': 'Credit_Score'
        })

        X = data[['Car_Brand', 'Car_Model', 'Seats', 'Location_City', 'Pick_Up_Day', 
                  'Pick_Up_Month', 'Drop_Off_Day', 'Drop_Off_Month', 'Credit_Score']]
        y = data['Price']

        # Preprocessing
        categorical_features = ['Car_Brand', 'Car_Model', 'Location_City']
        numerical_features = ['Seats', 'Pick_Up_Day', 'Pick_Up_Month', 'Drop_Off_Day', 
                              'Drop_Off_Month', 'Credit_Score']

        preprocessor = ColumnTransformer(
            transformers=[
                ('cat', OneHotEncoder(), categorical_features),
                ('num', 'passthrough', numerical_features)
            ]
        )

        # Build the pipeline
        self.model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', LinearRegression())
        ])

        # Train the model
        self.model.fit(X, y)

    def estimate_price(self, car_brand, car_model, seats, location_city, 
                       pick_up_day, pick_up_month, drop_off_day, drop_off_month, credit_score):
        """Estimate the rental price based on input features."""
        if not self.model:
            raise ValueError("Model has not been trained yet.")

        input_data = pd.DataFrame([{
            'Car_Brand': car_brand,
            'Car_Model': car_model,
            'Seats': seats,
            'Location_City': location_city,
            'Pick_Up_Day': pick_up_day,
            'Pick_Up_Month': pick_up_month,
            'Drop_Off_Day': drop_off_day,
            'Drop_Off_Month': drop_off_month,
            'Credit_Score': credit_score
        }])
        
        estimated_price = self.model.predict(input_data)[0]
        return round(estimated_price, 2)


reservation_data = pd.read_sql(Reservation.query.statement, db.engine)
car_data = pd.read_sql(CarType.query.statement, db.engine)
branch_data = pd.read_sql(BranchLocation.query.statement, db.engine)

estimator = RentalPriceEstimator()
estimator.train_model(reservation_data, car_data, branch_data)

joblib.dump(estimator, 'rental_price_model.pkl')
