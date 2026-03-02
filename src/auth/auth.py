import streamlit as st

def check_password():
    """Kullanıcı adı ve şifreyi kontrol eder."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Giriş Ekranı
    st.title("🔐 Yönetim Paneli")
    with st.form("login_form"):
        user = st.text_input("Kullanıcı Adı")
        pw = st.text_input("Şifre", type="password")
        submitted = st.form_submit_button("Giriş Yap")
        
        if submitted:
            if user == "nidakd" and pw == "muhasebe123":
                st.session_state["password_correct"] = True
                st.rerun() # Bilgiler doğruysa sayfayı yenile ve içeri al
            else:
                st.error("❌ Kullanıcı adı veya şifre hatalı!")
    return False
