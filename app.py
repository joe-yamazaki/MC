import streamlit as st
import pdfplumber
import csv
import re
import datetime
import io

def extract_label_data(text):
    if not text:
        return None
    
    lines = text.split('\n')
    # Filter out empty lines
    lines = [line.strip() for line in lines if line.strip()]
    
    if not lines:
        return None

    product_name = ""
    val1 = ""
    val2 = ""
    val3 = ""
    val4 = ""
    val5 = ""
    val6 = ""
    
    # Iterate through lines to find patterns
    processed_indices = set()
    
    # 1. Find Bottom Line first (most distinct)
    for i, line in enumerate(lines):
        if i in processed_indices: continue
        
        # Pattern: value - value - value (allowing alphanumeric and special chars like ^)
        match_hyphen = re.search(r'([^-\s]+)\s*-\s*([^-\s]+)\s*-\s*([^-\s]+)', line)
        match_slash = re.search(r'(\d+)\s*/\s*(\d+)', line)
        
        if match_hyphen:
            val3 = match_hyphen.group(1)
            val4 = match_hyphen.group(2)
            val5 = match_hyphen.group(3)
            processed_indices.add(i)
            
            # Slash might be on the same line
            if match_slash:
                val6 = f"{match_slash.group(1)}/{match_slash.group(2)}"
            break # Assume only one bottom line
            
    # 2. Find Value Line (middle)
    for i, line in enumerate(lines):
        if i in processed_indices: continue
        
        # Look for "1900 ( 673160)" pattern
        match_middle = re.search(r'(\d+)\s*\(\s*(\d+)\s*\)', line)
        if match_middle:
            val1 = match_middle.group(1)
            val2 = match_middle.group(2)
            processed_indices.add(i)
            break
        
    # 3. Find Product Name (remaining line, usually first)
    for i, line in enumerate(lines):
        if i in processed_indices: continue
        
        if not product_name:
            product_name = line
            processed_indices.add(i)
        else:
            pass

    # Combine val3, val4, val5 with hyphens
    # User requested: 1, 05, 1 -> 1-05-1 (Removed apostrophe)
    val345 = ""
    if val3 and val4 and val5:
        val345 = f"{val3}-{val4}-{val5}"
    
    # Add leading apostrophe to val6
    # User requested: 1/1 -> '1/1
    if val6:
        val6 = f"'{val6}"

    return [product_name, val1, val2, val345, val6]

def process_pdf(pdf_file):
    data_rows = []
    
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            width = page.width
            height = page.height
            
            col_width = width / 3
            # Fixed row height and margin based on analysis
            row_height = 72
            top_margin = 20
            
            for row in range(10):
                for col in range(3):
                    # Calculate coordinates with fixed margin and height
                    x0 = col * col_width
                    top = top_margin + (row * row_height)
                    x1 = (col + 1) * col_width
                    bottom = top + row_height
                    
                    # Crop the cell
                    cell = page.crop((x0, top, x1, bottom))
                    
                    # Extract text
                    text = cell.extract_text(layout=True)
                    
                    # Parse data
                    row_data = extract_label_data(text)
                    
                    if row_data:
                        # Validation: Product name should not look like the bottom row
                        if re.search(r'[A-Za-z0-9]+\s*-\s*[A-Za-z0-9]+\s*-\s*[A-Za-z0-9]+', row_data[0]):
                            continue
                            
                        data_rows.append(row_data)
    return data_rows

def main():
    st.title("部材シール PDF to CSV Converter")
    st.write("PDFファイルをアップロードして、CSVに変換します。")

    uploaded_file = st.file_uploader("PDFファイルを選択してください", type="pdf")

    if uploaded_file is not None:
        if st.button("変換開始"):
            with st.spinner("変換中..."):
                try:
                    data_rows = process_pdf(uploaded_file)
                    
                    if not data_rows:
                        st.warning("データが見つかりませんでした。")
                    else:
                        st.success(f"{len(data_rows)}件のデータを抽出しました。")
                        
                        # Preview
                        st.write("抽出データプレビュー:")
                        st.dataframe(data_rows)
                        
                        # Create CSV in memory
                        output = io.StringIO()
                        writer = csv.writer(output)
                        writer.writerows(data_rows)
                        csv_data = output.getvalue()
                        
                        # Generate filename with timestamp
                        now = datetime.datetime.now()
                        timestamp = now.strftime("%Y%m%d_%H%M%S")
                        filename = f"output_{timestamp}.csv"
                        
                        st.download_button(
                            label="CSVをダウンロード",
                            data=csv_data,
                            file_name=filename,
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
