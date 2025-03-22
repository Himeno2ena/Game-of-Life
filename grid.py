# grid.py

import numpy as np

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = np.zeros((height, width), dtype=int)

    def expand_grid(self, direction):
        """根据方向扩展网格"""
        if direction == "up":
            self.cells = np.vstack((np.zeros((1, self.width)), self.cells))
            self.height += 1
        elif direction == "down":
            self.cells = np.vstack((self.cells, np.zeros((1, self.width))))
            self.height += 1
        elif direction == "left":
            self.cells = np.hstack((np.zeros((self.height, 1)), self.cells))
            self.width += 1
        elif direction == "right":
            self.cells = np.hstack((self.cells, np.zeros((self.height, 1))))
            self.width += 1

    def check_and_expand(self):
        """检查是否需要扩展网格，并在需要时扩展"""
        # 检查上边界
        if np.any(self.cells[0, :] == 1):
            self.expand_grid("up")
        # 检查下边界
        if np.any(self.cells[-1, :] == 1):
            self.expand_grid("down")
        # 检查左边界
        if np.any(self.cells[:, 0] == 1):
            self.expand_grid("left")
        # 检查右边界
        if np.any(self.cells[:, -1] == 1):
            self.expand_grid("right")

    def update(self, survive_rule, birth_rule):
        """根据规则更新网格"""
        new_cells = np.zeros((self.height, self.width), dtype=int)
        for y in range(self.height):
            for x in range(self.width):
                # 计算周围活细胞数量
                neighbors = np.sum(self.cells[max(y-1, 0):min(y+2, self.height),
                                  max(x-1, 0):min(x+2, self.width)]) - self.cells[y, x]
                # 应用规则
                if self.cells[y, x] == 1:
                    if neighbors in survive_rule:
                        new_cells[y, x] = 1
                else:
                    if neighbors in birth_rule:
                        new_cells[y, x] = 1
        self.cells = new_cells