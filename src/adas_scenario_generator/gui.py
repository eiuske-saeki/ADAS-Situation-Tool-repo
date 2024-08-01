import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

class ADASScenarioGeneratorGUI:
    def __init__(self, master, category_manager, scenario_generator, exclusion_rules_manager):
        self.master = master
        self.category_manager = category_manager
        self.scenario_generator = scenario_generator
        self.exclusion_rules_manager = exclusion_rules_manager
        
        self.master.title("ADAS Scenario Generator")
        
        self.selected_items = {}
        self.update_selected_items()
        
        self.create_gui()

    def update_selected_items(self):
        self.selected_items = {category: {subcategory: {item: tk.BooleanVar() for item in items} 
                               for subcategory, items in subcategories.items()} 
                               for category, subcategories in self.category_manager.categories.items()}

    def create_gui(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_category_tabs()
        self.create_exclusion_tab()
        self.create_execution_tab()
        self.create_category_management_tab()

    def create_category_tabs(self):
        for category, subcategories in self.category_manager.categories.items():
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

        self.exclusion_description = tk.Text(exclusion_frame, height=3, width=50)
        self.exclusion_description.pack(pady=5)

        add_button = ttk.Button(exclusion_frame, text="除外ルール追加", command=self.add_exclusion_rule)
        add_button.pack(pady=5)

        # Treeviewを使用して除外ルールと理由を表示
        self.exclusion_tree = ttk.Treeview(exclusion_frame, columns=('rule', 'reason'), show='headings', height=10)
        self.exclusion_tree.heading('rule', text='除外ルール')
        self.exclusion_tree.heading('reason', text='理由')
        self.exclusion_tree.column('rule', width=200)
        self.exclusion_tree.column('reason', width=300)
        self.exclusion_tree.pack(pady=5, fill=tk.BOTH, expand=True)

        # スクロールバーの追加
        scrollbar = ttk.Scrollbar(exclusion_frame, orient="vertical", command=self.exclusion_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.exclusion_tree.configure(yscrollcommand=scrollbar.set)

        self.exclusion_tree.bind('<<TreeviewSelect>>', self.on_rule_select)

        remove_button = ttk.Button(exclusion_frame, text="選択したルールを削除", command=self.remove_exclusion_rule)
        remove_button.pack(pady=5)

        file_frame = ttk.Frame(exclusion_frame)
        file_frame.pack(pady=10)

        load_button = ttk.Button(file_frame, text="ルールを読み込む", command=self.load_exclusion_rules)
        load_button.pack(side=tk.LEFT, padx=5)

        save_button = ttk.Button(file_frame, text="ルールを保存", command=self.exclusion_rules_manager.save_rules)
        save_button.pack(side=tk.LEFT, padx=5)

        self.update_exclusion_listbox()

    def create_category_management_tab(self):
        management_frame = ttk.Frame(self.notebook)
        self.notebook.add(management_frame, text="カテゴリ管理")

        file_button = ttk.Button(management_frame, text="カテゴリファイル選択", command=self.category_manager.select_category_file)
        file_button.pack(pady=10)

        category_frame = ttk.Frame(management_frame)
        category_frame.pack(pady=10)
        ttk.Label(category_frame, text="カテゴリ:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(category_frame, textvariable=self.category_var, values=list(self.category_manager.categories.keys()))
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
        ttk.Button(button_frame, text="カテゴリ削除", command=self.remove_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="サブカテゴリ追加", command=self.add_subcategory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="サブカテゴリ削除", command=self.remove_subcategory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="項目追加", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="項目削除", command=self.remove_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="変更を保存", command=self.category_manager.save_categories).pack(side=tk.LEFT, padx=5)

    def on_category_selected(self, event):
        category = self.category_var.get()
        self.subcategory_combobox['values'] = list(self.category_manager.categories[category].keys())
        self.subcategory_combobox.set('')
        self.items_listbox.delete(0, tk.END)

    def on_subcategory_selected(self, event):
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        self.items_listbox.delete(0, tk.END)
        for item in self.category_manager.categories[category][subcategory]:
            self.items_listbox.insert(tk.END, item)

    def add_category(self):
        new_category = simpledialog.askstring("カテゴリ追加", "新しいカテゴリ名を入力してください:")
        if new_category and new_category not in self.category_manager.categories:
            self.category_manager.add_category(new_category)
            self.update_gui()

    def add_subcategory(self):
        category = self.category_var.get()
        if not category:
            messagebox.showerror("エラー", "カテゴリを選択してください")
            return
        new_subcategory = simpledialog.askstring("サブカテゴリ追加", "新しいサブカテゴリ名を入力してください:")
        if new_subcategory and new_subcategory not in self.category_manager.categories[category]:
            self.category_manager.add_subcategory(category, new_subcategory)
            self.update_gui()

    def add_item(self):
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        if not category or not subcategory:
            messagebox.showerror("エラー", "カテゴリとサブカテゴリを選択してください")
            return
        new_item = simpledialog.askstring("項目追加", "新しい項目名を入力してください:")
        if new_item and new_item not in self.category_manager.categories[category][subcategory]:
            self.category_manager.add_item(category, subcategory, new_item)
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
        self.category_manager.remove_item(category, subcategory, item)
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
        return self.category_manager.get_all_items()

    def add_exclusion_rule(self):
        item1 = self.exclusion_entry1.get()
        item2 = self.exclusion_entry2.get()
        description = self.exclusion_description.get("1.0", tk.END).strip()
        
        if item1 and item2 and item1 != item2:
            # 既存のルールと重複していないかチェック
            existing_rules = self.exclusion_rules_manager.get_rules()
            rule = f"{item1} * {item2}"
            reverse_rule = f"{item2} * {item1}"
            
            if rule in existing_rules or reverse_rule in existing_rules:
                messagebox.showwarning("重複", "この組み合わせの除外ルールは既に存在します。")
            else:
                self.exclusion_rules_manager.add_rule(item1, item2, description)
                self.update_exclusion_listbox()
                self.exclusion_description.delete("1.0", tk.END)  # Clear the description field
                messagebox.showinfo("追加成功", "新しい除外ルールが追加されました。")
        else:
            messagebox.showerror("エラー", "2つの異なる項目を選択してください。")

    def remove_exclusion_rule(self):
        selection = self.exclusion_tree.selection()
        if selection:
            item = self.exclusion_tree.item(selection[0])
            rule = item['values'][0]
            self.exclusion_rules_manager.remove_rule(rule)
            self.update_exclusion_listbox()

    def load_exclusion_rules(self):
        if self.exclusion_rules_manager.load_rules():
            self.update_exclusion_listbox()

    def update_exclusion_listbox(self):
        # Treeviewの内容をクリア
        for i in self.exclusion_tree.get_children():
            self.exclusion_tree.delete(i)
        
        # 除外ルールと理由を追加
        for rule in self.exclusion_rules_manager.get_rules():
            description = self.exclusion_rules_manager.get_rule_description(rule)
            self.exclusion_tree.insert('', 'end', values=(rule, description))

    def on_rule_select(self, event):
        selection = self.exclusion_tree.selection()
        if selection:
            item = self.exclusion_tree.item(selection[0])
            rule = item['values'][0]
            description = item['values'][1]
            # 選択されたルールの詳細を表示する場合はここに処理を追加

    def remove_category(self):
        category = self.category_var.get()
        if not category:
            messagebox.showerror("エラー", "削除するカテゴリを選択してください")
            return
        if messagebox.askyesno("確認", f"カテゴリ '{category}' を削除してもよろしいですか？"):
            self.category_manager.remove_category(category)
            self.update_gui()

    def remove_subcategory(self):
        category = self.category_var.get()
        subcategory = self.subcategory_var.get()
        if not category or not subcategory:
            messagebox.showerror("エラー", "削除するサブカテゴリを選択してください")
            return
        if messagebox.askyesno("確認", f"サブカテゴリ '{subcategory}' を削除してもよろしいですか？"):
            self.category_manager.remove_subcategory(category, subcategory)
            self.update_gui()
    def create_execution_tab(self):
        execution_frame = ttk.Frame(self.notebook)
        self.notebook.add(execution_frame, text="実行")

        self.generate_button = ttk.Button(execution_frame, text="シナリオ生成", command=self.generate_scenarios)
        self.generate_button.pack(pady=20)

        columns = tuple(self.category_manager.categories.keys())
        self.tree = ttk.Treeview(execution_frame, columns=columns, show="headings")
        for category in columns:
            self.tree.heading(category, text=category)
            self.tree.column(category, width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(execution_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
    
    def generate_scenarios(self):
        selected = {category: {subcategory: [item for item, var in items.items() if var.get()] 
                            for subcategory, items in subcategories.items() if any(var.get() for var in items.values())}
                    for category, subcategories in self.selected_items.items()}

        scenarios = self.scenario_generator.generate_scenarios(selected)

        for i in self.tree.get_children():
            self.tree.delete(i)

        if not any(selected.values()):
            self.tree.insert("", "end", values=("シナリオを生成するには、", "各カテゴリから少なくとも1つの項目を選択してください。"))
            return

        total_scenarios = 0
        for scenario in scenarios:
            if not self.exclusion_rules_manager.is_excluded(scenario):
                scenario_values = []
                for category in self.category_manager.categories.keys():
                    if category in scenario:
                        scenario_values.append(", ".join(scenario[category]))
                    else:
                        scenario_values.append("")
                self.tree.insert("", "end", values=tuple(scenario_values))
                total_scenarios += 1
            else:
                excluded_values = [f"除外: {', '.join(scenario.get(category, []))}" for category in self.category_manager.categories.keys()]
                self.tree.insert("", "end", values=tuple(excluded_values), tags=('excluded',))

        self.tree.tag_configure('excluded', foreground='gray')
        self.tree.insert("", "end", values=(f"合計 {total_scenarios} 件の有効なシナリオが生成されました。", ""))    