import streamlit as st


import pandas as pd


import plotly.express as px


import plotly.graph_objects as go


import datetime





# --- Cấu hình trang ---


st.set_page_config(page_title="Báo Cáo An Khang", page_icon="🌿", layout="wide")





import traceback


try:


    


    st.html("""


    <style>


    .ak-banner {


        background-color: #008c44;


        padding: 15px 20px;


        display: flex;


        align-items: center;


        border-radius: 10px;


        margin-top: -30px;


        margin-bottom: 25px;


        box-shadow: 0 4px 10px rgba(0,0,0,0.1);


    }


    .ak-banner img {


        height: 50px;


        margin-right: 20px;


    }


    .ak-banner h1 {


        color: white !important;


        margin: 0;


        font-size: 26px;


        font-family: sans-serif;


        font-weight: bold;


    }


    .ak-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 14px; margin-bottom: 20px; }


    .ak-table th { background-color: #008c44 !important; color: white !important; font-weight: bold; text-align: center; padding: 10px; border: 1px solid #ddd; position: sticky; top: 0; z-index: 1; }


    .ak-table td { padding: 8px; border: 1px solid #ddd; text-align: right; }


    .ak-table tr:nth-child(even) { background-color: rgba(0,0,0,0.02); }


    .ak-table tr:hover { background-color: rgba(0,140,68,0.1); }


    </style>


    


    <div class="ak-banner">


        <img src="https://cdn.tgdd.vn/mwgcart/ankhang/images/logo.png" onerror="this.src='https://www.nhathuocankhang.com/images/logo.png'">


        <h1>BÁO CÁO KINH DOANH AN KHANG</h1>


    </div>


    """)


    


    # Chuyển sang dùng CSV để né lỗi Crash ngầm của thư viện PyArrow trên Streamlit Cloud


    @st.cache_data(ttl=300)


    def load_data(f_master='master.csv', f_monthly='monthly.csv', f_inv='inventory.csv'):


        # Dùng engine 'c' của Pandas rất ổn định, không dùng pyarrow


        df_master = pd.read_csv(f_master, low_memory=False)


        df_monthly = pd.read_csv(f_monthly, low_memory=False)


        df_inv = pd.read_csv(f_inv, low_memory=False)


        


        # Ép kiểu Category để tiết kiệm RAM


        for col in ['ma_sp', 'thang', 'nganh_hang', 'nhom_hang']:


            if col in df_monthly.columns: df_monthly[col] = df_monthly[col].astype('category')


            


        for col in ['ma_sp', 'ten_sp', 'kho', 'nganh_hang', 'nhom_hang']:


            if col in df_inv.columns: df_inv[col] = df_inv[col].astype('category')


            


        for col in ['ma_sp', 'ten_sp', 'nganh_hang', 'nhom_hang', 'giam_doc_mua', 'buyer', 'ma_model', 'trang_thai_kd']:


            if col in df_master.columns: df_master[col] = df_master[col].astype('category')


        


        # Merge master with monthly


        df_m = pd.merge(df_monthly, df_master[['ma_sp', 'nganh_hang', 'nhom_hang']], on='ma_sp', how='left')


        # Merge master with inv


        df_i = pd.merge(df_inv, df_master[['ma_sp', 'nganh_hang', 'nhom_hang', 'ten_sp']], on='ma_sp', how='left')


        


        return df_master, df_m, df_i


    


    # --- Sidebar: Upload Dữ Liệu ---


    st.sidebar.header("📥 Cập nhật dữ liệu thủ công")


    st.sidebar.markdown("Nếu không tự động đồng bộ được, bạn có thể tự upload 3 file **.csv** tại đây:")


    uploaded_master = st.sidebar.file_uploader("1. Upload master.csv", type=["csv"], key="up_master")


    uploaded_monthly = st.sidebar.file_uploader("2. Upload monthly.csv", type=["csv"], key="up_monthly")


    uploaded_inv = st.sidebar.file_uploader("3. Upload inventory.csv", type=["csv"], key="up_inv")


    


    try:


        if uploaded_master and uploaded_monthly and uploaded_inv:


            # Nếu người dùng upload đủ 3 file thì ưu tiên đọc từ file upload


            df_master, df_monthly, df_inv = load_data(uploaded_master, uploaded_monthly, uploaded_inv)


            st.sidebar.success("✅ Đã tải dữ liệu từ file upload thành công!")


        else:


            # Mặc định đọc từ file local


            df_master, df_monthly, df_inv = load_data('master.csv', 'monthly.csv', 'inventory.csv')


    except Exception as e:


        st.error(f"⚠️ Chưa tìm thấy dữ liệu CSV hoặc file bị lỗi.\n\n**Cách khắc phục:**\n1. Chạy file `sync_github.py` trên máy tính để tự động tạo và đồng bộ file.\n2. Hoặc upload thủ công 3 file `.csv` ở menu bên trái.\n\nChi tiết lỗi: {e}")


        st.stop()


    


    tab1, tab2 = st.tabs(["📈 Phân tích Ngành hàng & Thời gian", "🔍 Tra cứu Sản phẩm & Kho"])


    


    # ==========================================


    # TAB 1: PHÂN TÍCH NGÀNH HÀNG & THỜI GIAN


    # ==========================================


    with tab1:


        st.header("Phân tích Ngành hàng & Chỉ số theo Thời gian")


        


        col1, col2 = st.columns([1, 4])


        with col1:


            with st.expander("🛠️ Bộ lọc Thời gian & Ngành", expanded=False):


                available_months = sorted(df_monthly['thang'].dropna().unique(), reverse=True)


                


                # Get current month in format YYYY/TMM


                now = datetime.datetime.now()


                current_month_str = f"{now.year}/T{now.month:02d}"


                


                if current_month_str in available_months:


                    default_month = current_month_str


                elif available_months:


                    default_month = available_months[0]


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


                selected_nganh = st.multiselect("Chọn Ngành hàng", options=df_master['nganh_hang'].dropna().unique(), default=default_nganh)


                


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


                    "purple": ("#6f42c1", "#59339d"),


                    "teal": ("#20c997", "#1aa179"),


                }


                bg, bottom_bg = color_map.get(color, ("#6c757d", "#5a6268"))


                return f"""


                <div style="background-color: {bg}; padding: 15px; border-radius: 5px 5px 0 0; color: white; position: relative; height: 110px; box-sizing: border-box; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">


                    <h2 style="margin: 0; font-size: 24px; font-weight: bold; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{value}</h2>


                    <p style="margin: 5px 0 0 0; font-size: 13px; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{title}</p>


                    <i class="{icon_class}" style="position: absolute; right: 15px; top: 15px; font-size: 40px; opacity: 0.15; color: white;"></i>


                </div>


                <div style="background-color: {bottom_bg}; padding: 5px; border-radius: 0 0 5px 5px; text-align: center; color: rgba(255,255,255,0.9); font-size: 12px; margin-bottom: 15px; cursor: pointer;">


                    Chi Tiết <i class="fas fa-arrow-circle-right" style="margin-left: 5px;"></i>


                </div>


                """


    


            c1, c2, c3, c4, c5, c6 = st.columns(6)


            


            v1 = f"{f_monthly['dt_ban'].sum() / 1e6:,.0f}"


            v2 = f"{f_monthly['ds_nhap'].sum() / 1e6:,.0f}"


            v3 = f"{f_monthly['sl_ban'].sum():,.0f}"


            v4 = f"{f_monthly['sl_nhap'].sum():,.0f}"


            


            tong_ton_sl = f_master['tong_ton_st'].sum() + f_master['tong_ton_kho'].sum()


            tong_sb = f_master['tong_sb'].sum() if 'tong_sb' in f_master.columns else 0


            sntk_sl = tong_ton_sl / tong_sb if tong_sb > 0 else 0


            


            # SNTK Giá trị = Tổng Giá trị Tồn / Tổng sức bán Giá vốn


            # Tính Sức bán giá vốn = tổng (Sức bán * Giá BQGQ) từ master


            if 'tong_sb' in f_master.columns and 'gia_bqgq' in f_master.columns:


                tong_sb_gv = (f_master['tong_sb'] * f_master['gia_bqgq']).sum()


            else:


                tong_sb_gv = 0


                


            tong_gt_ton = f_master['tong_gia_tri_ton'].sum()


            sntk_gt = tong_gt_ton / tong_sb_gv if tong_sb_gv > 0 else 0


            


            v5 = f"{sntk_sl:,.2f}"


            v6 = f"{sntk_gt:,.2f}"


    


            c1.html(make_card("DT Bán (Tr)", v1, "green", "fas fa-money-bill-wave"))


            c2.html(make_card("DS Nhập (Tr)", v2, "orange", "fas fa-download"))


            c3.html(make_card("SNTK Số lượng", v5, "purple", "fas fa-calculator"))


            c4.html(make_card("SNTK Giá trị", v6, "teal", "fas fa-chart-line"))


            c5.html(make_card("Tổng SL Bán", v3, "blue", "fas fa-shopping-cart"))


            c6.html(make_card("Tổng SL Nhập", v4, "red", "fas fa-box"))


            


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


        


        # Sắp xếp theo DT Bán giảm dần và reset index


        tbl_nganh = tbl_nganh.sort_values(by="DT Bán (Tr VNĐ)", ascending=False).reset_index(drop=True)


        


        num_cols_fmt = [


            "SL Bán", "DT Bán (Tr VNĐ)", "DT Giá vốn (Tr VNĐ)", 


            "Tồn kho ST", "Tồn kho Kho", "Tổng Giá trị Tồn (Tr VNĐ)",


            "Tồn Kho (Mới)", "Tồn ST (Mới)", "Tồn Kho (Cận)", "Tồn ST (Cận)",


            "GT Kho (Mới) (Tr VNĐ)", "GT ST (Mới) (Tr VNĐ)", "GT Kho (Cận) (Tr VNĐ)", "GT ST (Cận) (Tr VNĐ)"


        ]


        


        def fmt_num(x):


            try:


                val = float(x)


                if pd.isna(val) or val == 0: return "-"


                return f"{val:,.0f}"


            except:


                return x


    


        def fmt_pct_vat(x):


            try:


                val = float(x)


                if pd.isna(val) or val == 0: return "-"


                if val.is_integer():


                    return f"{int(val)}%"


                return f"{val:g}%"


            except:


                return x


    


        def fmt_pct_front(x):


            try:


                val = float(x)


                if pd.isna(val) or val == 0: return "-"


                return f"{val:,.2f}%"


            except:


                return x


        


        html_nganh = tbl_nganh.style.format(formatter=fmt_num, subset=num_cols_fmt).set_table_attributes('class="ak-table"').hide(axis="index").to_html()


        st.html(f'<div style="overflow-x: auto; max-height: 600px;">{html_nganh}</div>')


    


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


        


        # 3. Loại bỏ #N/A, 0, Không kinh doanh, nan


        na_vals = ['#N/A', 'N/A', 'N/a', '0', 0, '#N/a', '#n/a', 'không kinh doanh', 'Không kinh doanh', 'Không KD', 'nan', 'NaN']


        df_piv = df_piv[~df_piv['trang_thai_kd'].isin(na_vals)]


        df_piv = df_piv.dropna(subset=['trang_thai_kd'])


        


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


            


        # Đưa Ngành hàng từ index thành cột để header nằm ngang nhau


        pivot_df = pivot_df.reset_index()


        pivot_df.rename(columns={'index': 'Ngành hàng', 'nganh_hang': 'Ngành hàng'}, inplace=True)


        pivot_df.columns.name = None


            


        def highlight_grand_total(row):


            is_total = (row['Ngành hàng'] == 'Grand Total')


            if is_total:


                return ['font-weight: bold; color: #dc3545; background-color: transparent;'] * len(row)


            return ['font-weight: bold; color: #dc3545; background-color: transparent;' if col == 'Grand Total' else '' for col in row.index]


    


        def align_nganh_hang(val):


            return 'text-align: left; font-weight: bold;'


    


        # Hỗ trợ tương thích ngược với Pandas < 2.1.0 (trên Streamlit Cloud)


        styler = pivot_df.style.format(formatter=fmt_num)


        try:


            styler = styler.map(align_nganh_hang, subset=['Ngành hàng'])


        except AttributeError:


            styler = styler.applymap(align_nganh_hang, subset=['Ngành hàng'])


            


        html_piv = styler.apply(highlight_grand_total, axis=1).set_table_attributes('class="ak-table"').hide(axis="index").to_html()


        st.html(f'<div style="overflow-x: auto; max-height: 600px;">{html_piv}</div>')


    


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


        


        # Dùng Streamlit column_config để format số ở frontend, tiết kiệm 90% RAM cho server


        inv_format_cols = ['Sức bán', 'Tổng tồn kho', 'Tồn kho mới', 'Tồn kho cận', 'Tồn siêu thị mới', 'Tồn siêu thị cận', 'Tổng giá trị', 'Giá trị kho mới', 'Giá trị kho cận', 'Giá trị ST mới', 'Giá trị ST cận']


        


        col_cfg = {c: st.column_config.NumberColumn(format="%,.0f") for c in inv_format_cols}


        


        # Giới hạn 500 dòng để chống văng trình duyệt (browser crash) khi load bảng quá lớn


        if len(df_inv_disp) > 500:


            st.info(f"💡 Đang hiển thị 500 dòng đầu tiên (trên tổng số {len(df_inv_disp):,.0f} dòng). Vui lòng chọn bộ lọc Sản phẩm/Kho để xem chi tiết chính xác.")


            df_inv_disp = df_inv_disp.head(500)


            


        st.dataframe(df_inv_disp, use_container_width=True, hide_index=True, column_config=col_cfg)


        


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


        


        # Tối ưu RAM: Không ép kiểu str trong dataframe, để Streamlit xử lý hiển thị


        df_master_disp["Phần trăm VAT"] = pd.to_numeric(df_master_disp["Phần trăm VAT"], errors='coerce').fillna(0)


        df_master_disp["Tỉ lệ Front"] = pd.to_numeric(df_master_disp["Tỉ lệ Front"], errors='coerce').fillna(0)


        


        # Đảm bảo các cột giá là số


        for c in ["Giá bán DVN", "Giá bán DVL", "Giá BQGQ", "Tổng siêu thị"]:


            df_master_disp[c] = pd.to_numeric(df_master_disp[c], errors='coerce').fillna(0)


            


        master_cfg = {


            "Phần trăm VAT": st.column_config.NumberColumn(format="%.2f %%"),


            "Tỉ lệ Front": st.column_config.NumberColumn(format="%.2f %%"),


            "Giá bán DVN": st.column_config.NumberColumn(format="%,.0f"),


            "Giá bán DVL": st.column_config.NumberColumn(format="%,.0f"),


            "Giá BQGQ": st.column_config.NumberColumn(format="%,.0f"),


            "Tổng siêu thị": st.column_config.NumberColumn(format="%,.0f")


        }


        


        # Giới hạn 500 dòng để chống văng trình duyệt (browser crash) khi load bảng quá lớn


        if len(df_master_disp) > 500:


            st.info(f"💡 Đang hiển thị 500 dòng đầu tiên (trên tổng số {len(df_master_disp):,.0f} dòng). Vui lòng chọn bộ lọc Sản phẩm/Ngành hàng để xem chi tiết chính xác.")


            df_master_disp = df_master_disp.head(500)


            


        st.dataframe(df_master_disp, use_container_width=True, hide_index=True, column_config=master_cfg)


    


    st.markdown("---")


    st.markdown("<p style='text-align: center; color: gray;'>Hệ thống Báo cáo Nội bộ - Phát triển bằng Python Streamlit</p>", unsafe_allow_html=True)





except Exception as e:


    st.error(f"⚠️ Lỗi Ứng dụng: {e}")


    st.code(traceback.format_exc(), language="python")


