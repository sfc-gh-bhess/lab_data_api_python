import os
import requests
from urllib.parse import urlparse

def get_pat_filename():
    files = os.listdir()
    pat_files = [x for x in files if x.endswith('-token-secret.txt')]
    if len(pat_files) < 1:
        return None
    return pat_files[0]

def get_pat(pfname):
    if not pfname or not os.path.isfile(pfname):
        return None
    return open(pfname, 'r').read()

def get_token(account_url, role, endpoint, pat):
    endpoint_host = urlparse(endpoint).hostname
    scope = f'session:scope:{role.upper()} {endpoint_host}'
    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'scope': scope,
        'subject_token': pat,
        'subject_token_type': 'programmatic_access_token'
    }
    url = f'https://{account_url}/oauth/token'
    resp = requests.post(url=url, data=data)
    return resp.text

def call_endpoint(token, url, method='GET'):
    headers = {'Authorization': f'Snowflake Token="{token}"'}
    return requests.request(method=method, url=url, headers=headers)

def streamlit():
    import streamlit as st
    st.title('Test your API')
    default_pat = get_pat(get_pat_filename())
    with st.form("Details"):
        acct_url = st.text_input("Account URL", help="Account URL in the form of: <ORGNAME>-<ACCTNAME>.snowflakecomputing.com")
        role = st.text_input("Role", help="Snowflake ROLE to use")
        pat = default_pat if default_pat else st.text_input("PAT Token", help="PAT token to use")
        url = st.text_input("SPCS request URL", help="SPCS reqeust URL (including 'https://')")
        if st.form_submit_button("Fetch it!"):
            st.toast("Trading PAT for Token...")
            token = get_token(acct_url, role, url, pat)
            st.toast("Getting data...")
            resp = call_endpoint(token, url)
            st.json(resp.json())

if __name__ == '__main__':
    streamlit()
