import itertools

class ScenarioGenerator:
    def __init__(self, category_manager, exclusion_rules_manager):
        self.category_manager = category_manager
        self.exclusion_rules_manager = exclusion_rules_manager

    def generate_scenarios(self, selected):
        env_scenarios = list(itertools.product(*(
            selected["環境状況"][subcategory] 
            for subcategory in selected["環境状況"] 
            if selected["環境状況"][subcategory]
        )))
        
        vehicle_scenarios = list(itertools.product(*(
            selected["車両状況"][subcategory] 
            for subcategory in selected["車両状況"] 
            if selected["車両状況"][subcategory]
        )))

        scenarios = []
        for env, vehicle in itertools.product(env_scenarios, vehicle_scenarios):
            scenario = {
                "環境状況": env,
                "車両状況": vehicle
            }
            scenarios.append(scenario)

        return scenarios

    def filter_scenarios(self, scenarios):
        return [
            scenario for scenario in scenarios 
            if not self.exclusion_rules_manager.is_excluded(scenario)
        ]

    def generate_and_filter_scenarios(self, selected):
        scenarios = self.generate_scenarios(selected)
        return self.filter_scenarios(scenarios)