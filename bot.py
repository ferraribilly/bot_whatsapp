from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import threading
import time

app = Flask(__name__)
driver = webdriver.Chrome()
mensagens_respondidas = set()

def iniciar_automatizacao():
    global mensagens_respondidas

    driver.get("https://whats-delivery-uber-vairapido.onrender.com/")

    email_input = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div/form/div[1]/input')
    email_input.send_keys("delivery@gmail.com")

    password_input = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div/form/div[2]/input')
    password_input.send_keys("230872Ferrari@@")

    login_button = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div/div/div/form/button')
    login_button.click()

    time.sleep(5)

    try:
        notificaco_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[2]/div[2]/div/div[2]/button[1]'))
        )
        notificaco_button.click()
        time.sleep(5)
    except:
        print("❌ Botão de notificação não encontrado.")

   
    try:
        mensagens_atuais = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[2]/ul/li'))
        )
        for msg in mensagens_atuais:
            mensagens_respondidas.add(msg.text.strip())
        print(f"✅ Ignorando mensagens antigas: {len(mensagens_respondidas)} mensagens")
    except Exception as e:
        print(f"❌ Erro ao capturar mensagens iniciais: {e}")

    while True:
        try:
            mensagens = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[2]/ul/li'))
            )

            for msg_element in mensagens:
                try:
                    texto_msg = msg_element.text.strip()
                except StaleElementReferenceException:
                    continue 

                if texto_msg and texto_msg not in mensagens_respondidas:
                    print(f"📩 Nova mensagem recebida: {texto_msg}")

                    try:
                        msg_element.click()
                        time.sleep(2)

                        campo_input = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[2]/div/form/div/div/input'))
                        )
                        campo_input.clear() 
                        campo_input.send_keys("Seja bem-vindo")
                        campo_input.send_keys(Keys.ENTER)
                        print("✅ Resposta enviada: Seja bem-vindo")

                        mensagens_respondidas.add(texto_msg)

                    except (StaleElementReferenceException, TimeoutException) as e:
                        print(f"❌ Erro ao responder mensagem (elemento mudou): {e}")

                    except Exception as e:
                        print(f"❌ Erro ao responder mensagem: {e}")

        except (TimeoutException, StaleElementReferenceException):
           
            pass
        except Exception as e:
            print(f"❌ Erro ao monitorar mensagens: {e}")

        time.sleep(5)

threading.Thread(target=iniciar_automatizacao, daemon=True).start()

@app.route('/')
def index():
    return 'Servidor WhatsApp Delivery rodando na porta 3001 ✅'

@app.route('/enviar-mensagem', methods=['POST'])
def enviar_mensagem():
    try:
        texto = request.json.get('mensagem', '')

        send_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[2]/div/form/div/div/input'))
        )
        send_message.clear()
        send_message.send_keys(texto)
        send_message.send_keys(Keys.ENTER)
        return jsonify({'status': 'Mensagem enviada com sucesso ✅', 'mensagem': texto})
    except Exception as e:
        return jsonify({'status': 'Erro ao enviar mensagem ❌', 'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
