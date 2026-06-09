import os
import re
import threading 
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from crypto_engine import CryptoEngine
from stego_engine import StegoEngine

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class StegoApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        
        self.crypto = CryptoEngine()
        self.stego = StegoEngine()

        self.title("Advanced Steganography Engine")
        self.geometry("900x880") 
        self.resizable(True, True)

        self.font_h1 = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        self.font_h2 = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        self.font_body = ctk.CTkFont(family="Segoe UI", size=13)
        self.font_mono = ctk.CTkFont(family="Consolas", size=12)

        self.cover_path = None
        self.stego_path = None
        self.secret_file_path = None 

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=40, pady=(15, 5))

        self.header_title = ctk.CTkLabel(self.header_frame, text="STEGANOGRAPHY ENGINE", font=self.font_h1, text_color=["#333", "#ccc"])
        self.header_title.pack(side="left")

        self.theme_var = ctk.BooleanVar(value=True) 
        self.theme_switch = ctk.CTkSwitch(
            self.header_frame,
            text="Dark Mode",
            variable=self.theme_var,
            command=self.toggle_theme, 
            font=self.font_body
        )
        self.theme_switch.pack(side="right")

        self.tab_view = ctk.CTkTabview(self, width=820, height=780, command=self.reset_all_data) 
        self.tab_view.pack(padx=40, pady=5, fill="both", expand=True)

        self.tab_view.add("Encode (Hide Data)")
        self.tab_view.add("Decode (Extract Data)")

        self.setup_hide_tab()
        self.setup_extract_tab()

    def toggle_theme(self):
        if self.theme_var.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")

    def toggle_pass_visibility(self, entry_widget, btn_widget):
        
        if entry_widget.cget('show') == '*':
            entry_widget.configure(show='')
            btn_widget.configure(text='Hide', fg_color="#555")
        else:
            entry_widget.configure(show='*')
            btn_widget.configure(text='Show', fg_color=["#3B8ED0", "#1F6AA5"])

    def setup_hide_tab(self):
        tab = self.tab_view.tab("Encode (Hide Data)")
        
        content_frame = ctk.CTkFrame(tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=40, pady=5)

        ctk.CTkLabel(content_frame, text="1. Carrier Image", font=self.font_h2).pack(anchor="w")
        
        self.hide_preview_frame = ctk.CTkFrame(content_frame, height=110, border_width=1, border_color=["#ddd", "#333"])
        self.hide_preview_frame.pack(fill="x", pady=(2, 5)) 
        self.hide_preview_frame.pack_propagate(False)

        self.cover_btn = ctk.CTkButton(self.hide_preview_frame, text="📁 Browse", width=100, command=self.select_cover_image)
        self.cover_btn.pack(side="left", padx=20)

        self.hide_thumb_label = ctk.CTkLabel(self.hide_preview_frame, text="", width=100)
        self.hide_thumb_label.pack(side="left", padx=(0, 20))

        self.hide_stats_label = ctk.CTkLabel(
            self.hide_preview_frame,
            text="No Image Selected.\nWaiting for carrier file...",
            font=self.font_mono,
            justify="left",
            anchor="w"
        )
        self.hide_stats_label.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(content_frame, text="2. Secret Payload", font=self.font_h2).pack(anchor="w", pady=(5, 2))
        
        self.payload_type = ctk.StringVar(value="Text Message")
        self.payload_selector = ctk.CTkSegmentedButton(
            content_frame, 
            values=["Text Message", "Secret File"], 
            variable=self.payload_type,
            command=self.toggle_payload_ui,
            font=self.font_body
        )
        self.payload_selector.pack(fill="x", pady=(0, 5))

        self.payload_container = ctk.CTkFrame(content_frame, fg_color="transparent", height=90) 
        self.payload_container.pack(fill="x")
        self.payload_container.pack_propagate(False)

        self.text_payload_frame = ctk.CTkFrame(self.payload_container, fg_color="transparent")
        self.secret_entry = ctk.CTkTextbox(self.text_payload_frame, height=90, font=self.font_body)
        self.secret_entry.pack(fill="both", expand=True)
        self.secret_entry.bind("<KeyRelease>", lambda event: self.analyze_payload_sufficiency()) #Every time a key is released, we check
        
        self.file_payload_frame = ctk.CTkFrame(self.payload_container, fg_color="transparent")
        self.secret_file_btn = ctk.CTkButton(self.file_payload_frame, text="📎 Attach Secret File", command=self.select_secret_file, fg_color="#555")
        self.secret_file_btn.pack(pady=(15, 5))
        self.secret_file_label = ctk.CTkLabel(self.file_payload_frame, text="No payload file attached.", text_color="gray", font=self.font_body)
        self.secret_file_label.pack()

        self.text_payload_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(content_frame, text="3. Security Configuration", font=self.font_h2).pack(anchor="w", pady=(10, 2))
        
        self.hide_plain_mode = ctk.BooleanVar(value=False)
        self.hide_switch = ctk.CTkSwitch(
            content_frame,
            text="Unsecured Mode (Bypass AES Encryption)",
            variable=self.hide_plain_mode,
            command=self.toggle_hide_security_mode,
            progress_color="#e74c3c",
            font=self.font_body
        )
        self.hide_switch.pack(anchor="w", pady=(0, 5))

        self.hide_pass_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.hide_pass_frame.pack(fill="x", pady=0)

        pass_label = ctk.CTkLabel(self.hide_pass_frame, text="Cryptographic Passphrase:", font=self.font_body)
        pass_label.pack(side="left", padx=(0, 10))
        
        pass_input_frame = ctk.CTkFrame(self.hide_pass_frame, fg_color="transparent")
        pass_input_frame.pack(side="left", fill="x", expand=True)
        
        self.send_pass_entry = ctk.CTkEntry(pass_input_frame, show="*", width=250)
        self.send_pass_entry.pack(side="left", fill="x", expand=True)
        self.send_pass_btn = ctk.CTkButton(pass_input_frame, text="Show", width=50, command=lambda: self.toggle_pass_visibility(self.send_pass_entry, self.send_pass_btn))
        self.send_pass_btn.pack(side="left", padx=(5, 0))

        self.encode_status = ctk.CTkLabel(content_frame, text="", font=self.font_body)
        self.encode_status.pack(pady=(2, 0))
        self.encode_progress = ctk.CTkProgressBar(content_frame, mode="indeterminate")

        self.encode_btn_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.encode_btn_container.pack(fill="x", pady=(10, 5))

        self.encode_btn = ctk.CTkButton(
            self.encode_btn_container, 
            text="🔒 Encrypt & Hide Data", 
            command=self.run_encoding, 
            font=self.font_h2,
            height=40
        )
        self.encode_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.hide_reset_btn = ctk.CTkButton(
            self.encode_btn_container,
            text="🗑️ Reset",
            command=self.reset_all_data,
            fg_color="#7f8c8d", hover_color="#95a5a6",
            font=self.font_h2,
            height=40,
            width=80
        )
        self.hide_reset_btn.pack(side="right")

    def setup_extract_tab(self):
        tab = self.tab_view.tab("Decode (Extract Data)")
        
        content_frame = ctk.CTkFrame(tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=40, pady=5)

        ctk.CTkLabel(content_frame, text="1. Encoded Target", font=self.font_h2).pack(anchor="w")
        
        self.extract_preview_frame = ctk.CTkFrame(content_frame, height=110, border_width=1, border_color=["#ddd", "#333"])
        self.extract_preview_frame.pack(fill="x", pady=(2, 10))
        self.extract_preview_frame.pack_propagate(False)

        self.stego_btn = ctk.CTkButton(self.extract_preview_frame, text="📁 Browse", width=100, command=self.select_stego_image)
        self.stego_btn.pack(side="left", padx=20)

        self.extract_thumb_label = ctk.CTkLabel(self.extract_preview_frame, text="", width=100)
        self.extract_thumb_label.pack(side="left", padx=(0, 20))

        self.extract_stats_label = ctk.CTkLabel(
            self.extract_preview_frame,
            text="No Stego-Image Loaded.\nWaiting for target file...",
            font=self.font_mono,
            justify="left",
            anchor="w"
        )
        self.extract_stats_label.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(content_frame, text="2. Decryption Parameters", font=self.font_h2).pack(anchor="w", pady=(10, 2))

        self.extract_plain_mode = ctk.BooleanVar(value=False)
        self.extract_switch = ctk.CTkSwitch(
            content_frame,
            text="Unsecured Mode (Extract cleartext without password)",
            variable=self.extract_plain_mode,
            command=self.toggle_extract_security_mode,
            progress_color="#e74c3c",
            font=self.font_body
        )
        self.extract_switch.pack(anchor="w", pady=(0, 5))

        self.extract_deep_scan_mode = ctk.BooleanVar(value=False)
        self.deep_scan_switch = ctk.CTkSwitch(
            content_frame,
            text="Deep Scan Extraction (Brute-force read all LSBs)",
            variable=self.extract_deep_scan_mode,
            command=self.toggle_extract_security_mode,
            progress_color="#8e44ad", 
            font=self.font_body
        )
        self.deep_scan_switch.pack(anchor="w", pady=(0, 5))

        self.apply_regex_filter = ctk.BooleanVar(value=True) 
        self.regex_checkbox = ctk.CTkCheckBox(
            content_frame,
            text="Apply Readable Text Filter (Isolate human-readable strings)",
            variable=self.apply_regex_filter,
            font=self.font_body,
            text_color="#8e44ad",
            fg_color="#8e44ad",
            hover_color="#9b59b6"
        )

        self.extract_pass_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.extract_pass_frame.pack(fill="x", pady=5)

        pass_label = ctk.CTkLabel(self.extract_pass_frame, text="Decryption Passphrase:", font=self.font_body)
        pass_label.pack(side="left", padx=(0, 10))
        
        recv_input_frame = ctk.CTkFrame(self.extract_pass_frame, fg_color="transparent")
        recv_input_frame.pack(side="left", fill="x", expand=True)
        
        self.recv_pass_entry = ctk.CTkEntry(recv_input_frame, show="*", width=250)
        self.recv_pass_entry.pack(side="left", fill="x", expand=True)
        self.recv_pass_btn = ctk.CTkButton(recv_input_frame, text="Show", width=50, command=lambda: self.toggle_pass_visibility(self.recv_pass_entry, self.recv_pass_btn))
        self.recv_pass_btn.pack(side="left", padx=(5, 0))

        self.decode_status = ctk.CTkLabel(content_frame, text="", font=self.font_body)
        self.decode_status.pack(pady=(2, 0))
        self.decode_progress = ctk.CTkProgressBar(content_frame, mode="indeterminate")

        self.decode_btn_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.decode_btn_container.pack(fill="x", pady=(5, 10))

        self.decode_btn = ctk.CTkButton(
            self.decode_btn_container, 
            text="🔓 Extract & Decrypt", 
            command=self.run_decoding, 
            font=self.font_h2,
            height=40
        )
        self.decode_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.extract_reset_btn = ctk.CTkButton(
            self.decode_btn_container,
            text="🗑️ Reset",
            command=self.reset_all_data,
            fg_color="#7f8c8d", hover_color="#95a5a6",
            font=self.font_h2,
            height=40,
            width=80
        )
        self.extract_reset_btn.pack(side="right")

        ctk.CTkLabel(content_frame, text="3. Output Data Stream", font=self.font_h2).pack(anchor="w")
        
        self.output_display = ctk.CTkTextbox(content_frame, height=90, font=self.font_body)
        self.output_display.pack(fill="x", pady=(5, 10))

        self.save_output_btn = ctk.CTkButton(
            content_frame, 
            text="💾 Save Extracted Bytes to File", 
            command=self.save_extracted_file, 
            fg_color="#27ae60", 
            hover_color="#2ecc71",
            font=self.font_body
        )
        self.save_output_btn.pack(anchor="e")

    def reset_all_data(self, *args):
        self.cover_path = None
        self.stego_path = None
        self.secret_file_path = None
        if hasattr(self, 'extracted_file_bytes'):
            self.extracted_file_bytes = None

        self.secret_entry.delete("1.0", "end") 
        self.output_display.delete("1.0", "end")
        self.send_pass_entry.delete(0, "end") 
        self.recv_pass_entry.delete(0, "end")

        self.hide_plain_mode.set(False)
        self.extract_plain_mode.set(False)
        self.extract_deep_scan_mode.set(False)
        self.apply_regex_filter.set(True) 
        
        self.toggle_hide_security_mode(silent=True)
        self.toggle_extract_security_mode(silent=True)

        self.hide_thumb_label.configure(image="", text="")
        self.extract_thumb_label.configure(image="", text="")

        self.hide_stats_label.configure(text="No Image Selected.\nWaiting for carrier file...", text_color=["black", "white"])
        self.extract_stats_label.configure(text="No Stego-Image Loaded.\nWaiting for target file...", text_color=["black", "white"])
        self.encode_status.configure(text="")
        self.decode_status.configure(text="")
        self.secret_file_label.configure(text="No payload file attached.")

        self.payload_type.set("Text Message")
        self.toggle_payload_ui("Text Message")
        self.encode_btn.configure(state="normal")
        self.decode_btn.configure(state="normal")
        
        self.encode_progress.stop()
        self.encode_progress.pack_forget()
        self.decode_progress.stop()
        self.decode_progress.pack_forget()

    def generate_thumbnail(self, image_path: str, widget_target: ctk.CTkLabel):
        """Safely opens an image, scales it down, and assigns it to a UI label."""
        try:
            pil_img = Image.open(image_path)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(90, 90))
            widget_target.configure(image=ctk_img, text="")
            return pil_img
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {str(e)}")
            return None

    def select_cover_image(self):
        path = filedialog.askopenfilename(title="Select Cover Image", filetypes=[("Image Files", "*.png *.bmp")])
        if path:
            self.cover_path = path
            if self.generate_thumbnail(path, self.hide_thumb_label):
                self.analyze_payload_sufficiency()

    def select_stego_image(self):
        path = filedialog.askopenfilename(title="Select Stego Image", filetypes=[("Image Files", "*.png *.bmp")])
        if path:
            self.stego_path = path
            img = self.generate_thumbnail(path, self.extract_thumb_label)
            if img:
                self.extract_stats_label.configure(text=f"Target: {os.path.basename(path)}\nDimensions: {img.size[0]} x {img.size[1]} px\nFormat: {img.format}\n\nStatus: Target acquired.")

    def select_secret_file(self):
        path = filedialog.askopenfilename(title="Select File to Hide", filetypes=[("All Files", "*.*")])
        if path:
            self.secret_file_path = path
            # os.path.getsize retrieves file weight directly from the hard drive without loading it into RAM
            file_size_kb = os.path.getsize(path) / 1024
            self.secret_file_label.configure(text=f"Attached: {os.path.basename(path)} ({file_size_kb:.2f} KB)", text_color=["black", "white"])
            self.analyze_payload_sufficiency()

    def toggle_payload_ui(self, choice):
        if choice == "Text Message":
            self.file_payload_frame.pack_forget()
            self.text_payload_frame.pack(fill="both", expand=True)
        else:
            self.text_payload_frame.pack_forget()
            self.file_payload_frame.pack(fill="both", expand=True)
        self.analyze_payload_sufficiency() 

    def analyze_payload_sufficiency(self):
        if not self.cover_path:
            return
        try:
            img = Image.open(self.cover_path)
            max_bits = img.size[0] * img.size[1] * 3
            max_allowed_bytes = (max_bits - 32) // 8 
            
            if self.payload_type.get() == "Text Message":
                current_payload_bytes = len(self.secret_entry.get("1.0", "end-1c").encode("utf-8"))
            else:
                current_payload_bytes = os.path.getsize(self.secret_file_path) if self.secret_file_path else 0

            if current_payload_bytes == 0:
                 self.hide_stats_label.configure(
                    text=f"File: {os.path.basename(self.cover_path)}\nCapacity: {max_allowed_bytes:,} Bytes\n\nAwaiting payload input...",
                    text_color=["black", "white"]
                )
                 self.encode_btn.configure(state="disabled")
            elif current_payload_bytes > max_allowed_bytes:
                 self.hide_stats_label.configure(
                    text=f"File: {os.path.basename(self.cover_path)}\n\n[!] OVERFLOW DETECTED\nRequired: {current_payload_bytes:,} B | Max: {max_allowed_bytes:,} B",
                    text_color="#e74c3c" 
                )
                 self.encode_btn.configure(state="disabled")
            else:
                 self.hide_stats_label.configure(
                    text=f"File: {os.path.basename(self.cover_path)}\nPayload: {current_payload_bytes:,} B\nCapacity: {max_allowed_bytes:,} B\n\n[OK] Safe to Encode",
                    text_color=["#27ae60", "#2ecc71"] 
                )
                 self.encode_btn.configure(state="normal")
        except Exception:
            pass

    def toggle_hide_security_mode(self, silent=False):
        if self.hide_plain_mode.get():
            if not silent:
                confirm = messagebox.askyesno("Warning", "Disabling encryption writes plain text directly to pixels.\nProceed?")
                if not confirm:
                    self.hide_switch.deselect() 
                    return
            self.hide_pass_frame.pack_forget() 
            self.encode_btn.configure(text="⚠️ Save Unsecured Image", fg_color="#c0392b", hover_color="#e74c3c")
        else:
            self.hide_pass_frame.pack(fill="x", pady=0, before=self.encode_status)
            self.encode_btn.configure(text="🔒 Encrypt & Hide Data", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])

    def toggle_extract_security_mode(self, silent=False):
        is_plain = self.extract_plain_mode.get()
        is_deep = self.extract_deep_scan_mode.get()

        if is_deep:
            if not silent:
                confirm = messagebox.askyesno(
                    "Deep Scan Warning", 
                    "This mode blind-rips the raw data from EVERY pixel in the image, bypassing all security, headers, and sequence mapping.\n\nIt will produce massive amounts of raw binary data.\n\nAre you sure you want to proceed?"
                )
                if not confirm:
                    self.deep_scan_switch.deselect()
                    return
            
            self.extract_pass_frame.pack_forget()
            self.regex_checkbox.pack(anchor="w", pady=(0, 5), before=self.decode_status) # Reveals the Regex checkbox
            self.decode_btn.configure(text="🕵️ Execute Deep Scan", fg_color="#8e44ad", hover_color="#9b59b6")
        
        elif is_plain:
            self.regex_checkbox.pack_forget()
            self.extract_pass_frame.pack_forget()
            self.decode_btn.configure(text="⚠️ Extract Unsecured Data", fg_color="#c0392b", hover_color="#e74c3c")
        
        else:
            self.regex_checkbox.pack_forget()
            self.extract_pass_frame.pack(fill="x", pady=5, before=self.decode_status)
            self.decode_btn.configure(text="🔓 Extract & Decrypt", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
    
    def run_encoding(self):
        if not self.cover_path:
            messagebox.showerror("Error", "Please select a carrier image first.")
            return

        if self.payload_type.get() == "Text Message":
            secret_text = self.secret_entry.get("1.0", "end-1c")
            if not secret_text:
                messagebox.showerror("Error", "Secret message cannot be empty.")
                return
            payload_bytes = secret_text.encode("utf-8")
        else:
            if not self.secret_file_path:
                messagebox.showerror("Error", "Please attach a secret file.")
                return
            payload_bytes_array = bytearray()
            try:
                with open(self.secret_file_path, "rb") as f:
                    while chunk := f.read(1024 * 1024):
                        payload_bytes_array.extend(chunk)
                payload_bytes = bytes(payload_bytes_array)
            except Exception as e:
                messagebox.showerror("File Error", f"Failed to read file: {str(e)}")
                return

        is_plain = self.hide_plain_mode.get()
        seed = None
        password = None
        
        if not is_plain:
            password = self.send_pass_entry.get()
            if not password:
                messagebox.showerror("Error", "Passphrase is required for secure mode.")
                return
            seed = password

        output_path = filedialog.asksaveasfilename(
            title="Save Stego-Image As...", 
            defaultextension=".png",
            filetypes=[("PNG Image (Lossless)", "*.png")]
        )
        if not output_path:
            return

        self.encode_btn.configure(state="disabled")
        self.hide_reset_btn.configure(state="disabled")
        
        self.encode_status.configure(text="Encoding in progress... Please wait.", text_color=["#d35400", "#e67e22"])
        self.encode_progress.pack(fill="x", pady=(0, 10))
        self.encode_progress.start()

        threading.Thread(
            target=self._encoding_thread, 
            args=(payload_bytes, password, is_plain, seed, output_path), 
            daemon=True
        ).start()

    def _encoding_thread(self, payload_bytes, password, is_plain, seed, output_path):
        try:
            if not is_plain:
                payload_bytes = self.crypto.encrypt_data(payload_bytes, password)
            self.stego.encode(self.cover_path, payload_bytes, output_path, seed)
            success = True
            err_msg = ""
        except Exception as e:
            success = False
            err_msg = str(e)
            
        self.after(0, self._encoding_complete, success, output_path, err_msg)

    def _encoding_complete(self, success, output_path, err_msg):
        """Runs back on the Main GUI Thread. Cleans up the progress bar and shows popups."""
        self.encode_progress.stop()
        self.encode_progress.pack_forget()
        self.encode_btn.configure(state="normal")
        self.hide_reset_btn.configure(state="normal")
        
        if success:
            self.encode_status.configure(text="Process Complete", text_color=["green", "#2ecc71"])
            messagebox.showinfo("Success", f"Payload successfully embedded!\nSaved to: {output_path}")
        else:
            self.encode_status.configure(text="Encoding Failed", text_color="red")
            messagebox.showerror("Error", f"Failed to embed data: {err_msg}")

    def run_decoding(self):
        if not self.stego_path:
            messagebox.showerror("Error", "Please select a stego-image target first.")
            return

        is_plain = self.extract_plain_mode.get()
        is_deep = self.extract_deep_scan_mode.get()
        apply_filter = self.apply_regex_filter.get()
        seed = None
        password = None

        if not is_plain and not is_deep:
            password = self.recv_pass_entry.get()
            if not password:
                messagebox.showerror("Error", "Passphrase is required to decrypt.")
                return
            seed = password

        self.decode_btn.configure(state="disabled")
        self.extract_reset_btn.configure(state="disabled")
        
        if is_deep:
            self.decode_status.configure(text="Dumping ALL pixels... This may take a moment.", text_color=["#8e44ad", "#9b59b6"])
        else:
            self.decode_status.configure(text="Decoding image array... Please wait.", text_color=["#d35400", "#e67e22"])
            
        self.decode_progress.pack(fill="x", pady=(0, 10))
        self.decode_progress.start()

        threading.Thread(
            target=self._decoding_thread, 
            args=(is_plain, is_deep, apply_filter, seed, password), 
            daemon=True
        ).start()

    def _decoding_thread(self, is_plain, is_deep, apply_filter, seed, password):
        try:
            if is_deep:
                extracted_bytes = self.stego.deep_scan_dump(self.stego_path)
            else:
                extracted_bytes = self.stego.decode(self.stego_path, seed)
                if not is_plain:
                    extracted_bytes = self.crypto.decrypt_data(extracted_bytes, password)
            success = True
            err_msg = ""
        except ValueError as e:
             success = False
             extracted_bytes = None
             err_msg = str(e)
        except Exception as e:
            success = False
            extracted_bytes = None
            err_msg = str(e)

        self.after(0, self._decoding_complete, success, extracted_bytes, err_msg, is_deep, apply_filter)

    def _decoding_complete(self, success, extracted_bytes, err_msg, is_deep, apply_filter):
        self.decode_progress.stop()
        self.decode_progress.pack_forget()
        self.decode_btn.configure(state="normal")
        self.extract_reset_btn.configure(state="normal")

        if not success:
            self.decode_status.configure(text="Extraction Failed", text_color="red")
            messagebox.showerror("Decryption Error", err_msg)
            return

        self.decode_status.configure(text="Extraction Complete", text_color=["green", "#2ecc71"])
        
        self.extracted_file_bytes = extracted_bytes 
        self.output_display.delete("1.0", "end")
        
        if is_deep:
            if apply_filter:
                readable_chunks = re.findall(b'[ -~]{5,}', extracted_bytes) #This returns a list of byte sequences that match the criteria of all printable ASCII characters from ' ' to '~', with a minimum length of 5 characters
                if readable_chunks:
                    decoded_text = "\n".join([chunk.decode('ascii') for chunk in readable_chunks])
                    self.output_display.insert("1.0", f"--- FILTERED STRINGS ---\n{decoded_text}")
                else:
                    self.output_display.insert("1.0", "No readable text found in pixel dump.")
            else:
                raw_text = extracted_bytes.decode('latin-1', errors='replace')
                #It is difficult to display millions of characters in the textbox so we put a cap of 5000 characters
                if len(raw_text) > 5000:
                    display_text = raw_text[:5000] + "\n\n... [DATA TRUNCATED: 5000+ CHARACTERS] ...\n\n[ PLEASE USE 'SAVE EXTRACTED BYTES TO FILE' TO VIEW FULL DUMP ]"
                else:
                    display_text = raw_text
                self.output_display.insert("1.0", f"--- RAW BINARY DUMP ---\n{display_text}")
        else:
            try:
                decoded_text = extracted_bytes.decode("utf-8")
                self.output_display.insert("1.0", decoded_text)
            except UnicodeDecodeError:
                self.output_display.insert("1.0", "[ Binary File Extracted ]\n\nThe hidden payload is not readable text. Please use the 'Save Extracted Bytes to File' button below to save it to your computer.")

    def save_extracted_file(self):
        if not hasattr(self, 'extracted_file_bytes') or not self.extracted_file_bytes:
            messagebox.showerror("Error", "No data has been extracted yet.")
            return
            
        path = filedialog.asksaveasfilename(title="Save Extracted Data As...")
        if path:
            try:
                with open(path, "wb") as f:
                    f.write(self.extracted_file_bytes)
                messagebox.showinfo("Success", f"Data saved successfully to:\n{path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save file: {str(e)}")

if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()