import pandas as pd
import streamlit as st
import numpy as np
from data import create_sample_data
from history_data import get_history_data  # HISTORY 데이터 임포트

# Streamlit 페이지 설정: 넓은 레이아웃
st.set_page_config(layout="wide")

# Streamlit 앱 설정
st.title("신한은행 테크핀 데이터 비교 (24.10~25.07)")
st.write("2024.10~2025.07 데이터를 테이블별로 탭으로 나누어 비교합니다.")

# CSS로 표 스타일링 (줄 바꿈, 헤더 색상, 최대/최소 강조)
st.markdown("""
<style>
table {
    width: 100% !important;
    table-layout: fixed;
    border-collapse: collapse;
}
table th, table td {
    padding: 8px;
    font-size: 12px;
    overflow: hidden;
    text-overflow: ellipsis;
    border: 1px solid #ddd;
}
table th {
    background-color: #e6f3ff !important; /* 연한 파란색 헤더 */
}
table th:nth-child(1), table td:nth-child(1) {
    width: 150px; /* 데이터 항목 컬럼 고정 너비 (HISTORY의 기준월 포함) */
}
table th:nth-child(n+2), table td:nth-child(n+2) {
    text-align: right !important; /* 숫자 컬럼 오른쪽 정렬 */
    max-width: 100px; /* 숫자 컬럼 너비 제한 */
}
.history-table th:nth-child(1), .history-table td:nth-child(1) {
    width: 100px; /* HISTORY 기준월 너비 */
}
.history-table th:nth-child(2), .history-table td:nth-child(2) {
    width: 100px; /* HISTORY 전송일 너비 */
}
.history-table th:nth-child(3), .history-table td:nth-child(3) {
    width: 300px; /* HISTORY ASIS 너비 */
    text-align: left !important; /* HISTORY ASIS 왼쪽 정렬 */
    white-space: pre-wrap; /* 줄 바꿈 유지 */
    padding-left: 0 !important; /* 텍스트를 맨 왼쪽으로 */
}
.history-table th:nth-child(4), .history-table td:nth-child(4) {
    width: 300px; /* HISTORY TOBE 너비 */
    text-align: left !important; /* HISTORY TOBE 왼쪽 정렬 */
    white-space: pre-wrap; /* 줄 바꿈 유지 */
    padding-left: 0 !important; /* 텍스트를 맨 왼쪽으로 */
}
.max-column {
    border: 2px solid red !important;
}
.min-column {
    border: 2px solid blue !important;
}
</style>
""", unsafe_allow_html=True)

# 데이터 로드
data = create_sample_data()
df = pd.DataFrame(data)

# 테이블 목록 (HISTORY를 맨 처음에 배치)
tables = ["HISTORY"] + list(df['테이블'].unique())

# Streamlit 탭 생성
tabs = st.tabs(tables)

# 최대/최소 값을 강조하는 함수 (전체 열 강조)
def highlight_max_min(df):
    df_numeric = df.select_dtypes(include=np.number).copy()
    if df_numeric.empty:
        return df
    max_value = df_numeric.max().max()
    min_value = df_numeric.min().min()
    max_columns = df_numeric.columns[df_numeric.eq(max_value).any()]
    min_columns = df_numeric.columns[df_numeric.eq(min_value).any()]
    
    styled_df = df.copy()
    for col in df.columns:
        if col in max_columns:
            styled_df[col] = styled_df[col].apply(
                lambda x: f'<span class="max-column">{x:,.0f}</span>' if pd.notnull(x) else '<span class="max-column">-</span>'
            )
        elif col in min_columns:
            styled_df[col] = styled_df[col].apply(
                lambda x: f'<span class="min-column">{x:,.0f}</span>' if pd.notnull(x) else '<span class="min-column">-</span>'
            )
        else:
            styled_df[col] = styled_df[col].apply(
                lambda x: f'{x:,.0f}' if pd.notnull(x) else '-'
            )
    return styled_df

# 테이블별 데이터 표시
for i, table in enumerate(tables):
    with tabs[i]:
        if table == "HISTORY":
            st.subheader("HISTORY")
            history_df = get_history_data()
            st.table(history_df.style.set_table_attributes('class="history-table"'))
        else:
            st.subheader(f"{table}")
            table_data = df[df['테이블'] == table].copy()
            
            # 중복제거X 피벗 테이블
            pivot_nodedup = pd.pivot_table(
                table_data,
                values=['법인사업자_중복제거X', '개인사업자_중복제거X', '총사업자_중복제거X'],
                index=None,
                columns='기준월',
                aggfunc='sum'
            ).reset_index(drop=True)
            pivot_nodedup.index = ['법인사업자_중복제거X', '개인사업자_중복제거X', '총사업자_중복제거X']
            pivot_nodedup.columns = [col[1] if isinstance(col, tuple) else col for col in pivot_nodedup.columns]
            
            # 중복제거 피벗 테이블
            pivot_dedup = pd.pivot_table(
                table_data,
                values=['법인사업자_중복제거', '개인사업자_중복제거', '총사업자_중복제거'],
                index=None,
                columns='기준월',
                aggfunc='sum'
            ).reset_index(drop=True)
            pivot_dedup.index = ['법인사업자_중복제거', '개인사업자_중복제거', '총사업자_중복제거']
            pivot_dedup.columns = [col[1] if isinstance(col, tuple) else col for col in pivot_dedup.columns]
            
            # 숫자 포맷팅 및 최대/최소 강조
            pivot_nodedup_formatted = pivot_nodedup.copy()
            for col in pivot_nodedup.select_dtypes(include=np.number).columns:
                pivot_nodedup_formatted[col] = pivot_nodedup[col].apply(lambda x: x if pd.notnull(x) else np.nan)
            pivot_nodedup_formatted = highlight_max_min(pivot_nodedup_formatted)
            
            pivot_dedup_formatted = pivot_dedup.copy()
            for col in pivot_dedup.select_dtypes(include=np.number).columns:
                pivot_dedup_formatted[col] = pivot_dedup[col].apply(lambda x: x if pd.notnull(x) else np.nan)
            pivot_dedup_formatted = highlight_max_min(pivot_dedup_formatted)
            
            st.write("중복제거X 데이터 (법인/개인/총사업자):")
            st.markdown(pivot_nodedup_formatted.to_html(escape=False), unsafe_allow_html=True)
            
            st.write("중복제거 데이터 (법인/개인/총사업자):")
            st.markdown(pivot_dedup_formatted.to_html(escape=False), unsafe_allow_html=True)
