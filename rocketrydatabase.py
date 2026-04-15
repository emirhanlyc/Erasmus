import pyodbc
from tkinter import *
from tkinter import messagebox, ttk

# ===== DATABASE CONNECTION =====
server = r'ASUSGAMING\SQLEXPRESS'
database = 'Rocketry Competition'

conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'Trusted_Connection=yes;'
    f'TrustServerCertificate=yes;'
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Bağlantı Başarılı!")
except Exception as e:
    messagebox.showerror("Bağlantı Hatası", str(e))
    exit()

# ===== MAIN WINDOW & UI THEME =====
root = Tk()
root.title("🚀 Roket Yarışması - Veritabanı Yönetim Sistemi")
root.geometry("1100x750")
root.configure(bg="#F4F6F9") # Açık gri, modern arka plan

# Modern ttk Stilleri
style = ttk.Style()
style.theme_use("clam")

# Sekme (Notebook) Stilleri
style.configure("TNotebook", background="#F4F6F9", borderwidth=0)
style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 8], background="#E0E6ED", foreground="#333333")
style.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", "#2C3E50")])

# Tablo (Treeview) Stilleri
style.configure("Treeview", font=("Segoe UI", 10), rowheight=35, borderwidth=0, background="#FFFFFF")
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#2C3E50", foreground="white", relief="flat")
style.map("Treeview", background=[("selected", "#3498DB")], foreground=[("selected", "white")])

# Ana Başlık
header_frame = Frame(root, bg="#F4F6F9")
header_frame.pack(fill=X, pady=(20, 10))
Label(header_frame, text="Yarışma Kontrol Paneli", font=("Segoe UI", 22, "bold"), bg="#F4F6F9", fg="#2C3E50").pack()

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True, padx=25, pady=(0, 25))

# ===== GENERIC TAB FUNCTION =====
def create_tab(notebook, tab_name, columns, headers, query, table_name):
    # Sekme Arka Planı
    tab_frame = Frame(notebook, bg="#FFFFFF")
    notebook.add(tab_frame, text=f" {tab_name} ")

    # ===== TREEVIEW =====
    tree_frame = Frame(tab_frame, bg="#FFFFFF")
    tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=(20, 10))
    
    # Scrollbar
    scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL)
    scroll_y.pack(side=RIGHT, fill=Y)

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", yscrollcommand=scroll_y.set)
    tree.pack(fill=BOTH, expand=True)
    scroll_y.config(command=tree.yview)

    for col, head in zip(columns, headers):
        tree.heading(col, text=head)
        tree.column(col, width=130, anchor=CENTER)

    # ===== FORM AREA =====
    form_outer_frame = Frame(tab_frame, bg="#FFFFFF")
    form_outer_frame.pack(fill=X, padx=20, pady=10)
    
    # Görsel ayrım için form alanının arkasına çok açık bir gri ekliyoruz
    form_frame = Frame(form_outer_frame, bg="#F8F9FA", bd=1, relief=SOLID)
    form_frame.pack(pady=5, ipadx=10, ipady=10)

    entries = {}

    for i, col in enumerate(columns):
        # Sütun isimlerini görsel olarak daha güzel göstermek için (örn: "team_id" -> "Team Id")
        display_name = col.replace("_", " ").title()
        
        Label(form_frame, text=display_name, font=("Segoe UI", 10, "bold"), bg="#F8F9FA", fg="#34495E").grid(row=0, column=i, padx=12, pady=(10, 2), sticky=W)
        ent = ttk.Entry(form_frame, font=("Segoe UI", 10), width=18)
        ent.grid(row=1, column=i, padx=12, pady=(0, 10))
        entries[col] = ent

    # ===== LOAD DATA =====
    def load_data():
        tree.delete(*tree.get_children())
        try:
            cursor.execute(query)
            for row in cursor.fetchall():
                tree.insert("", END, values=list(row))
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    load_data()

    # ===== SELECT =====
    def select_item(event):
        selected = tree.focus()
        values = tree.item(selected, "values")

        if not values:
            return

        for i, col in enumerate(columns):
            entries[col].delete(0, END)
            entries[col].insert(0, values[i])

    tree.bind("<<TreeviewSelect>>", select_item)

    # ===== ADD =====
    def add_data():
        cols_to_insert = columns[1:]
        vals = [entries[col].get() for col in cols_to_insert]
        col_names = ", ".join(cols_to_insert)
        placeholders = ", ".join(["?"] * len(vals))
        sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"

        try:
            cursor.execute(sql, vals)
            conn.commit()
            load_data()
            for col in columns:
                entries[col].delete(0, END)
            messagebox.showinfo("Başarılı", "Kayıt başarıyla eklendi!")
        except Exception as e:
            messagebox.showerror("Ekleme Hatası", str(e))

    # ===== DELETE =====
    def delete_data():
        selected = tree.focus()
        values = tree.item(selected, "values")
        if not values:
            return
            
        confirm = messagebox.askyesno("Silme Onayı", "Bu kaydı silmek istediğinize emin misiniz?")
        if confirm:
            try:
                cursor.execute(f"DELETE FROM {table_name} WHERE {columns[0]}=?", values[0])
                conn.commit()
                load_data()
                # Kutuları temizle
                for col in columns:
                    entries[col].delete(0, END)
            except Exception as e:
                messagebox.showerror("Silme Hatası", str(e))

    # ===== UPDATE =====
    def update_data():
        vals = [entries[col].get() for col in columns]
        set_clause = ", ".join([f"{col}=?" for col in columns[1:]])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]}=?"

        try:
            cursor.execute(sql, vals[1:] + [vals[0]])
            conn.commit()
            load_data()
            messagebox.showinfo("Başarılı", "Kayıt başarıyla güncellendi!")
        except Exception as e:
            messagebox.showerror("Güncelleme Hatası", str(e))

    # ===== BUTTONS =====
    btn_frame = Frame(tab_frame, bg="#FFFFFF")
    btn_frame.pack(pady=(0, 20))

    # Modern buton tasarımları
    Button(btn_frame, text="➕ Ekle", command=add_data, bg="#2ECC71", fg="white", font=("Segoe UI", 10, "bold"), relief=FLAT, width=12, cursor="hand2").pack(side=LEFT, padx=10)
    Button(btn_frame, text="✏️ Güncelle", command=update_data, bg="#F39C12", fg="white", font=("Segoe UI", 10, "bold"), relief=FLAT, width=12, cursor="hand2").pack(side=LEFT, padx=10)
    Button(btn_frame, text="🗑️ Sil", command=delete_data, bg="#E74C3C", fg="white", font=("Segoe UI", 10, "bold"), relief=FLAT, width=12, cursor="hand2").pack(side=LEFT, padx=10)
    Button(btn_frame, text="🔄 Yenile", command=load_data, bg="#3498DB", fg="white", font=("Segoe UI", 10, "bold"), relief=FLAT, width=12, cursor="hand2").pack(side=LEFT, padx=10)

# ===== TABS =====

create_tab(notebook, "Teams", 
           ["team_id", "team_name", "institution_id", "category_id"], 
           ["Team ID", "Team Name", "Institution", "Category"], 
           "SELECT team_id, team_name, institution_id, category_id FROM Teams", "Teams")

create_tab(notebook, "Cities", 
           ["city_id", "city_name"], 
           ["City ID", "City Name"], 
           "SELECT city_id, city_name FROM Cities", "Cities")

create_tab(notebook, "Institutions", 
           ["institution_id", "institution_name", "institution_type", "city_id"], 
           ["ID", "Name", "Type", "City"], 
           "SELECT institution_id, institution_name, institution_type, city_id FROM Institutions", "Institutions")

create_tab(notebook, "Categories", 
           ["category_id", "category_name", "min_altitude"], 
           ["ID", "Name", "Min Altitude"], 
           "SELECT category_id, category_name, min_altitude FROM Categories", "Categories")

create_tab(notebook, "Roles", 
           ["role_id", "role_name"], 
           ["Role ID", "Role Name"], 
           "SELECT role_id, role_name FROM Roles", "Roles")

create_tab(notebook, "Members", 
           ["member_id", "member_name", "role_id", "team_id"], 
           ["ID", "Name", "Role", "Team"], 
           "SELECT member_id, member_name, role_id, team_id FROM Members", "Members")

create_tab(notebook, "Motors", 
           ["motor_id", "motor_name", "thrust_pow", "manuf_id"], 
           ["ID", "Name", "Thrust", "Manufacturer"], 
           "SELECT motor_id, motor_name, thrust_pow, manuf_id FROM Motors", "Motors")

create_tab(notebook, "Rockets", 
           ["rocket_id", "rocket_name", "motor_id", "team_id", "category_id"], 
           ["ID", "Name", "Motor", "Team", "Category"], 
           "SELECT rocket_id, rocket_name, motor_id, team_id, category_id FROM Rockets", "Rockets")

create_tab(notebook, "Payloads", 
           ["payload_id", "payload_name", "payload_weight", "mission_purpose", "rocket_id"], 
           ["ID", "Name", "Weight", "Mission", "Rocket"], 
           "SELECT payload_id, payload_name, payload_weight, mission_purpose, rocket_id FROM Payloads", "Payloads")

create_tab(notebook, "Stages", 
           ["stage_id", "stage_name"], 
           ["Stage ID", "Stage Name"], 
           "SELECT stage_id, stage_name FROM Stages", "Stages")

create_tab(notebook, "Team Progress", 
           ["progress_id", "team_id", "stage_id", "status", "score", "pass_date"], 
           ["Progress ID", "Team ID", "Stage ID", "Status", "Score", "Pass Date"], 
           "SELECT progress_id, team_id, stage_id, status, score, pass_date FROM Team_Progress", "Team_Progress")

create_tab(notebook, "Referees", 
           ["ref_id", "ref_name", "rocket_id"], 
           ["Referee ID", "Referee Name", "Rocket ID"], 
           "SELECT ref_id, ref_name, rocket_id FROM Referees", "Referees")

create_tab(notebook, "Sponsors", 
           ["sponsor_id", "sponsor_name", "industry", "contribution_type"], 
           ["Sponsor ID", "Sponsor Name", "Industry", "Contribution Type"], 
           "SELECT sponsor_id, sponsor_name, industry, contribution_type FROM Sponsors", "Sponsors")

root.mainloop()