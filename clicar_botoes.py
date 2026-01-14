import time
import re
import pyautogui as pg
from pathlib import Path
import keyboard

ASSETS = Path(__file__).parent / "assets"

pg.FAILSAFE = True
pg.PAUSE = 0.2

TEMPO_PARA_ALT_TAB = 5  # segundos para mudar de tela

# ===== MAPA CÓDIGO -> NOME DA EMPRESA =====
EMPRESAS = {
    "590": "SECARTI SERVICOS MEDICOS LTDA",
    "591": "IMED SUDESTE ATENDIMENTO MEDICO S.A.",
}

# ===== LISTA DE EMPRESAS PARA O LOOP =====
EMPRESAS_LOOP = [
    "590",
    "591",
]

def abortar():
    # Atalho para abortar (mais seguro que esc, pois esc você usa no fluxo)
    if keyboard.is_pressed("ctrl+shift+q"):
        raise SystemExit("Automação abortada (Ctrl+Shift+Q).")

def esperar_pos(img_name, confidence=0.82, timeout=40):
    img = str(ASSETS / img_name)
    start = time.time()
    while time.time() - start < timeout:
        abortar()
        pos = pg.locateCenterOnScreen(img, confidence=confidence)
        if pos:
            return pos
        time.sleep(0.25)
    raise RuntimeError(f"Não encontrei: {img_name}")

def clicar(img_name, confidence=0.82, timeout=40):
    pos = esperar_pos(img_name, confidence, timeout)
    pg.click(pos)

def clicar_flex(img_name, confs, timeout=120):
    for conf in confs:
        try:
            clicar(img_name, confidence=conf, timeout=timeout)
            return
        except Exception:
            pass
    raise RuntimeError(f"Falha ao clicar: {img_name}")

def hover(img_name, confidence=0.82, timeout=40):
    pos = esperar_pos(img_name, confidence, timeout)
    pg.moveTo(pos)

def normalizar_nome_arquivo(texto: str) -> str:
    texto = re.sub(r'[<>:"/\\|?*]', " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def gerar_nome_pdf(codigo: str, mes_ano: str) -> str:
    nome = EMPRESAS.get(codigo, f"EMPRESA_{codigo}")
    nome = normalizar_nome_arquivo(nome)
    mes_ano = mes_ano.replace("/", "-")
    return f"{nome} - {mes_ano} - PIS.COFINS.pdf"

def apertar_esc_duas_vezes():
    pg.press("esc")
    time.sleep(0.5)
    pg.press("esc")
    time.sleep(2)

def trocar_empresa(codigo: str):
    pg.press("f8")
    time.sleep(0.6)
    pg.hotkey("ctrl", "a")
    pg.write(codigo, interval=0.05)
    pg.press("enter")
    time.sleep(5)

def salvar_pdf(nome_pdf: str):
    # Garantir foco na aba do PDF
    w, h = pg.size()
    pg.click(w // 2, h // 2)
    time.sleep(1)

    # Clica no botão Salvar como (ícone do lápis)
    clicar("salvar_como.png", confidence=0.82, timeout=60)
    time.sleep(2)

    # Renomeia e salva
    pg.hotkey("ctrl", "a")
    time.sleep(0.2)
    pg.write(nome_pdf, interval=0.03)
    time.sleep(0.5)
    pg.press("enter")

    # Confirma substituir, se aparecer
    time.sleep(1)
    pg.press("enter")

    # Espera garantir que salvou e fecha a guia (última coisa)
    time.sleep(3)
    pg.hotkey("ctrl", "w")
    time.sleep(2)

def processar_empresa(codigo: str, data: str):
    apertar_esc_duas_vezes()
    trocar_empresa(codigo)

    clicar("relatorios.png")
    time.sleep(2)

    hover("impostos.png")
    time.sleep(2)

    clicar("efd_pis_cofins.png")

    time.sleep(1)
    pg.hotkey("ctrl", "a")
    time.sleep(0.2)
    pg.press("backspace")
    time.sleep(0.2)
    pg.write(data, interval=0.05)

    clicar("botao_ok.png")
    time.sleep(18)

    clicar_flex("botao_pdf.png", [0.88, 0.84, 0.80], timeout=120)
    time.sleep(1)

    clicar("gerar_pdf_unico.png")
    time.sleep(6)

    clicar("downloads.png")
    time.sleep(1)

    clicar("ok_azul.png")
    time.sleep(6)

    nome_pdf = gerar_nome_pdf(codigo, data)
    salvar_pdf(nome_pdf)

def main():
    data = input("Digite o mês/ano (ex: 11/2025): ").strip()

    print(f"\nVocê tem {TEMPO_PARA_ALT_TAB}s para dar Alt+Tab e deixar o sistema em foco.")
    print("Para abortar: Ctrl+Shift+Q\n")
    time.sleep(TEMPO_PARA_ALT_TAB)

    for codigo in EMPRESAS_LOOP:
        print(f"➡ Processando empresa {codigo} - {EMPRESAS.get(codigo, '')}")
        processar_empresa(codigo, data)

    print("\n✅ Todas as empresas processadas com sucesso!")

if __name__ == "__main__":
    main()
