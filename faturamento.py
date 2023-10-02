import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from ttkthemes import ThemedTk
from config import FONT, BACKGROUND_COLOR, BUTTON_COLOR, TEXT_COLOR

class Faturamento:
    def __init__(self):
        self.root = ThemedTk(theme="radiance")
        self.root.title("Faturamento")

        self.gc = gspread.service_account(filename='coloque aqui o json da credencial')
        self.sh = self.gc.open_by_key('id tabela google sheets')

        # Applying the updated styles
        ttk.Button(self.root, text="Cadastrar uma nova venda", command=self.open_sales_entry).grid(row=0, column=0, pady=20, padx=20)
        ttk.Button(self.root, text="Cadastrar um custo", command=self.open_cost_entry).grid(row=1, column=0, pady=20, padx=20)
        ttk.Button(self.root, text="Visualizar Resumo do Mês", command=self.open_monthly_summary).grid(row=2, column=0, pady=20, padx=20)

    def open_sales_entry(self):
        sales_window = tk.Toplevel(self.root)
        sales_window.title("Cadastrar Venda")

        ttk.Label(sales_window, text="Canal:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        channel_entry = ttk.Entry(sales_window)
        channel_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(sales_window, text="Data:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        date_entry = DateEntry(sales_window, date_pattern='dd/mm/yyyy')
        date_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(sales_window, text="Valor pago:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        paid_value_entry = ttk.Entry(sales_window)
        paid_value_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(sales_window, text="- intermediador:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        intermediary_value_entry = ttk.Entry(sales_window)
        intermediary_value_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(sales_window, text="Custo:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        cost_value_entry = ttk.Entry(sales_window)
        cost_value_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(sales_window, text="Salvar",
                   command=lambda: self.save_data("venda", date_entry.get_date(), paid_value_entry.get(),
                                                  intermediary_value_entry.get(), cost_value_entry.get(),
                                                  channel_entry.get())).grid(row=5, column=0, columnspan=2, pady=20)

    def open_cost_entry(self):
        cost_window = tk.Toplevel(self.root)
        cost_window.title("Cadastrar Custo")

        months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro",
                  "Novembro", "Dezembro"]
        month_var = tk.StringVar(cost_window)
        month_var.set(months[0])

        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 6))
        year_var = tk.IntVar(cost_window)
        year_var.set(current_year)

        ttk.Label(cost_window, text="Mês:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        month_dropdown = ttk.Combobox(cost_window, textvariable=month_var, values=months)
        month_dropdown.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(cost_window, text="Ano:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        year_dropdown = ttk.Combobox(cost_window, textvariable=year_var, values=years)
        year_dropdown.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(cost_window, text="Nome do Custo:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        cost_name_entry = ttk.Entry(cost_window)
        cost_name_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(cost_window, text="Valor:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        cost_value_entry = ttk.Entry(cost_window)
        cost_value_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(cost_window, text="Salvar",
                   command=lambda: self.save_data("custo", month_var.get(), year_var.get(), cost_name_entry.get(),
                                                  cost_value_entry.get())).grid(row=4, column=0, columnspan=2, pady=20)

    def save_data(self, type, *args):
        if type == "venda":
            ws = self.sh.worksheet("Vendas")
            date_str = args[0].strftime('%d/%m/%Y')

            if float(args[1]) != 0:  # Evitar divisão por zero
                sales_tax = 100 - (float(args[2]) / float(args[1])) * 100
                gross_profit = float(args[2]) - float(args[3])  # Correção para o cálculo do Lucro bruto
                profit_percentage = (gross_profit / float(args[1])) * 100
            else:
                sales_tax, gross_profit, profit_percentage = 0, 0, 0

            ws.append_row([
                args[4],
                date_str,
                args[1],
                args[2],
                f"{sales_tax:.2f}%",
                args[3],
                gross_profit,
                f"{profit_percentage:.2f}%"
            ])
            messagebox.showinfo("Info",
                                f"Venda cadastrada e salva no Google Sheets:\nData: {date_str}\nValor Pago: {args[1]}\nIntermediador: {args[2]}\nCusto: {args[3]}")
        elif type == "custo":
            ws = self.sh.worksheet("Custos")
            ws.append_row([args[0], args[1], args[2], args[3]])
            messagebox.showinfo("Info",
                                f"Custo cadastrado e salva no Google Sheets:\nMês: {args[0]}\nAno: {args[1]}\nNome do Custo: {args[2]}\nValor: {args[3]}")

    def open_monthly_summary(self):
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Resumo do Mês")

        months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro",
                  "Novembro", "Dezembro"]
        month_var = tk.StringVar(summary_window)
        month_var.set(months[0])

        current_year = datetime.now().year
        years = list(range(current_year - 5, current_year + 6))
        year_var = tk.IntVar(summary_window)
        year_var.set(current_year)

        ttk.Label(summary_window, text="Mês:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        month_dropdown = ttk.Combobox(summary_window, textvariable=month_var, values=months)
        month_dropdown.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(summary_window, text="Ano:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        year_dropdown = ttk.Combobox(summary_window, textvariable=year_var, values=years)
        year_dropdown.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(summary_window, text="Mostrar Resumo",
                   command=lambda: self.show_summary(month_var.get(), year_var.get())).grid(row=2, column=0,
                                                                                            columnspan=2, pady=20)

    def show_summary(self, month, year):
        ws_sales = self.sh.worksheet("Vendas")
        sales_data = ws_sales.get_all_values()
        ws_costs = self.sh.worksheet("Custos")
        costs_data = ws_costs.get_all_values()

        month_idx = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro",
                     "Outubro", "Novembro", "Dezembro"].index(month) + 1

        total_sales = 0
        total_costs = 0
        total_intermediary = 0
        for sale in sales_data[1:]:
            try:
                sale_date = datetime.strptime(sale[1], '%d/%m/%Y')
                if sale_date.month == month_idx and sale_date.year == int(year):
                    total_sales += float(sale[2])
                    total_intermediary += float(sale[3])
            except ValueError:
                pass  # Ignora entradas que não possuem datas válidas

        for cost in costs_data[1:]:
            if cost[0] == month and int(cost[1]) == int(year):
                total_costs += float(cost[3])
        net_profit = total_sales - total_costs - total_intermediary
        sales_tax = (total_intermediary / total_sales) * 100 if total_sales else 0

        summary_message = f"Resumo para {month} de {year}:\n"
        summary_message += f"Vendas totais: R$ {total_sales:.2f}\n"
        summary_message += f"Custos totais: R$ {total_costs:.2f}\n"
        summary_message += f"Lucro líquido: R$ {net_profit:.2f}\n"
        summary_message += f"Taxa de venda: {sales_tax:.2f}%"
        messagebox.showinfo("Resumo", summary_message)


# Create and run the GUI application
if __name__ == "__main__":
    app = Faturamento()
    app.root.mainloop()


