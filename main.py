# Created By FatihKabak : @fatihkabakk on GitHub
# -*- coding: utf-8 -*-
from tkinter import *
import tkinter.messagebox as messagebox
import sqlite3
from os import path, system
from datetime import datetime
from PIL import Image, ImageTk

background = "black"
font = ("Arial", 11)
colour = "orange"

success_messages = {"added": "Değerler Veritabanına Başarıyla Eklendi", "edited": "Değerler Başarıyla Güncellendi"}

if not path.exists("./data"):
    try:
        system("mkdir data")
    except Exception as oserror:
        messagebox.showerror("Veritabanı Hatası", "Veritabanı İçin Dosya Oluşturma Esnasında Bir Hata Oluştu"
                             f"\nHata Açıklaması: {oserror}")
database = "./data/records.db"


try:
    # Configurations
    root = Tk()
    root.title("Şeker Takibi v1.1")
    root.iconbitmap('./icons/icon.ico')

    app_width = 425
    app_height = 425

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width / 2) - (app_width / 2))
    y = int((screen_height / 2) - (app_height / 2))
    root.geometry(f"{app_width}x{app_height}+{x}+{y}")
    root.configure(background=background)

    # bg_photo = ImageTk.PhotoImage(Image.open("./icons/background.png"))
    # bg_label = Label(root, image=bg_photo)
    # bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Auto Disappearing Success Box Creation
    def success(message):
        s_level = Toplevel()
        s_level.title('İşlem Başarılı')
        s_level.overrideredirect(True)
        s_level.configure(background=background)
        s_width = 350
        s_height = 150

        sc_width = root.winfo_screenwidth()
        sc_height = root.winfo_screenheight()

        x_s = int((sc_width / 2) - (s_width / 2))
        y_s = int((sc_height / 2) - (s_height / 2))
        s_level.geometry(f"{s_width}x{s_height}+{x_s}+{y_s}")
        suc_img = ImageTk.PhotoImage(Image.open("./icons/new_tick.png"))
        Label(s_level, image=suc_img, background=background, padx=10).place(x=20, y=2)
        Message(s_level, text=message, padx=45, pady=21, font=font, background=background, fg=colour).place(x=150, y=5)
        s_level.after(1100, s_level.destroy)
        s_level.image = suc_img

    # Timestamp Calculation
    def calc_stamp(time):
        try:
            time_data = list(map(int, time.split("/")))
            if len(time_data) == 3:
                used_stamp = datetime.timestamp(datetime(time_data[2], time_data[1], time_data[0]))
                if used_stamp > timestamp:
                    raise RuntimeError("Future dates can't be processed.")
                return used_stamp
            else:
                raise RuntimeError("Date Format Error.")

        except RuntimeError as error:
            messagebox.showerror("Tarih Hatası", "Girdiğiniz Tarih Aşağıdaki Formatta Olmalıdır."
                                                 "\nGün/Ay/Yıl"
                                                 f"\nHata Açıklaması: {error}")

    # Value Validation
    def validate(value_list, vali_date):
        con_validate = sqlite3.connect(database)
        cursor_validate = con_validate.cursor()
        cursor_validate.execute("SELECT * FROM degerler WHERE date = ?", (vali_date,))
        selected = cursor_validate.fetchall()
        con_validate.close()
        print(selected)

        try:
            if len(selected) < 1:
                validation_result = {"add": True, "edit": False}
            else:
                validation_result = {"add": False, "edit": True, "data": selected}
            value_list = list(map(int, value_list))

            if len(value_list) < 1 or any(i for i in value_list if i < 40):
                raise ValueError("Value Format Error.\nSome Values Are Too Low!")
            elif any([i for i in value_list if i > 600]):
                raise ValueError("Value Format Error.\nSome Values Are Too High!")
            return validation_result

        except ValueError as err_v:
            messagebox.showerror("Değer Hatası", "Girdiğiniz Değer Hatalı.\nLütfen Geçerli Değerler Giriniz."
                                 f"\nHata Açıklaması: {err_v}")
            validation_result = {"add": False, "edit": False}
            return validation_result

    # Average Calculation
    def calc_average():
        stamp_to_use = (datetime.timestamp(datetime.now()) - 7776000)
        cursor.execute("SELECT * FROM degerler WHERE stamp > ?", (stamp_to_use,))
        degerler = cursor.fetchall()
        summary = 0
        if len(degerler) == 0:
            message = "Veri Yok"
            return {'message': message, "place": 347}
        print(degerler)

        for i in degerler:
            summary += i[1]
        to_process = summary // len(degerler)

        if 65 <= to_process < 600:
            temp = 4 + (to_process - 65) / 35
            num = round(temp, 2)
            if len(str(num)) >= 5:
                testing_var = 22
            elif 3 < len(str(num)) < 5:
                testing_var = 10
            else:
                testing_var = 0
            message = f"Ortalama: {num}"
            return {'message': message, "place": 310 - testing_var}

        else:
            message = f"Sınır Aşıldı! Sayı: {to_process}"
            return {'message': message, "place": 237}

    # Value Updating
    def update():
        global average_label
        con_update = sqlite3.connect(database)
        cursor_update = con_update.cursor()
        values = list()
        values.append(editor_value_entry1.get())
        values.append(editor_value_entry2.get())
        values.append(editor_value_entry3.get())
        values.append(editor_value_entry4.get())
        date_to_update = editor_date_entry.get()

        result = validate(values, date_to_update)
        if result["edit"]:
            try:
                used_stamp = calc_stamp(editor_date_entry.get())
                cursor_update.execute("UPDATE degerler SET value1 = ?, value2 = ?, value3 = ?, value4 = ?, "
                                      "stamp = ? WHERE date = ?",
                                      (values[0], values[1], values[2], values[3], used_stamp, date_to_update))
                con_update.commit()
                con_update.close()
                editor.destroy()
                success(success_messages["edited"])
                average_label.place_forget()
                val2 = calc_average()
                average_label = Label(root, text=val2['message'], bg=background, font=font, fg=colour)
                average_label.place(x=val2['place'], y=397)

            except Exception as update_error:
                messagebox.showerror("Beklenmedik Bir Hata Oluştu", "Beklenmedik Bir Hata Oluştu."
                                     "\nLütfen Geliştiriciye Aşağıdaki Hatayı Bildirin."
                                     f"\nHata Açıklaması: {update_error}")

    # Record Adding
    def add_record():
        con_add = sqlite3.connect(database)
        cursor_add = con_add.cursor()
        global average_label
        date_get = date_entry.get()
        value1 = value_entry1.get()
        value2 = value_entry2.get()
        value3 = value_entry3.get()
        value4 = value_entry4.get()
        values = list()
        values.append(value1)
        values.append(value2)
        values.append(value3)
        values.append(value4)

        result = validate(values, date_get)
        used_stamp = calc_stamp(date_get)
        if result["add"]:
            cursor_add.execute("INSERT INTO degerler VALUES (?, ?, ?, ?, ?, ?)",
                               (date_get, values[0], values[1], values[2], values[3], used_stamp))
            con_add.commit()
            success(success_messages["added"])
        if result["edit"]:
            selection = result["data"]
            messagebox.showwarning("Veritabanında Zaten Mevcut",
                                   "Belirtilen Tarihe Ait Değerler Zaten Veritabanında Mevcut."
                                   "\n'Düzenle' Butonundan Veriyi Değiştirebilirsiniz."
                                   f"\nTarih: {selection[0][0]}, Değerler: "
                                   f"{selection[0][1], selection[0][2], selection[0][3], selection[0][4]}")
        else:
            pass

        print(date_get, values)
        val1 = calc_average()
        average_label.place_forget()
        average_label = Label(root, text=val1['message'], bg=background, font=font, fg=colour)
        average_label.place(x=val1['place'], y=397)

    # Value Editing
    def edit():
        global editor
        global editor_value_entry1
        global editor_value_entry2
        global editor_value_entry3
        global editor_value_entry4
        global editor_date_entry
        editor_date = date_entry.get()
        editor = Toplevel()
        editor.title("Şeker Editörü v1.1")
        editor.iconbitmap('./icons/icon.ico')
        editor.geometry(f"{app_width}x{app_height}+{x-50}+{y-50}")
        editor.configure(background=background)

        # editor_photo_label = Label(editor, image=bg_photo)
        # editor_photo_label.place(x=0, y=0, relwidth=1, relheight=1)

        editor_date_label = Label(editor, text=date, bg=background, font=font, fg=colour)
        editor_date_label.place(x=320, y=8)

        editor_value_label = Label(editor, text="Değerler: ", font=font, bg=background, fg=colour)
        editor_value_label.place(x=10, y=100, height=30)

        editor_value_entry1 = Entry(editor)
        editor_value_entry1.place(x=183, y=100, height=30, width=51)

        editor_value_entry2 = Entry(editor)
        editor_value_entry2.place(x=241, y=100, height=30, width=51)

        editor_value_entry3 = Entry(editor)
        editor_value_entry3.place(x=300, y=100, height=30, width=51)

        editor_value_entry4 = Entry(editor)
        editor_value_entry4.place(x=359, y=100, height=30, width=51)

        editor_date_label = Label(editor, text="Tarih: ", font=font, bg=background, fg=colour)
        editor_date_label.place(x=10, y=50, height=30)

        editor_date_entry = Entry(editor, width=28)
        editor_date_entry.place(x=183, y=50, height=30)
        editor_date_entry.insert(0, editor_date)

        editor_update_button = Button(editor, text="Veriyi Güncelle", command=update, font=font,
                                      bg="#b8bbb5", activebackground=colour)
        editor_update_button.place(x=184, y=150, width=228, height=40)

        con_edit = sqlite3.connect(database)
        cursor_edit = con_edit.cursor()
        print(editor_date)

        cursor_edit.execute("SELECT * FROM degerler WHERE date = ?", (editor_date,))
        records = cursor_edit.fetchall()

        for record in records:
            editor_value_entry1.insert(0, record[1])
            editor_value_entry2.insert(0, record[2])
            editor_value_entry3.insert(0, record[3])
            editor_value_entry4.insert(0, record[4])

    # Actual Application
    moment = datetime.now()
    date = moment.strftime('%d-%m-%Y').replace("-", "/")
    timestamp = datetime.timestamp(moment)
    delete_stamp = timestamp - 10368000

    con = sqlite3.connect(database)
    cursor = con.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS degerler (
                date text, 
                value1 integer,
                value2 integer,
                value3 integer,
                value4 integer,
                stamp real
                )""")
    cursor.execute("DELETE FROM degerler WHERE stamp < ?", (delete_stamp,))
    con.commit()

    returned = calc_average()

    average_label = Label(root, text=returned['message'], bg=background, font=font, fg=colour)
    average_label.place(x=returned['place'], y=397)

    date_label = Label(root, text=date, bg=background, font=font, fg=colour)
    date_label.place(x=320, y=8)

    value_label = Label(root, text="Değerler: ", font=font, bg=background, fg=colour)
    value_label.place(x=15, y=100, height=30)

    value_entry1 = Entry(root)
    value_entry1.place(x=181, y=100, height=30, width=51)

    value_entry2 = Entry(root)
    value_entry2.place(x=240, y=100, height=30, width=51)

    value_entry3 = Entry(root)
    value_entry3.place(x=299, y=100, height=30, width=51)

    value_entry4 = Entry(root)
    value_entry4.place(x=358, y=100, height=30, width=51)

    date_label = Label(root, text="Tarih: ", font=font, bg=background, fg=colour)
    date_label.place(x=15, y=50, height=30)

    date_entry = Entry(root, width=28)
    date_entry.place(x=182, y=50, height=30)
    date_entry.insert(0, date)

    add_text = "Veritabanına Ekle"
    add_button = Button(root, text=add_text, command=add_record, font=font, bg="#b8bbb5", activebackground=colour)
    add_button.place(x=181, y=150, width=229, height=40)

    update_button = Button(root, text="Düzenle", command=edit, font=font, bg="#b8bbb5", activebackground=colour)
    update_button.place(x=15, y=150, width=150, height=40)

    root.mainloop()

except Exception as err:

    try:
        messagebox.showwarning("Error", "Bir Hata Oluştu.\nBilgiler Log Dosyasına Kaydediliyor..."
                                        f"\nHata Açıklaması: {err}")
        r_t = datetime.now()
        if not path.exists("logs"):
            system("mkdir logs")
        log_file = ("logs/" + r_t.strftime("%c").replace(" ", "_") + ".log").replace(":", "_")
        log_time = r_t.strftime("%X") + " " + r_t.strftime("%d") + "/" + r_t.strftime("%m") + "/" + r_t.strftime("%Y")
        with open(log_file, "a", encoding="utf-8") as log:
            log.write("*************************************************\n")
            log.write(f"Time: {log_time}\n")
            log.write(f"An Error Has Occurred\n")
            log.write(f"Error Code: {err}\n")
            log.write("*************************************************\n")

    except Exception as f_err:
        messagebox.showerror("Fatal Error", f"Beklenmedik Bir Sorun Oluştu ve Hata Kaydı Oluşturulamadı."
                                            f"\nLütfen Geliştiriciye Sorunu Bildiriniz.\nError Code: {f_err}")
