import streamlit as st
import os
import requests

def list_audio_files(directory):
    """List mp3 files in a specified directory."""
    files = [f for f in os.listdir(directory) if f.endswith('.mp3')]
    return files

def send_audio_to_api(audio_file):
    """Function to send an audio file to your API."""
    url = 'https://mozila-med-flask-vad2a77hmq-ey.a.run.app/upload'  # Replace with your actual API URL
    files = {'file': open(audio_file, 'rb')}
    try:
        response = requests.post(url, files=files)
        # st.write(response.text)
        if response.status_code == 400:
            return {"error": "Не знайшов аудіофайл. Спробуйте ще раз."}
        elif response.status_code == 429:
            return {"error": "Забагато запитів. Спробуйте ще раз через 10 секунд."}
        elif response.status_code != 200:
            # Handle other HTTP errors
            return {"error": f"Помилка під час обробки аудіо. Номер помилки: {response.status_code}"}
        return response.json()  # Assuming your API returns JSON and the response was successful
    except requests.RequestException as e:
        # Handle requests exceptions such as connection errors
        return {"error": f"Сталась помилка під час надсилання аудіо до сервера: {str(e)}"}
    finally:
        files['file'].close()

# Title of your app
st.title('Автоматичне розпізнавання мови')

st.markdown("""
    ### Інструкція
        1. Запишіть аудіо або виберіть готовий файл.
            1.1 Файл повинен бути у форматі .mp3.
            1.2 Аналізуватись буде лише перших 30 секунд.
            1.3 Мова аудіо - українська.
        2. Натисніть кнопку "Надіслати файл на обробку".
        3. Очікуйте результату розпізнавання.
            """)

# Audio file selection
audio_folder = 'data'
audio_files = list_audio_files(audio_folder)
selected_file = st.selectbox('Вибери готовий файл:', audio_files)

# External link to record audio
st.markdown('Або [запиши своє власне](https://online-voice-recorder.com/)', unsafe_allow_html=True)

# File uploader for user recordings
uploaded_file = st.file_uploader("Вибрати файл (.mp3):", type="mp3")
if uploaded_file is not None:
    with open(os.path.join(audio_folder, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getvalue())


if uploaded_file is not None:
    # Use the uploaded file
    audio_data = uploaded_file.getvalue()
    audio_file_to_display = uploaded_file.name
else:
    # Use the selected file from the dropdown
    audio_file_to_display = os.path.join(audio_folder, selected_file)
    audio_data = open(audio_file_to_display, "rb").read()
    
file_to_send = uploaded_file.name if uploaded_file is not None else selected_file
if st.button('Надіслати файл на обробку'):
    st.audio(audio_data)
    st.markdown(f"""
        ### Надсилання файлу на обробку
        - **Обраний файл:** `{file_to_send}`
        - **Орієнтовний час обробки:**
            - Зазвичай обробка триває **20 секунд**.
            - Або якщо сервер спить - це може зайняти до **1 хвилини**.
    """)
    
    with st.spinner('Обробка ...'):
        response = send_audio_to_api(os.path.join(audio_folder, file_to_send))
    
    if 'error' in response:
        st.error(response['error'])
    else:
        st.markdown(f"""
            ### Результат розпізнавання
            > {response['transcript']}
        """)


