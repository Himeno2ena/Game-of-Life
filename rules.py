# rules.py

def apply_rules(grid, survive_rule, birth_rule):
    """应用规则更新网格"""
    grid.update(survive_rule, birth_rule)