import os
import time
import random
import threading
from datetime import datetime
import urllib.parse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Modern GUI
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Global Esthetic Configuration
ctk.set_appearance_mode("System")  # Detects if system uses dark or light mode
ctk.set_default_color_theme("blue")

class WhatsAppBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WhatsApp Marketing Pro")
        self.geometry("550x400")
        self.resizable(False, False)

        self.excel_file = None
        self.is_running = False

        self.setup_ui()

    def setup_ui(self):
        # Main Title
        self.title_label = ctk.CTkLabel(self, text="WhatsApp Bulk Sender", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=20)

        # File Selection Section
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, fill="x", padx=20)

        self.btn_select = ctk.CTkButton(self.file_frame, text="Select Excel File", command=self.select_excel_file)
        self.btn_select.pack(side="left", padx=10, pady=10)

        self.lbl_file_status = ctk.CTkLabel(self.file_frame, text="No file selected", text_color="gray")
        self.lbl_file_status.pack(side="left", padx=10, pady=10)

        # Status & Information Panel
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.pack(pady=15, fill="both", expand=True, padx=20)

        self.lbl_status = ctk.CTkLabel(self.status_frame, text="Status: Waiting for file...", font=ctk.CTkFont(size=13))
        self.lbl_status.pack(pady=10)

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.lbl_counter = ctk.CTkLabel(self.status_frame, text="Processed: 0 / 0 (0%)", font=ctk.CTkFont(size=12))
        self.lbl_counter.pack(pady=5)

        # Main Action Button
        self.btn_start = ctk.CTkButton(self, text="Start Bulk Sending", state="disabled", command=self.start_process_thread, fg_color="#25D366", hover_color="#20BA5A", text_color="white")
        self.btn_start.pack(pady=20)

    def is_file_locked_by_libreoffice(self, file_path):
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        lock_file = os.path.join(directory, f".~lock.{filename}#")
        return os.path.exists(lock_file)

    def select_excel_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Customer File (Excel)",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        if self.is_file_locked_by_libreoffice(file_path):
            messagebox.showwarning("File Locked", "The file is currently open in LibreOffice/Excel.\n\nPlease close it and try again.")
            return

        try:
            df = pd.read_excel(file_path)
            required = ['Nombre', 'Telefono', 'Mensaje_Personalizado']
            missing = [col for col in required if col not in df.columns]
            
            if missing:
                messagebox.showerror("Error", f"Missing required columns:\n{missing}")
                return
            if len(df) == 0:
                messagebox.showerror("Error", "The Excel file is empty.")
                return
                
            self.excel_file = file_path
            self.lbl_file_status.configure(text=f"📂 {os.path.basename(file_path)} ({len(df)} contacts)", text_color=["black", "white"])
            self.lbl_status.configure(text="Status: Ready to start.")
            self.btn_start.configure(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{str(e)}")

    def get_driver(self, headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        else:
            options.add_argument("--start-maximized")
        
        session_dir = os.path.join(os.getcwd(), "whatsapp_session")
        options.add_argument(f"--user-data-dir={session_dir}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def is_number_invalid(self, driver):
        try:
            time.sleep(2.5)
            page_text = driver.page_source.lower()
            strong_errors = [
                "phone number shared via url is invalid",
                "el número de teléfono compartido a través de la url es inválido",
                "unable to open chat",
                "no se puede acceder al chat"
            ]
            for phrase in strong_errors:
                if phrase in page_text:
                    return True
            if driver.find_elements(By.XPATH, '//div[@id="main"] | //div[@role="textbox"]'):
                return False
            return False
        except:
            return False

    def start_process_thread(self):
        if self.is_running:
            return
        self.is_running = True
        self.btn_start.configure(state="disabled")
        self.btn_select.configure(state="disabled")
        
        threading.Thread(target=self.run_whatsapp_process, daemon=True).start()

    def run_whatsapp_process(self):
        df = pd.read_excel(self.excel_file)
        total_contacts = len(df)
        historial = []

        self.lbl_status.configure(text="Status: Checking WhatsApp session...")
        print("🔍 Checking WhatsApp session...")
        
        driver = self.get_driver(headless=True)
        try:
            driver.get("https://web.whatsapp.com")
            WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "pane-side")))
        except:
            self.lbl_status.configure(text="Status: QR Required. Opening browser...")
            print("📸 Session not found. Opening visible browser to scan QR...")
            driver.quit()
            driver = self.get_driver(headless=False)
            driver.get("https://web.whatsapp.com")
            WebDriverWait(driver, 180).until(EC.presence_of_element_located((By.ID, "pane-side")))
            driver.quit()
            
            self.lbl_status.configure(text="Status: Resuming in background...")
            print("🚀 QR Scanned successfully. Returning to background mode...")
            driver = self.get_driver(headless=True)
            driver.get("https://web.whatsapp.com")
            WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.ID, "pane-side")))

        for index, row in df.iterrows():
            current_num = index + 1
            nombre = str(row.get('Nombre', '')).strip()
            telefono = str(row.get('Telefono', '')).strip().replace('.0', '').replace(' ', '').lstrip('+')
            mensaje_personalizado = str(row.get('Mensaje_Personalizado', '')).strip()
            mensaje_final = f"Hello {nombre}, {mensaje_personalizado}"
            
            self.lbl_status.configure(text=f"Sending to: {nombre} ({telefono})")
            print(f"📦 [{current_num}/{total_contacts}] Processing: {nombre} ({telefono})")
            
            try:
                mensaje_codificado = urllib.parse.quote(mensaje_final)
                url = f"https://web.whatsapp.com/send?phone={telefono}&text={mensaje_codificado}"
                driver.get(url)
                time.sleep(3)

                if self.is_number_invalid(driver):
                    historial.append({"Name": nombre, "Phone": telefono, "Status": "Error: Invalid Number"})
                    print(f"⚠️ Invalid number or no WhatsApp account: {telefono}")
                    time.sleep(random.randint(2, 4))
                else:
                    sent = False
                    for attempt in range(2):
                        try:
                            input_box = WebDriverWait(driver, 8).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
                            )
                            input_box.send_keys(Keys.ENTER)
                            sent = True
                            break
                        except:
                            time.sleep(2)
                            webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
                    
                    if sent:
                        historial.append({"Name": nombre, "Phone": telefono, "Status": "Sent"})
                        print(f"✅ Successfully sent to {nombre}")
                    else:
                        historial.append({"Name": nombre, "Phone": telefono, "Status": "Error: Delivery Failed"})
                        print(f"❌ Automated send failed for {nombre}")

                    time.sleep(random.randint(7, 11))

            except Exception as e:
                historial.append({"Name": nombre, "Phone": telefono, "Status": f"Error: {str(e)[:40]}"})
                print(f"💥 Unexpected error with {nombre}: {str(e)[:50]}")

            porcentaje = current_num / total_contacts
            self.progress_bar.set(porcentaje)
            self.lbl_counter.configure(text=f"Processed: {current_num} / {total_contacts} ({int(porcentaje * 100)}%)")

        self.lbl_status.configure(text="Status: Saving delivery report...")
        driver.quit()

        # --- REWRITE: Create dlvryreports folder if it doesn't exist and save there ---
        report_dir = os.path.join(os.getcwd(), "dlvryreports")
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        report_file = os.path.join(report_dir, f"delivery_report_{timestamp}.xlsx")
        
        pd.DataFrame(historial).to_excel(report_file, index=False)
        print(f"🏁 Process completed! Report saved at: {report_file}")
        
        messagebox.showinfo("Process Finished", f"All contacts have been processed successfully.\n\nReport saved inside 'dlvryreports' as:\n{os.path.basename(report_file)}")
        # ------------------------------------------------------------------------------
        
        self.is_running = False
        self.btn_start.configure(state="normal")
        self.btn_select.configure(state="normal")
        self.lbl_status.configure(text="Status: Task completed successfully.")
        self.progress_bar.set(0)
        self.lbl_counter.configure(text="Processed: 0 / 0 (0%)")

if __name__ == "__main__":
    app = WhatsAppBotApp()
    app.mainloop()