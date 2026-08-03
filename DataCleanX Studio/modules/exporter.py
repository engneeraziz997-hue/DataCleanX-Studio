import pandas as pd
import io
from typing import Dict, Optional
from modules.data_loader import sanitize_formula_injection

def export_to_excel_buffer(
    dataframes: Dict[str, pd.DataFrame], 
    include_summary_sheet: bool = True
) -> bytes:
    """
    Exports dictionary of DataFrames to a styled, security-sanitized Excel file binary buffer.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'vcenter',
            'align': 'center',
            'fg_color': '#4F46E5',
            'font_color': '#FFFFFF',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'valign': 'vcenter',
            'align': 'center',
            'border': 1
        })

        for sheet_name, df in dataframes.items():
            # Security: Sanitize formulas to prevent Excel Formula Injection attacks
            safe_df = sanitize_formula_injection(df)
            clean_sheet_name = str(sheet_name)[:30]
            safe_df.to_excel(writer, sheet_name=clean_sheet_name, index=False)
            worksheet = writer.sheets[clean_sheet_name]
            
            for col_num, col_name in enumerate(safe_df.columns):
                worksheet.write(0, col_num, col_name, header_format)
                max_len = max(
                    safe_df[col_name].astype(str).map(len).max() if not safe_df[col_name].empty else 10,
                    len(str(col_name))
                ) + 3
                worksheet.set_column(col_num, col_num, min(max_len, 40), cell_format)

    return output.getvalue()

def export_to_csv_buffer(df: pd.DataFrame) -> bytes:
    """Exports DataFrame to CSV with utf-8-sig encoding and formula injection protection."""
    safe_df = sanitize_formula_injection(df)
    return safe_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

def export_to_json_buffer(df: pd.DataFrame) -> bytes:
    """Exports DataFrame to JSON formatted string."""
    safe_df = sanitize_formula_injection(df)
    return safe_df.to_json(orient='records', force_ascii=False, indent=2).encode('utf-8')
