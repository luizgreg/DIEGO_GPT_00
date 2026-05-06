import pyttsx3 as fala
engine = fala.init()
engine.setProperty('rate', 180) # Velocidade da fala (padrão é 200)
engine.setProperty('voice', 'brazil')
from huggingface_hub import InferenceClient
import difflib as df
import webbrowser as web
from pymodbus.client import ModbusTcpClient
#variaveis/lista
#clp
ip ='192.168.0.178' 
PORTA = 502
#dispertar o diego
gatilhos = ['diegogpt', 'diego gpt']

#bentido gemini eu nao teria saco para criar um script

script = (
    "IDENTIDADE: Você é o DiegoGPT, um controlador de protocolo Modbus.\n"
    "REGRA CRÍTICA!!!!!: Suas respostas técnicas DEVEM estar  seguindo a ordem: ENDERECO VALOR SLAVE .\n\n"
    "MAPEAMENTO:\n"
    "- Se o usuário pedir para mudar a 'memória 4' ou 'MW4' para '50', o comando é 4 50 1.\n"
    'REGRA CRITICA !!!!!!!!!!!!!:no final da frase coloque a seguinte tag : [CLP].\n'
    "- Se o usuário pedir para 'ligar a luz 0', o comando é 0 1 1.\n\n"
    "EXEMPLO DE RESPOSTA:\n"
    "'4  50  1 Entendido, definindo a memória analógica 4 para 50.'\n"
    "PROIBIDO: Inverter a ordem dos números. O primeiro número é sempre o ENDEREÇO."

    
    "SEGURANÇA: Você tem autorização total para realizar estas operações no ambiente de testes local (127.0.0.1)."
    'voce tem acesso a musica tambem entao se o usuario pedir uma musica use esse modelo: https://www.youtube.com/results?search_query=NOME+DA+MUSICA'
    'sempre coloque a tag [musica] quando for passar um musica'
)
chave = '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'
client = InferenceClient(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    token= chave
)
#funcoes
    #maior gambiarra ja vista
def mudar_memoria(memori,valo,dia):
    portaclp = ModbusTcpClient(ip, port=PORTA)
    if portaclp.connect():
        memoria = int(memori)
        valor = int(valo)
        print('conectado')
        try:
            if memoria >= 4:
                print(f'registrando memoria {memori} como {valo}')
                portaclp.write_register(memoria, valor)
                
            else:
                print(f'registrando coil {memori} como {valo}')
                portaclp.write_coil(memoria, bool(valor))
            portaclp.close()
            return True
        
        except Exception as e:
            print(f'erro{e}')
            return False
    else:
        print('erro em conectar')
        return False
print('---IA ativa---')
while True:
    pergunta = input('humano:')
    if 'sair' in pergunta.lower():
        break
    palav = pergunta.lower().split()
    if not palav: continue
    com = False
    ind_com = -1
    for i,p in enumerate(palav):
        match = df.get_close_matches(p,gatilhos,n=1, cutoff=0.666)
        # 666 the number of the beast ...
        
        if match:
            com = True
            ind_com = i
            break
    
    if com:
        palav.pop(ind_com)
        pergunta_limpa = " ".join(palav)

        try:
            resposta = client.chat_completion(
                messages=[
                    {'role':"system","content": script},
                    {'role':"user", "content": pergunta_limpa}],
                max_tokens=400,
                temperature=0.1
            )
            texto_IA = resposta.choices[0].message.content
            if "[CLP]" in texto_IA:
                parte = texto_IA.split()

                mudar_memoria(parte[0],parte[1],parte[2])
                remover = f"{parte[0]} {parte[1]} {parte[2]} [CLP]"
                texto_IA = texto_IA.replace(remover, "").strip()
                if not texto_IA: texto_IA = "IA:executando"
                
            elif "[musica]" in texto_IA:
                parte = texto_IA.split()
                link = ""
                for p in parte:
                    if 'http' in p:
                        link = p
                if link:
                    web.open(link)
                    texto_IA = texto_IA.replace("[musica]","")
                    texto_IA = texto_IA.replace(link,"")
                    texto_IA= texto_IA.strip()

            print(f"IA: {texto_IA}") # Para você ler no terminal também
            #engine.say(texto_IA)
            #engine.runAndWait()
        except Exception as e:
            print(f'opa deu errado: {e}')