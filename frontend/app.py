import streamlit as st
import requests
from typing import Optional
import time

DEFAULT_BACKEND = 'http://localhost:8000/api/v1'
POLL_INTERVAL_SECONDS = 5

def get_base_url() -> str:
    return DEFAULT_BACKEND

def api_headers():
    token = st.session_state.get('token')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers

def api_get(path: str, params: dict = None):
    url = f'{get_base_url()}{path}'
    try:
        r = requests.get(url=url, headers=api_headers(), params=params, timeout=10)
        return r
    except Exception as e:
        st.error(f'GET request failed: {e}')
        return None

def api_post(path: str, json_data: dict):
    url = f'{get_base_url()}{path}'
    try:
        r = requests.post(url=url, headers=api_headers(), json=json_data, timeout=10)
        return r
    except Exception as e:
        st.error(f'POST request failed: {e}')
        return None
    
def do_signup(email: str, username: str, password: str):
    payload = {'email': email, 'username': username, 'password': password}
    r = api_post('/auth/signup', payload)
    if not r:
        return False
    if r.status_code == 200 or r.status_code == 201:
        st.success('Signup successful - you can proceed to login now!')
        return True
    else:
        st.error(f'Signup failed. {r.status_code} {r.text}')
        return False

def do_login(email: str, password: str):
    payload = {'email': email, 'password': password}
    r = api_post('/auth/login',payload)
    if r.status_code == 200:
        token = r.json().get('access_token')
        st.session_state['token'] = token
        st.success('Logged in successfully!')
        return True
    else:
        st.error(f'Login failed: {r.status_code} {r.text}')
        return False
    
def require_login():
    if 'token' not in st.session_state:
        st.warning('Kindly login before perfoming this action')
        st.stop()

def page_login():
    tabs = st.tabs(['Login', 'Signup'])
    with tabs[0]:
        email = st.text_input('Enter your email', key='login_email')
        password = st.text_input('Enter your password', type='password', key='login_password')
        if st.button('Login'):
            do_login(email, password)
    with tabs[1]:
        s_email = st.text_input('Enter your email', key='signup_email')
        s_username = st.text_input('Enter your username', key='signup_username')
        s_password = st.text_input('Enter your password', type='password', key='signup_password')
        if st.button('Create account'):
            do_signup(s_email, s_username, s_password)

def page_dashboard():
    require_login()
    st.header('Dashboard')
    r = api_get('/users/me')
    if r and r.status_code == 200:
        user = r.json()
        st.subheader(f'Welcome {user.get('username')}')
        st.metric('Balance (INR): ', user.get('balance'))
    else:
        st.error('Account info unavailable')

    # implement positions and trade viewings later

def page_stocks():
    st.header('Stocks')
    r = api_get('/stocks/')
    if r and r.status_code == 200:
        stocks = r.json()
        for s in stocks:
            st.write(f'Ticker: {s.get('ticker')} Name: {s.get('name')} Price: {s.get('last_price')}') 
    else:
        st.error('Could not fetch stocks') 

def page_order_book_and_place():
    require_login()
    st.header('Order book & Place Order')
    # implement the calls later

def page_trades():
    require_login()
    st.header('Trade History')
    r = api_get('/trades/')
    if r and r.status_code == 200:
        trades = r.json()
        if trades:
            for t in reversed(trades[-50:]):
                st.write(f"#{t.get('id')} stock {t.get('stock_id')} qty {t.get('quantity')} @ {t.get('price')} ({t.get('traded_at')})")
        else:
            st.write('No trades yet')
    else:
        st.error('Could not fetch trades')

def page_account():
    require_login()
    st.header('Account')
    if st.button('Logout'):
        st.session_state.pop('token', None)
        st.rerun()


st.set_page_config(page_title='Trading Platform', layout='wide')
st.title('Trading Platform')
menu = ['Login/Signup', 'Dashboard', 'Stocks', 'Orders', 'Trades', 'Account']
choice = st.sidebar.selectbox('Navigation', menu)

if choice == 'Login/Signup':
    page_login()
elif choice == 'Dashboard':
    page_dashboard()
elif choice == 'Stocks':
    page_stocks()
elif choice == 'Orders':
    page_order_book_and_place()
elif choice == 'Trades':
    page_trades()
elif choice == 'Account':
    page_account()