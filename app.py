import pandas as pd
import streamlit as st
import io
import matplotlib
matplotlib.use('Agg')  # 비GUI 백엔드 설정 (Streamlit Cloud 호환)
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import plotly.express as px
import os
import numpy as np
import shutil
from data import create_sample_data  # 데이터 임포트

# Streamlit 페이지 설정: 넓은 레이아웃
st.set_page_config(layout="wide")

# matplotlib 폰트 캐시 삭제
cache_dir = matplotlib.get_cachedir()
if os.path.exists(cache_dir):
    shutil.rmtree(cache_dir)
    st.write(f"디버깅: matplotlib 캐시 디렉토리 {cache_dir} 삭제 완료")

# 한글 폰트 설정 (윈도우 및 Streamlit Cloud 호환)
font_paths = [
    'C:/Windows/Fonts/NotoSansKR-Regular.ttf',  # 윈도우: Noto Sans KR
    'C:/Windows/Fonts/NanumGothic.ttf',         # 윈도우: NanumGothic
    'C:/Windows/Fonts/malgun.ttf',              # 윈도우: Malgun Gothic
    '/usr/share/fonts/truetype/noto/NotoSansCJKkr-Regular.otf',  # Linux: Noto Sans CJK KR
    '/usr/share/fonts/truetype/noto/NotoSansKR-Regular.otf',     # Linux: Noto Sans KR
    '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',           # Linux: NanumGothic
    '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'       # Linux: NanumBarunGothic
]
font_name = None
for path in font_paths:
    if os.path.exists(path):
        fm.fontManager.addfont(path)
        font_name = fm.FontProperties(fname=path).get_name()
        plt.rc('font', family=font_name)
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
        st.write(f"디버깅: 폰트 {font_name} ({path}) 적용")
        break

# fc-list로 한글 폰트 동적 탐지 (Linux)
if font_name is None and os.name != 'nt':
    try:
        # fc-list 실행 전 fontconfig 설치 확인
        if os.system('command -v fc-list >/dev/null 2>&1') != 0:
            st.write("디버깅: fc-list 명령어가 설치되지 않았습니다. fontconfig 설치 필요.")
        else:
            font_list = os.popen('fc-list :lang=ko').read().splitlines()
            st.write(f"디버깅: fc-list 한글 폰트 목록: {font_list[:10]}")  # 상위 10개 출력
            for font in font_list:
                if 'Noto' in font or 'Nanum' in font:
                    font_path = font.split(':')[0].strip()
                    fm.fontManager.addfont(font_path)
                    font_name = fm.FontProperties(fname=font_path).get_name()
                    plt.rc('font', family=font_name)
                    plt.rcParams['axes.unicode_minus'] = False
                    st.write(f"디버깅: fc-list에서 폰트 {font_name} ({font_path}) 적용")
                    break
    except Exception as e:
        st.write(f"디버깅: fc-list 실행 오류: {str(e)}")

# 폰트 디버깅 정보 출력
if font_name is None:
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    st.write(f"디버깅: matplotlib 사용 가능 폰트 목록: {available_fonts[:20]}")
    st.warning("한글 폰트를 찾을 수 없습니다. 윈도우는 Malgun Gothic, Linux는 DejaVu Sans 사용.")
    plt.rc('font', family='Malgun Gothic' if os.name == 'nt' else 'DejaVu Sans')
else:
    st.write(f"디버깅: 최종 선택된 폰트: {font_name}")

# 시스템 폰트 디렉토리 확인
try:
    font_dir = 'C:/Windows/Fonts' if os.name == 'nt' else '/usr/share/fonts/truetype/'
    font_files = []
    for root, _, files in os.walk(font_dir):
        font_files.extend([os.path.join(root, f) for f in files if f.endswith(('.ttf', '.otf'))])
    st.write(f"디버깅: 폰트 디렉토리 {font_dir} 내 파일: {font_files[:5]}")  # 상위 5개 출력
except:
    st.write("디버깅: 폰트 디렉토리 확인 실패")

# Streamlit 앱 설정
st.title("신한은행 테크핀 데이터 비교 (24.10~25.07)")
st.write("2024.10~2025.07 데이터를 테이블별로 탭으로 나누어 비교합니다. 기준월을 가로 행(컬럼)으로, 법인/개인/총사업자의 중복제거와 중복제거X 데이터를 별도 표로 표시합니다. 숫자는 천 단위 쉼표로 포맷팅해 오른쪽 정렬됩니다.")

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
tables = list(df['테이블'].unique())

# Streamlit 탭 생성
tabs = st.tabs(tables)

# 테이블별 데이터 표시
for i, table in enumerate(tables):
    with tabs[i]:
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
        
        # 최대/최소 수치 요약
        st.write("중복제거X 데이터 요약:")
        numeric_cols_nodedup = pivot_nodedup.select_dtypes(include=np.number).columns
        summary_nodedup = pivot_nodedup[numeric_cols_nodedup].describe().loc[['max', 'min']].T
        st.write(summary_nodedup)
        
        st.write("중복제거 데이터 요약:")
        numeric_cols_dedup = pivot_dedup.select_dtypes(include=np.number).columns
        summary_dedup = pivot_dedup[numeric_cols_dedup].describe().loc[['max', 'min']].T
        st.write(summary_dedup)
        
        # 숫자 포맷팅 (천 단위 쉼표)
        pivot_nodedup_formatted = pivot_nodedup.copy()
        for col in numeric_cols_nodedup:
            pivot_nodedup_formatted[col] = pivot_nodedup[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "-")
        
        pivot_dedup_formatted = pivot_dedup.copy()
        for col in numeric_cols_dedup:
            pivot_dedup_formatted[col] = pivot_dedup[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "-")
        
        st.write("중복제거X 데이터 (법인/개인/총사업자):")
        st.write(pivot_nodedup_formatted)
        
        st.write("중복제거 데이터 (법인/개인/총사업자):")
        st.write(pivot_dedup_formatted)
        
        # Plotly 그래프
        st.subheader(f"{table} 월별 사업자 수 변화 (Plotly)")
        fig = px.line(table_data, x='기준월', y='총사업자_중복제거', 
                      title=f'{table} 월별 총사업자 수 (중복제거)', 
                      labels={'기준월': '기준월', '총사업자_중복제거': '총사업자 수 (중복제거)'})
        fig.update_layout(font=dict(family="Noto Sans KR, sans-serif", size=12))
        st.plotly_chart(fig, use_container_width=True)
        
        # matplotlib 그래프
        st.subheader(f"{table} 월별 사업자 수 변화 (matplotlib)")
        plt.figure(figsize=(10, 6))
        plt.plot(table_data['기준월'], table_data['총사업자_중복제거'], marker='o', label=table)
        plt.title(f'{table} 월별 총사업자 수 (중복제거)')
        plt.xlabel('기준월')
        plt.ylabel('총사업자 수 (중복제거)')
        plt.legend(title='유형')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)
        
        # PNG 다운로드 (테이블별)
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        st.download_button(
            label=f"{table} 그래프 PNG 다운로드",
            data=buf,
            file_name=f"business_graph_{table}.png",
            mime="image/png"
        )

# 전체 Plotly 그래프 (모든 테이블 비교)
st.subheader("모든 테이블 월별 사업자 수 변화 (Plotly)")
fig = px.line(df, x='기준월', y='총사업자_중복제거', color='테이블', 
              title='월별 총사업자 수 (중복제거)', 
              labels={'기준월': '기준월', '총사업자_중복제거': '총사업자 수 (중복제거)', '테이블': '유형'})
fig.update_layout(font=dict(family="Noto Sans KR, sans-serif", size=12))
st.plotly_chart(fig, use_container_width=True)

# 전체 matplotlib 그래프
st.subheader("모든 테이블 월별 사업자 수 변화 (matplotlib)")
plt.figure(figsize=(10, 6))
for table in tables:
    table_data = df[df['테이블'] == table]
    plt.plot(table_data['기준월'], table_data['총사업자_중복제거'], marker='o', label=table)
plt.title('월별 총사업자 수 (중복제거)')
plt.xlabel('기준월')
plt.ylabel('총사업자 수 (중복제거)')
plt.legend(title='유형')
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(plt)

# CSV 다운로드 (원본 데이터)
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="원본 데이터 CSV 다운로드",
    data=csv,
    file_name="business_data.csv",
    mime="text/csv"
)

# 중복제거X 피벗 테이블 CSV 다운로드
pivot_nodedup_all = pd.concat([pd.pivot_table(
    df[df['테이블'] == table],
    values=['법인사업자_중복제거X', '개인사업자_중복제거X', '총사업자_중복제거X'],
    index=None,
    columns='기준월',
    aggfunc='sum'
).reset_index(drop=True).assign(테이블=table) for table in tables])
pivot_nodedup_all.index = pd.MultiIndex.from_product([tables, ['법인사업자_중복제거X', '개인사업자_중복제거X', '총사업자_중복제거X']], names=['테이블', '항목'])
pivot_nodedup_all.columns = [col[1] if isinstance(col, tuple) else col for col in pivot_nodedup_all.columns]
pivot_nodedup_csv = pivot_nodedup_all.reset_index().to_csv(index=True).encode('utf-8')
st.download_button(
    label="중복제거X 피벗 테이블 CSV 다운로드",
    data=pivot_nodedup_csv,
    file_name="business_pivot_nodedup_data.csv",
    mime="text/csv"
)

# 중복제거 피벗 테이블 CSV 다운로드
pivot_dedup_all = pd.concat([pd.pivot_table(
    df[df['테이블'] == table],
    values=['법인사업자_중복제거', '개인사업자_중복제거', '총사업자_중복제거'],
    index=None,
    columns='기준월',
    aggfunc='sum'
).reset_index(drop=True).assign(테이블=table) for table in tables])
pivot_dedup_all.index = pd.MultiIndex.from_product([tables, ['법인사업자_중복제거', '개인사업자_중복제거', '총사업자_중복제거']], names=['테이블', '항목'])
pivot_dedup_all.columns = [col[1] if isinstance(col, tuple) else col for col in pivot_dedup_all.columns]
pivot_dedup_csv = pivot_dedup_all.reset_index().to_csv(index=True).encode('utf-8')
st.download_button(
    label="중복제거 피벗 테이블 CSV 다운로드",
    data=pivot_dedup_csv,
    file_name="business_pivot_dedup_data.csv",
    mime="text/csv"
)

# 전체 PNG 다운로드
buf = io.BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)
st.download_button(
    label="전체 그래프 PNG 다운로드",
    data=buf,
    file_name="business_graph_all.png",
    mime="image/png"
)
