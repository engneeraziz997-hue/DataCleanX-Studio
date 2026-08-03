import sys
import os
import pandas as pd
import numpy as np

# Ensure root directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_data_loader():
    print("Testing modules/data_loader.py...")
    from modules.data_loader import load_data_file, get_excel_sheet_names, sanitize_filename
    
    assert sanitize_filename("test/file@name.csv") == "test_file_name.csv"
    
    # Test CSV Loading
    csv_bytes = "a,b,c\n1,2,3\n4,5,6".encode('utf-8')
    df, err = load_data_file(csv_bytes, "test.csv")
    assert err is None
    assert df is not None
    assert len(df) == 2
    assert list(df.columns) == ['a', 'b', 'c']
    print("  [PASSED] Data Loader Module")

def test_cleaner():
    print("Testing modules/cleaner.py...")
    from modules.cleaner import (
        handle_missing_values, smart_auto_impute, group_by_impute,
        create_calculated_column, extract_datetime_features, remove_duplicates,
        clean_text_column, convert_column_types, detect_and_handle_outliers
    )
    
    df = pd.DataFrame({
        'num': [1.0, 2.0, np.nan, 4.0, 100.0],
        'cat': ['A', 'A', 'B', np.nan, 'A'],
        'txt': ['  hello ', 'WORLD ', 'test', 'clean', '  text  '],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
    })
    
    # Test Imputation
    df_imputed = handle_missing_values(df, ['num'], 'median')
    assert df_imputed['num'].isnull().sum() == 0
    assert df_imputed['num'].iloc[2] == 3.0
    
    # Test Smart Auto Impute
    df_auto, count = smart_auto_impute(df)
    assert df_auto.isnull().sum().sum() == 0
    
    # Test Group-by Impute
    df_grp = group_by_impute(df, 'num', 'cat', 'median')
    assert df_grp['num'].isnull().sum() == 0
    
    # Test Feature Engineering
    df_calc, err = create_calculated_column(df, 'num_double', 'num', 'num', 'multiply')
    assert err is None
    assert 'num_double' in df_calc.columns
    
    df_dt, added = extract_datetime_features(df, 'date')
    assert len(added) == 5
    
    # Test Text Clean
    df_txt = clean_text_column(df, 'txt', strip_whitespace=True, case_change='lower')
    assert df_txt['txt'].iloc[0] == 'hello'
    
    # Test Outliers
    df_out, count_out = detect_and_handle_outliers(df, 'num', method='iqr', threshold=1.5, action='clip')
    assert count_out == 1
    
    print("  [PASSED] Cleaner Module & Feature Engineering")

def test_analyzer():
    print("Testing modules/analyzer.py...")
    from modules.analyzer import (
        get_dataset_metrics, get_data_dictionary, get_numerical_summary,
        get_categorical_summary, get_correlation_matrix, generate_data_health_insights
    )
    
    df = pd.DataFrame({
        'val1': [10, 20, 30, 40, 50],
        'val2': [5, 15, 25, 35, 45],
        'cat': ['X', 'Y', 'X', 'Y', 'Z']
    })
    
    metrics = get_dataset_metrics(df)
    assert metrics['rows'] == 5
    assert metrics['cols'] == 3
    
    data_dict = get_data_dictionary(df)
    assert len(data_dict) == 3
    
    num_sum = get_numerical_summary(df)
    assert len(num_sum) == 2
    
    corr = get_correlation_matrix(df)
    assert corr.shape == (2, 2)
    
    insights = generate_data_health_insights(df)
    assert len(insights) > 0
    
    print("  [PASSED] Analyzer & EDA Module")

def test_visualizer():
    print("Testing modules/visualizer.py...")
    from modules.visualizer import (
        plot_missing_comparison, plot_bar_chart, plot_line_chart, plot_area_chart,
        plot_scatter_chart, plot_pie_chart, plot_treemap, plot_sunburst,
        plot_histogram, plot_box_chart, plot_correlation_heatmap, plot_scatter_matrix,
        create_dashboard_2x2
    )
    
    df = pd.DataFrame({
        'city': ['Riyadh', 'Jeddah', 'Dammam', 'Riyadh'],
        'amount': [100, 200, 150, 300],
        'qty': [1, 2, 3, 4]
    })
    
    fig_bar = plot_bar_chart(df, 'city', 'amount')
    assert fig_bar is not None
    
    fig_dash = create_dashboard_2x2(df, 'city', 'amount')
    assert fig_dash is not None
    
    print("  [PASSED] Visualizer & Dashboard Module")

def test_exporter():
    print("Testing modules/exporter.py...")
    from modules.exporter import export_to_excel_buffer, export_to_csv_buffer, export_to_json_buffer
    
    df = pd.DataFrame({'a': [1, 2], 'b': ['=SUM(1,2)', 'hello']})
    
    excel_buf = export_to_excel_buffer({'sheet1': df})
    assert len(excel_buf) > 0
    
    csv_buf = export_to_csv_buffer(df)
    assert len(csv_buf) > 0
    
    json_buf = export_to_json_buffer(df)
    assert len(json_buf) > 0
    
    print("  [PASSED] Exporter Module")

if __name__ == "__main__":
    print("=== STARTING SDLC AUTOMATED TEST SUITE ===")
    test_data_loader()
    test_cleaner()
    test_analyzer()
    test_visualizer()
    test_exporter()
    print("=== ALL TEST SUITES PASSED CLEANLY (100% SUCCESS) ===")
