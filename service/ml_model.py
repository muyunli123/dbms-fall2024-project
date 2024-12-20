import pandas as pd
# from models import db, Reservation, CarType, BranchLocation
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import numpy as np



from service.db_utils import get_db_connection

# load data
conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT * FROM branch")
branch_data = cursor.fetchall()

cursor.execute("SELECT * FROM reservation")
reservation_data = cursor.fetchall()

cursor.execute("SELECT * FROM car_type")
car_data = cursor.fetchall()

cursor.execute("SELECT * FROM account")
account_data = cursor.fetchall()

cursor.execute("SELECT * FROM customer")
customer_data = cursor.fetchall()

# train model
class RentalPriceEstimator:
    def __init__(self):
        self.model = None

    def train_model(self, reservation_data, car_data, branch_data, account_data, customer_data):
        # Merge datasets to prepare the training data
        df = reservation_data.merge(car_data, left_on='cartypeid', right_on='typeid')
        df = df.merge(branch_data, left_on='pickuplocationid', right_on='id', suffixes=('', '_pickup'))
        df = df.rename(columns={'city': 'pickupcity'})
        df = df.merge(branch_data, left_on='dropofflocationid', right_on='id', suffixes=('', '_dropoff'))
        df = df.rename(columns={'city': 'dropoffcity'})
        df = df.merge(account_data, left_on='accountid', right_on='id')
        df = df.merge(customer_data, left_on='memberid', right_on='memberid')
        df['pickuptime'] = pd.to_datetime(df['pickuptime'])
        df['dropofftime'] = pd.to_datetime(df['dropofftime'])
        # Create derived columns
        df['pick_up_day'] = df['pickuptime'].dt.dayofweek  # Day of the week (0 = Monday)
        df['pick_up_month'] = df['pickuptime'].dt.month
        df['drop_off_day'] = df['dropofftime'].dt.dayofweek
        df['drop_off_month'] = df['dropofftime'].dt.month
        df['price'] = (
            df['rentalpriceperday'] * (df['dropofftime'] - df['pickuptime']).dt.days
            + df['insuranceplanpriceperday'] * (df['dropofftime'] - df['pickuptime']).dt.days
        )
        
        df['creditscore'] = np.random.randint(300, 851, size=len(df))
        
        # Select features and target
        data = df[['brand', 'model', 'seats', 'pickupcity', 'pick_up_day', 'pick_up_month',
                'drop_off_day', 'drop_off_month', 'creditscore', 'price']]

        # np.random.seed(42) 
        # num_rows = 100

        # Create sample data
        # data = pd.DataFrame({
        #     'brand': np.random.choice(['Toyota', 'Honda', 'Ford', 'BMW', 'Audi'], num_rows),
        #     'model': np.random.choice(['Corolla', 'Civic', 'Focus', 'X5', 'A4'], num_rows),
        #     'seats': np.random.randint(2, 8, num_rows),  # Random number of seats between 2 and 7
        #     'pickupcity': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami'], num_rows),
        #     'pick_up_day': np.random.randint(0, 7, num_rows),  # Day of the week (0 = Monday)
        #     'pick_up_month': np.random.randint(1, 13, num_rows),  # Month (1 to 12)
        #     'drop_off_day': np.random.randint(0, 7, num_rows),  # Day of the week (0 = Monday)
        #     'drop_off_month': np.random.randint(1, 13, num_rows),  # Month (1 to 12)
        #     'credit_score': np.random.randint(300, 851, num_rows),  # Credit score between 300 and 850
        #     'price': np.random.uniform(50, 500, num_rows)  # Rental price between $50 and $500
        # })

        # Missing values
        data = data.dropna(subset=['brand', 'model', 'pickupcity', 'pick_up_day', 'pick_up_month',
                                'drop_off_day', 'drop_off_month'])
        mean_credit = data['credit_score'].mean()
        data['credit_score'].fillna(value=mean_credit, inplace=True)
        mean_price = data['price'].mean()
        data['price'].fillna(value=mean_price, inplace=True)
        mean_seats = data['seats'].mean()
        data['seats'].fillna(value=mean_seats, inplace=True)

        X = data[['brand', 'model', 'seats', 'pickupcity', 'pick_up_day', 
                'pick_up_month', 'drop_off_day', 'drop_off_month', 'credit_score']]
        y = data['price']

        # Preprocessing
        categorical_features = ['brand', 'model', 'pickupcity']
        numerical_features = ['seats', 'pick_up_day', 'pick_up_month', 'drop_off_day', 
                            'drop_off_month', 'credit_score']

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
            'brand': brand,
            'model': model,
            'seats': seats,
            'pickupcity': pickupcity,
            'pick_up_day': pick_up_day,
            'pick_up_month': pick_up_month,
            'drop_off_day': drop_off_day,
            'drop_off_month': drop_off_month,
            'credit_score': credit_score
        }])
        
        estimated_price = self.model.predict(input_data)[0]
        return round(estimated_price, 2)



# reservation_data = pd.read_sql(Reservation.query.statement, db.engine)
# car_data = pd.read_sql(CarType.query.statement, db.engine)
# branch_data = pd.read_sql(BranchLocation.query.statement, db.engine)

# reservation_data = pd.read_csv("service/reservation.csv")
# car_data = pd.read_csv("service/car_type.csv")
# branch_data = pd.read_csv("service/branch.csv")
# customer_data = pd.read_csv("service/customer.csv")
# account_data = pd.read_csv("service/account.csv")
estimator = RentalPriceEstimator()
estimator.train_model(reservation_data, car_data, branch_data, account_data, customer_data)

joblib.dump(estimator, 'rental_price_model.pkl')
