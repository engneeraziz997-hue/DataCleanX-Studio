import pandas as pd
import numpy as np

def generate_sample_sales_data(num_rows: int = 150) -> pd.DataFrame:
    """
    Generates a realistic, intentionally messy sample dataset for testing data cleaning and analysis tools.
    Includes:
    - Missing values (NaN)
    - Duplicate rows
    - Text formatting issues (extra spaces, mixed casing)
    - Outlier values
    - Date columns
    """
    np.random.seed(42)
    
    cities = [' Riyadh ', 'Jeddah', ' Dammam', 'MECCA', 'medina ', 'Riyadh', 'Jeddah ']
    categories = ['Electronics', 'Furniture', 'Clothing', '  Electronics ', 'Toys', 'Clothing']
    payment_methods = ['Credit Card', 'Cash', 'Apple Pay', 'STC Pay', None, 'Credit Card']
    
    dates = pd.date_range(start='2024-01-01', periods=num_rows, freq='D')
    
    data = {
        'Transaction_ID': [f'TXN-{1000 + i}' for i in range(num_rows)],
        'Date': np.random.choice(dates, size=num_rows),
        'Customer_Name': [f'  Customer_{i % 30} ' for i in range(num_rows)],
        'City': np.random.choice(cities, size=num_rows),
        'Product_Category': np.random.choice(categories, size=num_rows),
        'Quantity': np.random.randint(1, 15, size=num_rows).astype(float),
        'Unit_Price': np.round(np.random.uniform(20.0, 500.0, size=num_rows), 2),
        'Total_Amount': np.zeros(num_rows),
        'Payment_Method': np.random.choice(payment_methods, size=num_rows),
        'Customer_Rating': np.random.choice([1.0, 2.0, 3.0, 4.0, 5.0, np.nan], size=num_rows, p=[0.1, 0.1, 0.2, 0.3, 0.2, 0.1])
    }
    
    df = pd.DataFrame(data)
    
    # Calculate Total_Amount with intentional errors
    df['Total_Amount'] = df['Quantity'] * df['Unit_Price']
    
    # Inject missing values (NaNs)
    df.loc[df.sample(frac=0.1, random_state=1).index, 'Quantity'] = np.nan
    df.loc[df.sample(frac=0.1, random_state=2).index, 'City'] = np.nan
    df.loc[df.sample(frac=0.08, random_state=3).index, 'Total_Amount'] = np.nan
    
    # Inject Outliers
    df.loc[5, 'Total_Amount'] = 45000.0  # Extreme outlier
    df.loc[22, 'Quantity'] = 250.0       # Extreme quantity
    
    # Inject Duplicates (duplicate 5 rows)
    dup_rows = df.iloc[:5].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)
    
    return df
