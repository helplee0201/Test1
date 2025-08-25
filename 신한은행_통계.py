import pandas as pd
import streamlit as st
import io
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import os

# Streamlit 페이지 설정: 넓은 레이아웃
st.set_page_config(layout="wide")

# 한글 폰트 설정
font_paths = [
    'C:/Windows/Fonts/malgun.ttf',  # Malgun Gothic
    'C:/Windows/Fonts/NanumGothic.ttf',  # NanumGothic
]
font_path = None
for path in font_paths:
    if os.path.exists(path):
        font_path = path
        break

if font_path:
    font = fm.FontProperties(fname=font_path)
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
else:
    st.warning("한글 폰트 파일을 찾을 수 없습니다. 'C:/Windows/Fonts/malgun.ttf'를 확인하거나 NanumGothic을 설치하세요.")

# Streamlit 앱 설정
st.title("신한은행 테크핀 데이터 비교 (24.10~25.06)")
st.write("엑셀 파일을 업로드하면 2024.10~2025.06 데이터를 테이블별로 구분해 보여줍니다. 숫자는 천 단위로 쉼표를 넣어 읽기 쉽게, 오른쪽 정렬로 화면에 꽉 차게 표시됩니다. 각 표 위에 최대/최소 수치를 요약해 비교 가능합니다!")

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
    width: 120px; /* 사업자유형 컬럼 고정 너비 */
}
table th:nth-child(n+2), table td:nth-child(n+2) {
    text-align: right !important;
    padding-right: 8px !important;
    max-width: 80px; /* 숫자 컬럼 너비 제한 */
}
</style>
""", unsafe_allow_html=True)

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일 업로드 (xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # 엑셀 파일 읽기
    try:
        df = pd.read_excel(uploaded_file, sheet_name="25년 6월분_테크핀", header=None)
    except Exception as e:
        st.error(f"엑셀 파일 읽기 오류: {e}")
        st.stop()

    # 데이터 파싱 함수
    def parse_techfin_data(df):
        months = ["24.10", "24.11", "24.12", "25.01", "25.02", "25.03", "25.04", "25.05", "25.06"]
        start_rows = [4, 13, 22, 31, 40, 49, 67, 76, 85]
        parsed_data = []

        for month, start_row in zip(months, start_rows):
            non_dedup_corp = df.iloc[start_row, 2:9].values
            non_dedup_indiv = df.iloc[start_row + 1, 2:9].values
            non_dedup_total = df.iloc[start_row + 2, 2:9].values
            dedup_row = start_row + 3
            dedup_corp = df.iloc[dedup_row, 2:9].values
            dedup_indiv = df.iloc[dedup_row + 1, 2:9].values
            dedup_total = df.iloc[dedup_row + 2, 2:9].values

            for table_idx, table_name in enumerate(["Table 1", "Table 2", "Table 3", "Table 4", "Table 5", "Table 6", "Table 7"]):
                parsed_data.append({
                    "기준월": month,
                    "테이블": table_name,
                    "법인사업자_중복제거X": non_dedup_corp[table_idx],
                    "개인사업자_중복제거X": non_dedup_indiv[table_idx],
                    "총사업자_중복제거X": non_dedup_total[table_idx],
                    "법인사업자_중복제거": dedup_corp[table_idx],
                    "개인사업자_중복제거": dedup_indiv[table_idx],
                    "총사업자_중복제거": dedup_total[table_idx]
                })

        result_df = pd.DataFrame(parsed_data)
        numeric_cols = result_df.columns[2:]
        result_df[numeric_cols] = result_df[numeric_cols].fillna(0).astype(int)
        return result_df

    # 데이터 파싱
    try:
        comparison_df = parse_techfin_data(df)
    except Exception as e:
        st.error(f"데이터 파싱 오류: {e}")
        st.stop()

    # 천 단위 쉼표 포맷팅 함수
    def format_thousands(x):
        return f"{x:,.0f}" if isinstance(x, (int, float)) else x

    # 테이블별 탭으로 구분
    st.subheader("테이블별 비교 표 (24.10~25.06)")
    tabs = st.tabs(["Table 1", "Table 2", "Table 3", "Table 4", "Table 5", "Table 6", "Table 7"])

    for i, tab in enumerate(tabs):
        table_name = f"Table {i+1}"
        table_df = comparison_df[comparison_df["테이블"] == table_name].copy()

        with tab:
            # 중복제거X 피벗 표
            st.subheader(f"{table_name} - 중복제거X")
            non_dedup_melt = table_df.melt(id_vars=["기준월"], value_vars=["법인사업자_중복제거X", "개인사업자_중복제거X", "총사업자_중복제거X"],
                                           var_name="사업자유형", value_name="수치")
            non_dedup_pivot = non_dedup_melt.pivot(index="사업자유형", columns="기준월", values="수치")
            non_dedup_pivot = non_dedup_pivot.reset_index()
            formatted_non_dedup = non_dedup_pivot.copy()
            formatted_non_dedup.iloc[:, 1:] = formatted_non_dedup.iloc[:, 1:].applymap(format_thousands)

            # 최대/최소 월 요약 (총사업자 기준)
            total_non = non_dedup_melt[non_dedup_melt["사업자유형"] == "총사업자_중복제거X"]
            if not total_non.empty:
                max_month = total_non.loc[total_non["수치"].idxmax(), "기준월"]
                max_value = total_non["수치"].max()
                min_month = total_non.loc[total_non["수치"].idxmin(), "기준월"]
                min_value = total_non["수치"].min()
                st.markdown(f"**요약**: 최대 수치: {max_month} ({format_thousands(max_value)}), 최소 수치: {min_month} ({format_thousands(min_value)})")
                def highlight_max_min(col):
                    styles = [''] * len(col)
                    if col.name in formatted_non_dedup.columns[1:]:
                        if col.name == max_month:
                            styles = ['border: 2px solid red' for _ in col]
                        elif col.name == min_month:
                            styles = ['border: 2px solid blue' for _ in col]
                    return styles
                styled_non_dedup = formatted_non_dedup.style.set_properties(
                    subset=formatted_non_dedup.columns[1:],
                    **{'text-align': 'right', 'padding-right': '8px'}
                ).apply(highlight_max_min, axis=0)
                def highlight_rows(row):
                    return ['background-color: #f2f2f2' if row.name % 2 == 0 else '' for _ in row]
                styled_non_dedup = styled_non_dedup.apply(highlight_rows, axis=1)
            else:
                st.markdown("**요약**: 데이터 없음")
                styled_non_dedup = formatted_non_dedup.style.set_properties(
                    subset=formatted_non_dedup.columns[1:],
                    **{'text-align': 'right', 'padding-right': '8px'}
                ).apply(highlight_rows, axis=1)
            st.dataframe(styled_non_dedup, use_container_width=True, height=150)

            # 중복제거 피벗 표
            st.subheader(f"{table_name} - 중복제거")
            dedup_melt = table_df.melt(id_vars=["기준월"], value_vars=["법인사업자_중복제거", "개인사업자_중복제거", "총사업자_중복제거"],
                                       var_name="사업자유형", value_name="수치")
            dedup_pivot = dedup_melt.pivot(index="사업자유형", columns="기준월", values="수치")
            dedup_pivot = dedup_pivot.reset_index()  # 오타 수정: reset Mallory_index() -> reset_index()
            formatted_dedup = dedup_pivot.copy()
            formatted_dedup.iloc[:, 1:] = formatted_dedup.iloc[:, 1:].applymap(format_thousands)

            # 최대/최소 월 요약 (총사업자 기준)
            total_dedup = dedup_melt[dedup_melt["사업자유형"] == "총사업자_중복제거"]
            if not total_dedup.empty:
                max_month = total_dedup.loc[total_dedup["수치"].idxmax(), "기준월"]
                max_value = total_dedup["수치"].max()
                min_month = total_dedup.loc[total_dedup["수치"].idxmin(), "기준월"]
                min_value = total_dedup["수치"].min()
                st.markdown(f"**요약**: 최대 수치: {max_month} ({format_thousands(max_value)}), 최소 수치: {min_month} ({format_thousands(min_value)})")
                def highlight_max_min(col):
                    styles = [''] * len(col)
                    if col.name in formatted_dedup.columns[1:]:
                        if col.name == max_month:
                            styles = ['border: 2px solid red' for _ in col]
                        elif col.name == min_month:
                            styles = ['border: 2px solid blue' for _ in col]
                    return styles
                styled_dedup = formatted_dedup.style.set_properties(
                    subset=formatted_dedup.columns[1:],
                    **{'text-align': 'right', 'padding-right': '8px'}
                ).apply(highlight_max_min, axis=0)
                styled_dedup = styled_dedup.apply(highlight_rows, axis=1)
            else:
                st.markdown("**요약**: 데이터 없음")
                styled_dedup = formatted_dedup.style.set_properties(
                    subset=formatted_dedup.columns[1:],
                    **{'text-align': 'right', 'padding-right': '8px'}
                ).apply(highlight_rows, axis=1)
            st.dataframe(styled_dedup, use_container_width=True, height=150)

            # 막대 그래프 (중복제거X)
            st.subheader(f"{table_name} 수치 변화 그래프 (중복제거X)")
            fig_non, ax_non = plt.subplots(figsize=(16, 6))
            sns.barplot(data=non_dedup_melt, x="기준월", y="수치", hue="사업자유형", palette="Set2", ax=ax_non)
            ax_non.set_title(f"{table_name} 월별 사업자 수 변화 (중복제거X)")
            ax_non.set_ylabel("사업자 수")
            ax_non.tick_params(axis='x', rotation=45)
            ax_non.legend(title="유형")
            st.pyplot(fig_non)

            # 막대 그래프 (중복제거)
            st.subheader(f"{table_name} 수치 변화 그래프 (중복제거)")
            fig_dedup, ax_dedup = plt.subplots(figsize=(16, 6))
            sns.barplot(data=dedup_melt, x="기준월", y="수치", hue="사업자유형", palette="Set3", ax=ax_dedup)
            ax_dedup.set_title(f"{table_name} 월별 사업자 수 변화 (중복제거)")
            ax_dedup.set_ylabel("사업자 수")
            ax_dedup.tick_params(axis='x', rotation=45)
            ax_dedup.legend(title="유형")
            st.pyplot(fig_dedup)

            # 그래프 PNG 다운로드
            png_buffer_non = io.BytesIO()
            fig_non.savefig(png_buffer_non, format="png", bbox_inches='tight')
            st.download_button(label=f"{table_name} 중복제거X 그래프 PNG 다운로드", data=png_buffer_non, file_name=f"{table_name}_non_dedup_graph.png", mime="image/png")

            png_buffer_dedup = io.BytesIO()
            fig_dedup.savefig(png_buffer_dedup, format="png", bbox_inches='tight')
            st.download_button(label=f"{table_name} 중복제거 그래프 PNG 다운로드", data=png_buffer_dedup, file_name=f"{table_name}_dedup_graph.png", mime="image/png")

    # 전체 CSV 다운로드
    csv_buffer = io.StringIO()
    comparison_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    st.download_button(
        label="전체 비교 표 CSV 다운로드",
        data=csv_buffer.getvalue(),
        file_name="techfin_comparison_24.10_25.06.csv",
        mime="text/csv"
    )

else:
    st.info("엑셀 파일을 업로드해주세요.")