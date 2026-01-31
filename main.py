import customtkinter as ctk
import requests
import os
import subprocess
from datetime import datetime

# Configurações de interface
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CryptoMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Monitor & Simulador BTC")
        self.geometry("480x720")
        self.resizable(False, False)

        self.log_file = "simulacoes_btc.txt"

        # Variáveis de controle
        self.btc_brl_atual = 0.0
        self.update_interval = 30
        self.counter = self.update_interval

        self.setup_ui()
        self.update_data()
        self.run_countdown()

    def setup_ui(self):
        # Header
        self.lbl_title = ctk.CTkLabel(self, text="Cotações em Tempo Real", font=("Roboto", 22, "bold"))
        self.lbl_title.pack(pady=(20, 5))

        self.lbl_timer = ctk.CTkLabel(self, text=f"Atualizando em: {self.counter}s", font=("Roboto", 12),
                                      text_color="gray")
        self.lbl_timer.pack()

        # Frame de Cotações
        self.frame_prices = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.frame_prices.pack(pady=20, padx=20, fill="x")

        self.lbl_btc_usd = ctk.CTkLabel(self.frame_prices, text="BTC/USD: $ 0.00", font=("Roboto", 16))
        self.lbl_btc_usd.pack(pady=5)

        self.lbl_btc_brl = ctk.CTkLabel(self.frame_prices, text="BTC/BRL: R$ 0.00", font=("Roboto", 18, "bold"),
                                        text_color="#F7931A")
        self.lbl_btc_brl.pack(pady=5)

        self.lbl_usd_brl = ctk.CTkLabel(self.frame_prices, text="Dólar: R$ 0.00", font=("Roboto", 16))
        self.lbl_usd_brl.pack(pady=5)

        # Seção Calculadora
        self.lbl_calc_title = ctk.CTkLabel(self, text="Simulador de Valorização", font=("Roboto", 18, "bold"))
        self.lbl_calc_title.pack(pady=10)

        self.entry_brl_invest = ctk.CTkEntry(self, placeholder_text="Investimento Inicial (BRL)", width=320, height=35,
                                             justify="center")
        self.entry_brl_invest.pack(pady=5)

        self.entry_btc_target = ctk.CTkEntry(self, placeholder_text="Preço Alvo BTC (BRL)", width=320, height=35,
                                             justify="center")
        self.entry_btc_target.pack(pady=5)

        # Botões de Ação
        self.btn_calc = ctk.CTkButton(self, text="SIMULAR E SALVAR", font=("Roboto", 14, "bold"),
                                      height=40, fg_color="#27ae60", hover_color="#219150",
                                      command=self.calculate_and_save)
        self.btn_calc.pack(pady=10)

        self.btn_open_log = ctk.CTkButton(self, text="ABRIR HISTÓRICO (TXT)", font=("Roboto", 12),
                                          height=30, fg_color="#34495e", hover_color="#2c3e50",
                                          command=self.open_log_file)
        self.btn_open_log.pack(pady=5)

        # Frame de Resultados
        self.res_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.res_frame.pack(pady=15)

        self.lbl_final_val = ctk.CTkLabel(self.res_frame, text="Valor Final: R$ 0,00", font=("Roboto", 15))
        self.lbl_final_val.pack()

        self.lbl_profit = ctk.CTkLabel(self.res_frame, text="Lucro Líquido: R$ 0,00", font=("Roboto", 20, "bold"))
        self.lbl_profit.pack()

    def update_data(self):
        try:
            url = "https://economia.awesomeapi.com.br/last/BTC-USD,BTC-BRL,USD-BRL"
            response = requests.get(url, timeout=10)
            data = response.json()

            btc_usd = float(data['BTCUSD']['bid'])
            self.btc_brl_atual = float(data['BTCBRL']['bid'])
            usd_brl = float(data['USDBRL']['bid'])

            self.lbl_btc_usd.configure(text=f"BTC/USD: $ {btc_usd:,.2f}")
            self.lbl_btc_brl.configure(text=f"BTC/BRL: R$ {self.btc_brl_atual:,.2f}")
            self.lbl_usd_brl.configure(text=f"Dólar: R$ {usd_brl:,.4f}")
        except Exception as e:
            print(f"Erro: {e}")

    def run_countdown(self):
        if self.counter > 0:
            self.counter -= 1
        else:
            self.update_data()
            self.counter = self.update_interval
        self.lbl_timer.configure(text=f"Próxima atualização em: {self.counter}s")
        self.after(1000, self.run_countdown)

    def calculate_and_save(self):
        try:
            investimento = float(self.entry_brl_invest.get().replace(',', '.'))
            preco_alvo = float(self.entry_btc_target.get().replace(',', '.'))

            if self.btc_brl_atual > 0:
                quantidade_btc = investimento / self.btc_brl_atual
                valor_final = quantidade_btc * preco_alvo
                lucro_liquido = valor_final - investimento

                # UI Update
                self.lbl_final_val.configure(text=f"Valor Bruto Final: R$ {valor_final:,.2f}")
                cor = "#2ecc71" if lucro_liquido >= 0 else "#e74c3c"
                self.lbl_profit.configure(text=f"Lucro Líquido: R$ {lucro_liquido:,.2f}", text_color=cor)

                # Salvar no LOG
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                with open(self.log_file, "a") as f:
                    f.write(f"--- Simulação em {timestamp} ---\n")
                    f.write(f"Cotação Base: R$ {self.btc_brl_atual:,.2f}\n")
                    f.write(f"Investimento: R$ {investimento:,.2f} | Preço Alvo: R$ {preco_alvo:,.2f}\n")
                    f.write(f"Resultado: R$ {valor_final:,.2f} | Lucro: R$ {lucro_liquido:,.2f}\n")
                    f.write("-" * 40 + "\n\n")
            else:
                self.lbl_profit.configure(text="Erro: Cotação indisponível", text_color="yellow")

        except ValueError:
            self.lbl_profit.configure(text="Erro: Valores inválidos", text_color="#e74c3c")

    def open_log_file(self):
        # Verifica se o arquivo existe antes de tentar abrir
        if os.path.exists(self.log_file):
            try:
                # xdg-open funciona no Pop!_OS / Ubuntu para abrir o editor padrão
                subprocess.run(["xdg-open", self.log_file])
            except Exception as e:
                print(f"Erro ao abrir arquivo: {e}")
        else:
            self.lbl_profit.configure(text="Arquivo de log ainda não criado", text_color="yellow")


if __name__ == "__main__":
    app = CryptoMonitor()
    app.mainloop()