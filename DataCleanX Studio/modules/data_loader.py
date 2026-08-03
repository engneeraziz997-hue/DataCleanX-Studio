import pandas as pd
import io
import re
from typing import Tuple, List, Optional

# Security: Maximum allowed file size (50 MB) to prevent Denial of Service (Memory Exhaustion)
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024

def sanitize_filename(filename: str) -> str:
    """Sanitizes filename to prevent directory traversal and injection attacks."""
    clean_name = re.sub(r'[^\w\s\.-]', '_', filename)
    return clean_name[:100]

def sanitize_formula_injection(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prevents CSV/Excel Formula Injection attacks by stripping or escaping
    leading characters: '=', '+', '-', '@', '\t', '\r' in string columns.
    """
    df_clean = df.copy()
    for col in df_clean.select_dtypes(include=['object', 'string']).columns:
        df_clean[col] = df_clean[col].astype(str).apply(
            lambda val: f"'{val}" if val.startswith(('=', '+', '-', '@', '\t', '\r')) else val
        )
    return df_clean

def get_excel_sheet_names(file_bytes: bytes) -> List[str]:
    """Retrieves sheet names safely from an Excel file binary stream."""
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return []
    try:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        return excel_file.sheet_names
    except Exception:
        return []

def load_data_file(
    file_bytes: bytes, 
    filename: str, 
    sheet_name: Optional[str] = None
) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Parses file bytes safely into a Pandas DataFrame with security checks and memory optimizations.
    Returns (DataFrame, error_message).
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = round(len(file_bytes) / (1024 * 1024), 2)
        return None, f"⚠️ حظر أمني: حجم الملف ({size_mb} MB) يتجاوز الحد الأقصى المسموح به (50 MB)."

    filename_clean = sanitize_filename(filename)
    filename_lower = filename_clean.lower()
    
    try:
        if filename_lower.endswith(('.xlsx', '.xls')):
            buffer = io.BytesIO(file_bytes)
            if sheet_name:
                df = pd.read_excel(buffer, sheet_name=sheet_name)
            else:
                df = pd.read_excel(buffer)
            return df, None
        
        elif filename_lower.endswith('.csv'):
            for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1256']:
                try:
                    df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding)
                    return df, None
                except (UnicodeDecodeError, Exception):
                    continue
            return None, "فشل فك ترميز ملف CSV. يرجى التأكد من حفظ الملف بترميز UTF-8."
            
        elif filename_lower.endswith('.tsv'):
            df = pd.read_csv(io.BytesIO(file_bytes), sep='\t')
            return df, None
            
        elif filename_lower.endswith('.json'):
            df = pd.read_json(io.BytesIO(file_bytes))
            return df, None
            
        elif filename_lower.endswith('.parquet'):
            df = pd.read_parquet(io.BytesIO(file_bytes))
            return df, None
            
        else:
            return None, f"صيغة الملف غير مدعومة: {filename_clean}"
            
    except Exception as e:
        return None, f"حدث خطأ آمن أثناء قراءة الملف: {str(e)}"
