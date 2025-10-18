import tkinter as tk
from tkinter import messagebox
import json
import os
import csv
import customtkinter as ctk
from PIL import Image, ImageTk
import webbrowser


# ---------- CONFIG ----------
CSV_FILENAME = "gemgo_hidden_gems.csv"
LOGO_PATH = "gemgo_logo.png"


# ---------- BACKEND ----------
class User:
    def __init__(self, username):
        self.username = username
        self.gem_balance = 0

    def add_gems(self, amount):
        self.gem_balance += amount

    def get_balance(self):
        return self.gem_balance

def load_user_balance():
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r") as file:
            data = json.load(file)
            return data.get("gem_balance", 0)
    return 0

def save_user_balance(balance):
    with open("user_data.json", "w") as file:
        json.dump({"gem_balance": balance}, file)

class GemNode:
    def __init__(self, country, city, neighborhood, name, description, gem_type, season, stay_duration, image_path=None, map_link=None):
        self.country = country
        self.city = city
        self.neighborhood = neighborhood
        self.name = name
        self.description = description
        self.gem_type = gem_type
        self.season = season
        self.stay_duration = stay_duration
        self.image_path = image_path
        self.map_link = map_link

    def __str__(self):
        return f"{self.name} ({self.gem_type}) in {self.city}, {self.country}"

class Node:
    def __init__(self, gem):
        self.gem = gem
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def add_gem(self, gem):
        new_node = Node(gem)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def search_gem(self, country, city, gem_type=None):
        results = []
        current = self.head
        while current:
            gem = current.gem
            if (
                gem.country.lower() == country.lower() and
                gem.city.lower() == city.lower() and
                (not gem_type or gem.gem_type.lower() == gem_type.lower())
            ):
                results.append(gem)
            current = current.next
        return results

# ---------- LOAD DATA FROM CSV ----------
def load_gems_from_csv(filename, linked_list):
    if not os.path.exists(filename):
        return

    with open(filename, mode="r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        cleaned_fieldnames = [field.strip().replace('\ufeff', '').lower().replace(" ", "_") for field in reader.fieldnames]
        reader.fieldnames = cleaned_fieldnames

        for row in reader:
            gem = GemNode(
                row.get("country", ""),
                row.get("city", ""),
                row.get("neighborhood", ""),
                row.get("name", ""),
                row.get("description", ""),
                row.get("gem_type", ""),
                row.get("season", ""),
                row.get("stay_duration", ""),
                row.get("image_path", ""),
                row.get("map_link", "")
            )
            linked_list.add_gem(gem)


def load_gems_fresh():
    fresh_list = LinkedList()
    load_gems_from_csv(CSV_FILENAME, fresh_list)
    return fresh_list

# ---------- FUNCTIONS ----------

def bubble_sort_by_stay_duration(results, descending=False):
    def extract_minutes(duration):
        try:
            parts = duration.strip().lower().split()
            value = int(parts[0])
            unit = parts[1] if len(parts) > 1 else "minutes"
            if "hour" in unit:
                return value * 60
            elif "minute" in unit:
                return value
            else:
                return value
        except:
            return 0

    n = len(results)
    for i in range(n):
        for j in range(0, n - i - 1):
            a = extract_minutes(results[j].stay_duration)
            b = extract_minutes(results[j + 1].stay_duration)
            if (a < b and descending):  # מהגבוה לנמוך
                results[j], results[j + 1] = results[j + 1], results[j]
    return results

def add_gem_from_the_user():
    try:
        country = entry_country.get().strip()
        city = entry_city.get().strip()
        neighborhood = entry_neighborhood.get().strip()
        name = entry_name.get().strip()
        description = entry_description.get("1.0", "end").strip()
        gem_type = selected_type.get()
        season = selected_season.get()
        stay_duration = entry_minutes.get().strip()
        image = entry_image.get().strip()
        link = entry_link.get().strip()

        if not country or not city or not gem_type:
            messagebox.showerror("Missing Fields", "Please fill in all required fields: Country, City, and Type.")
            return

        if stay_duration and not stay_duration.isdigit():
            messagebox.showerror("Invalid Input", "Stay duration must be a number in minutes.")
            return

        with open(CSV_FILENAME, mode="a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([country, city, neighborhood, name, description, gem_type, season, stay_duration, image, link])

        current_user.add_gems(25)
        save_user_balance(current_user.get_balance())

        messagebox.showinfo("Success ✅", f"Gem added! You earned 25 Gems 💎")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_user_summary():
    balance = current_user.get_balance()
    summary = f"You have {balance} Gems 💎"
    messagebox.showinfo("My Gems", summary)

def search_window():
    win = ctk.CTkToplevel(fg_color="#f8f3e7")
    win.title("Search")
    win.geometry("400x550")
    win.grab_set()

    def create_entry_grid(label, row, col, required=False):
        text = f"{label} {'(required)' if required else ''}"
        ctk.CTkLabel(win, text=text).grid(row=row, column=col, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(win, corner_radius=10)
        entry.grid(row=row+1, column=col, padx=10, pady=5, sticky="ew")
        return entry

    win.grid_columnconfigure((0, 1), weight=1)

    entry_country = create_entry_grid("Country", 0, 0, True)
    entry_city = create_entry_grid("City", 0, 1, True)
    entry_neighborhood = create_entry_grid("Neighborhood", 2, 0)
    entry_name = create_entry_grid("Name", 2, 1)

    ctk.CTkLabel(win, text="Gem Type (required):").grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
    type_options = ["Viewpoint", "Trail", "Cave", "Water", "Beach", "Park/Garden", "Cafe", "Restaurant", "Biking", "Other"]
    selected_type = ctk.StringVar(value=type_options[0])
    ctk.CTkOptionMenu(win, variable=selected_type, values=type_options).grid(row=5, column=0, columnspan=2, padx=10, sticky="ew")

    ctk.CTkLabel(win, text="Season (optional):").grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
    season_options = ["Summer", "Winter", "Spring", "Autumn", "All year"]
    selected_season = ctk.StringVar(value=season_options[0])
    ctk.CTkOptionMenu(win, variable=selected_season, values=season_options).grid(row=7, column=0, columnspan=2, padx=10, sticky="ew")

    entry_minutes = create_entry_grid("Stay Duration (optional)", 8, 0)
    entry_description = create_entry_grid("Description (optional)", 8, 1)

    result_box = ctk.CTkTextbox(win, height=120, corner_radius=10)
    result_box.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def do_search():
        global gem_list
        gem_list = LinkedList()
        load_gems_from_csv(CSV_FILENAME, gem_list)
        
        country = entry_country.get()
        city = entry_city.get()
        gem_type = selected_type.get()
        neighborhood = entry_neighborhood.get()
        name = entry_name.get()
        season = selected_season.get()
        stay_duration = entry_minutes.get()
        description = entry_description.get()

        if not country or not city or not gem_type:
            messagebox.showerror("Missing Fields", "Please fill in all required fields: Country, City, and Type.")
            return

        fresh_gems = load_gems_fresh()
        results = fresh_gems.search_gem(country, city, gem_type)

        filtered_results = []
        for gem in results:
            if (not neighborhood or neighborhood.lower() in gem.neighborhood.lower()) and \
               (not name or name.lower() in gem.name.lower()):
                filtered_results.append(gem)

        result_box.delete("1.0", "end")

        if filtered_results:
            result_box.tag_config("link", foreground="blue", underline=True)

        for gem in filtered_results:
            result_box.insert("end", f"{gem.name} | {gem.city}, {gem.country} | {gem.gem_type} | {gem.season or 'All seasons'} | Stay: {gem.stay_duration or 'Unknown'} min\n", "bold")

            desc = gem.description.strip() if gem.description else "No description"
            result_box.insert("end", f"{desc}\n")

            if gem.map_link:
                start_index = result_box.index("end")
                result_box.insert("end", "link to address\n")
                end_index = result_box.index("end")
                result_box.tag_add(gem.map_link, start_index, end_index)
                result_box.tag_bind(gem.map_link, "<Button-1>", lambda e, url=gem.map_link: webbrowser.open(url))
                result_box.tag_config(gem.map_link, foreground="blue", underline=True)

            result_box.insert("end", "-" * 60 + "\n")

            sort_btn.grid(row=11, column=0, pady=10, padx=(20, 5), sticky="w")       
            sort_btn_desc.grid(row=11, column=1, pady=10, padx=(5, 20), sticky="e")
        else:
          result_box.insert("end", "No matching gems found.")

    def sort_by_duration(order):
        fresh_gems = load_gems_fresh()
        results = fresh_gems.search_gem(entry_country.get(), entry_city.get(), selected_type.get())
        sorted_results = bubble_sort_by_stay_duration(results, descending=(order=="desc"))
        result_box.delete("1.0", "end")
        for gem in sorted_results:
            formatted = (
                f"Name: {gem.name}\n"
                f"Country: {gem.country}\n"
                f"City: {gem.city}\n"
                f"Neighborhood: {gem.neighborhood}\n"
                f"Type: {gem.gem_type}\n"
                f"Season: {gem.season}\n"
                f"Stay Duration: {gem.stay_duration}\n"
                f"Description: {gem.description}\n"
                f"Image: {gem.image_path}\n"
                f"Map: {gem.map_link}\n"
                "--------------------------\n"
            )
            result_box.insert("end", formatted)

    ctk.CTkButton(win, text="Search", command=do_search).grid(row=11, column=0, columnspan=2,padx=(5, 0), pady=10)

    sort_btn = ctk.CTkButton(win, text="Sort by Duration (asc)", command=lambda: sort_by_duration("asc"))
    sort_btn_desc = ctk.CTkButton(win, text="Sort by Duration (Desc)", command=lambda: sort_by_duration("desc"))

def bubble_sort_by_stay_duration(results, descending=False):
    def extract_minutes(duration):
        try:
            parts = duration.strip().lower().split()
            value = int(parts[0])
            unit = parts[1] if len(parts) > 1 else "minutes"
            if "hour" in unit:
                return value * 60
            elif "minute" in unit:
                return value
            else:
                return value
        except:
            return 0

    n = len(results)
    for i in range(n):
        for j in range(0, n - i - 1):
            a = extract_minutes(results[j].stay_duration)
            b = extract_minutes(results[j + 1].stay_duration)
            if (a > b and not descending) or (a < b and descending):
                results[j], results[j + 1] = results[j + 1], results[j]
    return results

def add_gem_window():
    global entry_country, entry_city, entry_neighborhood, entry_name
    global entry_description, selected_type, selected_season
    global entry_minutes, entry_image, entry_link

    win = ctk.CTkToplevel(fg_color="#f8f3e7")
    win.title("Add New Gem")
    win.geometry("400x550")
    win.grab_set()

    def create_entry_grid(label, row, col, required=False):
        text = f"{label} {'(required)' if required else '(optional)'}"
        ctk.CTkLabel(win, text=text).grid(row=row, column=col, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(win, corner_radius=10)
        entry.grid(row=row+1, column=col, padx=10, pady=5, sticky="ew")
        return entry

    win.grid_columnconfigure((0, 1), weight=1)

    entry_country = create_entry_grid("Country", 0, 0, True)
    entry_city = create_entry_grid("City", 0, 1, True)
    entry_neighborhood = create_entry_grid("Neighborhood", 2, 0)
    entry_name = create_entry_grid("Name", 2, 1, True)

    ctk.CTkLabel(win, text="Description (optional):").grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
    entry_description = ctk.CTkTextbox(win, height=60, corner_radius=10)
    entry_description.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    ctk.CTkLabel(win, text="Type (required):").grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
    type_options = ["Viewpoint", "Trail", "Cave", "Water", "Beach", "Park/Garden", "Cafe", "Restaurant", "Biking", "Other"]
    selected_type = ctk.StringVar(value=type_options[0])
    ctk.CTkOptionMenu(win, variable=selected_type, values=type_options).grid(row=7, column=0, columnspan=2, padx=10, sticky="ew")

    ctk.CTkLabel(win, text="Season (optional):").grid(row=8, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))
    season_options = ["Summer", "Winter", "Spring", "Autumn", "All year"]
    selected_season = ctk.StringVar(value=season_options[0])
    ctk.CTkOptionMenu(win, variable=selected_season, values=season_options).grid(row=9, column=0, columnspan=2, padx=10, sticky="ew")

    entry_minutes = create_entry_grid("Minutes of Stay", 10, 0)
    entry_image = create_entry_grid("Image Link", 10, 1)
    entry_link = create_entry_grid("Map Link", 12, 0)

    ctk.CTkButton(win, text="Save Gem", command=add_gem_from_the_user).grid(row=99, column=0, columnspan=2, pady=(10, 20))

# ---------- MAIN GUI ----------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

root = ctk.CTk(fg_color="#f8f3e7")
root.title("Gem Go")
root.geometry("400x550")
header = ctk.CTkFrame(root, fg_color="transparent")
header.pack(fill="x", pady=(10, 0))
header.pack_propagate(False)

def create_colored_title(parent):
    return ctk.CTkLabel(
        parent,
        text="GemGo",
        font=("Quicksand", 75, "bold"),
        text_color="#17585f",
        fg_color="transparent"
    )

# --- לוגו מעל הכיתוב, ריווח מדויק ---
try:
    pil_img = Image.open(LOGO_PATH)
    target_h = 80
    ratio = pil_img.width / pil_img.height if pil_img.height else 1
    target_w = int(target_h * ratio)
    pil_img = pil_img.resize((target_w, target_h), Image.LANCZOS)

    logo_img = ctk.CTkImage(light_image=pil_img, size=(target_w, target_h))
    logo_label = ctk.CTkLabel(header, image=logo_img, text="", fg_color="transparent")
    # הלוגו ראשון => תמיד מעל; ריווח עליון קטן
    logo_label.pack(pady=(30, 0))
except Exception:
    # אם אין לוגו, ממשיכים בלי להפיל את האפליקציה
    logo_label = None

title_label = create_colored_title(header)
# ריווח בין הלוגו לכותרת כדי שלא תהיה חפיפה
title_label.pack(pady=(8, 10))

# ===== המשך המסך =====
subtitle = ctk.CTkLabel(
    root,
    text="FIND THE HIDDEN MAGIC.",
    font=("Quicksand", 14, "bold"),
    text_color="#58bf85"
)
subtitle.pack(pady=(7, 40))

current_user = User("guest")
current_user.gem_balance = load_user_balance()

ctk.CTkButton(root, text="  I want to find a Gem", command=search_window,
              font=("Helvetica", 13, "bold"), fg_color="#58bf85",
              text_color="#f8f3e7", corner_radius=20, height=40, width=200)\
    .pack(pady=(0, 20))

ctk.CTkButton(root, text="  I want to add a Gem", command=add_gem_window,
              font=("Helvetica", 13, "bold"), fg_color="#58bf85",
              text_color="#f8f3e7", corner_radius=20, height=40, width=200)\
    .pack()

ctk.CTkButton(root, text= "  My Gems 💎", font=("Helvetica", 13, "bold"),
              fg_color="#58bf85", text_color="white", width=100,
              command=show_user_summary, corner_radius=20)\
    .place(x=20, y=20)

footer = ctk.CTkLabel(
    root,
    text="© 2025 GemGo. All rights reserved.",
    font=("Helvetica", 10),
    text_color="#7a7a7a",
    fg_color="transparent"
)
footer.pack(side="bottom", pady=10)

root.mainloop()
