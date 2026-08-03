import pandas as pd
import numpy as np
from typing import Dict, Any, List

def get_dataset_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculates overall metrics for the dataset."""
    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols
    total_missing = df.isnull().sum().sum()
    missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
    duplicate_rows = df.duplicated().sum()
    memory_usage_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    return {
        "rows": total_rows,
        "cols": total_cols,
        "cells": total_cells,
        "missing_cells": total_missing,
        "missing_pct": round(missing_pct, 2),
        "duplicates": duplicate_rows,
        "memory_mb": round(memory_usage_mb, 2)
    }

def get_data_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    """Generates a detailed summary dictionary of all columns."""
    records = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].count()
        missing = df[col].isnull().sum()
        missing_pct = round((missing / len(df)) * 100, 2)
        unique_vals = df[col].nunique(dropna=True)
        sample_val = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else "N/A"
        
        records.append({
            "اسم العمود": col,
            "نوع البيانات": dtype,
            "القيم المملوءة": non_null,
            "القيم المفقودة": missing,
            "نسبة النقص (%)": missing_pct,
            "القيم الفريدة": unique_vals,
            "عينة بيانات": sample_val[:30]
        })
    return pd.DataFrame(records)

def get_numerical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns detailed statistics for numerical columns."""
    num_df = df.select_dtypes(include=[np.number])
    if num_df.empty:
        return pd.DataFrame()
    
    summary = num_df.describe().T
    summary['skewness'] = num_df.skew().round(2)
    summary['variance'] = num_df.var().round(2)
    summary = summary.round(2)
    summary.rename(columns={
        'count': 'العدد',
        'mean': 'المتوسط',
        'std': 'الانحراف المعياري',
        'min': 'أدنى قيمة',
        '25%': 'الربيع الأول (25%)',
        '50%': 'الوسيط (50%)',
        '75%': 'الربيع الثالث (75%)',
        'max': 'أعلى قيمة',
        'skewness': 'الالتواء',
        'variance': 'التباين'
    }, inplace=True)
    return summary

def get_categorical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns top value counts for categorical and string columns."""
    cat_cols = df.select_dtypes(include=['object', 'category', 'string']).columns
    if len(cat_cols) == 0:
        return pd.DataFrame()
    
    records = []
    for col in cat_cols:
        val_counts = df[col].value_counts(dropna=True)
        top_val = val_counts.index[0] if not val_counts.empty else "N/A"
        top_freq = val_counts.iloc[0] if not val_counts.empty else 0
        top_pct = round((top_freq / len(df)) * 100, 2) if len(df) > 0 else 0
        
        records.append({
            "العمود": col,
            "القيم الفريدة": df[col].nunique(),
            "الأكثر تكراراً": str(top_val),
            "عدد التكرار": top_freq,
            "نسبة التكرار (%)": top_pct
        })
    return pd.DataFrame(records)

def get_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Computes correlation matrix for numeric features."""
    num_df = df.select_dtypes(include=[np.number])
    if num_df.shape[1] < 2:
        return pd.DataFrame()
    return num_df.corr().round(3)

def generate_data_health_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Generates automated insights and recommendations regarding data health."""
    insights = []
    total_rows = len(df)
    
    # 1. Check Missing values
    for col in df.columns:
        null_cnt = df[col].isnull().sum()
        pct = (null_cnt / total_rows) * 100
        if pct > 30:
            insights.append({
                "type": "warning",
                "title": f"نسبة فقدان عالية في العمود '{col}'",
                "detail": f"يحتوي العمود على {null_cnt} قيمة مفقودة بنسبة ({pct:.1f}%). يُوصى بنظر إمكانية حذف العمود أو التعبئة."
            })
            
    # 2. Check Duplicates
    dup_cnt = df.duplicated().sum()
    if dup_cnt > 0:
        insights.append({
            "type": "warning",
            "title": f"صفوف مكررة ({dup_cnt} صف)",
            "detail": f"تم كشف {dup_cnt} صف مكرر بالكامل في الجدول. استخدم جناح التنظيف لحذف التكرارات."
        })
        
    # 3. Check constant columns
    for col in df.columns:
        if df[col].nunique(dropna=False) == 1:
            insights.append({
                "type": "info",
                "title": f"عمود ثابت القيمة '{col}'",
                "detail": f"يحتوي العمود '{col}' على قيمة واحدة فقط لكافة الصفوف. قد لا يقدم قيمة تحليلية."
            })
            
    # 4. Check high cardinality text
    for col in df.select_dtypes(include=['object', 'string']).columns:
        unique_cnt = df[col].nunique()
        if unique_cnt > total_rows * 0.9 and total_rows > 20:
            insights.append({
                "type": "info",
                "title": f"عمود معرف فريد '{col}'",
                "detail": f"يحتوي العمود على {unique_cnt} قيمة فريدة من أصل {total_rows}. يعتبر غالباً معرفاً (ID)."
            })
            
    if not insights:
        insights.append({
            "type": "success",
            "title": "جودة بيانات عالية!",
            "detail": "لم يتم كشف أي مشاكل حادة في هيكل البيانات أو القيم المفقودة والتكرار."
        })
        
    return insights
