import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a summary dataframe of missing values per column."""
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df)) * 100
    summary = pd.DataFrame({
        'إجمالي القيم المفقودة': missing_count,
        'النسبة المئوية (%)': missing_pct.round(2)
    })
    return summary[summary['إجمالي القيم المفقودة'] > 0].sort_values(by='إجمالي القيم المفقودة', ascending=False)

def handle_missing_values(
    df: pd.DataFrame, 
    columns: List[str], 
    strategy: str, 
    fill_value: Any = None
) -> pd.DataFrame:
    df_clean = df.copy()
    
    if strategy == 'drop_rows':
        df_clean = df_clean.dropna(subset=columns)
    elif strategy == 'drop_cols':
        df_clean = df_clean.drop(columns=columns)
    else:
        for col in columns:
            if col not in df_clean.columns:
                continue
            if strategy == 'mean' and pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
            elif strategy == 'median' and pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            elif strategy == 'mode':
                mode_val = df_clean[col].mode()
                if not mode_val.empty:
                    df_clean[col] = df_clean[col].fillna(mode_val[0])
            elif strategy == 'constant':
                df_clean[col] = df_clean[col].fillna(fill_value)
            elif strategy == 'ffill':
                df_clean[col] = df_clean[col].ffill()
            elif strategy == 'bfill':
                df_clean[col] = df_clean[col].bfill()
            elif strategy == 'interpolate' and pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].interpolate(method='linear')
                
    return df_clean

def smart_auto_impute(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """Smart 1-click Auto Imputer."""
    df_clean = df.copy()
    total_missing_before = df_clean.isnull().sum().sum()
    
    for col in df_clean.columns:
        if df_clean[col].isnull().sum() == 0:
            continue
        if pd.api.types.is_numeric_dtype(df_clean[col]):
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val if not pd.isna(median_val) else 0)
        else:
            mode_val = df_clean[col].mode()
            if not mode_val.empty:
                df_clean[col] = df_clean[col].fillna(mode_val[0])
            else:
                df_clean[col] = df_clean[col].fillna("غير محدد")
                
    total_missing_after = df_clean.isnull().sum().sum()
    filled_count = total_missing_before - total_missing_after
    return df_clean, filled_count

def group_by_impute(
    df: pd.DataFrame, 
    target_col: str, 
    group_col: str, 
    strategy: str = 'median'
) -> pd.DataFrame:
    """Fills missing values in target_col based on group statistics of group_col."""
    df_clean = df.copy()
    if target_col not in df_clean.columns or group_col not in df_clean.columns:
        return df_clean
    
    if strategy == 'mean':
        df_clean[target_col] = df_clean.groupby(group_col)[target_col].transform(lambda x: x.fillna(x.mean()))
    elif strategy == 'median':
        df_clean[target_col] = df_clean.groupby(group_col)[target_col].transform(lambda x: x.fillna(x.median()))
        
    if pd.api.types.is_numeric_dtype(df_clean[target_col]):
        df_clean[target_col] = df_clean[target_col].fillna(df_clean[target_col].median())
        
    return df_clean

def create_calculated_column(
    df: pd.DataFrame,
    new_col_name: str,
    col1: str,
    col2: str,
    operation: str # 'add', 'subtract', 'multiply', 'divide'
) -> Tuple[pd.DataFrame, Optional[str]]:
    """Creates a new feature column by performing mathematical operations on two columns."""
    df_clean = df.copy()
    try:
        s1 = pd.to_numeric(df_clean[col1], errors='coerce')
        s2 = pd.to_numeric(df_clean[col2], errors='coerce')
        
        if operation == 'add':
            df_clean[new_col_name] = s1 + s2
        elif operation == 'subtract':
            df_clean[new_col_name] = s1 - s2
        elif operation == 'multiply':
            df_clean[new_col_name] = s1 * s2
        elif operation == 'divide':
            df_clean[new_col_name] = np.where(s2 != 0, s1 / s2, np.nan)
            
        return df_clean, None
    except Exception as e:
        return df_clean, str(e)

def extract_datetime_features(df: pd.DataFrame, date_col: str) -> Tuple[pd.DataFrame, List[str]]:
    """Extracts Year, Month, Day, Day of Week, Quarter from date column."""
    df_clean = df.copy()
    new_cols = []
    try:
        dt_series = pd.to_datetime(df_clean[date_col], errors='coerce')
        
        y_col = f"{date_col}_السنة"
        m_col = f"{date_col}_الشهر"
        d_col = f"{date_col}_اليوم"
        w_col = f"{date_col}_يوم_الأسبوع"
        q_col = f"{date_col}_الربع"
        
        df_clean[y_col] = dt_series.dt.year
        df_clean[m_col] = dt_series.dt.month
        df_clean[d_col] = dt_series.dt.day
        df_clean[w_col] = dt_series.dt.day_name(locale='ar')
        df_clean[q_col] = dt_series.dt.quarter
        
        new_cols = [y_col, m_col, d_col, w_col, q_col]
        return df_clean, new_cols
    except Exception as e:
        return df_clean, []

def remove_duplicates(
    df: pd.DataFrame, 
    subset_cols: Optional[List[str]] = None, 
    keep: str = 'first'
) -> Tuple[pd.DataFrame, int]:
    df_clean = df.copy()
    initial_rows = len(df_clean)
    cols = subset_cols if subset_cols and len(subset_cols) > 0 else None
    df_clean = df_clean.drop_duplicates(subset=cols, keep=keep)
    removed_count = initial_rows - len(df_clean)
    return df_clean, removed_count

def clean_text_column(
    df: pd.DataFrame,
    col: str,
    strip_whitespace: bool = True,
    case_change: Optional[str] = None,
    remove_special_chars: bool = False,
    find_str: Optional[str] = None,
    replace_str: Optional[str] = None
) -> pd.DataFrame:
    df_clean = df.copy()
    if col not in df_clean.columns:
        return df_clean
    
    series = df_clean[col].astype(str)
    
    if strip_whitespace:
        series = series.str.strip()
        
    if case_change == 'lower':
        series = series.str.lower()
    elif case_change == 'upper':
        series = series.str.upper()
    elif case_change == 'title':
        series = series.str.title()
        
    if remove_special_chars:
        series = series.str.replace(r'[^\w\s]', '', regex=True)
        
    if find_str is not None and replace_str is not None and find_str != '':
        series = series.str.replace(find_str, replace_str, regex=False)
        
    df_clean[col] = series
    return df_clean

def convert_column_types(
    df: pd.DataFrame, 
    conversions: Dict[str, str]
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    df_clean = df.copy()
    status = {}
    
    for col, target_type in conversions.items():
        if col not in df_clean.columns:
            continue
        try:
            if target_type == 'numeric':
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                status[col] = "تم التحويل إلى رقم بنجاح"
            elif target_type == 'datetime':
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                status[col] = "تم التحويل إلى تاريخ بنجاح"
            elif target_type == 'string':
                df_clean[col] = df_clean[col].astype(str)
                status[col] = "تم التحويل إلى نص بنجاح"
            elif target_type == 'category':
                df_clean[col] = df_clean[col].astype('category')
                status[col] = "تم التحويل إلى فئة (Category) بنجاح"
        except Exception as e:
            status[col] = f"فشل التحويل: {str(e)}"
            
    return df_clean, status

def detect_and_handle_outliers(
    df: pd.DataFrame,
    col: str,
    method: str = 'iqr',
    threshold: float = 1.5,
    action: str = 'clip'
) -> Tuple[pd.DataFrame, int]:
    df_clean = df.copy()
    if col not in df_clean.columns or not pd.api.types.is_numeric_dtype(df_clean[col]):
        return df_clean, 0
    
    series = df_clean[col].dropna()
    outlier_mask = pd.Series(False, index=df_clean.index)
    
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outlier_mask = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
    elif method == 'zscore':
        mean = series.mean()
        std = series.std()
        if std != 0:
            z_scores = (df_clean[col] - mean) / std
            outlier_mask = z_scores.abs() > threshold
            lower_bound = mean - threshold * std
            upper_bound = mean + threshold * std
            
    outliers_count = int(outlier_mask.sum())
    
    if outliers_count > 0:
        if action == 'drop':
            df_clean = df_clean[~outlier_mask]
        elif action == 'clip' and method == 'iqr':
            df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
            
    return df_clean, outliers_count
