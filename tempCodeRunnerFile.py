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

# ===== MAIN WINDOW =====
root = Tk()
root.title("Roket Yarışması - Veritabanı Yönetimi")
root.geometry("1000x650")
root.configure(bg="#f0f2f5")

Label(root, text="Tüm Tablolar", font=("Helvetica", 16, "bold"), bg="#f0f2f5").pack(pady=10)

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True, padx=20, pady=20)

# ===== GENERIC TAB FUNCTION =====
def create_tab(notebook, tab_name, columns, headers, query, table_name):
    tab_frame = Frame(notebook, bg="#f0f2f5")
    notebook.add(tab_frame, text=tab_name)

    # ===== TREEVIEW =====
    tree = ttk.Treeview(tab_frame, columns=columns, show="headings")
    tree.pack(fill=BOTH, expand=True, pady=10)

    for col, head in zip(columns, headers):
        tree.heading(col, text=head)
        tree.column(col, width=130, anchor=CENTER)

    # ===== FORM =====
    form_frame = Frame(tab_frame, bg="#f0f2f5")
    form_frame.pack(pady=10)

    entries = {}

    for i, col in enumerate(columns):
        Label(form_frame, text=col, bg="#f0f2f5").grid(row=0, column=i)
        ent = Entry(form_frame)
        ent.grid(row=1, column=i, padx=5)
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
    # ===== ADD =====
    # ===== ADD =====
    def add_data():
        # 1. İlk sütunu (ID) atla, sadece veri eklenecek sütunları al
        cols_to_insert = columns[1:]
        
        # 2. Formdaki kutulardan ID hariç diğer değerleri çek
        vals = [entries[col].get() for col in cols_to_insert]

        # 3. SQL formatını hazırla
        col_names = ", ".join(cols_to_insert)
        placeholders = ", ".join(["?"] * len(vals))

        # 4. Sütun isimlerini belirterek INSERT INTO sorgusu oluştur
        sql = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
        
        # Hata ayıklama için SQL sorgusunu terminale yazdır:
        print("ÇALIŞTIRILAN SQL:", sql)
        print("GÖNDERİLEN DEĞERLER:", vals)

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

        try:
            cursor.execute(f"DELETE FROM {table_name} WHERE {columns[0]}=?", values[0])
            conn.commit()
            load_data()
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
        except Exception as e:
            messagebox.showerror("Güncelleme Hatası", str(e))

    # ===== BUTTONS =====
    btn_frame = Frame(tab_frame, bg="#f0f2f5")
    btn_frame.pack(pady=10)

    Button(btn_frame, text="Ekle", command=add_data, bg="green", fg="white", width=10).pack(side=LEFT, padx=5)
    Button(btn_frame, text="Güncelle", command=update_data, bg="orange", width=10).pack(side=LEFT, padx=5)
    Button(btn_frame, text="Sil", command=delete_data, bg="red", fg="white", width=10).pack(side=LEFT, padx=5)
    Button(btn_frame, text="Yenile", command=load_data, width=10).pack(side=LEFT, padx=5)

# ===== TABS =====

create_tab(
    notebook,
    "Teams",
    ["team_id", "team_name", "institution_id", "category_id"],
    ["Team ID", "Team Name", "Institution", "Category"],
    "SELECT team_id, team_name, institution_id, category_id FROM Teams",
    "Teams"
)

create_tab(
    notebook,
    "Cities",
    ["city_id", "city_name"],
    ["City ID", "City Name"],
    "SELECT city_id, city_name FROM Cities",
    "Cities"
)

create_tab(
    notebook,
    "Institutions",
    ["institution_id", "institution_name", "institution_type", "city_id"],
    ["ID", "Name", "Type", "City"],
    "SELECT institution_id, institution_name, institution_type, city_id FROM Institutions",
    "Institutions"
)

create_tab(
    notebook,
    "Categories",
    ["category_id", "category_name", "min_altitude"],
    ["ID", "Name", "Min Altitude"],
    "SELECT category_id, category_name, min_altitude FROM Categories",
    "Categories"
)

create_tab(
    notebook,
    "Roles",
    ["role_id", "role_name"],
    ["Role ID", "Role Name"],
    "SELECT role_id, role_name FROM Roles",
    "Roles"
)

create_tab(
    notebook,
    "Members",
    ["member_id", "member_name", "role_id", "team_id"], # DİKKAT: member_id en başa alındı!
    ["ID", "Name", "Role", "Team"],
    "SELECT member_id, member_name, role_id, team_id FROM Members", # Sorgu sırası da buna uyumlu yapıldı!
    "Members"
)

create_tab(
    notebook,
    "Motors",
    ["motor_id", "motor_name", "thrust_pow", "manuf_id"],
    ["ID", "Name", "Thrust", "Manufacturer"],
    "SELECT motor_id, motor_name, thrust_pow, manuf_id FROM Motors",
    "Motors"
)

create_tab(
    notebook,
    "Rockets",
    ["rocket_id", "rocket_name", "motor_id", "team_id", "category_id"],
    ["ID", "Name", "Motor", "Team", "Category"],
    "SELECT rocket_id, rocket_name, motor_id, team_id, category_id FROM Rockets",
    "Rockets"
)

create_tab(
    notebook,
    "Payloads",
    ["payload_id", "payload_name", "payload_weight", "mission_purpose", "rocket_id"],
    ["ID", "Name", "Weight", "Mission", "Rocket"],
    "SELECT payload_id, payload_name, payload_weight, mission_purpose, rocket_id FROM Payloads",
    "Payloads"
)


create_tab(
    notebook,
    "Stages",
    ["stage_id", "stage_name"],
    ["Stage ID", "Stage Name"],
    "SELECT stage_id, stage_name FROM Stages",
    "Stages"
)

create_tab(
    notebook,
    "Team Progress",
    ["progress_id", "team_id", "stage_id", "status", "score", "pass_date"],
    ["Progress ID", "Team ID", "Stage ID", "Status", "Score", "Pass Date"],
    "SELECT progress_id, team_id, stage_id, status, score, pass_date FROM Team_Progress",
    "Team_Progress"
)

create_tab(
    notebook,
    "Referees",
    ["ref_id", "ref_name", "rocket_id"],
    ["Referee ID", "Referee Name", "Rocket ID"],
    "SELECT ref_id, ref_name, rocket_id FROM Referees",
    "Referees"
)

create_tab(
    notebook,
    "Sponsors",
    ["sponsor_id", "sponsor_name", "industry", "contribution_type"],
    ["Sponsor ID", "Sponsor Name", "Industry", "Contribution Type"],
    "SELECT sponsor_id, sponsor_name, industry, contribution_type FROM Sponsors",
    "Sponsors"
)



root.mainloop()
