import pandas as pd
import streamlit as st
import numpy as np
from data import create_sample_data
try:
    from history_data import get_history_data  # HISTORY 데이터 임포트
except ImportError as e:
    st.error(f"history_data 모듈 임포트 실패: {e}")
    st.stop()

# Streamlit 페이지 설정: 넓은 레이아웃
st.set_page_config(layout="wide")

# Streamlit 앱 설정
st.title("7개 부가세 테이블 신한은행 전송 이력 (24.10~)")
st.write("테크핀-> 신한은행 전송 이력을 테이블별로 탭으로 나누어 비교합니다.")

# CSS로 표 스타일링 (줄 바꿈, 헤더 색상, 최대/최소 강조, 선 구분 강화, diff 강조)
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
    border: 2px solid #333 !important; /* 선 구분 강화: 굵기 2px, 색상 진하게 #333 */
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
.positive {
    color: green !important;
    font-weight: bold !important;
}
.negative {
    color: red !important;
    font-weight: bold !important;
}
.zero {
    color: gray !important;
}
.diff-column {
    background-color: #f9f9f9 !important; /* diff 열 배경색으로 구분 */
}
</style>
""", unsafe_allow_html=True)

# 데이터 로드
try:
    data = create_sample_data()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"create_sample_data 로드 실패: {e}")
    st.stop()

# 테이블 명칭 매핑 (한국어 이름을 키로, 영어 이름을 값으로 변경)
table_mapping = {
    '월별_매출정보': 'Table 1',
    '월별_매입정보': 'Table 2',
    '거래처별_매출채권정보': 'Table 3',
    '거래처별_매입채무정보': 'Table 4',
    '거래처별_매출채권_회수기간': 'Table 5',
    '거래처별_매입채무_지급기간': 'Table 6',
    '분기별_매출(매입)정보': 'Table 7'
}

# 테이블 목록 (HISTORY와 이슈사항을 맨 처음에 배치, 나머지는 한국어 이름 사용)
tables = ["HISTORY", "이슈사항"] + list(table_mapping.keys())

# Streamlit 탭 생성
tabs = st.tabs(tables)

# 최대/최소 값을 강조하는 함수 (전체 열 강조, diff에 이모지 추가)
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
        if col.endswith('_diff'):
            # diff 컬럼에 시각적 강조 적용 (양수: green ↑, 음수: red ↓, 0: gray -)
            styled_df[col] = styled_df[col].apply(
                lambda x: f'<span class="positive diff-column">↑ {x:,.0f}</span>' if x > 0 else 
                          f'<span class="negative diff-column">↓ {x:,.0f}</span>' if x < 0 else 
                          f'<span class="zero diff-column">- {x:,.0f}</span>' if pd.notnull(x) else '-'
            )
        elif col in max_columns:
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
            try:
                history_df = get_history_data()
                if history_df.empty:
                    st.warning("HISTORY 데이터가 비어 있습니다. history_data.py를 확인하세요.")
                else:
                    st.write("HISTORY 데이터 로드 성공:")
                    st.write(f"행 수: {len(history_df)}, 컬럼: {list(history_df.columns)}")
                    st.dataframe(history_df, hide_index=True, use_container_width=True)
            except Exception as e:
                st.error(f"HISTORY 데이터 로드 실패: {e}")
        elif table == "이슈사항":
            st.subheader("25.07_1 vs 25.07_2 비교")
            # 25.07_1과 25.07_2 데이터 필터링
            df_old = df[df['기준월'] == '25.07_1'].copy()
            df_new = df[df['기준월'] == '25.07_2'].copy()
            
            # 테이블 이름을 한국어로 매핑
            df_old['테이블'] = df_old['테이블'].map({v: k for k, v in table_mapping.items()})
            df_new['테이블'] = df_new['테이블'].map({v: k for k, v in table_mapping.items()})
            
            # 데이터 병합 (테이블을 인덱스로 설정)
            df_old = df_old.set_index('테이블')
            df_new = df_new.set_index('테이블')
            comparison = df_old.join(df_new, lsuffix='_old', rsuffix='_new')
            
            # 차이 계산
            rowcount_columns = ['법인사업자_중복제거X', '개인사업자_중복제거X', '총사업자_중복제거X']
            dedup_columns = ['법인사업자_중복제거', '개인사업자_중복제거', '총사업자_중복제거']
            for col in rowcount_columns:
                comparison[f'{col.replace("_중복제거X", "_행수")}_diff'] = comparison[f'{col}_new'] - comparison[f'{col}_old']
            for col in dedup_columns:
                comparison[f'{col.replace("_중복제거", "_사업자번호")}_diff'] = comparison[f'{col}_new'] - comparison[f'{col}_old']
            
            # 행수 관련 컬럼만 추출
            rowcount_comparison_columns = ['법인사업자_중복제거X_old', '법인사업자_중복제거X_new', '법인사업자_행수_diff',
                                          '개인사업자_중복제거X_old', '개인사업자_중복제거X_new', '개인사업자_행수_diff',
                                          '총사업자_중복제거X_old', '총사업자_중복제거X_new', '총사업자_행수_diff']
            comparison_rowcount = comparison[rowcount_comparison_columns]
            comparison_rowcount.columns = [col.replace('_중복제거X', '_행수') for col in comparison_rowcount.columns]
            
            # 사업자번호 기준 (중복제거) 관련 컬럼만 추출
            dedup_comparison_columns = ['법인사업자_중복제거_old', '법인사업자_중복제거_new', '법인사업자_사업자번호_diff',
                                        '개인사업자_중복제거_old', '개인사업자_중복제거_new', '개인사업자_사업자번호_diff',
                                        '총사업자_중복제거_old', '총사업자_중복제거_new', '총사업자_사업자번호_diff']
            comparison_dedup = comparison[dedup_comparison_columns]
            comparison_dedup.columns = [col.replace('_중복제거', '_사업자번호') for col in comparison_dedup.columns]
            
            # 숫자 포맷팅 및 최대/최소/차이 강조
            comparison_rowcount_formatted = comparison_rowcount.copy()
            for col in comparison_rowcount.select_dtypes(include=np.number).columns:
                comparison_rowcount_formatted[col] = comparison_rowcount[col].apply(lambda x: x if pd.notnull(x) else np.nan)
            comparison_rowcount_formatted = highlight_max_min(comparison_rowcount_formatted)
            
            comparison_dedup_formatted = comparison_dedup.copy()
            for col in comparison_dedup.select_dtypes(include=np.number).columns:
                comparison_dedup_formatted[col] = comparison_dedup[col].apply(lambda x: x if pd.notnull(x) else np.nan)
            comparison_dedup_formatted = highlight_max_min(comparison_dedup_formatted)
            
            # 테이블 열 제거하고 인덱스(한국어 테이블 이름)를 표시
            st.write("행수 비교 (25.07_1 (기존) vs 25.07_2 (신규) - 차이 = 신규 - 기존)")
            st.markdown(comparison_rowcount_formatted.reset_index().to_html(index=True, escape=False), unsafe_allow_html=True)
            
            st.write("사업자번호 기준 비교 (25.07_1 (기존) vs 25.07_2 (신규) - 차이 = 신규 - 기존)")
            st.markdown(comparison_dedup_formatted.reset_index().to_html(index=True, escape=False), unsafe_allow_html=True)
        else:
            # 원래 테이블 이름으로 데이터 필터링 (한국어 이름 사용)
            original_table = table_mapping.get(table, table)
            st.subheader(f"{table}")
            table_data = df[df['테이블'] == original_table].copy()
           
            # 한국어 테이블 이름으로 변환
            table_data['테이블'] = table_data['테이블'].map({v: k for k, v in table_mapping.items()})
            
            # 행수 (중복제거X) 피벗 테이블
            pivot_rowcount = pd.pivot_table(
                table_data,
                values=['법인사업자_중복제거X', '개인사업자_중복제거X', '총사업자_중복제거X'],
                index=None,
                columns='기준월',
                aggfunc='sum'
            ).reset_index(drop=True)
            pivot_rowcount.index = ['법인사업자_행수', '개인사업자_행수', '총사업자_행수']
            pivot_rowcount.columns = [col[1] if isinstance(col, tuple) else col for col in pivot_rowcount.columns]
           
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
            pivot_rowcount_formatted = pivot_rowcount.copy()
            for col in pivot_rowcount.select_dtypes(include=np.number).columns:
                pivot_rowcount_formatted[col] = pivot_rowcount[col].apply(lambda x: x if pd.notnull(x) else np.nan)
            pivot_rowcount_formatted = highlight_max_min(pivot_rowcount_formatted)
           
            pivot_dedup_formatted = pivot_dedup.copy()
            for col in pivot_dedup.select_dtypes(include=np.number).columns:
                pivot_dedup_formatted[col] = pivot_dedup[col].apply(lambda x: x if pd.notnull(x) else np.nan)
            pivot_dedup_formatted = highlight_max_min(pivot_dedup_formatted)
           
            st.write("행수 데이터 (법인/개인/총사업자): 전체 행수 기준")
            st.markdown(pivot_rowcount_formatted.to_html(escape=False), unsafe_allow_html=True)
           
            st.write("중복제거 데이터 (법인/개인/총사업자): 사업자번호 기준")
            st.markdown(pivot_dedup_formatted.to_html(escape=False), unsafe_allow_html=True)
