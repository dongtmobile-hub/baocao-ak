import streamlit as st
import pandas as pd
from google.cloud import bigquery
import plotly.express as px
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="Super Dashboard - An Khang", page_icon="💊", layout="wide")

# --- AUTO-DISCONNECT (15 Phút) ---
import streamlit.components.v1 as components
components.html(
    """
    <script>
    const TIMEOUT_MS = 15 * 60 * 1000; // 15 minutes
    let timeoutId;

    function resetTimer() {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            if(window.parent) {
                window.parent.document.body.innerHTML = "<div style='display:flex;justify-content:center;align-items:center;height:100vh;background:#020617;color:white;font-family:sans-serif;text-align:center;'><h1>Phiên làm việc đã kết thúc do bạn không thao tác quá 15 phút.</h1><p>Hệ thống tự ngắt kết nối để tiết kiệm chi phí máy chủ.</p><h2>Vui lòng ấn F5 để tải lại!</h2></div>";
                window.parent.location.href = "about:blank";
            }
        }, TIMEOUT_MS);
    }

    if(window.parent) {
        window.parent.document.addEventListener('mousemove', resetTimer);
        window.parent.document.addEventListener('keydown', resetTimer);
        window.parent.document.addEventListener('scroll', resetTimer);
        window.parent.document.addEventListener('click', resetTimer);
    }
    resetTimer();
    </script>
    """,
    height=0,
    width=0,
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
:root {
  --bg-primary: #020617;
  --bg-card: rgba(15, 23, 42, 0.8);
  --accent-green: #38bdf8;
  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
}
.stApp {
    background-color: var(--bg-primary);
    color: var(--text-primary);
}
div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 12px;
    border-left: 3px solid var(--accent-green);
}
.custom-header {
    background-color: #31A551;
    padding: 15px 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    color: white;
    font-weight: 700;
    font-size: 1.2rem;
}
.empty-state {
    text-align: center;
    padding: 40px;
    background: var(--bg-card);
    border-radius: 12px;
    border: 1px dashed rgba(255,255,255,0.2);
    color: var(--text-secondary);
}
</style>
""", unsafe_allow_html=True)

# Header removed per user request

# --- XÁC THỰC NGƯỜI DÙNG (AUTHENTICATION) ---
PROJECT_ID = 'powerbi-data-warehouse-500915'
from google.cloud import bigquery

@st.cache_data(ttl=60)
def load_user_roles():
    client = bigquery.Client(project=PROJECT_ID)
    try:
        df_roles = client.query("SELECT email, nganh_hang FROM `powerbi-data-warehouse-500915.retail_dashboard.dim_user_roles`").to_dataframe()
        return df_roles
    except Exception:
        return pd.DataFrame()

df_roles = load_user_roles()

# Nhận diện Email từ Google Cloud Run (IAP / Cloud Run Auth)
# Cloud Run tự động chèn header khi có user đăng nhập
header_email = st.context.headers.get("X-Goog-Authenticated-User-Email", "")
user_email = ""
if header_email:
    # Header format: "accounts.google.com:email@gmail.com"
    user_email = header_email.replace("accounts.google.com:", "").strip()
else:
    import streamlit.components.v1 as components
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    
    firebase_project_id = "powerbi-data-warehouse-5-9d617"
    
    # 1. Đọc token từ Cookie
    firebase_token = st.context.cookies.get("firebase_id_token")
    decoded_token = None
    
    if firebase_token:
        try:
            # Xác thực Token bằng thư viện google-auth
            decoded_token = id_token.verify_firebase_token(
                firebase_token, 
                google_requests.Request(), 
                audience=firebase_project_id
            )
        except Exception as e:
            decoded_token = None
            
    import os
    if os.environ.get("DEV_MODE") == "1":
        decoded_token = {'email': 'dong.tmobile@gmail.com', 'name': 'Local Dev'}
            
    # 2. Xử lý hiển thị
    if decoded_token:
        user_email = decoded_token.get('email', '')
        if decoded_token.get('picture'):
            st.sidebar.image(decoded_token.get('picture'))
        st.sidebar.write(f"👤 **{decoded_token.get('name', 'User')}**")
        if st.sidebar.button('🚪 Đăng xuất'):
            # Xóa cookie và reload
            components.html("""
            <script>
                document.cookie = "firebase_id_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                window.parent.location.href = window.parent.location.pathname;
            </script>
            """, height=0, width=0)
            st.stop()
    else:
        st.info("ℹ️ Hệ thống yêu cầu đăng nhập bằng Gmail nội bộ để xem báo cáo.")
        
        # Khởi tạo giao diện Firebase UI
        html_code = """
        <script>
          if (!window.parent.document.getElementById("firebase-auth-script")) {
              const script = window.parent.document.createElement("script");
              script.id = "firebase-auth-script";
              script.type = "module";
              script.innerHTML = `
                  import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
                  import { getAuth, signInWithPopup, GoogleAuthProvider } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

                  const firebaseConfig = {
                    apiKey: "AIzaSyD45W1sW0dnFm5-5QmRcNT8Z9Hr3WvdK_E",
                    authDomain: "powerbi-data-warehouse-5-9d617.firebaseapp.com",
                    projectId: "powerbi-data-warehouse-5-9d617",
                    storageBucket: "powerbi-data-warehouse-5-9d617.firebasestorage.app",
                    messagingSenderId: "835124086139",
                    appId: "1:835124086139:web:a074996f524d40e193e9de",
                    measurementId: "G-QQBZMSKJ81"
                  };

                  const app = initializeApp(firebaseConfig);
                  const auth = getAuth(app);
                  const provider = new GoogleAuthProvider();
                  
                  window.loginWithGoogle = function() {
                      signInWithPopup(auth, provider)
                        .then((result) => {
                          return result.user.getIdToken();
                        })
                        .then((idToken) => {
                          // Lưu Token vào Cookie để Streamlit đọc được (Sống sót qua F5)
                          document.cookie = "firebase_id_token=" + idToken + "; path=/; max-age=3600; SameSite=Lax;";
                          window.location.href = window.location.pathname;
                        })
                        .catch((error) => {
                          alert("Lỗi đăng nhập: " + error.message);
                        });
                  };
              `;
              window.parent.document.head.appendChild(script);
          }
        </script>
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <button onclick="window.parent.loginWithGoogle()" style="background-color: white; color: #757575; border: 1px solid #ddd; padding: 10px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; display: flex; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-family: Roboto, sans-serif; font-weight: 500;">
                <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" style="width: 18px; height: 18px; margin-right: 10px;"/>
                Đăng nhập bằng Google
            </button>
        </div>
        """
        components.html(html_code, height=200)
        st.stop()
        
    # Đoạn này sẽ không bao giờ được gọi nếu chưa đăng nhập (vì có st.stop())


if not user_email:
    st.error("⛔ Truy cập bị từ chối: Không tìm thấy thông tin đăng nhập Gmail của bạn. Vui lòng đăng nhập qua Google để truy cập link báo cáo.")
    st.stop()

# Kiểm tra quyền
user_roles_str = ""
if not df_roles.empty and user_email.lower() in df_roles['email'].str.lower().values:
    user_roles_str = df_roles[df_roles['email'].str.lower() == user_email.lower()]['nganh_hang'].iloc[0]
else:
    st.error(f"⛔ Truy cập bị từ chối: Email **{user_email}** chưa được cấp quyền truy cập Hệ thống. Vui lòng liên hệ Admin.")
    st.stop()

# Xử lý chuỗi quyền thành list
if "Tất cả" in user_roles_str or user_roles_str.strip() == "*":
    user_roles = ["Tất cả"]
else:
    user_roles = [r.strip() for r in user_roles_str.split(",")]

st.sidebar.info(f"👤 **{user_email}**\n\nQuyền hạn: {', '.join(user_roles)}")

# --- BACKEND CACHED DATA ---
@st.cache_data(ttl=86400, show_spinner=False) # Cache 24 hours
def load_master_data():
    client = bigquery.Client(project=PROJECT_ID)
    try:
        query = """
            SELECT ma_san_pham, ten_san_pham, ma_model, ten_model, nganh_hang, phan_tram_vat, vat 
            FROM `powerbi-data-warehouse-500915.retail_dashboard.dim_masterdata`
        """
        df = client.query(query).to_dataframe()
        # Normalize strings for faster searching
        df['search_str'] = df['ten_san_pham'].astype(str).str.lower() + " " + df['ma_san_pham'].astype(str)
        return df
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=1800)
def load_data_nhaphang():
    try:
        client = bigquery.Client(project=PROJECT_ID)
        query = f"SELECT * FROM `{PROJECT_ID}.retail_dashboard.fact_nhap_hang`"
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=1800)
def load_data_doanhthu():
    client = bigquery.Client(project=PROJECT_ID)
    query = """
        SELECT nganh_hang, thang,
            SUM(gia_von_tong) as gia_von_tong, 
            SUM(lai_gop_tong) as lai_gop_tong, 
            SUM(doanh_thu_tong) as doanh_thu_tong
        FROM `powerbi-data-warehouse-500915.retail_dashboard.fact_doanh_thu_xuat_ban`
        GROUP BY nganh_hang, thang
    """
    df = client.query(query).to_dataframe()
    for col in ['doanh_thu_tong', 'lai_gop_tong', 'gia_von_tong']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

@st.cache_data(ttl=1800)
def load_list_nganh():
    client = bigquery.Client(project=PROJECT_ID)
    try:
        query = "SELECT DISTINCT nganh_hang FROM `powerbi-data-warehouse-500915.retail_dashboard.dim_masterdata` WHERE nganh_hang IS NOT NULL"
        df = client.query(query).to_dataframe()
        return sorted(df['nganh_hang'].astype(str).tolist())
    except Exception as e:
        st.error(f"Lỗi tải danh sách ngành hàng: {e}")
        return []

@st.cache_data(ttl=1800)
def load_ds_kho():
    client = bigquery.Client(project=PROJECT_ID)
    try:
        query = "SELECT DISTINCT ten_kho_trung_tam FROM `powerbi-data-warehouse-500915.retail_dashboard.dim_dsst_theo_kho` WHERE ten_kho_trung_tam IS NOT NULL"
        df_kho = client.query(query).to_dataframe()
        return ["Tất cả các Kho"] + df_kho['ten_kho_trung_tam'].tolist()
    except Exception:
        return ["Tất cả các Kho"]

@st.cache_data(ttl=1800)
def load_parquet_data():
    try:
        df = pd.read_parquet("data/master_search_360.parquet")
        # Rename columns to remove "nan | "
        df.columns = [c.replace("nan | ", "") for c in df.columns]
        # Pre-calculate label_sp to save CPU time on every rerun
        if 'Mã sản phẩm cơ sở' in df.columns and 'Tên sản phẩm' in df.columns:
            df['label_sp'] = "[" + df['Mã sản phẩm cơ sở'].astype(str) + "] " + df['Tên sản phẩm'].astype(str)
        # Normalize for search
        if 'Tên sản phẩm' in df.columns and 'Mã sản phẩm' in df.columns and 'Mã sản phẩm cơ sở' in df.columns:
            df['search_str'] = df['Tên sản phẩm'].astype(str).str.lower() + " " + df['Mã sản phẩm'].astype(str) + " " + df['Mã sản phẩm cơ sở'].astype(str)
        return df
    except Exception as e:
        return pd.DataFrame()

with st.spinner("Đang tải dữ liệu từ BigQuery..."):
    df_raw = load_data_doanhthu()
    list_kho_chia_hang = load_ds_kho()

# Lọc dữ liệu theo Quyền (RLS)
if "Tất cả" not in user_roles:
    df_raw = df_raw[df_raw['nganh_hang'].isin(user_roles)]

# --- MULTI-TAB ARCHITECTURE ---
menu_options = ["📊 Báo Cáo Apps Script", "🔍 Tra cứu 360 Độ", "📦 Nhập & Tồn Kho"]
if "Tất cả" in user_roles:
    menu_options.append("⚙️ Quản trị Phân quyền")

st.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("---")
selected_tab = st.sidebar.radio("📌 ĐIỀU HƯỚNG BÁO CÁO", menu_options)
st.markdown("<hr style='margin-top: 0px;'>", unsafe_allow_html=True)

# ==========================================
# TAB 1: DASHBOARD TỔNG QUAN & BẢNG MA TRẬN
# ==========================================
if False: # Da an theo yeu cau cua user
    # --- BỘ LỌC (FILTERS) ---
    st.markdown('<div style="background: var(--bg-card); padding: 15px; border-radius: 12px; margin-bottom: 20px; border: 1px solid var(--border-subtle);">', unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.5, 1.5, 2])
    
    with f_col1:
        che_do = st.radio("CHẾ ĐỘ", ["Xem quý", "So sánh tháng", "So sánh cùng kỳ"], horizontal=True, label_visibility="collapsed")
    with f_col2:
        loai_st = st.selectbox("LOẠI SIÊU THỊ", ["Tất cả siêu thị", "Cũ", "Mới"])
    with f_col3:
        ht_xuat = st.selectbox("HÌNH THỨC XUẤT", ["Tất cả hình thức", "Bán lẻ", "Bán buôn"])
    with f_col4:
        ky_bc = st.select_slider("KỲ BÁO CÁO", options=["T1/2026", "T2/2026", "T3/2026", "T4/2026", "T5/2026", "T6/2026", "T7/2026"], value="T7/2026")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # --- KPI CARDS ---
    st.markdown("""
    <style>
    .kpi-container { display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
    .kpi-card { 
        flex: 1; min-width: 200px; background: var(--bg-card); padding: 15px; 
        border-radius: 12px; border: 1px solid var(--border-subtle);
    }
    .kpi-title { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; margin-bottom: 10px; }
    .kpi-value { font-size: 24px; font-weight: 700; color: #fff; margin-bottom: 5px; }
    .kpi-sub { font-size: 11px; color: var(--text-muted); }
    .badge-red { background: rgba(244, 63, 94, 0.2); color: #f43f5e; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 10px;}
    .badge-green { background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-weight: 600; font-size: 10px;}
    .kpi-highlight { color: #38bdf8; }
    </style>
    <div class="kpi-container">
        <div class="kpi-card" style="border-left: 3px solid #38bdf8;">
            <div class="kpi-title">DT T7/2026</div>
            <div class="kpi-value">5,35 <span style="font-size: 14px">tỷ</span></div>
            <div class="kpi-sub">5.354.037.204.678 đ</div>
            <div style="margin-top: 10px;"><span class="badge-red">▼ 21.8% vs T6/2026</span></div>
            <div style="margin-top: 15px; font-size: 12px; font-weight: 600;">Dự tính tháng: &nbsp; 165,98 tỷ &nbsp; <span class="badge-red">▼ 19.2%</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">HIỆU QUẢ KD T7/2026</div>
            <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; margin-bottom: 5px;">
                <span class="kpi-highlight">Lãi gộp:</span> <span>1,03 tỷ</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-bottom: 15px;">
                <span>Lãi gộp dự tính:</span> <span>31,94 tỷ <span class="badge-red">▼ 1.2%</span></span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600; margin-bottom: 5px;">
                <span>Giá vốn:</span> <span>4,32 tỷ</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted);">
                <span>Giá vốn dự tính:</span> <span>134,03 tỷ <span class="badge-red">▼ 22.6%</span></span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">NHẬP T7/2026</div>
            <div class="kpi-value">9,61 <span style="font-size: 14px">tỷ</span></div>
            <div class="kpi-sub" style="margin-bottom: 10px;">9.614.298.006 đ</div>
            <div><span class="badge-green">▲ 31.4% vs T6/2026</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">HỦY HÀNG (LŨY KẾ)</div>
            <div class="kpi-value">2,07 <span style="font-size: 14px">tỷ</span></div>
            <div class="kpi-sub" style="margin-bottom: 10px;">2.068.161.951 đ</div>
            <div><span style="font-size: 11px; color: var(--text-muted);">— mốc đầu</span></div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">TỒN KHO</div>
            <div class="kpi-value">651,96 <span style="font-size: 14px">tỷ</span></div>
            <div class="kpi-sub" style="margin-bottom: 10px;">651.955.552.387.474 đ</div>
            <div style="display: flex; justify-content: space-between; font-size: 11px; margin-top: 15px;">
                <div style="text-align: center;"><div style="color: var(--text-muted);">Mới</div><div style="color: #38bdf8; font-weight: 600;">638.18T</div></div>
                <div style="text-align: center;"><div style="color: var(--text-muted);">Cận Date</div><div style="color: #fbbf24; font-weight: 600;">10.79T</div></div>
                <div style="text-align: center;"><div style="color: var(--text-muted);">Hết Date</div><div style="color: #f43f5e; font-weight: 600;">2.99T</div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- BIỂU ĐỒ (CHARTS) ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div style="background: var(--bg-card); padding: 15px; border-radius: 12px; border: 1px solid var(--border-subtle);">', unsafe_allow_html=True)
        st.markdown("**Tổng doanh thu theo tháng đã chọn**")
        if not df_raw.empty:
            df_trend = df_raw.groupby('thang', as_index=False)['doanh_thu_tong'].sum().sort_values('thang')
            fig1 = px.bar(df_trend, x='thang', y='doanh_thu_tong', text_auto='.2s', color_discrete_sequence=['#38bdf8'])
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1', height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div style="background: var(--bg-card); padding: 15px; border-radius: 12px; border: 1px solid var(--border-subtle);">', unsafe_allow_html=True)
        st.markdown("**Cơ cấu ngành hàng theo tháng**")
        if not df_raw.empty:
            df_ind = df_raw.groupby('nganh_hang', as_index=False)['doanh_thu_tong'].sum().sort_values('doanh_thu_tong', ascending=False).head(7)
            fig2 = px.bar(df_ind, x='nganh_hang', y='doanh_thu_tong', text_auto='.2s', color_discrete_sequence=['#c084fc'])
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1', height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("TỔNG CỘNG & SO SÁNH TARGET")
    
    if not df_raw.empty:
        # Giả lập dữ liệu Bảng Ma Trận từ df_raw (Vì chưa có Data Target và data 2025 đầy đủ)
        # Trong thực tế sẽ JOIN với df_target và df_2025
        
        # 1. Pivot dữ liệu thực tế theo tháng
        df_pivot = df_raw.pivot_table(index='nganh_hang', columns='thang', values='doanh_thu_tong', aggfunc='sum').fillna(0)
        
        # Sắp xếp các cột tháng (T1, T2...)
        months = sorted(df_pivot.columns.tolist())
        
        # Tạo bảng hiển thị
        df_display = pd.DataFrame(index=df_pivot.index)
        
        # Sinh số liệu giả lập cho các cột phức tạp để tạo giao diện
        import numpy as np
        np.random.seed(42)
        df_display['SSG CÙNG KỲ'] = np.random.uniform(-0.5, 3.5, len(df_display)) # Sinh số ngẫu nhiên từ -50% đến 350%
        df_display['SSG LIỀN KỀ'] = np.random.uniform(-0.2, 2.5, len(df_display))
        df_display['TARGET LK 2026'] = df_pivot.sum(axis=1) * np.random.uniform(1.1, 1.5, len(df_display))
        df_display['TT LŨY KẾ'] = df_pivot.sum(axis=1)
        df_display['% HT TARGET'] = df_display['TT LŨY KẾ'] / df_display['TARGET LK 2026']
        
        # Nối các cột tháng vào
        for m in months:
            df_display[m] = df_pivot[m]
            
        # Tính dòng TOTAL
        total_row = df_display.sum()
        # Tính lại tỷ lệ cho dòng Total
        total_row['SSG CÙNG KỲ'] = np.random.uniform(0.5, 2.5) 
        total_row['SSG LIỀN KỀ'] = np.random.uniform(0.1, 1.5)
        total_row['% HT TARGET'] = total_row['TT LŨY KẾ'] / total_row['TARGET LK 2026']
        
        df_display.loc['TOTAL'] = total_row
        
        # Đưa dòng TOTAL lên đầu
        df_display = df_display.reindex(['TOTAL'] + [idx for idx in df_display.index if idx != 'TOTAL'])
        
        # 2. Hàm Format Màu Sắc (Pandas Styler)
        def style_ssg(val):
            if val > 0:
                return 'color: #00E676; font-weight: bold;' # Xanh lá
            elif val < 0:
                return 'color: #FF5252; font-weight: bold;' # Đỏ
            return ''
            
        def format_ssg_text(val):
            if val > 0:
                return f"▲ {val*100:,.1f}%".replace(',', 'X').replace('.', ',').replace('X', '.')
            elif val < 0:
                return f"▼ {abs(val)*100:,.1f}%".replace(',', 'X').replace('.', ',').replace('X', '.')
            return "0,0%"
            
        def format_vnd(val):
            return f"{val/1_000_000:,.0f}".replace(',', '.')
            
        # Format hiển thị
        format_dict = {
            'SSG CÙNG KỲ': format_ssg_text,
            'SSG LIỀN KỀ': format_ssg_text,
            '% HT TARGET': lambda x: f"{x*100:,.1f}%".replace(',', 'X').replace('.', ',').replace('X', '.'),
            'TARGET LK 2026': format_vnd,
            'TT LŨY KẾ': format_vnd,
        }
        for m in months:
            format_dict[m] = format_vnd
            
        # Áp dụng Styler
        styled_df = df_display.style.format(format_dict) \
            .map(style_ssg, subset=['SSG CÙNG KỲ', 'SSG LIỀN KỀ']) \
            .set_properties(**{'background-color': '#1e293b', 'color': '#f8fafc', 'border': '1px solid #334155'}) \
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#0f172a'), ('color', '#38bdf8'), ('font-weight', 'bold'), ('text-align', 'center')]},
                {'selector': 'th.row_heading', 'props': [('background-color', '#0f172a'), ('color', '#f8fafc')]},
            ])

        # Cố định cột đầu (Ngành hàng)
        st.dataframe(styled_df, use_container_width=True, height=500)
        
        st.info("💡 Lưu ý: Cột Cùng kỳ, Liền kề và Target đang dùng số liệu giả lập vì chưa đồng bộ Target và data 2025 vào BigQuery.")
    else:
        st.warning("Không có dữ liệu hoặc bạn không có quyền truy cập.")

# ==========================================
# TAB 2: TRA CỨU SẢN PHẨM (BIGQUERY / PARQUET)
# ==========================================
if selected_tab == menu_options[1]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Tra cứu 360 Độ (Dữ liệu tĩnh)")
    
    with st.spinner("Đang tải dữ liệu tĩnh siêu tốc..."):
        df_master = load_parquet_data()
        
    if not df_master.empty:
        # ÁP DỤNG RLS
        if "Tất cả" not in user_roles and "*" not in user_roles:
            df_master = df_master[df_master['Ngành hàng'].isin(user_roles)]
            
    if not df_master.empty:
        # TÍNH TOÁN KPI SNTK
        import pandas as pd
        def safe_sum(col):
            if col in df_master.columns:
                return pd.to_numeric(df_master[col].astype(str).str.replace(',', '').str.replace(' ', ''), errors='coerce').fillna(0).sum()
            return 0
            
        tong_ton = safe_sum('Total   Tổng tồn Siêu Thị ( HDD + CO )') + safe_sum('Total   Tổng tồn Kho ( HDD + CO )')
        tong_sb = safe_sum('Tổng SB')
        sntk_sl = tong_ton / tong_sb if tong_sb > 0 else 0
        
        gt_ton_col = [c for c in df_master.columns if 'Tổng Giá trị  tồn' in c and '|' in c and c.split('|')[0].strip().startswith('T')]
        ds_ban_col = [c for c in df_master.columns if 'DS bán giá vốn' in c and '|' in c and c.split('|')[0].strip().startswith('T')]
        
        gt_ton = safe_sum(gt_ton_col[0]) if gt_ton_col else 0
        ds_ban = safe_sum(ds_ban_col[0]) if ds_ban_col else 0
        sntk_gt = gt_ton / ds_ban if ds_ban > 0 else 0
        
        # DEBUG LOG
        with open("debug_sntk.txt", "w", encoding="utf-8") as f:
            f.write(f"gt_ton_col: {gt_ton_col}\n")
            f.write(f"ds_ban_col: {ds_ban_col}\n")
            f.write(f"gt_ton: {gt_ton}\n")
            f.write(f"ds_ban: {ds_ban}\n")
            f.write(f"sntk_gt: {sntk_gt}\n")
        
        # HIỂN THỊ KPI CARDS
        kpi_col1, kpi_col2, _, _ = st.columns(4)
        with kpi_col1:
            st.markdown(f'''
                <div style="background-color:#7c3aed; padding:15px; border-radius:10px; color:white; text-align:center;">
                    <h3 style="margin:0; font-size:24px;">{sntk_sl:,.2f}</h3>
                    <p style="margin:0; font-size:14px; opacity:0.9;">SNTK Số lượng</p>
                </div>
            ''', unsafe_allow_html=True)
            
        with kpi_col2:
            st.markdown(f'''
                <div style="background-color:#10b981; padding:15px; border-radius:10px; color:white; text-align:center;">
                    <h3 style="margin:0; font-size:24px;">{sntk_gt:,.2f}</h3>
                    <p style="margin:0; font-size:14px; opacity:0.9;">SNTK Giá trị</p>
                </div>
            ''', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)

    
    if df_master.empty:
        st.warning("⚠️ Chưa có dữ liệu Parquet! Vui lòng dùng Admin Panel chạy tính toán để sinh file trước.")
    else:
        # --- BỘ LỌC TÌM KIẾM ---
        f2_col1, f2_col2, f2_col3, f2_col4 = st.columns(4)
        
        # 1. Lọc Ngành Hàng
        list_nganh = sorted([str(x) for x in df_master['Ngành hàng'].dropna().unique()]) if 'Ngành hàng' in df_master.columns else []
        with f2_col1:
            loc_nganh = st.multiselect("Lọc Ngành hàng", list_nganh, placeholder="Choose options")
            
        df_filtered = df_master
        if loc_nganh:
            df_filtered = df_filtered[df_filtered['Ngành hàng'].isin(loc_nganh)]
            
        # 2. Lọc Nhóm Hàng
        list_nhom = sorted([str(x) for x in df_filtered['Nhóm hàng'].dropna().unique()]) if 'Nhóm hàng' in df_filtered.columns else []
        with f2_col2:
            loc_nhom = st.multiselect("Lọc Nhóm hàng", list_nhom, placeholder="Choose options")
            
        if loc_nhom:
            df_filtered = df_filtered[df_filtered['Nhóm hàng'].isin(loc_nhom)]
            
        # 3. Lọc Sản Phẩm
        if not df_filtered.empty and 'label_sp' in df_filtered.columns:
            # Dùng label_sp đã được pre-calculate trong load_parquet_data() để giảm thiểu độ trễ
            list_sp = sorted(df_filtered['label_sp'].dropna().unique())
        else:
            list_sp = []
            
        with f2_col3:
            # Đã gỡ bỏ giới hạn 1000 để user search thoải mái
            loc_sp = st.multiselect("Lọc Sản phẩm", list_sp, placeholder="Choose options")
            
        if loc_sp:
            df_filtered = df_filtered[df_filtered['label_sp'].isin(loc_sp)]
            
        # 4. Lọc Kho
        khos_all = sorted(list(set([c.split(" | ")[0] for c in df_master.columns if " | " in c and "-" in c.split(" | ")[0]])))
        with f2_col4:
            loc_kho = st.multiselect("Lọc Kho", khos_all, placeholder="Choose options")
            
        st.markdown("---")
        
        if not df_filtered.empty:
            # Hàm tiện ích làm sạch chuỗi số bằng regex
            def clean_num_series(series):
                return pd.to_numeric(series.astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0)
                
            # --- THÔNG TIN CHI TIẾT SẢN PHẨM ---
            st.subheader("Thông tin chi tiết Sản phẩm")
            
            # Khai báo các cột hiển thị theo yêu cầu
            info_cols_map = {
                "Ngành hàng": "Ngành hàng",
                "Nhóm hàng": "Nhóm hàng",
                "GIÁM ĐỐC MUA HÀNG": "Giám đốc mua hàng",
                "BUYER MUA HÀNG": "Buyer mua hàng",
                "Mã Model": "Model",
                "Mã sản phẩm": "Mã SP (Quy cách lớn)",
                "Mã sản phẩm cơ sở": "Mã SP cơ sở",
                "Tên sản phẩm": "Tên sản phẩm",
                "Phần trăm VAT": "VAT",
                "Trạng thái kinh doanh của sản phẩm": "Trạng thái kinh doanh",
                "ĐVT QC lớn": "DVT Quy cách lớn",
                "Đơn vị tính cơ sở": "Đơn vị cơ sở",
                "Quy đổi": "Quy đổi",
                "Giá bán ĐVL": "Giá bán ĐVL",
                "Giá bán ĐVN": "Giá bán (Cơ sở)",
                "Giá BQGQ": "Giá BQGQ",
                "Front": "Front",
                "Tỷ lệ Front": "Tỉ lệ Front"
            }
            
            available_cols = [c for c in info_cols_map.keys() if c in df_filtered.columns]
            if available_cols:
                # Group by 'Tên sản phẩm' để lấy info duy nhất
                df_info = df_filtered[available_cols].drop_duplicates(subset=['Tên sản phẩm']).copy()
                
                # BẢN ĐỂ XUẤT EXCEL (Giữ nguyên định dạng số nguyên thủy)
                df_excel = df_info.copy()
                rename_dict = {k: v for k, v in info_cols_map.items()}
                df_excel = df_excel.rename(columns=rename_dict)
                
                # BẢN ĐỂ HIỂN THỊ WEB (Format đẹp)
                # Format các cột tiền tệ
                money_cols = ["Giá bán ĐVN", "Giá BQGQ", "Giá bán ĐVL"]
                for mc in money_cols:
                    if mc in df_info.columns:
                        df_info[mc] = clean_num_series(df_info[mc]).apply(lambda x: f"{x:,.0f}" if pd.notnull(x) and x > 0 else "-")
                        
                # Format Front (Lấy 2 thập phân)
                if "Front" in df_info.columns:
                    df_info["Front"] = clean_num_series(df_info["Front"]).apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "-")
                    
                # Format phần trăm (Nhân 100 và thêm %)
                pct_cols = ["Tỷ lệ Front", "Phần trăm VAT"]
                for pc in pct_cols:
                    if pc in df_info.columns:
                        df_info[pc] = clean_num_series(df_info[pc]).apply(lambda x: f"{x*100:,.2f}%" if pd.notnull(x) else "-")

                # Đổi tên cột cho trực quan
                df_info = df_info.rename(columns=rename_dict)
            
                # Hiển thị bảng
                st.dataframe(df_info, use_container_width=True, hide_index=True)
                
                # Tạo nút xuất Excel
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_excel.to_excel(writer, index=False, sheet_name='Chi Tiet San Pham')
                
                st.download_button(
                    label="📥 Tải Excel Thông Tin Sản Phẩm",
                    data=buffer.getvalue(),
                    file_name="thong_tin_san_pham.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
                
            # --- HIỂN THỊ BẢNG CHI TIẾT ---
            st.subheader("Thống kê Tồn kho theo Kho/Siêu thị")
            
            khos_to_process = loc_kho if loc_kho else khos_all
            frames = []
            
            for k in khos_to_process:
                # Kiểm tra xem kho này có cột Sức bán hoặc Tổng tồn kho không
                if f"{k} | TỔNG TỒN KHO" not in df_filtered.columns:
                    continue
                    
                # Trích xuất dữ liệu của Kho k
                temp_df = pd.DataFrame()
                temp_df["Tên sản phẩm"] = df_filtered.get('Tên sản phẩm', 'N/A').astype(str)
                temp_df["Kho/Siêu thị"] = str(k)
                
                # Ép kiểu numeric tốc độ cao
                ton_col = clean_num_series(df_filtered.get(f"{k} | TỔNG TỒN KHO", 0))
                sb_col = clean_num_series(df_filtered.get(f"{k} | Sức bán", 0))
                
                temp_df["Sức bán"] = sb_col
                temp_df["Tổng tồn kho"] = ton_col
                
                # Chỉ lấy các dòng có Tồn Kho > 0 hoặc Sức Bán > 0 (Tối ưu RAM)
                valid_mask = (temp_df["Tổng tồn kho"] > 0) | (temp_df["Sức bán"] > 0)
                if not valid_mask.any():
                    continue
                    
                # Gán các cột còn lại
                temp_df["Tồn kho mới"] = clean_num_series(df_filtered.get(f"{k} | Tổng tồn Kho ( HDD + CO ) Mới", 0))
                temp_df["Tồn kho cận"] = clean_num_series(df_filtered.get(f"{k} | Tổng tồn Kho ( HDD + CO ) Cận date", 0))
                temp_df["Tồn siêu thị mới"] = clean_num_series(df_filtered.get(f"{k} | Tổng tồn Siêu Thị ( HDD + CO ) Mới", 0))
                temp_df["Tồn siêu thị cận"] = clean_num_series(df_filtered.get(f"{k} | Tổng tồn Siêu Thị ( HDD + CO ) Cận date", 0))
                temp_df["Tổng giá trị"] = clean_num_series(df_filtered.get(f"{k} | TỔNG TỒN KHO_1", 0))
                temp_df["Giá trị kho mới"] = clean_num_series(df_filtered.get(f"{k} | Tổng tồn Kho ( HDD + CO ) Mới_1", 0))
                temp_df["Giá trị kho cận"] = clean_num_series(df_filtered.get(f"{k} | Tổng tồn Kho ( HDD + CO ) Cận date_1", 0))
                temp_df["Giá trị ST mới"] = clean_num_series(df_filtered.get(f"{k} | Tổng tồn Siêu Thị ( HDD + CO ) Mới_1", 0))
                temp_df["Giá trị ST cận"] = clean_num_series(df_filtered.get(f"{k} | Tổng tồn Siêu Thị ( HDD + CO ) Cận date_1", 0))
                temp_df["Có tồn"] = clean_num_series(df_filtered.get(f"{k} | Có tồn", 0))
                temp_df["Siêu thị có DM"] = clean_num_series(df_filtered.get(f"{k} | Siêu thị có DM", 0))
                
                # Áp dụng mask
                temp_df = temp_df[valid_mask]
                frames.append(temp_df)
            
            if not frames:
                st.info("Không có dữ liệu Tồn kho/Sức bán cho các lựa chọn trên.")
            else:
                df_kho_display = pd.concat(frames, ignore_index=True)
                
                # Sắp xếp cho đẹp
                df_kho_display = df_kho_display.sort_values(by=["Tổng tồn kho", "Sức bán"], ascending=[False, False])
                
                # Format hiển thị (nếu >0 thì định dạng có phẩy, ngược lại hiện "-")
                cols_to_format = [c for c in df_kho_display.columns if c not in ["Tên sản phẩm", "Kho/Siêu thị"]]
                for col in cols_to_format:
                    df_kho_display[col] = df_kho_display[col].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")
                    
                # Hiển thị bảng
                st.dataframe(df_kho_display, use_container_width=True, hide_index=True)



        st.markdown("---")
        st.subheader("Bảng Phân tích SKU theo Trạng thái kinh doanh")
        
        if 'Trạng thái kinh doanh của sản phẩm' in df_master.columns and 'Ngành hàng' in df_master.columns:
            pivot_df = pd.crosstab(
                df_master['Ngành hàng'], 
                df_master['Trạng thái kinh doanh của sản phẩm']
            ).fillna(0).astype(int)
            
            # Add margins manually to avoid PyArrow schema inference bugs with pd.crosstab margins
            pivot_df['Grand Total'] = pivot_df.sum(axis=1)
            pivot_df.loc['Grand Total'] = pivot_df.sum(axis=0)
            
            if 'Grand Total' in pivot_df.columns and 'Grand Total' in pivot_df.index:
                sorted_cols = pivot_df.loc['Grand Total'].drop('Grand Total').sort_values(ascending=False).index.tolist()
                sorted_cols.append('Grand Total')
                sorted_rows = pivot_df['Grand Total'].drop('Grand Total').sort_values(ascending=False).index.tolist()
                sorted_rows.append('Grand Total')
                pivot_df = pivot_df.loc[sorted_rows, sorted_cols]
                
            pivot_df.index.name = None
            pivot_df.columns.name = None
                
            # Format numbers with commas
            styled_pivot = pivot_df.style.format("{:,}")\
                .set_properties(**{
                    'background-color': '#1e293b',
                    'color': 'white',
                    'border': '1px solid #334155'
                })\
                .apply(lambda x: ['color: #ef4444; font-weight: bold' if x.name == 'Grand Total' or col == 'Grand Total' else '' for col in x.index], axis=1)\
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#10b981'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center')]},
                    {'selector': 'th.row_heading', 'props': [('background-color', '#0f172a'), ('color', 'white'), ('font-weight', 'bold')]}
                ])
                
            st.dataframe(styled_pivot, use_container_width=True)
        else:
            st.info("Chưa đủ dữ liệu (Ngành hàng, Trạng thái kinh doanh) để hiển thị bảng.")


# ==========================================
# TAB 3: NHẬP VÀ TỒN KHO 
# ==========================================
if selected_tab == menu_options[2]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📦 Quản lý Dữ liệu Phiếu Nhập & Phân tích IN/OUT")
    
    with st.container():
        st.markdown("### 📊 Phân tích Tỷ lệ Nhập / Xuất (IN/OUT)")
        
        # Load dữ liệu Nhập từ BigQuery
        df_nhap = load_data_nhaphang()
        
        if df_nhap.empty:
            st.info("Chưa có dữ liệu Nhập Hàng. Vui lòng sang Tab '2. Upload Phiếu Nhập' để cập nhật dữ liệu từ file Excel.")
        else:
            # Load dữ liệu Bán từ df_raw (đã load ở đầu script)
            # df_raw có 'ma_san_pham', 'doanh_thu_tong', 'so_luong' (nếu có cột số lượng), 'thang', 'nganh_hang'
            
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            with c1:
                # Lọc theo Ngành Hàng
                list_nganh = ["Tất cả"] + sorted(df_nhap['nganh_hang'].dropna().unique().tolist()) if 'nganh_hang' in df_nhap.columns else ["Tất cả"]
                loc_nganh = st.selectbox("Chọn Ngành Hàng:", list_nganh)
            
            with c2:
                # Lọc theo NCC
                list_ncc = ["Tất cả"] + sorted(df_nhap['nha_cung_cap'].dropna().unique().tolist()) if 'nha_cung_cap' in df_nhap.columns else ["Tất cả"]
                loc_ncc = st.selectbox("Chọn Nhà Cung Cấp:", list_ncc)
                
            with c3:
                # Chọn Tháng/Năm
                list_thang = ["Tất cả"] + sorted(df_nhap['thang_nam'].dropna().unique().tolist()) if 'thang_nam' in df_nhap.columns else ["Tất cả"]
                loc_thang = st.selectbox("Chọn Tháng:", list_thang)
                
            with c4:
                # Tìm kiếm Model / Mã SP
                search_text = st.text_input("Tìm kiếm Model / Tên / Mã SP:")
                
            # Xử lý lọc dữ liệu Nhập
            df_nhap_filter = df_nhap.copy()
            if loc_nganh != "Tất cả" and 'nganh_hang' in df_nhap_filter.columns:
                df_nhap_filter = df_nhap_filter[df_nhap_filter['nganh_hang'] == loc_nganh]
            if loc_ncc != "Tất cả" and 'nha_cung_cap' in df_nhap_filter.columns:
                df_nhap_filter = df_nhap_filter[df_nhap_filter['nha_cung_cap'] == loc_ncc]
            if loc_thang != "Tất cả" and 'thang_nam' in df_nhap_filter.columns:
                df_nhap_filter = df_nhap_filter[df_nhap_filter['thang_nam'] == loc_thang]
            if search_text:
                mask = df_nhap_filter.apply(lambda row: row.astype(str).str.contains(search_text, case=False).any(), axis=1)
                df_nhap_filter = df_nhap_filter[mask]
                
            st.markdown("---")
            
            # --- TÍNH TỔNG (SUM) ---
            # Group by Tháng/Năm, Ngành hàng, Model, Mã SP, Tên SP, Tên khách hàng (NCC)
            group_cols = [c for c in ['thang_nam', 'nganh_hang', 'model', 'ma_san_pham', 'ten_san_pham', 'nha_cung_cap'] if c in df_nhap_filter.columns]
            
            if not df_nhap_filter.empty and group_cols:
                # Sum các cột metric (Loại bỏ tong_so_luong_nhap theo yêu cầu)
                agg_dict = {}
                for m in ['tong_sl_quy_doi', 'tong_gia_tri_nhap']:
                    if m in df_nhap_filter.columns:
                        agg_dict[m] = 'sum'
                        
                df_report = df_nhap_filter.groupby(group_cols, as_index=False).agg(agg_dict)
                
                # Ép kiểu Model và Mã sản phẩm về dạng String để tránh bị dấu phẩy số (e.g. 1,607,000,031)
                for col in ['model', 'ma_san_pham']:
                    if col in df_report.columns:
                        df_report[col] = df_report[col].apply(lambda x: str(x).replace('.0', '').replace(',', ''))
                
                # --- ĐỐI CHIẾU VỚI DỮ LIỆU BÁN (OUT) TỪ BIGQUERY ---
                df_ban_sum = pd.DataFrame()
                
                if loc_thang != "Tất cả":
                    # Chuyển đổi định dạng tháng (VD: 7/2026 -> 2026/T07)
                    parts = loc_thang.split('/')
                    if len(parts) == 2:
                        mm = int(parts[0])
                        yyyy = parts[1]
                        dt_thang = f"{yyyy}/T{mm:02d}"
                        
                        try:
                            client = bigquery.Client(project=PROJECT_ID)
                            query = f"""
                                SELECT 
                                    CAST(ma_item AS STRING) as ma_san_pham,
                                    SUM(CAST(so_luong_co_so_tong AS FLOAT64)) as tong_ban_ra,
                                    SUM(CAST(doanh_thu_tong AS FLOAT64)) as tong_doanh_thu_ban
                                FROM `powerbi-data-warehouse-500915.retail_dashboard.fact_doanh_thu_xuat_ban`
                                WHERE thang = '{dt_thang}'
                                GROUP BY ma_item
                            """
                            df_ban_sum = client.query(query).to_dataframe()
                        except Exception as e:
                            st.warning(f"Không thể tải số liệu bán ra cho tháng {dt_thang}: {e}")
                            
                else:
                    st.info("💡 Mẹo: Hãy chọn một Tháng cụ thể để hệ thống có thể tính toán số lượng Bán Ra và tỷ lệ IN/OUT.")
                    
                if not df_ban_sum.empty:
                    # Đảm bảo kiểu dữ liệu giống nhau
                    df_ban_sum['ma_san_pham'] = df_ban_sum['ma_san_pham'].apply(lambda x: str(x).replace('.0', '').replace(',', ''))
                    
                    # Merge vào bảng báo cáo Nhập
                    df_report = pd.merge(df_report, df_ban_sum, on='ma_san_pham', how='left')
                    df_report['tong_ban_ra'] = df_report['tong_ban_ra'].fillna(0)
                    df_report['tong_doanh_thu_ban'] = df_report['tong_doanh_thu_ban'].fillna(0)
                    
                    # Tính tỷ lệ IN / OUT
                    if 'tong_sl_quy_doi' in df_report.columns:
                        df_report['ty_le_ban_nhap'] = np.where(
                            df_report['tong_sl_quy_doi'] > 0,
                            (df_report['tong_ban_ra'] / df_report['tong_sl_quy_doi']),
                            0
                        )
                else:
                    df_report['tong_ban_ra'] = 0
                    df_report['tong_doanh_thu_ban'] = 0
                    df_report['ty_le_ban_nhap'] = 0
                
                # Sắp xếp và định dạng bảng hiển thị cho giống Google Sheet
                display_rename = {
                    'thang_nam': 'Tháng/Năm',
                    'nganh_hang': 'Ngành hàng',
                    'model': 'Model',
                    'ma_san_pham': 'Mã sản phẩm',
                    'ten_san_pham': 'Tên sản phẩm',
                    'nha_cung_cap': 'Nhà cung cấp',
                    'tong_gia_tri_nhap': 'Tổng giá trị nhập (Vốn)',
                    'tong_sl_quy_doi': 'Tổng SL Nhập',
                    'tong_ban_ra': 'Tổng SL Đã Bán',
                    'tong_doanh_thu_ban': 'Doanh thu Bán',
                    'ty_le_ban_nhap': 'Tỷ lệ IN/OUT'
                }
                
                df_display = df_report.rename(columns=display_rename)
                
                # Format hiển thị số liệu
                if 'Tổng giá trị nhập (Vốn)' in df_display.columns:
                    df_display['Tổng giá trị nhập (Vốn)'] = df_display['Tổng giá trị nhập (Vốn)'].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")
                if 'Doanh thu Bán' in df_display.columns:
                    df_display['Doanh thu Bán'] = df_display['Doanh thu Bán'].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")
                if 'Tỷ lệ IN/OUT' in df_display.columns:
                    df_display['Tỷ lệ IN/OUT'] = df_display['Tỷ lệ IN/OUT'].apply(lambda x: f"{x*100:,.1f}%" if x > 0 else "-")
                if 'Tổng SL Nhập' in df_display.columns:
                    df_display['Tổng SL Nhập'] = df_display['Tổng SL Nhập'].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")
                if 'Tổng SL Đã Bán' in df_display.columns:
                    df_display['Tổng SL Đã Bán'] = df_display['Tổng SL Đã Bán'].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")
                    
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.warning("Không tìm thấy dữ liệu khớp với bộ lọc!")
# TAB APPS SCRIPT
# ==========================================
if selected_tab == menu_options[0]:
    st.markdown("<br>", unsafe_allow_html=True)
    app_script_url = "https://script.google.com/macros/s/AKfycbx2Xs6-OO5OUmcfdD5yfhq2mZdmzMV089rITuCsNpdmy1ZrlKXF1WCTgopIk2u1IXCq/exec"
    st.components.v1.iframe(app_script_url, height=900, scrolling=True)

# ==========================================
# TAB 4: QUẢN TRỊ PHÂN QUYỀN (ADMIN ONLY)
# ==========================================
if "Tất cả" in user_roles and "⚙️ Quản trị Phân quyền" in menu_options:
    if selected_tab == "⚙️ Quản trị Phân quyền":
        st.subheader("⚙️ Bảng Phân Quyền Nhân Sự")
        st.info("Chỉnh sửa trực tiếp trên bảng và bấm Lưu để cập nhật lên BigQuery. Nhập 'Tất cả' ở cột nganh_hang để cấp full quyền.")
    
        # Trả lại dạng Text để hiển thị được chuỗi nhiều ngành (vd: "Thuốc, Tã")
        if not df_roles.empty:
            if not df_master.empty and 'Ngành hàng' in df_master.columns:
                valid_nganh = ["Tất cả"] + sorted(df_master['Ngành hàng'].dropna().unique().tolist())
            else:
                valid_nganh = ["Tất cả", "Thực Phẩm Chức Năng", "Thuốc", "Trang Thiết Bị Y Tế", "Mỹ phẩm các loại"]
            
            # --- CÔNG CỤ CẤP QUYỀN NHIỀU NGÀNH ---
            st.markdown("---")
            st.markdown("### 🛠️ Bộ công cụ Cấp quyền Nhiều ngành")
            with st.form("multi_role_form"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    input_email = st.text_input("Nhập Email nhân sự:")
                with c2:
                    selected_nganh = st.multiselect("Chọn các ngành hàng:", valid_nganh)
                
                c_btn1, c_btn2 = st.columns([1, 1])
                with c_btn1:
                    submit_btn = st.form_submit_button("Cấp quyền cho Email này", type="primary")
                with c_btn2:
                    delete_btn = st.form_submit_button("Xóa quyền Email này")
                
                if submit_btn:
                    if input_email and selected_nganh:
                        nganh_str = ", ".join(selected_nganh)
                        # Cập nhật df_roles
                        if input_email in df_roles['email'].values:
                            df_roles.loc[df_roles['email'] == input_email, 'nganh_hang'] = nganh_str
                        else:
                            new_row = pd.DataFrame({'email': [input_email], 'nganh_hang': [nganh_str]})
                            df_roles = pd.concat([df_roles, new_row], ignore_index=True)
                        
                        with st.spinner("Đang lưu phân quyền lên BigQuery..."):
                            try:
                                client = bigquery.Client(project=PROJECT_ID)
                                job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
                                job = client.load_table_from_dataframe(df_roles, "powerbi-data-warehouse-500915.retail_dashboard.dim_user_roles", job_config=job_config)
                                job.result() # Wait for job to finish
                                st.success(f"✅ Đã cấp quyền thành công cho {input_email}! Hãy tải lại trang (F5).")
                                load_user_roles.clear()
                            except Exception as e:
                                st.error(f"Lỗi: {e}")
                    else:
                        st.warning("Vui lòng nhập Email và chọn ít nhất 1 ngành.")
                        
                if delete_btn:
                    if input_email:
                        if input_email in df_roles['email'].values:
                            df_roles = df_roles[df_roles['email'] != input_email]
                            with st.spinner("Đang xóa quyền trên BigQuery..."):
                                try:
                                    client = bigquery.Client(project=PROJECT_ID)
                                    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
                                    job = client.load_table_from_dataframe(df_roles, "powerbi-data-warehouse-500915.retail_dashboard.dim_user_roles", job_config=job_config)
                                    job.result()
                                    st.success(f"✅ Đã XÓA quyền thành công cho {input_email}! Hãy tải lại trang (F5).")
                                    load_user_roles.clear()
                                except Exception as e:
                                    st.error(f"Lỗi: {e}")
                        else:
                            st.warning(f"Không tìm thấy Email {input_email} trong hệ thống.")
                    else:
                        st.warning("Vui lòng nhập Email cần xóa.")
            st.markdown("---")
            st.markdown("### 📋 Bảng Phân Quyền Hiện Tại")
            
            df_edit = st.data_editor(
                df_roles, 
                num_rows="dynamic", 
                use_container_width=True, 
                key="roles_editor_table"
            )
        
            if st.button("Lưu Phân Quyền"):
                with st.spinner("Đang lưu lên BigQuery..."):
                    # Sử dụng pandas-gbq thông qua to_gbq
                    try:
                        client = bigquery.Client(project=PROJECT_ID)
                        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
                        job = client.load_table_from_dataframe(df_edit, "powerbi-data-warehouse-500915.retail_dashboard.dim_user_roles", job_config=job_config)
                        job.result()
                        st.success("✅ Đã lưu thành công! Hãy tải lại trang để áp dụng.")
                        load_user_roles.clear()
                    except Exception as e:
                        st.error(f"Lỗi khi lưu lên BigQuery: {e}")
        else:
            st.warning("Không lấy được dữ liệu phân quyền từ BigQuery.")

