import streamlit as st
import fitz
import csv
import re
import pandas as pd
import io

def extract_pdf_data_from_bytes(pdf_bytes, filename):
    """
    Extracts specific data from the left-hand form of each page in the PDF (from bytes).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_data = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        midpoint = page.rect.width / 2
        words = page.get_text("words")

        # Group words on the left side
        left_words = [w for w in words if w[2] < midpoint]

        # 1. Extract '製番' (Seiban)
        seiban = ""
        for w in left_words:
            if 40 < w[1] < 80:
                if "(" in w[4] or re.match(r'^\d+', w[4]):
                    seiban = w[4]
                    break

        # 2. Extract item rows (品名, 仕様, 数量)
        rows_data = {}
        for w in left_words:
            x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
            if 190 < y0 < 460:
                line_y = round(y0)
                if line_y not in rows_data:
                    rows_data[line_y] = []
                rows_data[line_y].append(w)

        for line_y in sorted(rows_data.keys()):
            line_words = sorted(rows_data[line_y], key=lambda w: w[0])
            himmey = ""
            shiyou = ""
            suuryou = ""
            
            for w in line_words:
                x0, text = w[0], w[4]
                if x0 < 150: # 品名 area
                    himmey += text + " "
                elif 200 < x0 < 320: # 仕様 area
                    shiyou += text
                elif 350 < x0 < 410: # 数量 area
                    suuryou = text

            himmey = himmey.strip()
            shiyou_match = re.search(r'^\d+', shiyou)
            shiyou_clean = shiyou_match.group(0) if shiyou_match else ""

            if himmey or shiyou_clean or suuryou:
                if himmey == "品名" or shiyou == "仕様" or suuryou == "数量":
                    continue
                if himmey:
                    all_data.append({
                        "ファイル名": filename,
                        "製番": seiban,
                        "品名": himmey,
                        "仕様": shiyou_clean,
                        "数量": suuryou
                    })

    doc.close()
    return all_data

# Streamlit UI
st.set_page_config(page_title="現品票 PDF to CSV Converter", layout="wide")

st.title("📄 現品票 PDF to CSV Converter")
st.write("PDFをアップロードすると、左側の現品票からデータを抽出します。")

uploaded_files = st.file_uploader("PDFファイルをアップロードしてください", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("変換開始"):
        all_extracted_data = []
        
        with st.spinner('データを抽出中...'):
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.read()
                data = extract_pdf_data_from_bytes(file_bytes, uploaded_file.name)
                all_extracted_data.extend(data)

        if all_extracted_data:
            st.success(f"{len(uploaded_files)} 個のファイルから {len(all_extracted_data)} 行のデータを抽出しました。")
            
            df = pd.DataFrame(all_extracted_data)
            st.dataframe(df, use_container_width=True)

            # CSV Download
            csv_buffer = io.StringIO()
            csv_writer = csv.writer(csv_buffer)
            for row in all_extracted_data:
                csv_writer.writerow([row["製番"], row["品名"], row["仕様"], row["数量"]])
            
            st.download_button(
                label="CSVをダウンロード",
                data=csv_buffer.getvalue(),
                file_name="extracted_data.csv",
                mime="text/csv",
            )
        else:
            st.warning("データが見つかりませんでした。")
else:
    st.info("PDFファイルをアップロードして開始してください。")
