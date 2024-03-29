import requests
import psycopg2
from tenacity import retry, stop_never, stop_after_attempt, wait_fixed


def establish_connection(database, user, password, host, port):
    def connect():
        try:
            print("Trying connection ...")
            return psycopg2.connect(
                                database=database,
                                user=user,
                                password=password,
                                host=host,
                                port=port
                            )
        except psycopg2.OperationalError:
            raise
    return connect()

def authorize(url_login, data_login, headers_login, url_login_backup):
    try:
        response_login = requests.post(
                url_login,json=data_login,
                headers=headers_login,
                verify=False
            )
        
        session_id = response_login.cookies.get("BAUMSID")
        return {"Cookie": f"BAUMSID={session_id}"}

    except requests.exceptions.RequestException:
        pass
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def authorize_backup():
        response_login_backup = requests.post(
                url_login_backup,
                json=data_login,
                headers=headers_login,
                verify=False
            )
    
        response_login_backup.raise_for_status()
        session_id_backup = response_login_backup.cookies.get("BAUMSID")
        return {"Cookie": f"BAUMSID={session_id_backup}"}
    return authorize_backup

def api_diskspace(url_diskspace, headers_diskspace, url_diskspace_backup):
    try:
        response_diskspace = requests.get(
                url_diskspace,
                headers=headers_diskspace,
                verify=False
            )
        response_diskspace.raise_for_status()
        return response_diskspace.json()
    except requests.exceptions.RequestException:
        pass
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def api_diskspace_backup():
        response_diskspace_backup = requests.get(
                url_diskspace_backup,
                headers=headers_diskspace,
                verify=False
            )
    
        response_diskspace_backup.raise_for_status()
        return response_diskspace_backup.json().get('result', {})
    return api_diskspace_backup
