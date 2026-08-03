import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, List, Dict

DARK_TEMPLATE = "plotly_dark"

# Vibrant & Modern Color Palettes
PALETTES = {
    "🌈 نيون فيفيو (Vivid Neon)": ["#6366F1", "#EC4899", "#10B981", "#F59E0B", "#8B5CF6", "#06B6D4", "#EF4444", "#3B82F6"],
    "🎆 سايبر بانك (Cyberpunk)": ["#FF007F", "#00F0FF", "#7000FF", "#FFB800", "#00FF66", "#FF4400"],
    "🌅 الغروب المتدرج (Sunset)": ["#FF5E36", "#FFAE33", "#EF3B70", "#8E44AD", "#3498DB"],
    "🌿 الطبيعة الزمردية (Emerald)": ["#10B981", "#059669", "#34D399", "#065F46", "#A7F3D0", "#6EE7B7"],
    "🌌 مجرة الليلة (Midnight Galaxy)": ["#312E81", "#4C1D95", "#581C87", "#701A75", "#831843", "#9F1239"]
}

def get_color_sequence(palette_name: str) -> List[str]:
    return PALETTES.get(palette_name, PALETTES["🌈 نيون فيفيو (Vivid Neon)"])

def plot_missing_comparison(before_df: pd.DataFrame, after_df: pd.DataFrame) -> go.Figure:
    """Renders a comparative side-by-side bar chart of missing values BEFORE vs AFTER."""
    before_missing = before_df.isnull().sum()
    after_missing = after_df.isnull().sum()
    
    all_cols = list(set(before_missing.index).union(set(after_missing.index)))
    
    comp_df = pd.DataFrame({
        'العمود': all_cols,
        'قبل التنظيف': [before_missing.get(c, 0) for c in all_cols],
        'بعد التنظيف': [after_missing.get(c, 0) for c in all_cols]
    })
    
    comp_df = comp_df[(comp_df['قبل التنظيف'] > 0) | (comp_df['بعد التنظيف'] > 0)]
    
    if comp_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="🎉 ممتاز! لا توجد أي قيم مفقودة في البيانات!", showarrow=False, font=dict(size=20, color="#10B981"))
        fig.update_layout(template=DARK_TEMPLATE)
        return fig
        
    fig = px.bar(
        comp_df,
        x='العمود',
        y=['قبل التنظيف', 'بعد التنظيف'],
        barmode='group',
        color_discrete_sequence=['#EF4444', '#10B981'],
        title="📊 المقارنة البصرية الملونة للقيم المفقودة: قبل التنظيف (أحمر) 🆚 بعد التنظيف (أخضر)",
        template=DARK_TEMPLATE
    )
    fig.update_layout(title_x=0.5, hovermode="x unified", yaxis_title="عدد الخلايا المفقودة")
    return fig

def plot_bar_chart(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: Optional[str] = None, 
    agg_func: str = 'sum',
    color_col: Optional[str] = None,
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)",
    title: str = "مخطط الأعمدة"
) -> go.Figure:
    colors = get_color_sequence(palette_name)
    if y_col and y_col != "بدون (تكرار الصفوف)":
        group_cols = [x_col] + ([color_col] if color_col else [])
        if agg_func == 'sum':
            df_plot = df.groupby(group_cols)[y_col].sum().reset_index()
        elif agg_func == 'mean':
            df_plot = df.groupby(group_cols)[y_col].mean().round(2).reset_index()
        elif agg_func == 'count':
            df_plot = df.groupby(group_cols)[y_col].count().reset_index()
        else:
            df_plot = df
        fig = px.bar(df_plot, x=x_col, y=y_col, color=color_col or x_col, color_discrete_sequence=colors, template=DARK_TEMPLATE, text_auto='.2s')
    else:
        fig = px.histogram(df, x=x_col, color=color_col or x_col, color_discrete_sequence=colors, template=DARK_TEMPLATE, text_auto=True)
        
    fig.update_traces(marker_line_color='rgba(255,255,255,0.2)', marker_line_width=1, opacity=0.9)
    fig.update_layout(title=title, hovermode="x unified", title_x=0.5)
    return fig

def plot_line_chart(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    color_col: Optional[str] = None,
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)",
    title: str = "مخطط الخطوط"
) -> go.Figure:
    colors = get_color_sequence(palette_name)
    fig = px.line(
        df.sort_values(by=x_col), 
        x=x_col, 
        y=y_col, 
        color=color_col, 
        color_discrete_sequence=colors, 
        template=DARK_TEMPLATE,
        markers=True
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8, stroke_width=2, stroke_color="white"))
    fig.update_layout(title=title, hovermode="x unified", title_x=0.5)
    return fig

def plot_area_chart(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    color_col: Optional[str] = None,
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)",
    title: str = "مخطط المساحات المعبأة"
) -> go.Figure:
    colors = get_color_sequence(palette_name)
    fig = px.area(
        df.sort_values(by=x_col), 
        x=x_col, 
        y=y_col, 
        color=color_col, 
        color_discrete_sequence=colors, 
        template=DARK_TEMPLATE
    )
    fig.update_layout(title=title, hovermode="x unified", title_x=0.5)
    return fig

def plot_scatter_chart(
    df: pd.DataFrame, 
    x_col: str, 
    y_col: str, 
    color_col: Optional[str] = None,
    size_col: Optional[str] = None,
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)",
    title: str = "مخطط التشتت الملون"
) -> go.Figure:
    colors = get_color_sequence(palette_name)
    fig = px.scatter(
        df, 
        x=x_col, 
        y=y_col, 
        color=color_col or x_col, 
        size=size_col, 
        color_discrete_sequence=colors, 
        template=DARK_TEMPLATE,
        opacity=0.85
    )
    fig.update_traces(marker=dict(line=dict(width=1, color='white')))
    fig.update_layout(title=title, title_x=0.5)
    return fig

def plot_pie_chart(
    df: pd.DataFrame, 
    names_col: str, 
    values_col: Optional[str] = None, 
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)",
    title: str = "القطاع الدائري (Donut Chart)"
) -> go.Figure:
    colors = get_color_sequence(palette_name)
    if values_col and values_col != "بدون (تكرار فقط)":
        fig = px.pie(df, names=names_col, values=values_col, color_discrete_sequence=colors, template=DARK_TEMPLATE, hole=0.45)
    else:
        counts = df[names_col].value_counts().reset_index()
        counts.columns = [names_col, 'count']
        fig = px.pie(counts, names=names_col, values='count', color_discrete_sequence=colors, template=DARK_TEMPLATE, hole=0.45)
        
    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
    fig.update_layout(title=title, title_x=0.5)
    return fig

def plot_treemap(
    df: pd.DataFrame, 
    path_cols: List[str], 
    values_col: Optional[str] = None, 
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)",
    title: str = "المخطط الهيكلي (Treemap)"
) -> go.Figure:
    colors = get_color_sequence(palette_name)
    fig = px.treemap(
        df, 
        path=path_cols, 
        values=values_col, 
        color_discrete_sequence=colors, 
        template=DARK_TEMPLATE
    )
    fig.update_layout(title=title, title_x=0.5)
    return fig

def plot_sunburst(
    df: pd.DataFrame, 
    path_cols: List[str], 
    values_col: Optional[str] = None, 
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)",
    title: str = "المخطط الشمسي (Sunburst Chart)"
) -> go.Figure:
    colors = get_color_sequence(palette_name)
    fig = px.sunburst(
        df, 
        path=path_cols, 
        values=values_col, 
        color_discrete_sequence=colors, 
        template=DARK_TEMPLATE
    )
    fig.update_layout(title=title, title_x=0.5)
    return fig

def plot_histogram(
    df: pd.DataFrame, 
    col: str, 
    bins: int = 30, 
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)",
    title: str = "مخطط التوزيع التكراري"
) -> go.Figure:
    colors = get_color_sequence(palette_name)
    fig = px.histogram(df, x=col, nbins=bins, color_discrete_sequence=[colors[0]], template=DARK_TEMPLATE, marginal="box")
    fig.update_layout(title=title, title_x=0.5)
    return fig

def plot_box_chart(
    df: pd.DataFrame, 
    y_col: str, 
    x_col: Optional[str] = None, 
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)",
    title: str = "مخطط الصندوق والطرفين (Box Plot)"
) -> go.Figure:
    colors = get_color_sequence(palette_name)
    fig = px.box(df, y=y_col, x=x_col, color=x_col, color_discrete_sequence=colors, template=DARK_TEMPLATE, points="outliers")
    fig.update_layout(title=title, title_x=0.5)
    return fig

def plot_correlation_heatmap(
    corr_df: pd.DataFrame, 
    title: str = "مصفوفة الارتباط (Correlation Heatmap)"
) -> go.Figure:
    fig = px.imshow(
        corr_df, 
        text_auto=True, 
        aspect="auto", 
        color_continuous_scale="Plasma", 
        template=DARK_TEMPLATE
    )
    fig.update_layout(title=title, title_x=0.5)
    return fig

def plot_scatter_matrix(
    df: pd.DataFrame, 
    numeric_cols: List[str], 
    color_col: Optional[str] = None,
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)"
) -> go.Figure:
    """Generates a Pairwise Scatter Plot Matrix (SPLOM)."""
    colors = get_color_sequence(palette_name)
    fig = px.scatter_matrix(
        df, 
        dimensions=numeric_cols[:5], 
        color=color_col, 
        color_discrete_sequence=colors, 
        template=DARK_TEMPLATE,
        title="✨ مصفوفة العلاقات المتعددة (Scatter Plot Matrix)"
    )
    fig.update_layout(title_x=0.5, height=700)
    return fig

def create_dashboard_2x2(
    df: pd.DataFrame, 
    x_cat: str, 
    y_num: str, 
    palette_name: str = "🌈 نيون فيفيو (Vivid Neon)"
) -> go.Figure:
    """Generates an executive 2x2 multi-chart dashboard figure."""
    colors = get_color_sequence(palette_name)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            f"مجموع {y_num} حسب {x_cat}",
            f"توزيع قيم {y_num}",
            f"نسب التكرار لـ {x_cat}",
            f"مخطط الصندوق والشواذ لـ {y_num}"
        ),
        specs=[[{"type": "bar"}, {"type": "histogram"}],
               [{"type": "pie"}, {"type": "box"}]]
    )
    
    # 1. Bar Chart
    df_bar = df.groupby(x_cat)[y_num].sum().reset_index()
    fig.add_trace(go.Bar(x=df_bar[x_cat], y=df_bar[y_num], marker_color=colors[0], name="إجمالي المبيعات"), row=1, col=1)
    
    # 2. Histogram
    fig.add_trace(go.Histogram(x=df[y_num], marker_color=colors[1], name="التوزيع التكراري"), row=1, col=2)
    
    # 3. Pie Chart
    counts = df[x_cat].value_counts().reset_index()
    counts.columns = [x_cat, 'count']
    fig.add_trace(go.Pie(labels=counts[x_cat], values=counts['count'], marker=dict(colors=colors), hole=0.3, name="النسب"), row=2, col=1)
    
    # 4. Box Plot
    fig.add_trace(go.Box(y=df[y_num], marker_color=colors[2], name="الصندوق والشواذ"), row=2, col=2)
    
    fig.update_layout(
        template=DARK_TEMPLATE,
        title_text=f"📊 لوحة القيادة التنفيذية والشاملة لـ ({y_num} 🆚 {x_cat})",
        title_x=0.5,
        height=750,
        showlegend=False
    )
    return fig
