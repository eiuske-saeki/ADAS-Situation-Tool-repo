import os
import json
import codecs
from tkinter import messagebox, filedialog

class CategoryManager:
    def __init__(self):
        self.categories = {}
        self.category_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'categories.json')
        self.load_categories()

    def load_categories(self):
        if not os.path.exists(self.category_file):
            messagebox.showinfo("情報", "categories.jsonファイルが見つかりません。ファイルを選択してください。")
            self.select_category_file()
            return

        try:
            with codecs.open(self.category_file, 'r', 'utf-8') as file:
                self.categories = json.load(file)
            print(f"Successfully loaded categories from {self.category_file}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            messagebox.showerror("エラー", f"'{self.category_file}' の解析に失敗しました。JSONフォーマットを確認してください。")
            self.select_category_file()
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            messagebox.showerror("エラー", f"予期せぬエラーが発生しました: {str(e)}")
            self.select_category_file()

    def select_category_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.category_file = file_path
            self.load_categories()
        else:
            if not self.categories:
                messagebox.showwarning("警告", "カテゴリファイルが選択されていません。デフォルトの空のカテゴリを使用します。")
                self.categories = {"環境状況": {}, "車両状況": {}}


    def save_categories(self):
        try:
            with codecs.open(self.category_file, 'w', 'utf-8') as file:
                json.dump(self.categories, file, ensure_ascii=False, indent=2)
            messagebox.showinfo("保存完了", f"カテゴリ情報を '{self.category_file}' に保存しました。")
        except Exception as e:
            messagebox.showerror("エラー", f"カテゴリの保存中にエラーが発生しました: {str(e)}")

    def add_category(self, category):
        if category not in self.categories:
            self.categories[category] = {}

    def add_subcategory(self, category, subcategory):
        if category in self.categories and subcategory not in self.categories[category]:
            self.categories[category][subcategory] = []

    def add_item(self, category, subcategory, item):
        if category in self.categories and subcategory in self.categories[category]:
            if item not in self.categories[category][subcategory]:
                self.categories[category][subcategory].append(item)

    def remove_item(self, category, subcategory, item):
        if category in self.categories and subcategory in self.categories[category]:
            if item in self.categories[category][subcategory]:
                self.categories[category][subcategory].remove(item)

    def get_all_items(self):
        return [item for category in self.categories.values() 
                for subcategory in category.values() 
                for item in subcategory]

    def get_categories(self):
        return list(self.categories.keys())

    def get_subcategories(self, category):
        return list(self.categories[category].keys()) if category in self.categories else []

    def get_items(self, category, subcategory):
        return self.categories[category][subcategory] if category in self.categories and subcategory in self.categories[category] else []
    
    def remove_category(self, category):
        if category in self.categories:
            del self.categories[category]

    def remove_subcategory(self, category, subcategory):
        if category in self.categories and subcategory in self.categories[category]:
            del self.categories[category][subcategory]