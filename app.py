import pandas as pd
import numpy
import streamlit as st
import requests
from bs4 import BeautifulSoup
import ndjson
import os
import io
import xlsxwriter



st.set_page_config(
    page_title= '書籍情報取得アプリ'
    )
st.title('書籍情報取得アプリ')


st.write('本を探す↓')
st.caption('https://www.books.or.jp', unsafe_allow_html=True, help=None)

st.write("""
         ### データ取得
         """)
url = st.text_input('本のURLを入力して下さい')


def get_data():
    # url 取得
    res = requests.get(url)
    soup=BeautifulSoup(res.text,"html.parser")

    #タイトル
    title = soup.find("h1", class_ = "detail-title").text.replace("\n","")

    #著者
    author = soup.find("h2", class_ = "detail-author").text.replace("著：","")


    #出版社
    a = soup.find("div", class_ = "book-other-data").text
    text_list =a.split("。")
    for text in text_list:
       if "出版社" in text:
           pub = text
    publisher = pub.split("：")[1]

    #価格
    a = soup.find("div", class_ = "book-other-data").text
    text_list =a.split("。")
    for text in text_list:
       if "定価" in text:
           pr = text
    price = pr.split("：")[1]

    #データフレームに格納
    df = pd.DataFrame({'タイトル': title,
                        '著者': author,
                        '出版社': publisher,
                        '定価':price}, index = [0]
                     )
    return df

if not url:
    st.error('少なくとも一つURLを入力してください。')
else:
    #データを取得し編集
    edited_data = st.data_editor(get_data())
    st.write('直接編集できます。編集終了後、下の「保存」ボタンを押して下さい。')



if st.button('保存する'):
    # 編集後データ取得
    a = edited_data.to_dict()
    ed_title = a['タイトル'][0]
    ed_author = a['著者'][0]
    ed_publisher = a['出版社'][0]
    ed_price = a['定価'][0]

    ed_data = {'タイトル': ed_title,
             '著者': ed_author,
             '出版社': ed_publisher,
             '定価':ed_price}

    #ファイルに保存
    with open("bookdetails.ndjson", "a") as f:
        writer = ndjson.writer(f)
        writer.writerow(ed_data)


st.write("""
         ### データ一覧
         """)

try:
    #ファイルを開く
    with open("bookdetails.ndjson") as f:
        datas = ndjson.load(f)

    #データを更新
    final_df = pd.DataFrame(datas)
    
    st.write(final_df)
except:
    st.write('まだデータがありません')


    
#エクセルデータの取得

if st.button('エクセルファイルに変換'):
    # Create a BytesIO buffer to hold the Excel file
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    final_df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.close()
    output.seek(0)

    # Download the Excel file
    st.download_button(
        label='エクセルファイルのダウンロード',
        data=output,
        file_name='選書リスト.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )



#データを削除
if st.button('データを削除する'):
    try:
        os.remove('./bookdetails.ndjson')
        st.write('ページを更新してください')
    except:
        st.write('まだデータがありません')
    #ページを更新
    



    






