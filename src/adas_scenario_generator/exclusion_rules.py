import json
import codecs
from tkinter import filedialog, messagebox

class ExclusionRulesManager:
    def __init__(self):
        self.rules = []
        self.rule_descriptions = {}  # 新しく追加：ルールの説明を保持する辞書

    def add_rule(self, item1, item2, description=""):
        rule = f"{item1} * {item2}"
        if rule not in self.rules:
            self.rules.append(rule)
            self.rule_descriptions[rule] = description  # 説明を保存

    def remove_rule(self, rule):
        if rule in self.rules:
            self.rules.remove(rule)
            self.rule_descriptions.pop(rule, None)  # 説明も削除

    def get_rules(self):
        return self.rules

    def get_rule_description(self, rule):
        return self.rule_descriptions.get(rule, "")  # ルールの説明を取得

    def is_excluded(self, scenario):
        scenario_items = scenario["環境状況"] + scenario["車両状況"]
        for rule in self.rules:
            items = rule.split(" * ")
            if all(item in scenario_items for item in items):
                return True
        return False

    def is_excluded_with_rules(self, scenario):
        scenario_items = set(scenario.get("環境状況", []) + scenario.get("車両状況", []))
        applied_rules = []
        for rule in self.rules:
            items = set(rule.split(" * "))
            if items.issubset(scenario_items):
                applied_rules.append(rule)
        return len(applied_rules) > 0, applied_rules

    def load_rules(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with codecs.open(file_path, 'r', 'utf-8-sig') as file:
                    data = json.load(file)
                    if data.get("version") == "1.0":
                        self.rules = []
                        self.rule_descriptions = {}
                        for rule in data["rules"]:
                            rule_str = " * ".join(rule["items"])
                            self.rules.append(rule_str)
                            self.rule_descriptions[rule_str] = rule["description"]
                        messagebox.showinfo("成功", "除外ルールを読み込みました。")
                        return True
                    else:
                        messagebox.showerror("エラー", f"サポートされていないファイルバージョンです: {data.get('version')}")
            except json.JSONDecodeError as e:
                messagebox.showerror("エラー", f"JSONファイルの解析に失敗しました: {str(e)}")
            except Exception as e:
                messagebox.showerror("エラー", f"ファイルの読み込み中に予期せぬエラーが発生しました: {str(e)}")
        return False

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
                            "description": self.rule_descriptions.get(rule, f"Rule {i + 1}")
                        } for i, rule in enumerate(self.rules)
                    ]
                }
                with codecs.open(file_path, 'w', 'utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", "除外ルールを保存しました。")
            except Exception as e:
                messagebox.showerror("エラー", f"ファイルの保存中にエラーが発生しました: {str(e)}")