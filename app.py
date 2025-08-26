import pandas as pd
import streamlit as st
import numpy as np
from data import create_sample_data
from history_data import get_history_data  # HISTORY 데이터 임포트

# Streamlit 페이지 설정: 넓은 레이아웃
st.set_page_config(layout="wide")

# Streamlit 앱 설정
st.title("신한은행 테크핀 데이터 비교 (24.10~25.07)")
st.write("2024.10~2025.07 데이터를 테이블별로 탭으로 나누어 비교합니다. 기준월을 가로 행(컬럼)으로, 법인/개인/총사업자의 중복제거와 중복제거X 데이터를 별도 표로 표시합니다. 숫자는 천 단위 쉼표로 포맷팅해 오른쪽 정렬됩니다. HISTORY 탭은 데이터 전송 및 변동 내역을 표시합니다.")

# CSS로 표 스타일링 (가로 스크롤바 없이 전체 화면 활용, 숫자 오른쪽 정렬)
st.markdown("""
<style>
table {
    width: 100% !important;
    table-layout: fixed;
    border-collapse: collapse;
}
table th, table td {
    padding: 5px;
    font-size: 11px;
    overflow: hidden;
    text-overflow: ellipsis;
}
table th:nth-child(1), table td:nth-child(1) {
    width: 150px; /* 데이터 항목 컬럼 고정 너비 */
}
table th:nth-child(n+2), table td:nth-child(n+2) {
    text-align: right !important;
    padding-right: 8px !important;
    max-width: 100px; /* 숫자 컬럼 너비 제한 */
}
</style>
""", unsafe_allow_html=True)

# 데이터 로드
data = create_sample_data()
df = pd.DataFrame(data)

# 테이블 목록 (NumPy 배열을 리스트로 변환)
tables = list(df['테이블'].unique()) + ["HISTORY"]

# Streamlit 탭 생성
tabs = st.tabs(tables)

# 테이블별 데이터 표시
for i, table in enumerate(tables):
    with tabs[i]:
        if table == "HISTORY":
            st.subheader("HISTORY")
            history_df = get_history_data()
            st.write(history_df)
        else:
            st.subheader(f"{table}")
            table_data = df[df['테이블'] == table].copy()
            
            # 중복제거X 피벗 테이블 (법인사업자_중복제거X, 개인사업자_중복제거X, 총사업자_중복제거X)
            pivot_nodedup = pd.pivot_table(
                table_data,
                values=['법인사업자_중복제거X', '개인사업자_중복제거X', '총사업자_중복제거X'],
                index=None,
                columns='기준월',
                aggfunc='sum'
            ).reset_index(drop=True)
            pivot_nodedup.index = ['법인사업자_중복제거X', '개인사업자_중복제거X', '총사업자_중복제거X']
            pivot_nodedup.columns = [col[1] if isinstance(col, tuple) else col for col in pivot_nodedup.columns]
            
            # 중복제거 피벗 테이블 (법인사업자_중복제거, 개인사업자_중복제거, 총사업자_중복제거)
            pivot_dedup = pd.pivot_table(
                table_data,
                values=['법인사업자_중복제거', '개인사업자_중복제거', '총사업자_중복제거'],
                index=None,
                columns='기준월',
                aggfunc='sum'
            ).reset_index(drop=True)
            pivot_dedup.index = ['법인사업자_중복제거', '개인사업자_중복제거', '총사업자_중복제거']
            pivot_dedup.columns = [col[1] if isinstance(col, tuple) else col for col in pivot_dedup.columns]
            
            # 숫자 포맷팅 (천 단위 쉼표)
            pivot_nodedup_formatted = pivot_nodedup.copy()
            for col in pivot_nodedup.select_dtypes(include=np.number).columns:
                pivot_nodedup_formatted[col] = pivot_nodedup[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "-")
            
            pivot_dedup_formatted = pivot_dedup.copy()
            for col in pivot_dedup.select_dtypes(include=np.number).columns:
                pivot_dedup_formatted[col] = pivot_dedup[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "-")
            
            st.write("중복제거X 데이터 (법인/개인/총사업자):")
            st.write(pivot_nodedup_formatted)
            
            st.write("중복제거 데이터 (법인/개인/총사업자):")
            st.write(pivot_dedup_formatted)
