# game.py

import pygame
import numpy as np
from config import *
from grid import Grid
from rules import apply_rules

# 初始化pygame
pygame.init()

# 设置字体
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 16)

def draw_button(screen, x, y, width, height, label):
    """绘制按钮"""
    pygame.draw.rect(screen, COLOR_BUTTON, (x, y, width, height))
    text = FONT.render(label, True, COLOR_TEXT)
    screen.blit(text, (x + 10, y + 5))

def draw_ui(screen, survive_min, survive_max, birth_min, birth_max, is_running, ui_x):
    """绘制 UI 元素"""
    # 绘制生存规则
    survive_min_text = FONT.render(f"Survive Min: {survive_min}", True, COLOR_TEXT)
    screen.blit(survive_min_text, (ui_x, 10))
    draw_button(screen, ui_x + 120, 10, 30, 30, "+")
    draw_button(screen, ui_x + 160, 10, 30, 30, "-")

    survive_max_text = FONT.render(f"Survive Max: {survive_max}", True, COLOR_TEXT)
    screen.blit(survive_max_text, (ui_x, 50))
    draw_button(screen, ui_x + 120, 50, 30, 30, "+")
    draw_button(screen, ui_x + 160, 50, 30, 30, "-")

    # 绘制繁殖规则
    birth_min_text = FONT.render(f"Birth Min: {birth_min}", True, COLOR_TEXT)
    screen.blit(birth_min_text, (ui_x, 90))
    draw_button(screen, ui_x + 120, 90, 30, 30, "+")
    draw_button(screen, ui_x + 160, 90, 30, 30, "-")

    birth_max_text = FONT.render(f"Birth Max: {birth_max}", True, COLOR_TEXT)
    screen.blit(birth_max_text, (ui_x, 130))
    draw_button(screen, ui_x + 120, 130, 30, 30, "+")
    draw_button(screen, ui_x + 160, 130, 30, 30, "-")

    # 绘制启动/暂停按钮
    button_label = "Pause" if is_running else "Start"
    draw_button(screen, ui_x, 170, 80, 30, button_label)

    # 绘制应用按钮
    draw_button(screen, ui_x + 100, 170, 80, 30, "Apply")

    # 绘制保存按钮
    draw_button(screen, ui_x, 210, 80, 30, "Save")

    # 绘制加载按钮
    draw_button(screen, ui_x + 100, 210, 80, 30, "Load")

    # 绘制清空按钮
    draw_button(screen, ui_x, 250, 180, 30, "Clear")

def draw_slider(screen, x, y, width, height, value, max_value, is_vertical=False):
    """绘制滑块"""
    pygame.draw.rect(screen, COLOR_SLIDER, (x, y, width, height))
    if is_vertical:
        slider_pos = y + (value / max_value) * height
        pygame.draw.rect(screen, COLOR_BUTTON, (x, slider_pos - 5, width, 10))
    else:
        slider_pos = x + (value / max_value) * width
        pygame.draw.rect(screen, COLOR_BUTTON, (slider_pos - 5, y, 10, height))

def save_grid_state(grid, filename="grid_state.npy"):
    """保存当前网格状态到文件"""
    np.save(filename, grid.cells)
    print(f"Grid state saved to {filename}")

def load_grid_state(grid, filename="grid_state.npy"):
    """从文件加载网格状态"""
    try:
        grid.cells = np.load(filename)
        grid.height, grid.width = grid.cells.shape
        print(f"Grid state loaded from {filename}")
    except FileNotFoundError:
        print(f"File {filename} not found.")

def main():
    # 计算窗口大小
    window_width = INIT_GRID_WIDTH * CELL_SIZE + UI_WIDTH
    window_height = INIT_GRID_HEIGHT * CELL_SIZE

    # 创建窗口
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption("Conway's Game of Life")

    # 初始化网格
    grid = Grid(INIT_GRID_WIDTH, INIT_GRID_HEIGHT)
    grid.cells = np.zeros((INIT_GRID_HEIGHT, INIT_GRID_WIDTH), dtype=int)

    # 游戏循环
    running = True
    is_running = False  # 默认不启动
    clock = pygame.time.Clock()

    # 当前规则
    current_survive_rule = [DEFAULT_SURVIVE_MIN, DEFAULT_SURVIVE_MAX]
    current_birth_rule = [DEFAULT_BIRTH_MIN, DEFAULT_BIRTH_MAX]

    # 待应用的规则
    pending_survive_rule = [DEFAULT_SURVIVE_MIN, DEFAULT_SURVIVE_MAX]
    pending_birth_rule = [DEFAULT_BIRTH_MIN, DEFAULT_BIRTH_MAX]

    # 滑块状态
    scroll_x = 0  # 水平滚动偏移
    scroll_y = 0  # 垂直滚动偏移
    is_dragging_horizontal = False  # 是否正在拖动水平滑块
    is_dragging_vertical = False  # 是否正在拖动垂直滑块

    # 鼠标拖动状态
    is_dragging_mouse = False  # 是否正在拖动鼠标设置细胞

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    grid.cells = np.zeros((grid.height, grid.width), dtype=int)  # 重置网格
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                ui_x = window_width - UI_WIDTH

                # 处理网格点击
                if x < window_width - UI_WIDTH and y < window_height:
                    # 计算点击的网格坐标
                    grid_x = (x + scroll_x) // CELL_SIZE
                    grid_y = (y + scroll_y) // CELL_SIZE
                    # 切换细胞状态
                    if 0 <= grid_x < grid.width and 0 <= grid_y < grid.height:
                        grid.cells[grid_y, grid_x] = 1 - grid.cells[grid_y, grid_x]
                        is_dragging_mouse = True  # 开始拖动鼠标

                # 处理生存规则最小值的按钮
                elif ui_x + 120 <= x <= ui_x + 150 and 10 <= y <= 40:  # "+" 按钮
                    pending_survive_rule[0] = min(pending_survive_rule[0] + 1, 8)
                elif ui_x + 160 <= x <= ui_x + 190 and 10 <= y <= 40:  # "-" 按钮
                    pending_survive_rule[0] = max(pending_survive_rule[0] - 1, 0)

                # 处理生存规则最大值的按钮
                elif ui_x + 120 <= x <= ui_x + 150 and 50 <= y <= 80:  # "+" 按钮
                    pending_survive_rule[1] = min(pending_survive_rule[1] + 1, 8)
                elif ui_x + 160 <= x <= ui_x + 190 and 50 <= y <= 80:  # "-" 按钮
                    pending_survive_rule[1] = max(pending_survive_rule[1] - 1, 0)

                # 处理繁殖规则最小值的按钮
                elif ui_x + 120 <= x <= ui_x + 150 and 90 <= y <= 120:  # "+" 按钮
                    pending_birth_rule[0] = min(pending_birth_rule[0] + 1, 8)
                elif ui_x + 160 <= x <= ui_x + 190 and 90 <= y <= 120:  # "-" 按钮
                    pending_birth_rule[0] = max(pending_birth_rule[0] - 1, 0)

                # 处理繁殖规则最大值的按钮
                elif ui_x + 120 <= x <= ui_x + 150 and 130 <= y <= 160:  # "+" 按钮
                    pending_birth_rule[1] = min(pending_birth_rule[1] + 1, 8)
                elif ui_x + 160 <= x <= ui_x + 190 and 130 <= y <= 160:  # "-" 按钮
                    pending_birth_rule[1] = max(pending_birth_rule[1] - 1, 0)

                # 处理启动/暂停按钮
                elif ui_x <= x <= ui_x + 80 and 170 <= y <= 200:
                    is_running = not is_running  # 切换启动/暂停状态

                # 处理应用按钮
                elif ui_x + 100 <= x <= ui_x + 180 and 170 <= y <= 200:
                    current_survive_rule = pending_survive_rule.copy()
                    current_birth_rule = pending_birth_rule.copy()

                # 处理保存按钮
                elif ui_x <= x <= ui_x + 80 and 210 <= y <= 240:
                    save_grid_state(grid)  # 保存当前网格状态

                # 处理加载按钮
                elif ui_x + 100 <= x <= ui_x + 180 and 210 <= y <= 240:
                    load_grid_state(grid)  # 加载网格状态

                # 处理清空按钮
                elif ui_x <= x <= ui_x + 180 and 250 <= y <= 280:
                    grid.cells = np.zeros((grid.height, grid.width), dtype=int)  # 清空网格

                # 处理水平滑块点击
                if 0 <= x <= window_width - UI_WIDTH and window_height - 20 <= y <= window_height:
                    is_dragging_horizontal = True
                # 处理垂直滑块点击
                elif window_width - UI_WIDTH - 20 <= x <= window_width - UI_WIDTH and 0 <= y <= window_height:
                    is_dragging_vertical = True

            elif event.type == pygame.MOUSEBUTTONUP:
                # 停止拖动滑块和鼠标
                is_dragging_horizontal = False
                is_dragging_vertical = False
                is_dragging_mouse = False

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging_horizontal:
                    # 更新水平滚动偏移
                    scroll_x = max(0, min(grid.width * CELL_SIZE - (window_width - UI_WIDTH), scroll_x + event.rel[0]))
                elif is_dragging_vertical:
                    # 更新垂直滚动偏移
                    scroll_y = max(0, min(grid.height * CELL_SIZE - window_height, scroll_y + event.rel[1]))
                elif is_dragging_mouse and event.buttons[0]:  # 左键拖动
                    x, y = event.pos
                    if x < window_width - UI_WIDTH and y < window_height:
                        # 计算点击的网格坐标
                        grid_x = (x + scroll_x) // CELL_SIZE
                        grid_y = (y + scroll_y) // CELL_SIZE
                        # 设置细胞状态为存活
                        if 0 <= grid_x < grid.width and 0 <= grid_y < grid.height:
                            grid.cells[grid_y, grid_x] = 1

            elif event.type == pygame.VIDEORESIZE:
                # 窗口大小变化时调整网格和 UI 的显示区域
                window_width, window_height = event.size
                screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

        # 更新网格
        if is_running:
            apply_rules(grid, current_survive_rule, current_birth_rule)
            grid.check_and_expand()  # 检查并扩展网格

        # 绘制网格
        screen.fill(COLOR_BG)
        visible_width = window_width - UI_WIDTH
        visible_height = window_height

        for y in range(grid.height):
            for x in range(grid.width):
                cell_x = x * CELL_SIZE - scroll_x
                cell_y = y * CELL_SIZE - scroll_y
                if 0 <= cell_x < visible_width and 0 <= cell_y < visible_height:
                    if grid.cells[y, x] == 1:
                        pygame.draw.rect(screen, COLOR_ALIVE,
                                        (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, COLOR_GRID,
                                    (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)

        # 绘制 UI
        ui_x = window_width - UI_WIDTH
        draw_ui(screen, pending_survive_rule[0], pending_survive_rule[1],
                pending_birth_rule[0], pending_birth_rule[1], is_running, ui_x)

        # 绘制水平滑块
        if grid.width * CELL_SIZE > visible_width:
            slider_width = visible_width
            slider_value = scroll_x
            slider_max = grid.width * CELL_SIZE - visible_width
            draw_slider(screen, 0, window_height - 20, slider_width, 20, slider_value, slider_max)

        # 绘制垂直滑块
        if grid.height * CELL_SIZE > visible_height:
            slider_height = visible_height
            slider_value = scroll_y
            slider_max = grid.height * CELL_SIZE - visible_height
            draw_slider(screen, window_width - UI_WIDTH - 20, 0, 20, slider_height, slider_value, slider_max, is_vertical=True)

        pygame.display.flip()
        clock.tick(10)  # 控制帧率

    pygame.quit()

if __name__ == "__main__":
    main()