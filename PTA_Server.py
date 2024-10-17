import socket
import threading
import os

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 11550        # Porta que o servidor vai escutar

# Lista de usuários permitidos
with open(r"./pta-server/users.txt", 'r') as file:
    valid_users = [line.strip() for line in file.readlines()]

# Pasta onde estão os arquivos disponíveis
file_directory = r"./pta-server/files"

# Função para lidar com a conexão do cliente
def handle_client(conn, addr):
    print(f"Conexão estabelecida com {addr}")
    seq_num = 0
    authenticated = False
    
    try:
        while True:
            # Receber a mensagem do cliente
            data = conn.recv(1024).decode()
            if not data:
                break
            
            print(f"Recebido: {data}")
            parts = data.split(" ")
            client_seq_num = int(parts[0])
            command = parts[1]
            
            # Verifica se o comando é "CUMP" (Apresentação)
            if command == "CUMP":
                user = parts[2]
                if user in valid_users:
                    authenticated = True
                    response = f"{client_seq_num} OK"
                else:
                    response = f"{client_seq_num} NOK"
                    conn.sendall(response.encode())
                    break  # Fechar a conexão se o usuário for inválido
                
            elif authenticated:
                # Comando LIST - Listar arquivos disponíveis
                if command == "LIST":
                    try:
                        files = os.listdir(file_directory)
                        file_list = ",".join(files)
                        response = f"{client_seq_num} ARQS {len(files)} {file_list}"
                    except Exception:
                        response = f"{client_seq_num} NOK"
                
                # Comando PEGA - Requisição de arquivo
                elif command == "PEGA":
                    file_name = parts[2]
                    #print(file_name)
                    file_path = os.path.join(file_directory, file_name)
                    if os.path.exists(file_path):
                        print("o arquivo existe")
                        file_size = os.path.getsize(file_path)
                        with open(file_path, "rb") as f:
                            file_data = f.read()
                        print(file_data)
                        response = f"{client_seq_num} ARQ {file_size} {file_data}"
                        conn.sendall(response.encode())
                        #conn.sendall(file_data)  # Envia o conteúdo do arquivo
                        continue  # Pular envio de resposta adicional
                    else:
                        print("o arquivo não existe")
                        response = f"{client_seq_num} NOK"
                
                # Comando TERM - Fechar conexão
                elif command == "TERM":
                    response = f"{client_seq_num} OK"
                    conn.sendall(response.encode())
                    break  # Fechar a conexão
                
                # Comando desconhecido
                else:
                    response = f"{client_seq_num} NOK"
            
            else:
                # Cliente não autenticado tentando outro comando
                response = f"{client_seq_num} NOK"
                conn.close()
                break
            
            # Envia a resposta ao cliente
            conn.sendall(response.encode())
    finally:
        conn.close()
        print(f"Conexão com {addr} encerrada")

# Função para iniciar o servidor
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Servidor PTA escutando em {HOST}:{PORT}")
        
        try:
            while True:
                conn, addr = s.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.start()
        except KeyboardInterrupt:
            print("\nServidor encerrado com Ctrl+C")

if __name__ == "__main__":
    start_server()
