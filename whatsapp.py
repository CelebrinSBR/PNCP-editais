from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import urllib.parse
import time
import os

# Certifique-se que o chromedriver.exe v151 está na mesma pasta!
CAMINHO_CHROMEDRIVER = "chromedriver.exe" 

def iniciar_driver():
    options = webdriver.ChromeOptions()
    
    # Perfil para salvar o login
    caminho_perfil = os.path.join(os.getcwd(), "Perfil_WA")
    options.add_argument(f"user-data-dir={caminho_perfil}")
    
    # ==========================================
    # FLAGS DE ESTABILIDADE PARA AMBIENTE CORPORATIVO
    # ==========================================
    options.add_argument('--no-sandbox') # Contorna restrições de segurança do SO
    options.add_argument('--disable-dev-shm-usage') # Resolve problemas de memória RAM no Chrome
    options.add_argument('--disable-gpu') # Evita travamentos de renderização gráfica
    options.add_argument('--log-level=3') # Esconde avisos no terminal
    
    # Usando o ChromeDriver local (sem baixar da internet)
    servico = Service(CAMINHO_CHROMEDRIVER)
    driver = webdriver.Chrome(service=servico, options=options)
    
    print("Abrindo WhatsApp Web...")
    driver.get("https://web.whatsapp.com/")
    
    print("Aguardando o WhatsApp carregar (Escaneie o QR Code se for a primeira vez)...")
    try:
        # Procurando a barra lateral que confirma o login
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, 'side'))
        )
        print("✅ WhatsApp Web logado e pronto para os disparos!")
        return driver
    except Exception as e:
        print(f"❌ Tempo esgotado ou erro ao carregar o WhatsApp: {e}")
        driver.quit()
        return None

def enviar_mensagem(driver, telefone, mensagem):
    telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
    
    if not telefone_limpo.startswith("55"):
        telefone_limpo = f"55{telefone_limpo}"
        
    mensagem_url = urllib.parse.quote(mensagem)
    link = f"https://web.whatsapp.com/send?phone={telefone_limpo}&text={mensagem_url}"
    
    print(f"Preparando envio para: {telefone_limpo}...")
    driver.get(link)
    
    try:
        # Procurando a caixa de texto
        caixa_de_texto = WebDriverWait(driver, 35).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer//div[@contenteditable="true"]'))
        )
        time.sleep(2) 
        
        caixa_de_texto.send_keys(Keys.ENTER)
        
        time.sleep(3) 
        print(f"✅ Mensagem enviada com sucesso para {telefone_limpo}!")
        return True
        
    except Exception as e:
        print(f"❌ Falha ao enviar para {telefone_limpo}. O número existe? Erro: {e}")
        return False

def fechar_driver(driver):
    print("Fechando o navegador...")
    driver.quit()

