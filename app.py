import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

st.set_page_config(page_title="Dashboard Báo Cáo AK", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    .stMetric {
        background-color: #262730;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border-left: 5px solid #4CAF50;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #d1d5db !important;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    df_master = pd.read_parquet('master.parquet')
    df_monthly = pd.read_parquet('monthly.parquet')
    df_inv = pd.read_parquet('inventory.parquet')
    
    # Merge master with monthly
    df_m = pd.merge(df_monthly, df_master[['ma_sp', 'nganh_hang', 'nhom_hang']], on='ma_sp', how='left')
    # Merge master with inv
    df_i = pd.merge(df_inv, df_master[['ma_sp', 'nganh_hang', 'nhom_hang', 'ten_sp']], on='ma_sp', how='left')
    
    return df_master, df_m, df_i

try:
    df_master, df_monthly, df_inv = load_data()
except Exception as e:
    st.error(f"Chưa tìm thấy dữ liệu Parquet. Vui lòng chạy file `etl.py` trước.\nChi tiết lỗi: {e}")
    st.stop()

st.title("📊 BÁO CÁO NGÀNH HÀNG AK 2026")

tab1, tab2 = st.tabs(["📈 Phân tích Ngành hàng & Thời gian", "🔍 Tra cứu Sản phẩm & Kho"])

# ==========================================
# TAB 1: PHÂN TÍCH NGÀNH HÀNG & THỜI GIAN
# ==========================================
with tab1:
    st.header("Phân tích Ngành hàng & Chỉ số theo Thời gian")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("Bộ lọc Thời gian & Ngành")
        available_months = sorted(df_monthly['thang'].unique())
        
        # Get current month in format YYYY/TMM
        now = datetime.datetime.now()
        current_month_str = f"{now.year}/T{now.month:02d}"
        
        if current_month_str in available_months:
            default_month = current_month_str
        elif available_months:
            default_month = available_months[-1]
        else:
            default_month = None
            
        selected_months = st.multiselect("Chọn Tháng/Năm", options=available_months, default=[default_month] if default_month else [])
        
        std_nganh = [
            "Thuốc", "Trang Thiết Bị Y Tế", "Thực Phẩm Chức Năng", 
            "Sữa - Thức uống bổ dưỡng các loại", "Mỹ phẩm các loại", 
            "Hóa phẩm các loại", "Điện gia dụng", "BHX - Hàng khuyến mãi", 
            "AK - Hàng Khuyến Mãi", "Thức uống giải khát các loại", "Làm Đẹp"
        ]
        default_nganh = [n for n in std_nganh if n in df_master['nganh_hang'].unique()]
        selected_nganh = st.multiselect("Chọn Ngành hàng", options=df_master['nganh_hang'].unique(), default=default_nganh)
        
        f_monthly = df_monthly[(df_monthly['thang'].isin(selected_months)) & (df_monthly['nganh_hang'].isin(selected_nganh))]
        f_inv = df_inv[df_inv['nganh_hang'].isin(selected_nganh)]
        f_master = df_master[df_master['nganh_hang'].isin(selected_nganh)]
        
    with col2:
        st.subheader("Tổng quan Chỉ số (Theo thời gian chọn)")
        st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)
        
        def make_card(title, value, color, icon_class):
            color_map = {
                "green": ("#28a745", "#218838"),
                "blue": ("#007bff", "#0062cc"),
                "orange": ("#fd7e14", "#e85e0b"),
                "red": ("#dc3545", "#c82333"),
            }
            bg, bottom_bg = color_map.get(color, ("#6c757d", "#5a6268"))
            return f"""
            <div style="background-color: {bg}; padding: 20px; border-radius: 5px 5px 0 0; color: white; position: relative; min-height: 120px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="margin: 0; font-size: 32px; font-weight: bold; color: white;">{value}</h2>
                <p style="margin: 5px 0 0 0; font-size: 15px; color: white;">{title}</p>
                <i class="{icon_class}" style="position: absolute; right: 20px; top: 25px; font-size: 55px; opacity: 0.15; color: white;"></i>
            </div>
            <div style="background-color: {bottom_bg}; padding: 5px; border-radius: 0 0 5px 5px; text-align: center; color: rgba(255,255,255,0.9); font-size: 13px; margin-bottom: 15px; cursor: pointer;">
                Chi Tiết <i class="fas fa-arrow-circle-right" style="margin-left: 5px;"></i>
            </div>
            """

        c1, c2, c3, c4 = st.columns(4)
        
        v1 = f"{f_monthly['dt_ban'].sum() / 1e6:,.0f}"
        v2 = f"{f_monthly['ds_nhap'].sum() / 1e6:,.0f}"
        v3 = f"{f_monthly['sl_ban'].sum():,.0f}"
        v4 = f"{f_monthly['sl_nhap'].sum():,.0f}"

        c1.markdown(make_card("Doanh thu Bán (Tr VNĐ)", v1, "green", "fas fa-money-bill-wave"), unsafe_allow_html=True)
        c2.markdown(make_card("Doanh số Nhập (Tr VNĐ)", v2, "orange", "fas fa-download"), unsafe_allow_html=True)
        c3.markdown(make_card("Tổng SL Bán", v3, "blue", "fas fa-shopping-cart"), unsafe_allow_html=True)
        c4.markdown(make_card("Tổng SL Nhập", v4, "red", "fas fa-box"), unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("Bảng Phân tích Ngành hàng (Tổng Tồn Kho & Doanh Thu)")
    
    # Bảng phân tích theo ngành: tổng sức bán, tổng tồn kho SNTK, DT, DT GV, tổng GT tồn Mới/Cận theo Tổng/Kho/ST
    # Sức bán (theo tháng chọn)
    sb_df = f_monthly.groupby('nganh_hang')[['sl_ban', 'dt_ban', 'dt_ban_gv']].sum().reset_index()
    # Tồn kho (lấy từ inventory data không phụ thuộc tháng, hoặc master)
    # Tồn SNTK từ master
    inv_df_agg = f_master.groupby('nganh_hang')[['tong_ton_st', 'tong_ton_kho', 'tong_gia_tri_ton']].sum().reset_index()
    
    # Chi tiết Kho/ST/Mới/Cận từ df_inv
    inv_detail = f_inv.groupby('nganh_hang')[['ton_kho_kho_moi', 'ton_kho_st_moi', 'ton_kho_kho_can', 'ton_kho_st_can', 'gt_kho_moi', 'gt_st_moi', 'gt_kho_can', 'gt_st_can']].sum().reset_index()
    
    # Merge for final table
    tbl_nganh = pd.merge(sb_df, inv_df_agg, on='nganh_hang', how='left')
    tbl_nganh = pd.merge(tbl_nganh, inv_detail, on='nganh_hang', how='left')
    
    # Rename for display
    tbl_nganh.columns = [
        "Ngành hàng", "SL Bán", "DT Bán", "DT Giá vốn", 
        "Tồn kho ST", "Tồn kho Kho", "Tổng Giá trị Tồn",
        "Tồn Kho (Mới)", "Tồn ST (Mới)", "Tồn Kho (Cận)", "Tồn ST (Cận)",
        "GT Kho (Mới)", "GT ST (Mới)", "GT Kho (Cận)", "GT ST (Cận)"
    ]
    
    # Quy đổi các cột giá trị sang Triệu VNĐ
    gt_cols = ["DT Bán", "DT Giá vốn", "Tổng Giá trị Tồn", "GT Kho (Mới)", "GT ST (Mới)", "GT Kho (Cận)", "GT ST (Cận)"]
    for c in gt_cols:
        tbl_nganh[c] = tbl_nganh[c] / 1e6
        
    # Đổi tên cột thêm hậu tố (Triệu VNĐ)
    tbl_nganh.rename(columns={c: f"{c} (Tr VNĐ)" for c in gt_cols}, inplace=True)
    
    # Sắp xếp theo DT Bán giảm dần
    tbl_nganh = tbl_nganh.sort_values(by="DT Bán (Tr VNĐ)", ascending=False)
    
    num_cols_fmt = [
        "SL Bán", "DT Bán (Tr VNĐ)", "DT Giá vốn (Tr VNĐ)", 
        "Tồn kho ST", "Tồn kho Kho", "Tổng Giá trị Tồn (Tr VNĐ)",
        "Tồn Kho (Mới)", "Tồn ST (Mới)", "Tồn Kho (Cận)", "Tồn ST (Cận)",
        "GT Kho (Mới) (Tr VNĐ)", "GT ST (Mới) (Tr VNĐ)", "GT Kho (Cận) (Tr VNĐ)", "GT ST (Cận) (Tr VNĐ)"
    ]
    
    th_props = [('background-color', '#00b050'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center')]
    styles = [{'selector': 'th', 'props': th_props}]
    
    st.dataframe(tbl_nganh.style.format(formatter="{:,.0f}", subset=num_cols_fmt, na_rep="-").set_table_styles(styles), use_container_width=True)

    # ------------------------------------------
    # BẢNG THỐNG KÊ PIVOT THEO TRẠNG THÁI KD
    # ------------------------------------------
    st.markdown("---")
    st.subheader("Bảng Phân tích SKU theo Trạng thái kinh doanh")
    
    # 1. Tính tổng sl_ban theo tháng đang chọn cho mỗi mã SP
    sales_by_sp = f_monthly.groupby('ma_sp')['sl_ban'].sum().reset_index()
    
    # 2. Merge vào df_master (đã lọc theo ngành)
    df_piv = pd.merge(f_master, sales_by_sp, on='ma_sp', how='left')
    df_piv['sl_ban'] = df_piv['sl_ban'].fillna(0)
    
    # 3. Loại bỏ #N/A, 0
    na_vals = ['#N/A', 'N/A', 'N/a', '0', 0, '#N/a', '#n/a']
    df_piv = df_piv[~df_piv['trang_thai_kd'].isin(na_vals)]
    
    # 4. Áp dụng Rule
    mask_cond = (df_piv['tong_ton_kho'] > 0) | (df_piv['tong_ton_st'] > 0) | (df_piv['sl_ban'] > 0)
    mask_exempt = df_piv['trang_thai_kd'].str.lower().isin(['đa dạng', 'kd bình thường', 'kinh doanh bình thường'])
    
    df_piv = df_piv[mask_cond | mask_exempt]
    
    # 5. Pivot Table
    pivot_df = pd.pivot_table(
        df_piv, 
        index='nganh_hang', 
        columns='trang_thai_kd', 
        values='ma_model', 
        aggfunc=pd.Series.nunique, 
        fill_value=0,
        margins=True,
        margins_name='Grand Total'
    )
    
    # 6. Sắp xếp giảm dần theo Total
    if 'Grand Total' in pivot_df.columns and 'Grand Total' in pivot_df.index:
        grand_total_row = pivot_df.loc[['Grand Total']]
        pivot_df = pivot_df.drop('Grand Total').sort_values(by='Grand Total', ascending=False)
        
        col_totals = grand_total_row.drop(columns=['Grand Total']).squeeze()
        sorted_cols = col_totals.sort_values(ascending=False).index.tolist()
        
        pivot_df = pivot_df[sorted_cols + ['Grand Total']]
        pivot_df = pd.concat([pivot_df, grand_total_row[sorted_cols + ['Grand Total']]])
        
    st.dataframe(pivot_df.style.set_table_styles(styles), use_container_width=True)

# ==========================================
# TAB 2: TRA CỨU SẢN PHẨM & KHO
# ==========================================
with tab2:
    st.header("Tra cứu Sản phẩm chi tiết theo Kho")
    
    t2_c1, t2_c2, t2_c3 = st.columns(3)
    with t2_c1:
        s_nganh = st.multiselect("Lọc Ngành hàng", options=df_master['nganh_hang'].unique(), default=[])
    with t2_c2:
        opts_sp = df_master[df_master['nganh_hang'].isin(s_nganh)]['ten_sp'].unique() if s_nganh else df_master['ten_sp'].unique()
        s_sp = st.multiselect("Lọc Sản phẩm", options=opts_sp, default=[])
    with t2_c3:
        s_kho = st.multiselect("Lọc Kho", options=df_inv['kho'].unique(), default=[])
        
    # Lọc df_inv theo sp, kho
    res_inv = df_inv.copy()
    if s_nganh: res_inv = res_inv[res_inv['nganh_hang'].isin(s_nganh)]
    if s_sp: res_inv = res_inv[res_inv['ten_sp'].isin(s_sp)]
    if s_kho: res_inv = res_inv[res_inv['kho'].isin(s_kho)]
    
    st.subheader("Thống kê Tồn Kho theo Kho/Siêu thị")
    disp_inv_cols = ['ten_sp', 'kho', 'suc_ban', 'ton_kho_tong', 'ton_kho_kho_moi', 'ton_kho_kho_can', 'ton_kho_st_moi', 'ton_kho_st_can', 'gt_tong', 'gt_kho_moi', 'gt_kho_can', 'gt_st_moi', 'gt_st_can', 'co_ton', 'st_co_dm']
    inv_rename = {
        'ten_sp': 'Tên sản phẩm', 'kho': 'Kho/Siêu thị', 'suc_ban': 'Sức bán', 
        'ton_kho_tong': 'Tổng tồn kho', 'ton_kho_kho_moi': 'Tồn kho mới', 'ton_kho_kho_can': 'Tồn kho cận', 
        'ton_kho_st_moi': 'Tồn siêu thị mới', 'ton_kho_st_can': 'Tồn siêu thị cận', 
        'gt_tong': 'Tổng giá trị', 'gt_kho_moi': 'Giá trị kho mới', 'gt_kho_can': 'Giá trị kho cận', 
        'gt_st_moi': 'Giá trị ST mới', 'gt_st_can': 'Giá trị ST cận', 'co_ton': 'Có tồn', 'st_co_dm': 'Siêu thị có danh mục'
    }
    df_inv_disp = res_inv[disp_inv_cols].rename(columns=inv_rename)
    
    th_props = [('background-color', '#00b050'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center')]
    styles = [{'selector': 'th', 'props': th_props}]
    st.dataframe(df_inv_disp.style.set_table_styles(styles), use_container_width=True)
    
    st.subheader("Chi tiết Thông tin Sản phẩm (Master)")
    res_master = df_master.copy()
    if s_nganh: res_master = res_master[res_master['nganh_hang'].isin(s_nganh)]
    if s_sp: res_master = res_master[res_master['ten_sp'].isin(s_sp)]
    
    disp_master_cols = [
        "nganh_hang", "nhom_hang", "giam_doc_mua", "buyer", "ma_model", "ma_sp", "ten_sp", "vat", "trang_thai_kd",
        "gia_ban_dvn", "gia_ban_dvl", "gia_bqgq", "front", "ty_le_front", "st_co_ton", "tong_st"
    ]
    master_rename = {
        "nganh_hang": "Ngành hàng", "nhom_hang": "Nhóm hàng", "giam_doc_mua": "Giám đốc mua hàng", 
        "buyer": "Buyer mua hàng", "ma_model": "Mã Model", "ma_sp": "Mã sản phẩm", "ten_sp": "Tên sản phẩm", 
        "vat": "Phần trăm VAT", "trang_thai_kd": "Trạng thái kinh doanh", "gia_ban_dvn": "Giá bán DVN", 
        "gia_ban_dvl": "Giá bán DVL", "gia_bqgq": "Giá BQGQ", "front": "Front", "ty_le_front": "Tỉ lệ Front", 
        "st_co_ton": "Siêu thị có tồn", "tong_st": "Tổng siêu thị"
    }
    df_master_disp = res_master[disp_master_cols].rename(columns=master_rename)
    
    df_master_disp["Phần trăm VAT"] = pd.to_numeric(df_master_disp["Phần trăm VAT"], errors='coerce').fillna(0) * 100
    df_master_disp["Tỉ lệ Front"] = pd.to_numeric(df_master_disp["Tỉ lệ Front"], errors='coerce').fillna(0) * 100
    
    format_dict = {
        "Phần trăm VAT": "{:,.3f}%",
        "Tỉ lệ Front": "{:,.3f}%"
    }
    st.dataframe(df_master_disp.style.format(format_dict, na_rep="-").set_table_styles(styles), use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Hệ thống Báo cáo Nội bộ - Phát triển bằng Python Streamlit</p>", unsafe_allow_html=True)
