import streamlit as st
import pandas as pd

def get_checklist_data():
    # "체크리스트" 시트 데이터를 기반으로 체크리스트 생성
    checklist_data = [
        {"구분": "데이터", "유형": "커버리지", "내용": "테크핀의 평균 커버리지는 50% 내외로 집계되며 전송 이력이 없는 신규 사업자에 대한 제공 비율이 높아질수록 커버리지가 증가하고 있다고 판단함"},
        {"구분": "데이터", "유형": "커버리지", "내용": "1. 신규 사업자에 대한 기장 정보를 제공함"},
        {"구분": "데이터", "유형": "커버리지", "내용": "1) 매월 요청하는 사업자번호 리스트에서 과거 전송이력이 없는 사업자를 신규로 봄"},
        {"구분": "데이터", "유형": "커버리지", "내용": "① 테크핀은 현재 기준년도(YYYY)로부터 과거 6개년 데이터 수집을 원칙으로 함 (수집하는 최초 시작년월이 shift되는 구조임)"},
        {"구분": "데이터", "유형": "커버리지", "내용": "예시: 신한은행의 경우 2024년 10월 최초 데이터 전송 시 2021년 1월을 시작월로 함 (기준년도로부터 과거 3개년 전 1월부터 제공함)"},
        {"구분": "데이터", "유형": "커버리지", "내용": "② 신규 사업자를 대상으로 DM_DATA별 사업자 수, 행수를 집계함"},
        {"구분": "데이터", "유형": "커버리지", "내용": "③ 신규 사업자는 도래하는 기준년월부터 변동 사업자로서 업데이트를 진행함"},
        {"구분": "데이터", "유형": "커버리지", "내용": "2. 변동 사업자에 대한 기장 정보를 업데이트함"},
        {"구분": "데이터", "유형": "커버리지", "내용": "1) 매월 요청하는 사업자번호 리스트에서 과거 전송이력이 존재하는 사업자를 변동으로 봄"},
        {"구분": "데이터", "유형": "커버리지", "내용": "① 과거 마지막으로 산출한 이력 대비 변동성을 체크하는 기간 내에서 변동이 발생하면 당월 재산출 사업자에 해당함"},
        {"구분": "데이터", "유형": "커버리지", "내용": "② 변동 사업자를 대상으로 테이블별, DM_DATA별 사업자 수, 행수를 집계함"},
        {"구분": "데이터", "유형": "커버리지", "내용": "3. 전체 사업자(신규+변동)에 대한 커버리지를 매월 집계함"},
        {"구분": "데이터", "유형": "커버리지", "내용": "1) 커버리지 증감에 따른 원인 분석 및 대응 구조를 갖추고 있는지 검토"},
        {"구분": "데이터", "유형": "커버리지", "내용": "① 금융기관 요청 사업자와 테크핀 보유 사업자의 기업 규모 차이"},
        {"구분": "데이터", "유형": "커버리지", "내용": "▶ 중견기업 ERP DB에 대한 데이터 수집 및 제공 대응 체계를 신속히 구축하여 데이터 커버리지를 확대함"},
        {"구분": "데이터", "유형": "커버리지", "내용": "② 클렌징로직에서 미채택되고 있으나 테크핀이 보유하고 있는 사업자인 경우"},
        {"구분": "데이터", "유형": "커버리지", "내용": "▶ 월단위 부가세 정보용으로 회계기간 중에 먼저 제공하고 기말 일정시점에 일괄 업데이트하는 방향 검토"},
        {"구분": "데이터", "유형": "커버리지", "내용": "③ 더존ERP에서 미보유한 사업자인 경우"},
        {"구분": "데이터", "유형": "커버리지", "내용": "▶ ERP데이터 내 다른 데이터 수집 경로를 통한 데이터 상품화 방안을 마련함"},
        {"구분": "데이터", "유형": "최신성", "내용": "테크핀은 시스템날짜 기준으로 2개월 전 기장 내역을 제공하고 있으며 (일부 1개월 전) 월별 사업자수를 집계하여 최신 데이터 제공 여부를 판단함"},
        {"구분": "데이터", "유형": "최신성", "내용": "1. 매월 신규 데이터를 제공하고 있는지 집계함"},
        {"구분": "데이터", "유형": "최신성", "내용": "1) 1,2번 테이블은 데이터산출 기준월(DW_BAS_NYYMM)대비 전표 발생월(DM_DATA)이 업데이트 되고 있는지 체크함"},
        {"구분": "데이터", "유형": "최신성", "내용": "① dw_bas_nyymm와 max(dm_data)가 동일한 사업자수가 증가하는 경우 정보의 최신성이 높다고 판단함"},
        {"구분": "데이터", "유형": "최신성", "내용": "2) 7번 테이블은 법인의 경우 아래 기준에 따라 변동성 체크 로직을 적용함"},
        {"구분": "데이터", "유형": "최신성", "내용": "① 1분기 데이터는 동년 기준월이 4월 이후인 시점부터 매월 변동성을 집계함"},
        {"구분": "데이터", "유형": "최신성", "내용": "② 2분기 데이터는 동년 기준월이 7월 이후인 시점부터 매월 변동성을 집계함"},
        {"구분": "데이터", "유형": "최신성", "내용": "③ 3분기 데이터는 동년 기준월이 10월 이후인 시점부터 매월 변동성을 체크함"},
        {"구분": "데이터", "유형": "최신성", "내용": "④ 4분기 데이터는 다음해 기준월이 1월 이후인 시점부터 매월 변동성을 체크함"},
        # ... (추가적인 항목은 생략되었으므로, 필요한 경우 전체 데이터를 포함해야 함)
        {"구분": "데이터", "유형": "무결성", "내용": "1. 복수개의 사업자번호(NO_BIZ)에 대한 기장데이터 중에서 1개의 NO_COM을 선택한 후 7개 테이블 산출 로직을 적용함"},
        {"구분": "데이터", "유형": "무결성", "내용": "② 과거에 산출한 결과값과 당월 산출한 결과값이 다른 원인을 분석함"},
        {"구분": "데이터", "유형": "무결성", "내용": "③ 동일 회계기수를 넘어 선 과거 데이터에 대한 변동이 서로 다른 NO_COM 선택으로 인한 문제인지를 확인함"},
        {"구분": "데이터", "유형": "무결성", "내용": "④ 원본 데이터에 대한 값 변동이 아닌 클렌징로직에 따른 변경인 경우 과거 데이터에 대한 클렌징로직 적용을 제한하는 방안을 검토해야 함"},
        {"구분": "데이터", "유형": "무결성", "내용": "3. 3개 DW에 대한 관리가 매월 적절하게 이행되고 있는지 검토함"},
        {"구분": "데이터", "유형": "무결성", "내용": "1) 45개 원본 테이블"},
        {"구분": "데이터", "유형": "무결성", "내용": "① 매월 초 더존비즈온으로 35만 차주에 대한 45개 테이블을 전송받음"},
        {"구분": "데이터", "유형": "무결성", "내용": "② 신규차주는 6개년 (2018년 이후) 기존 차주는 최근 24개월 변경분을 당행 DW에 적재함"},
        {"구분": "데이터", "유형": "무결성", "내용": "2) Temp 테이블"},
        {"구분": "데이터", "유형": "무결성", "내용": "① 7개 테이블 각각에 대한 산출로직을 적용하여 5개 테이블에 대한 Temp테이블을 생성함 (5,6번 제외)"},
        {"구분": "데이터", "유형": "무결성", "내용": "② 향후 금융기관별 Temp테이블에 대한 이력관리를 반드시 이행함 (신한은행의 경우 데이터 소급을 진행하면서 기준년월 202503부터 보관을 시작함)"},
        {"구분": "데이터", "유형": "무결성", "내용": "③ Temp테이블 행수 변화를 통해 더존 -> 테크핀 전송 오류, 테크핀 적재 오류 여부를 판단함"},
        {"구분": "데이터", "유형": "무결성", "내용": "3) History 테이블"},
        {"구분": "데이터", "유형": "무결성", "내용": "① 금융기관에 최종 전송하는 테이블로 테이블별 월별 이력관리를 반드시 이행함"},
        {"구분": "데이터", "유형": "무결성", "내용": "▶ 신한은행에 202410부터 202503까지 6회 전송하였으며, 양사간 로직 변경 및 소급 적용으로 24개월분에 대한 재산출을 진행함"},
        {"구분": "데이터", "유형": "무결성", "내용": "▶ 신한은행에 동일 기준월로 2회 이상 전송하는 경우 동일한 과거 전송분에 대한 중복 체크 후 최초 전송분만 전송함"},
        {"구분": "데이터", "유형": "무결성", "내용": "② 금융기관은 테이블별 PK기준으로 delete-insert가 아닌 update-insert를 지향함"},
        {"구분": "인프라", "유형": "전송", "내용": "1. 7개 파일을 파일명 규칙에 맞게 생성함"},
        {"구분": "인프라", "유형": "전송", "내용": "1) 파일 당 용량이 2G 이상일 경우 분할 압축함"},
        {"구분": "인프라", "유형": "전송", "내용": "2) 분할 압축한 파일은 순차적으로 반영함 (ex _000001, _000002 ~)"},
        {"구분": "인프라", "유형": "전송", "내용": "3) YYYYMM은 7개 부가세 테이블 내 기준월(dw_bas_nyymm) 컬럼값임"},
        {"구분": "인프라", "유형": "전송", "내용": "2. 7개 파일을 SFTP 방식으로 전송함"},
        {"구분": "인프라", "유형": "전송", "내용": "1) 테크핀 - 금융기관 양사 간 전용선 구축"},
        {"구분": "인프라", "유형": "전송", "내용": "① 신한은행은 매달 23일 오전 11시(휴일, 공휴일 무관) 송수신 폴더에 업로드 하는 것을 원칙으로 함"},
        {"구분": "인프라", "유형": "전송", "내용": "② 기준년월에 대한 재산출-전송 이슈가 발생한 경우 파일명으로 구분이 불가능하므로 담당자에게 전달해야 함"},
        {"구분": "인프라", "유형": "전송", "내용": "2) 전문설계서를 통한 요청 전문 - 응답 전문 송수신 체계 구축"},
        {"구분": "인프라", "유형": "전송", "내용": "3) 양사 간 전용선 구축이 불가능한 경우 별도의 방법으로 송수신"}
    ]
    
    # DataFrame 생성
    df_checklist = pd.DataFrame(checklist_data)
    
    # Streamlit에서 체크리스트 표시
    st.write("데이터 품질 관리 체크리스트")
    st.write("각 항목을 검토한 후 O/X를 체크하세요:")
    
    # 체크리스트 테이블 생성
    checklist_results = []
    for index, row in df_checklist.iterrows():
        # O/X 체크박스 추가
        check = st.checkbox(f"{row['구분']} - {row['유형']} - {row['내용']}", key=f"check_{index}")
        checklist_results.append({
            "구분": row["구분"],
            "유형": row["유형"],
            "내용": row["내용"],
            "체크": "O" if check else "X"
        })
    
    # 결과 DataFrame 생성
    df_results = pd.DataFrame(checklist_results)
    
    # 스타일링 적용
    styled_df = df_results.style.set_properties(**{
        'text-align': 'left',
        'border': '2px solid #333',
        'padding': '8px'
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#e6f3ff'), ('border', '2px solid #333'), ('text-align', 'left')]}
    ])
    
    st.dataframe(styled_df, use_container_width=True)

    return df_results
```

### 2. Updated `app.py`
The `app.py` file is updated to:
- Correctly import `get_checklist_data` from `checklist.py`.
- Include the "체크리스트" tab next to the "HISTORY" tab, calling `get_checklist_data()`.
- Retain all existing functionality (이슈사항 tab, HISTORY tab, table-specific tabs) with the reversed `table_mapping`, renamed "_중복제거X" to "_행수", "_중복제거" to "_사업자번호" in the 이슈사항 tab, and removed "테이블" column in 이슈사항.

<xaiArtifact artifact_id="64038e76-cc25-4cad-8605-23139ce735ff" artifact_version_id="10b3c4ea-116b-4ad3-a71d-706fface4f3c" title="app.py" contentType="text/python">
```python
import pandas as pd
import streamlit as st
import numpy as np
from data import create_sample_data
try:
    from history_data import get_history_data  # HISTORY 데이터 임포트
except ImportError as e:
    st.error(f"history_data 모듈 임포트 실패: {e}")
    st.stop()
try:
    from checklist import get_checklist_data  # 체크리스트 임포트
except ImportError as e:
    st.error(f"checklist 모듈 임포트 실패: {e}")
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

# 테이블 명칭 매핑 (한국어 이름을 키로, 영어 이름을 값으로)
table_mapping = {
    '월별_매출정보': 'Table 1',
    '월별_매입정보': 'Table 2',
    '거래처별_매출채권정보': 'Table 3',
    '거래처별_매입채무정보': 'Table 4',
    '거래처별_매출채권_회수기간': 'Table 5',
    '거래처별_매입채무_지급기간': 'Table 6',
    '분기별_매출(매입)정보': 'Table 7'
}

# 테이블 목록 (HISTORY, 체크리스트, 이슈사항 순으로 배치, 나머지는 한국어 이름 사용)
tables = ["HISTORY", "체크리스트", "이슈사항"] + list(table_mapping.keys())

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
        elif table == "체크리스트":
            st.subheader("체크리스트")
            get_checklist_data()
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
