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
st.write("2024.10~2025.07 데이터를 테이블별로 비교합니다. 기준월을 컬럼으로, 숫자는 천 단위 쉼표로 포맷팅해 오른쪽 정렬로 표시됩니다. 각 표 위에 최대/최소 수치를 요약합니다!")

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

# 테이블 목록
tables = df['테이블'].unique()

# 테이블별 피벗 테이블 생성 및 표시
for table in tables:
    st.subheader(f"{table}")
    table_data = df[df['테이블'] == table].copy()
    
    # 피벗 테이블 생성 (기준월을 컬럼으로)
    pivot_data = table_data.pivot_table(
        index=['테이블'], 
        columns='기준월', 
        values=['법인사업자_중복제거', '개인사업자_중복제거', '총사업자_중복제거', 
                '법인사업자_중복제거X', '개인사업자_중복제거X', '총사업자_중복제거X'],
        aggfunc='sum'
    )
    
    # 멀티인덱스 컬럼을 단일 레벨로 변환
    pivot_data.columns = [f'{col[1]}_{col[0]}' for col in pivot_data.columns]
    pivot_data = pivot_data.reset_index()
    
    # 최대/최소 수치 요약
    numeric_cols = pivot_data.select_dtypes(include=np.number).columns
    summary = pivot_data[numeric_cols].describe().loc[['max', 'min']].T
    st.write(f"{table} 요약 (기준월별):")
    st.write(summary)
    
    # 숫자 포맷팅 (천 단위 쉼표)
    pivot_data_formatted = pivot_data.copy()
    for col in numeric_cols:
        pivot_data_formatted[col] = pivot_data[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "-")
    
    st.write(pivot_data_formatted)

# Plotly 그래프 (한글 폰트 문제 우회)
st.subheader("월별 사업자 수 변화 (Plotly)")
fig = px.line(df, x='기준월', y='총사업자_중복제거', color='테이블', 
              title='월별 총사업자 수 (중복제거)', 
              labels={'기준월': '기준월', '총사업자_중복제거': '총사업자 수 (중복제거)', '테이블': '유형'})
fig.update_layout(font=dict(family="Noto Sans KR, sans-serif", size=12))
st.plotly_chart(fig, use_container_width=True)

# matplotlib 그래프
st.subheader("월별 사업자 수 변화 (matplotlib)")
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

# 피벗 테이블 CSV 다운로드
pivot_all = pd.concat([df[df['테이블'] == table].pivot_table(
    index=['테이블'], 
    columns='기준월', 
    values=['법인사업자_중복제거', '개인사업자_중복제거', '총사업자_중복제거'],
    aggfunc='sum'
).reset_index() for table in tables])
pivot_all.columns = [f'{col[1]}_{col[0]}' if isinstance(col, tuple) else col for col in pivot_all.columns]
pivot_csv = pivot_all.to_csv(index=False).encode('utf-8')
st.download_button(
    label="피벗 테이블 CSV 다운로드",
    data=pivot_csv,
    file_name="business_pivot_data.csv",
    mime="text/csv"
)

# PNG 다운로드
buf = io.BytesIO()
plt.savefig(buf, format="png")
buf.seek(0)
st.download_button(
    label="그래프 PNG 다운로드",
    data=buf,
    file_name="business_graph.png",
    mime="image/png"
)
