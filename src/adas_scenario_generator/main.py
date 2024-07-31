import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import codecs
import itertools
import os

class ADASScenarioGenerator:
    def __init__(self, master):
        self.master = master
        master.title("ADAS Scenario Generator")

        self.categories = {}
        self.category_file = 'categories.json'  # デフォルトのファイル名
        self.load_categories()

        self.selected_items = {}
        self.update_selected_items()

        self.exclusion_rules = []

        self.create_gui()

    def load_categories(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), self.category_file)
            with codecs.open(file_path, 'r', 'utf-8') as file:
                self.categories = json.load(file)
            print(f"Successfully loaded categories from {file_path}")  # デバッグ用
        except FileNotFoundError:
            print(f"File not found: {file_path}")  # デバッグ用
            messagebox.showerror("エラー", f"'{self.category_file}' が見つかりません。ファイルを選択してください。")
            self.select_category_file()
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")  # デバッグ用
            messagebox.showerror("エラー", f"'{self.category_file}' の解析に失敗しました。JSONフォーマットを確認してください。")
            self.select_category_file()
        except Exception as e:
            print(f"Unexpected error: {str(e)}")  # デバッグ用
            messagebox.showerror("エラー", f"予期せぬエラーが発生しました: {str(e)}")
            self.select_category_file()

    def select_category_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.category_file = file_path
            self.load_categories()
        else:
            if not self.categories:  # カテゴリーが空の場合のみ終了
                messagebox.showerror("エラー", "カテゴリファイルが選択されていません。プログラムを終了します。")
                self.master.quit()

    def save_categories(self):
        with codecs.open(self.category_file, 'w', 'utf-8') as file:
            json.dump(self.categories, file, ensure_ascii=False, indent=2)
        messagebox.showinfo("保存完了", f"カテゴリ情報を '{self.category_file}' に保存しました。")

    def update_selected_items(self):
        self.selected_items = {category: {subcategory: {item: tk.BooleanVar() for item in items} 
                               for subcategory, items in subcategories.items()} 
                               for category, subcategories in self.categories.items()}

    def create_gui(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_category_tabs()
        self.create_exclusion_tab()
        self.create_execution_tab()
        self.create_category_management_tab()

    def create_category_tabs(self):
        for category, subcategories in self.categories.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=category)

            for subcategory, items in subcategories.items():
                subframe = ttk.LabelFrame(frame, text=subcategory)
                subframe.pack(fill=tk.X, padx=5, pady=5)

                for item in items:
                    cb = ttk.Checkbutton(subframe, text=item, variable=self.selected_items[category][subcategory][item])
                    cb.pack(anchor=tk.W)

    def create_exclusion_tab(self):
        exclusion_frame = ttk.Frame(self.notebook)
        self.notebook.add(exclusion_frame, text="除外ルール")

        self.exclusion_entry1 = ttk.Combobox(exclusion_frame, values=self.get_all_items())
        self.exclusion_entry1.pack(pady=5)
        self.exclusion_entry2 = ttk.Combobox(exclusion_frame, values=self.get_all_items())
        self.exclusion_entry2.pack(pady=5)

        add_button = ttk.Button(exclusion_frame, text="除外ルール追加", command=self.add_exclusion_rule)
        add_button.pack(pady=5)

        self.exclusion_listbox = tk.Listbox(exclusion_frame, width=50)
        self.exclusion_listbox.pack(pady=5)

        remove_button = ttk.Button(exclusion_frame, text="選択したルールを削除", command=self.remove_exclusion_rule)
        remove_button.pack(pady=5)

        file_frame = ttk.Frame(exclusion_frame)
        file_frame.pack(pady=10)

        load_button = ttk.Button(file_frame, text="ルールを読み込む", command=self.load_rules)
        load_button.pack(side=tk.LEFT, padx=5)

        save_button = ttk.Button(file_frame, text="ルールを保存", command=self.save_rules)
        save_button.pack(side=tk.LEFT, padx=5)

    def create_execution_tab(self):
        execution_frame = ttk.Frame(self.notebook)
        self.notebook.add(execution_frame, text="実行")

        self.generate_button = ttk.Button(execution_frame, text="シナリオ生成", command=self.generate_scenarios)
        self.generate_button.pack(pady=20)

        self.tree = ttk.Treeview(execution_frame, columns=("環境状況", "車両状況"), show="headings")
        self.tree.heading("環境状況", text="環境状況")
        self.tree.heading("車両状況", text="車両状況")
        self.tree.column("環境状況", width=300)
        self.tree.column("車両状況", width=300)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(execution_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def create_category_management_tab(self):
        management_frame = ttk.Frame(self.notebook)
        self.notebook.add(management_frame, text="カテゴリ管理")

        file_button = ttk.Button(management_frame, text="カテゴリファイル選択", command=self.select_category_file)
        file_button.pack(pady=10)

        category_frame = ttk.Frame(management_frame)
        category_frame.pack(pady=10)
        ttk.Label(category_frame, text="カテゴリ:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, values=list(self.categories.keys()))
        self.category_combobox.pack(side=tk.LEFT)
        self.category_combobox.bind("<<ComboboxSelected>>", self.on_category_selected)

        subcategory_frame = ttk.Frame(management_frame)
        subcategory_frame.pack(pady=10)
        ttk.Label(subcategory_frame, text="サブカテゴリ:").pack(side=tk.LEFT)
        self.subcategory_var = tk.StringVar()
        self.subcategory_combobox = ttk.Combobox(subcategory_frame, textvariable=self.subcategory_var)
        self.subcategory_combobox.pack(side=tk.LEFT)
        self.subcategory_combobox.bind("<<ComboboxSelected>>", self.on_subcategory_selected)

        self.items_listbox = tk.Listbox(management_frame, width=50)
        self.items_listbox.pack(pady=10)

        button_frame = ttk.Frame(management_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="カテゴリ追加", command=self.add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="サブカテゴリ追加", command=self.add_subcategory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="項目追加", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="項目削除", command=self.remove_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="変更を保存", command=self.save_categories).pack(side=tk.LEFT, padx=5)

    def on_category_selected(self, event):
        category = self.category_var.get()
        self.subcategory_combobox['values'] = list(self.categories[category].keys())
        self.subcategory_combobox.set('')
        self.items_listbox.delete(0, tk.END)

    def on_subcategory_selected(self, event):
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        self.items_listbox.delete(0, tk.END)
        for item in self.categories[category][subcategory]:
            self.items_listbox.insert(tk.END, item)

    def add_category(self):
        new_category = simpledialog.askstring("カテゴリ追加", "新しいカテゴリ名を入力してください:")
        if new_category and new_category not in self.categories:
            self.categories[new_category] = {}
            self.update_gui()

    def add_subcategory(self):
        category = self.category_var.get()
        if not category:
            messagebox.showerror("エラー", "カテゴリを選択してください")
            return
        new_subcategory = simpledialog.askstring("サブカテゴリ追加", "新しいサブカテゴリ名を入力してください:")
        if new_subcategory and new_subcategory not in self.categories[category]:
            self.categories[category][new_subcategory] = []
            self.update_gui()

    def add_item(self):
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        if not category or not subcategory:
            messagebox.showerror("エラー", "カテゴリとサブカテゴリを選択してください")
            return
        new_item = simpledialog.askstring("項目追加", "新しい項目名を入力してください:")
        if new_item and new_item not in self.categories[category][subcategory]:
            self.categories[category][subcategory].append(new_item)
            self.update_gui()

    def remove_item(self):
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        if not category or not subcategory:
            messagebox.showerror("エラー", "カテゴリとサブカテゴリを選択してください")
            return
        selected = self.items_listbox.curselection()
        if not selected:
            messagebox.showerror("エラー", "削除する項目を選択してください")
            return
        item = self.items_listbox.get(selected[0])
        self.categories[category][subcategory].remove(item)
        self.update_gui()

    def update_gui(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        self.update_selected_items()
        self.create_category_tabs()
        self.create_exclusion_tab()
        self.create_execution_tab()
        self.create_category_management_tab()

    def get_all_items(self):
        return [item for category in self.categories.values() for subcategory in category.values() for item in subcategory]

    def add_exclusion_rule(self):
        item1 = self.exclusion_entry1.get()
        item2 = self.exclusion_entry2.get()
        if item1 and item2 and item1 != item2:
            rule = f"{item1} * {item2}"
            if rule not in self.exclusion_rules:
                self.exclusion_rules.append(rule)
                self.exclusion_listbox.insert(tk.END, rule)

    def remove_exclusion_rule(self):
        selection = self.exclusion_listbox.curselection()
        if selection:
            index = selection[0]
            rule = self.exclusion_listbox.get(index)
            self.exclusion_rules.remove(rule)
            self.exclusion_listbox.delete(index)

    def load_rules(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with codecs.open(file_path, 'r', 'utf-8-sig') as file:
                    data = json.load(file)
                    print(f"Loaded data: {data}")  # デバッグ用
                    if data.get("version") == "1.0":
                        self.exclusion_rules = [" * ".join(rule["items"]) for rule in data["rules"]]
                        self.update_exclusion_listbox()
                        messagebox.showinfo("成功", "除外ルールを読み込みました。")
                    else:
                        messagebox.showerror("エラー", f"サポートされていないファイルバージョンです: {data.get('version')}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")  # デバッグ用
                messagebox.showerror("エラー", f"JSONファイルの解析に失敗しました: {str(e)}")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")  # デバッグ用
                messagebox.showerror("エラー", f"ファイルの読み込み中に予期せぬエラーが発生しました: {str(e)}")

    def save_rules(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                data = {
                    "version": "1.0",
                    "rules": [
                        {
                            "id": i + 1,
                            "items": rule.split(" * "),
                            "description": f"Rule {i + 1}"
                        } for i, rule in enumerate(self.exclusion_rules)
                    ]
                }
                with codecs.open(file_path, 'w', 'utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", "除外ルールを保存しました。")
            except Exception as e:
                print(f"Save error: {str(e)}")  # デバッグ用
                messagebox.showerror("エラー", f"ファイルの保存中にエラーが発生しました: {str(e)}")

    def update_exclusion_listbox(self):
        self.exclusion_listbox.delete(0, tk.END)
        for rule in self.exclusion_rules:
            self.exclusion_listbox.insert(tk.END, rule)

    def is_excluded(self, scenario):
        for rule in self.exclusion_rules:
            items = rule.split(" * ")
            if all(item in scenario for item in items):
                return True
        return False

    def generate_scenarios(self):
        selected = {category: {subcategory: [item for item, var in items.items() if var.get()] 
                               for subcategory, items in subcategories.items()}
                    for category, subcategories in self.selected_items.items()}

        env_scenarios = list(itertools.product(*(selected["環境状況"][subcategory] for subcategory in selected["環境状況"] if selected["環境状況"][subcategory])))
        vehicle_scenarios = list(itertools.product(*(selected["車両状況"][subcategory] for subcategory in selected["車両状況"] if selected["車両状況"][subcategory])))

        for i in self.tree.get_children():
            self.tree.delete(i)

        if not env_scenarios or not vehicle_scenarios:
            self.tree.insert("", "end", values=("シナリオを生成するには、", "各カテゴリから少なくとも1つの項目を選択してください。"))
            return

        total_scenarios = 0
        for i, (env, vehicle) in enumerate(itertools.product(env_scenarios, vehicle_scenarios), 1):
            scenario = env + vehicle
            if not self.is_excluded(scenario):
                env_text = ", ".join(env)
                vehicle_text = ", ".join(vehicle)
                self.tree.insert("", "end", values=(env_text, vehicle_text))
                total_scenarios += 1
            else:
                self.tree.insert("", "end", values=(f"除外: {', '.join(env)}", f"{', '.join(vehicle)}"), tags=('excluded',))

        self.tree.tag_configure('excluded', foreground='gray')
        self.tree.insert("", "end", values=(f"合計 {total_scenarios} 件の有効なシナリオが生成されました。", ""))

root = tk.Tk()
app = ADASScenarioGenerator(root)
root.mainloop()