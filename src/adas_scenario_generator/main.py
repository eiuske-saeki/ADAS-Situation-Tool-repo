import tkinter as tk
from .gui import ADASScenarioGeneratorGUI
from .category_manager import CategoryManager
from .scenario_generator import ScenarioGenerator
from .exclusion_rules import ExclusionRulesManager

# 残りのコードは変更なし
# 残りのコードは変更なし

def main():
    root = tk.Tk()
    root.geometry("800x600")  # ウィンドウサイズを設定

    category_manager = CategoryManager()
    exclusion_rules_manager = ExclusionRulesManager()
    scenario_generator = ScenarioGenerator(category_manager, exclusion_rules_manager)
    
    app = ADASScenarioGeneratorGUI(root, category_manager, scenario_generator, exclusion_rules_manager)
    
    root.mainloop()

if __name__ == "__main__":
    main()