import streamlit as st
import pandas as pd
import numpy as np

from modules.sample_data import generate_sample_sales_data
from modules.data_loader import load_data_file, get_excel_sheet_names
from modules.cleaner import (
    get_missing_summary, 
    handle_missing_values, 
    smart_auto_impute,
    group_by_impute,
    create_calculated_column,
    extract_datetime_features,
    remove_duplicates, 
    clean_text_column, 
    convert_column_types, 
    detect_and_handle_outliers
)
from modules.analyzer import (
    get_dataset_metrics, 
    get_data_dictionary, 
    get_numerical_summary, 
    get_categorical_summary, 
    get_correlation_matrix, 
    generate_data_health_insights
)
from modules.visualizer import (
    PALETTES,
    plot_missing_comparison,
    plot_bar_chart, 
    plot_line_chart, 
    plot_area_chart,
    plot_scatter_chart, 
    plot_pie_chart, 
    plot_treemap,
    plot_sunburst,
    plot_histogram, 
    plot_box_chart, 
    plot_correlation_heatmap,
    plot_scatter_matrix,
    create_dashboard_2x2
)
from modules.exporter import (
    export_to_excel_buffer, 
    export_to_csv_buffer, 
    export_to_json_buffer
)

# ---------------------------------------------------------
# Page Config & Responsive UI Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="DataCleanX Studio | المنصة الآمنة عالية الأداء لتنظيف وتحليل البيانات",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Responsive & Secure Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
    
    html, body, [class*="css"], div, span, h1, h2, h3, h4, h5, h6 {
        font-family: 'Tajawal', sans-serif !important;
    }
    
    /* Responsive Grid Layouts */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #EC4899;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #818CF8, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 5px;
    }
    .metric-label {
        font-size: 14px;
        color: #94A3B8;
        font-weight: 500;
    }
    
    .main-header {
        background: linear-gradient(90deg, #818CF8, #EC4899, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.3rem;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }
    
    .log-item {
        background-color: #1E293B;
        border-right: 4px solid #6366F1;
        padding: 10px 15px;
        margin-bottom: 8px;
        border-radius: 6px;
        font-size: 14px;
    }

    /* Media Queries for Mobile Responsiveness */
    @media (max-width: 768px) {
        .main-header { font-size: 1.7rem !important; }
        .sub-header { font-size: 0.9rem !important; }
        .metric-card { padding: 12px !important; margin-bottom: 10px; }
        .metric-value { font-size: 20px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Caching Heavy Computations for Maximum Performance
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_metrics(df_data: pd.DataFrame):
    return get_dataset_metrics(df_data)

@st.cache_data(show_spinner=False)
def cached_data_dictionary(df_data: pd.DataFrame):
    return get_data_dictionary(df_data)

@st.cache_data(show_spinner=False)
def cached_numerical_summary(df_data: pd.DataFrame):
    return get_numerical_summary(df_data)

@st.cache_data(show_spinner=False)
def cached_correlation_matrix(df_data: pd.DataFrame):
    return get_correlation_matrix(df_data)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if 'raw_df' not in st.session_state:
    st.session_state['raw_df'] = None
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'file_name' not in st.session_state:
    st.session_state['file_name'] = "لم يتم اختيار ملف"
if 'audit_log' not in st.session_state:
    st.session_state['audit_log'] = []

def log_action(action_desc: str):
    st.session_state['audit_log'].append(action_desc)

# ---------------------------------------------------------
# Sidebar Component
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚡ **DataCleanX Studio**")
    st.caption("منصة عالية الأداء وآمنة لتنظيف وتحليل البيانات")
    st.markdown("---")
    
    menu_option = st.radio(
        "📌 **انتقل إلى القسم:**",
        [
            "🏠 الرئيسية واستيراد البيانات",
            "🧹 جناح تنظيف وتعويض البيانات",
            "📊 التقييم البصري (قبل/بعد التنظيف)",
            "📊 التحليل الإحصائي (EDA)",
            "📈 الرسوم والمخططات الملونة",
            "📱 لوحة القيادة (2x2 Dashboard)",
            "⚙️ الهندسة واستخراج الخصائص",
            "🔀 التحويل والجداول المحورية",
            "📥 تصدير النتائج والتقارير"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 🎨 **نسق الألوان والتصميم:**")
    selected_palette = st.selectbox(
        "اختر باليت الألوان للمخططات:",
        list(PALETTES.keys())
    )
    
    st.markdown("---")
    st.markdown("### 📁 **مصدر البيانات (حد أقصى 50 MB)**")
    
    if st.button("✨ تحميل بيانات تجريبية (مبيعات ملوثة)", use_container_width=True):
        sample_df = generate_sample_sales_data(150)
        st.session_state['raw_df'] = sample_df.copy()
        st.session_state['df'] = sample_df.copy()
        st.session_state['file_name'] = "sample_sales_data.xlsx"
        st.session_state['audit_log'] = ["تم تحميل البيانات التجريبية للمبيعات."]
        st.success("تم تحميل البيانات التجريبية بنجاح!")
        st.rerun()
        
    uploaded_file = st.file_uploader(
        "أو قم برفع ملفك الخاّص:", 
        type=["xlsx", "xls", "csv", "tsv", "json", "parquet"]
    )
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        filename = uploaded_file.name
        
        sheet_name = None
        if filename.lower().endswith(('.xlsx', '.xls')):
            sheets = get_excel_sheet_names(file_bytes)
            if len(sheets) > 1:
                sheet_name = st.selectbox("اختر ورقة العمل (Sheet):", sheets)
                
        if st.button("🚀 معالجة وقراءة الملف", use_container_width=True):
            df_loaded, err = load_data_file(file_bytes, filename, sheet_name)
            if err:
                st.error(err)
            else:
                st.session_state['raw_df'] = df_loaded.copy()
                st.session_state['df'] = df_loaded.copy()
                st.session_state['file_name'] = filename
                st.session_state['audit_log'] = [f"تم تحميل الملف '{filename}' بنجاح."]
                st.success(f"تم تحميل {filename} بنجاح!")
                st.rerun()

    if st.session_state['raw_df'] is not None:
        st.markdown("---")
        if st.button("🔄 إعادة تعيين للبيانات الأصلية", use_container_width=True):
            st.session_state['df'] = st.session_state['raw_df'].copy()
            st.session_state['audit_log'].append("تم إلغاء التعديلات وإعادة التعيين إلى الملف الأصلي.")
            st.toast("تم استرجاع البيانات الأصلية بنجاح!")
            st.rerun()

# ---------------------------------------------------------
# Main Page Header
# ---------------------------------------------------------
st.markdown('<div class="main-header">⚡ DataCleanX Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">التطبيق المتجاوب والأمن والسرع لتنظيف، تعويض، وتحليل البيانات وعرضها إحصائياً وبيانياً</div>', unsafe_allow_html=True)

if st.session_state['df'] is None:
    st.info("👈 **مرحباً بك!** يرجى رفع ملف بيانات من القائمة الجانبية أو الضغط على زر **'تحميل بيانات تجريبية'** للبدء فوراً.")
    st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80", caption="المنصة المتكاملة لتحليل وتنظيف البيانات والتصور البصري", use_container_width=True)
    st.stop()

df = st.session_state['df']
raw_df = st.session_state['raw_df']
filename = st.session_state['file_name']

# Cached High-Performance Metrics Computation
metrics = cached_metrics(df)

# =========================================================
# Page 1: Overview & Data Import
# =========================================================
if menu_option == "🏠 الرئيسية واستيراد البيانات":
    st.markdown(f"### 📋 **نظرة عامة على الملف:** `{filename}`")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">عدد الصفوف</div><div class="metric-value">{metrics["rows"]:,}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">عدد الأعمدة</div><div class="metric-value">{metrics["cols"]}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">نسبة المفقود</div><div class="metric-value">{metrics["missing_pct"]}%</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">الصفوف المكررة</div><div class="metric-value">{metrics["duplicates"]}</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-label">حجم الذاكرة</div><div class="metric-value">{metrics["memory_mb"]} MB</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 👁️ **معاينة الجدول الحالي (عرض سريع لأول 100 صف للأداء العالي):**")
    st.dataframe(df.head(100), use_container_width=True, height=400)

# =========================================================
# Page 2: Data Cleaning & Imputation
# =========================================================
elif menu_option == "🧹 جناح تنظيف وتعويض البيانات":
    st.markdown("### 🧹 **جناح تنظيف وتعويض البيانات المفقودة والمعطوبة**")
    
    with st.container():
        sc1, sc2 = st.columns([3, 1])
        with sc1:
            st.markdown("#### ⚡ **التنظيف والتعويض التلقائي الذكي بضغطة زر (Smart 1-Click Auto Clean):**")
            st.caption("يقوم النظام تلقائياً بكشف وتعبئة كافة الأرقام المفقودة بالوسيط الحسابي، والنصوص بالقيم الأكثر تكراراً.")
        with sc2:
            if st.button("🚀 تعويض كل المفقودات تلقائياً", use_container_width=True):
                cleaned_df, count = smart_auto_impute(df)
                st.session_state['df'] = cleaned_df
                log_action(f"تم تعويض {count} قيمة مفقودة تلقائياً بنجاح.")
                st.success(f"تم تعويض {count} قيمة مفقودة بنجاح!")
                st.rerun()
                
    st.markdown("---")
    
    clean_tab1, clean_tab2, clean_tab3, clean_tab4, clean_tab5 = st.tabs([
        "🧩 تعويض القيم المفقودة (Imputation)",
        "👥 التكرارات (Duplicates)",
        "🔤 تنظيف النصوص (Text Normalization)",
        "🔢 تحويل أنواع البيانات (Type Casting)",
        "📈 القيم الشاذة (Outliers)"
    ])
    
    with clean_tab1:
        missing_sum = get_missing_summary(df)
        if missing_sum.empty:
            st.success("🎉 لا توجد أي قيم مفقودة في الجدول الحالي!")
        else:
            st.warning(f"تم كشف قيم مفقودة في {len(missing_sum)} عمود.")
            st.dataframe(missing_sum, use_container_width=True)
            
            st.markdown("#### **1. تعويض القيم المفقودة المباشر:**")
            selected_cols = st.multiselect("اختر الأعمدة المراد معالجتها:", options=df.columns.tolist())
            strategy = st.selectbox(
                "اختر طريقة التعويض / الحذف:",
                [
                    ("median", "تعبئة بالوسيط الحسابي (الخيار الموصى به للأرقام)"),
                    ("mean", "تعبئة بالمتوسط الحسابي"),
                    ("mode", "تعبئة بالقيم الأكثر تكراراً (المنوال)"),
                    ("constant", "تعبئة بقيمة ثابتة محددة"),
                    ("interpolate", "تعبئة بالاستكمال الخطي (Linear Interpolation)"),
                    ("ffill", "تعبئة للأمام (Forward Fill)"),
                    ("bfill", "تعبئة للخلف (Backward Fill)"),
                    ("drop_rows", "حذف الصفوف المفقودة"),
                    ("drop_cols", "حذف العمود بالكامل")
                ],
                format_func=lambda x: x[1]
            )[0]
            
            fill_custom = None
            if strategy == "constant":
                fill_custom = st.text_input("أدخل القيمة الثابتة للتعبئة:", value="غير محدد")
                
            if st.button("✅ تطبيق تعويض القيم المفقودة") and selected_cols:
                st.session_state['df'] = handle_missing_values(df, selected_cols, strategy, fill_custom)
                log_action(f"تم تعويض مفقودات الأعمدة ({', '.join(selected_cols)}) باستخدام {strategy}.")
                st.success("تمت معالجة وتعويض القيم المفقودة بنجاح!")
                st.rerun()

            st.markdown("---")
            st.markdown("#### **2. التعويض الذكي المعتمد على تجميع فئة أخرى (Group-By Imputation):**")
            gc1, gc2, gc3 = st.columns(3)
            with gc1:
                t_col = st.selectbox("العمود المراد تعويض مفقوداته:", df.select_dtypes(include=[np.number]).columns.tolist())
            with gc2:
                g_col = st.selectbox("العمود التجميعي (مثال: المدينة أو الفئة):", df.columns.tolist())
            with gc3:
                g_strat = st.selectbox("طريقة الحساب بالتجميع:", ["median", "mean"], format_func=lambda x: "الوسيط الحسابي للمجموعة" if x == "median" else "المتوسط الحسابي للمجموعة")
                
            if st.button("✨ تنفيذ التعويض المجموعاتي الذكي"):
                st.session_state['df'] = group_by_impute(df, t_col, g_col, g_strat)
                log_action(f"تم تعويض مفقودات العمود '{t_col}' بناءً على تجميع العمود '{g_col}'.")
                st.success("تم التعويض بنجاح!")
                st.rerun()

    with clean_tab2:
        dup_count = df.duplicated().sum()
        st.info(f"عدد الصفوف المكررة بالكامل حالياً: **{dup_count} صف**")
        subset_cols = st.multiselect("اختر أعمدة محددة لفحص التكرار:", options=df.columns.tolist())
        keep_opt = st.selectbox("القيمة المراد الإبقاء عليها:", ["first", "last"], format_func=lambda x: "الصف الأول" if x == "first" else "الصف الأخير")
        if st.button("🗑️ حذف الصفوف المكررة"):
            cleaned_df, removed = remove_duplicates(df, subset_cols, keep_opt)
            st.session_state['df'] = cleaned_df
            log_action(f"تم حذف {removed} صف مكرر.")
            st.success(f"تم بنجاح حذف {removed} صف مكرر!")
            st.rerun()

    with clean_tab3:
        str_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        if str_cols:
            col_to_clean = st.selectbox("اختر العمود النصي المراد تنظيفه:", str_cols)
            strip_ws = st.checkbox("إزالة الفراغات الزائدة (Strip)", value=True)
            rem_special = st.checkbox("إزالة الرموز الخاصة والترقيم", value=False)
            casing = st.selectbox("حالة الأحرف:", [("none", "بدون تغيير"), ("lower", "lowercase"), ("upper", "UPPERCASE"), ("title", "Title Case")], format_func=lambda x: x[1])[0]
            find_txt = st.text_input("البحث عن (Find):")
            replace_txt = st.text_input("البديل (Replace):")
            if st.button("✨ تنفيذ تنظيف النص"):
                case_arg = None if casing == "none" else casing
                st.session_state['df'] = clean_text_column(df, col_to_clean, strip_whitespace=strip_ws, case_change=case_arg, remove_special_chars=rem_special, find_str=find_txt, replace_str=replace_txt)
                log_action(f"تم تنظيف العمود النصي '{col_to_clean}'.")
                st.success(f"تم تنظيف العمود '{col_to_clean}' بنجاح!")
                st.rerun()

    with clean_tab4:
        col_to_convert = st.selectbox("اختر العمود:", df.columns.tolist())
        target_type = st.selectbox("اختر نوع البيانات الجديد:", [("numeric", "رقمي"), ("datetime", "تاريخ ووقت"), ("string", "نصي"), ("category", "فئة")], format_func=lambda x: x[1])[0]
        if st.button("🔄 تحويل النوع"):
            cleaned_df, status = convert_column_types(df, {col_to_convert: target_type})
            st.session_state['df'] = cleaned_df
            log_action(f"تم تحويل نوع العمود '{col_to_convert}' إلى {target_type}.")
            st.success(status.get(col_to_convert, "تم التحويل بنجاح!"))
            st.rerun()

    with clean_tab5:
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            col_outlier = st.selectbox("اختر العمود الرقمي:", num_cols)
            method = st.selectbox("طريقة الكشف:", [("iqr", "IQR"), ("zscore", "Z-Score")], format_func=lambda x: x[1])[0]
            thresh = st.slider("المعامل (Threshold):", min_value=1.0, max_value=3.5, value=1.5, step=0.1)
            action = st.selectbox("الإجراء:", [("clip", "تعديل القيم (Clipping)"), ("drop", "حذف الصفوف الشاذة")], format_func=lambda x: x[1])[0]
            if st.button("🔍 كشف ومعالجة القيم الشاذة"):
                cleaned_df, count = detect_and_handle_outliers(df, col_outlier, method=method, threshold=thresh, action=action)
                st.session_state['df'] = cleaned_df
                log_action(f"تم كشف ومعالجة {count} قيمة شاذة.")
                st.success(f"تم كشف ومعالجة {count} قيمة شاذة بنجاح!")
                st.rerun()

# =========================================================
# Page 3: Visual Comparison
# =========================================================
elif menu_option == "📊 التقييم البصري (قبل/بعد التنظيف)":
    st.markdown("### 📊 **المقارنة البصرية الشاملة: البيانات قبل التنظيف 🆚 بعد التنظيف**")
    comp_fig = plot_missing_comparison(raw_df, df)
    st.plotly_chart(comp_fig, use_container_width=True)
    st.markdown("---")
    vc1, vc2 = st.columns(2)
    with vc1:
        st.markdown("#### 🔴 **البيانات الأصلية (قبل التنظيف):**")
        st.dataframe(raw_df.head(50), use_container_width=True)
    with vc2:
        st.markdown("#### 🟢 **البيانات الحالية (بعد التنظيف والتعويض):**")
        st.dataframe(df.head(50), use_container_width=True)

# =========================================================
# Page 4: Exploratory Data Analysis (EDA)
# =========================================================
elif menu_option == "📊 التحليل الإحصائي (EDA)":
    st.markdown("### 📊 **التحليل الإحصائي والاستكشافي وصحة البيانات (EDA)**")
    
    eda_tab1, eda_tab2, eda_tab3, eda_tab4, eda_tab5 = st.tabs([
        "💡 كشف صحة البيانات والتوصيات",
        "📚 قاموس البيانات (Data Dictionary)",
        "🔢 الإحصاء الوصفي الشامل",
        "🔗 مصفوفة الارتباط (Correlation)",
        "✨ مصفوفة العلاقات المتعددة (SPLOM)"
    ])
    
    with eda_tab1:
        insights = generate_data_health_insights(df)
        for item in insights:
            if item["type"] == "warning":
                st.warning(f"**{item['title']}**: {item['detail']}")
            elif item["type"] == "info":
                st.info(f"**{item['title']}**: {item['detail']}")
            elif item["type"] == "success":
                st.success(f"**{item['title']}**: {item['detail']}")
                
    with eda_tab2:
        st.dataframe(cached_data_dictionary(df), use_container_width=True)

    with eda_tab3:
        num_summary = cached_numerical_summary(df)
        if not num_summary.empty:
            st.dataframe(num_summary, use_container_width=True)
        st.markdown("---")
        cat_summary = get_categorical_summary(df)
        if not cat_summary.empty:
            st.dataframe(cat_summary, use_container_width=True)

    with eda_tab4:
        corr_matrix = cached_correlation_matrix(df)
        if not corr_matrix.empty:
            st.dataframe(corr_matrix, use_container_width=True)
            fig_corr = plot_correlation_heatmap(corr_matrix)
            st.plotly_chart(fig_corr, use_container_width=True)

    with eda_tab5:
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(num_cols) >= 2:
            color_c = st.selectbox("التصنيف بالألوان في مصفوفة العلاقات:", [None] + df.columns.tolist())
            fig_splom = plot_scatter_matrix(df, num_cols, color_c, selected_palette)
            st.plotly_chart(fig_splom, use_container_width=True)
        else:
            st.info("يتطلب رسم مصفوفة العلاقات وجود عمودين رقميين على الأقل.")

# =========================================================
# Page 5: Colorful Visual Charts
# =========================================================
elif menu_option == "📈 الرسوم والمخططات الملونة":
    st.markdown(f"### 📈 **إنشاء المخططات والرسوم البيانية الملونة بالنسق: `{selected_palette}`**")
    
    chart_type = st.selectbox(
        "اختر نوع المخطط البياني الاحترافي الملون:", 
        [
            "📊 مخطط الأعمدة الملون (Bar Chart)",
            "📈 مخطط الخطوط (Line Chart)",
            "🏔️ مخطط المساحات المعبأة (Area Chart)",
            "🔵 مخطط التشتت (Scatter Plot)",
            "🍕 القطاع الدائري والدونات (Pie/Donut Chart)",
            "🌳 المخطط الهيكلي (Treemap)",
            "☀️ المخطط الشمسي (Sunburst Chart)",
            "📉 التوزيع التكراري (Histogram)",
            "📦 مخطط الصندوق والشواذ (Box Plot)"
        ]
    )
    
    c_col1, c_col2 = st.columns([1, 2])
    
    with c_col1:
        st.markdown("#### **إعدادات المحاور والبيانات:**")
        all_cols = df.columns.tolist()
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        fig = None
        if "Bar Chart" in chart_type:
            x_col = st.selectbox("المحور الأفقي X:", all_cols)
            y_col = st.selectbox("المحور الرأسي Y:", ["بدون (تكرار الصفوف)"] + num_cols)
            agg = st.selectbox("دالة التجميع:", ["sum", "mean", "count"])
            color_c = st.selectbox("التصنيف بالألوان (اختياري):", [None] + all_cols)
            fig = plot_bar_chart(df, x_col, y_col, agg, color_c, selected_palette, f"مخطط أعمدة ملون لـ {x_col}")
            
        elif "Line Chart" in chart_type:
            x_col = st.selectbox("المحور X:", all_cols)
            y_col = st.selectbox("المحور Y:", num_cols)
            color_c = st.selectbox("التصنيف بالألوان (اختياري):", [None] + all_cols)
            fig = plot_line_chart(df, x_col, y_col, color_c, selected_palette, f"مخطط خطي لـ {y_col}")
            
        elif "Area Chart" in chart_type:
            x_col = st.selectbox("المحور X:", all_cols)
            y_col = st.selectbox("المحور Y:", num_cols)
            color_c = st.selectbox("التصنيف بالألوان (اختياري):", [None] + all_cols)
            fig = plot_area_chart(df, x_col, y_col, color_c, selected_palette, f"مخطط مساحات لـ {y_col}")
            
        elif "Scatter Plot" in chart_type:
            x_col = st.selectbox("المحور X:", num_cols)
            y_col = st.selectbox("المحور Y:", num_cols)
            color_c = st.selectbox("التصنيف بالألوان (اختياري):", [None] + all_cols)
            size_c = st.selectbox("حجم النقاط حسب (اختياري):", [None] + num_cols)
            fig = plot_scatter_chart(df, x_col, y_col, color_c, size_c, selected_palette, f"تشتت {x_col} مع {y_col}")
            
        elif "Pie" in chart_type:
            names_c = st.selectbox("الفئات (Names):", all_cols)
            values_c = st.selectbox("القيم (Values):", ["بدون (تكرار فقط)"] + num_cols)
            fig = plot_pie_chart(df, names_c, values_c, selected_palette, f"توزيع النسب حسب {names_c}")
            
        elif "Treemap" in chart_type:
            path_c = st.multiselect("الهيكل (Hierarchy Path):", options=all_cols, default=all_cols[:2])
            val_c = st.selectbox("قيم الأحجام (Values):", num_cols) if num_cols else None
            fig = plot_treemap(df, path_c, val_c, selected_palette, "المخطط الهيكلي Treemap") if path_c else None
            
        elif "Sunburst" in chart_type:
            path_c = st.multiselect("المستويات (Sunburst Path):", options=all_cols, default=all_cols[:2])
            val_c = st.selectbox("قيم الأحجام (Values):", num_cols) if num_cols else None
            fig = plot_sunburst(df, path_c, val_c, selected_palette, "المخطط الشمسي Sunburst") if path_c else None
            
        elif "Histogram" in chart_type:
            hist_c = st.selectbox("العمود الرقمي:", num_cols)
            b_cnt = st.slider("عدد الأعمدة (Bins):", 5, 100, 30)
            fig = plot_histogram(df, hist_c, b_cnt, selected_palette, f"توزيع قيم {hist_c}")
            
        elif "Box Plot" in chart_type:
            y_box = st.selectbox("العمود الرقمي Y:", num_cols)
            x_box = st.selectbox("المجموعات X (اختياري):", [None] + all_cols)
            fig = plot_box_chart(df, y_box, x_box, selected_palette, f"مخطط الصندوق والشواذ لـ {y_box}")

    with c_col2:
        if fig:
            st.plotly_chart(fig, use_container_width=True)

# =========================================================
# Page 6: 2x2 Executive Dashboard Builder
# =========================================================
elif menu_option == "📱 لوحة القيادة (2x2 Dashboard)":
    st.markdown("### 📱 **منشئ لوحة القيادة التنفيذية الشاملة (Executive 2x2 Dashboard)**")
    st.caption("يعرض 4 رسوم بيانية تفاعلية متزامنة وملونة في شاشة واحدة!")
    
    all_cols = df.columns.tolist()
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if num_cols and all_cols:
        db_c1, db_c2 = st.columns(2)
        with db_c1:
            dash_x = st.selectbox("اختر العمود التصنيفي (المراد المقارنة حسابه):", all_cols)
        with db_c2:
            dash_y = st.selectbox("اختر العمود الرقمي (المبلغ / الكمية / التقييم):", num_cols)
            
        dash_fig = create_dashboard_2x2(df, dash_x, dash_y, selected_palette)
        st.plotly_chart(dash_fig, use_container_width=True)
    else:
        st.info("يحتاج إنشاء لوحة القيادة إلى عمود رقمي وعمود تصنيفي في الملف.")

# =========================================================
# Page 7: Feature Engineering
# =========================================================
elif menu_option == "⚙️ الهندسة واستخراج الخصائص":
    st.markdown("### ⚙️ **هندسة البيانات وإنشاء الخصائص الجديدة (Feature Engineering)**")
    
    fe_tab1, fe_tab2 = st.tabs(["🧮 حساب عمود جديد (Operations)", "📅 استخراج خصائص التواريخ (Datetime Features)"])
    
    with fe_tab1:
        st.markdown("#### **إنشاء عمود محسوب من عمودين أرقام:**")
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            new_col = st.text_input("اسم العمود الجديد:", value="المجموع_المحسوب")
        with fc2:
            c1_name = st.selectbox("العمود الأول:", num_cols, key="fe_c1")
        with fc3:
            op_type = st.selectbox("العملية الحسابية:", [("multiply", "ضرب (×)"), ("add", "جمع (+)"), ("subtract", "طرح (-)"), ("divide", "قسمة (÷)")], format_func=lambda x: x[1])[0]
        with fc4:
            c2_name = st.selectbox("العمود الثاني:", num_cols, key="fe_c2")
            
        if st.button("✨ إضافة العمود المحسوب"):
            cleaned_df, err = create_calculated_column(df, new_col, c1_name, c2_name, op_type)
            if err:
                st.error(err)
            else:
                st.session_state['df'] = cleaned_df
                log_action(f"تم إضافة العمود المحسوب '{new_col}' ({c1_name} {op_type} {c2_name}).")
                st.success(f"تم إنشاء العمود '{new_col}' بنجاح!")
                st.rerun()

    with fe_tab2:
        st.markdown("#### **استخراج تفاصيل التواريخ تلقائياً:**")
        date_col = st.selectbox("اختر عمود التاريخ:", df.columns.tolist())
        
        if st.button("📅 استخراج خصائص التاريخ"):
            cleaned_df, added_cols = extract_datetime_features(df, date_col)
            if added_cols:
                st.session_state['df'] = cleaned_df
                log_action(f"تم استخراج خصائص التاريخ من العمود '{date_col}': {added_cols}")
                st.success(f"تم إضافة الأعمدة التالية: {', '.join(added_cols)}")
                st.rerun()
            else:
                st.error("تعذر استخراج حقول التواريخ من هذا العمود. يرجى التأكد من صحة التنسيق.")

# =========================================================
# Page 8: Transformations & Pivot
# =========================================================
elif menu_option == "🔀 التحويل والجداول المحورية":
    st.markdown("### 🔀 **تحويل البيانات والجداول المحورية**")
    t_tab1, t_tab2, t_tab3 = st.tabs(["✏️ إعادة تسمية وحذف الأعمدة", "🔍 تصفية وفرز البيانات", "📊 الجدول المحوري (Pivot Table)"])
    
    with t_tab1:
        renames = {}
        rc1, rc2 = st.columns(2)
        for idx, col in enumerate(df.columns):
            with (rc1 if idx % 2 == 0 else rc2):
                new_name = st.text_input(f"الاسم الحالي: `{col}`", value=col, key=f"rename_{col}")
                if new_name != col:
                    renames[col] = new_name
                    
        if renames and st.button("💾 حفظ أسماء الأعمدة الجديدة"):
            st.session_state['df'] = df.rename(columns=renames)
            log_action(f"تم إعادة تسمية الأعمدة: {renames}")
            st.success("تم تحديث أسماء الأعمدة بنجاح!")
            st.rerun()

    with t_tab2:
        filter_col = st.selectbox("اختر العمود للتصفية:", df.columns.tolist())
        if pd.api.types.is_numeric_dtype(df[filter_col]):
            min_val = float(df[filter_col].min()) if not df[filter_col].empty else 0.0
            max_val = float(df[filter_col].max()) if not df[filter_col].empty else 100.0
            selected_range = st.slider("اختر نطاق القيم:", min_val, max_val, (min_val, max_val))
            if st.button("🔍 تطبيق التصفية"):
                st.session_state['df'] = df[(df[filter_col] >= selected_range[0]) & (df[filter_col] <= selected_range[1])]
                log_action(f"تم تصفية العمود '{filter_col}'.")
                st.success("تمت التصفية!")
                st.rerun()

    with t_tab3:
        p_index = st.multiselect("اختر أعمدة الصفوف (Index):", options=df.columns.tolist())
        p_columns = st.selectbox("اختر عمود الأعمدة (Columns - اختياري):", [None] + df.columns.tolist())
        p_values = st.multiselect("اختر أعمدة القيم (Values):", options=df.select_dtypes(include=[np.number]).columns.tolist())
        p_agg = st.selectbox("دالة التجميع (Aggregation):", ["sum", "mean", "count", "min", "max"])
        
        if p_index and p_values and st.button("📊 توليد الجدول المحوري"):
            pivot_df = pd.pivot_table(df, index=p_index, columns=p_columns, values=p_values, aggfunc=p_agg).reset_index()
            st.dataframe(pivot_df, use_container_width=True)

# =========================================================
# Page 9: Export & Reports
# =========================================================
elif menu_option == "📥 تصدير النتائج والتقارير":
    st.markdown("### 📥 **تصدير البيانات المنظفة وسجل التعديلات**")
    
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        st.markdown("#### **تنزيل الملفات المعدلة بترميز آمن:**")
        st.info(f"عدد الصفوف المتاحة للتصدير: **{len(df):,} صف**")
        
        excel_data = export_to_excel_buffer({"DataCleanX_Cleaned": df, "Data_Dictionary": get_data_dictionary(df)})
        st.download_button(
            label="📊 تحميل ملف Excel منسق آمن (.xlsx)",
            data=excel_data,
            file_name=f"Cleaned_{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        csv_data = export_to_csv_buffer(df)
        st.download_button(
            label="📄 تحميل ملف CSV محمي (.csv)",
            data=csv_data,
            file_name=f"Cleaned_{filename}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_col2:
        st.markdown("#### **سجل عمليات التنظيف (Audit Log):**")
        for idx, item in enumerate(st.session_state['audit_log'], 1):
            st.markdown(f'<div class="log-item"><b>{idx}.</b> {item}</div>', unsafe_allow_html=True)
