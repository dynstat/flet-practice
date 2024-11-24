import flet as ft
import asyncio
import time
import random
from collections import deque

class WebSocketVisualizer:
    def __init__(self, max_points=50, window_width=10):
        self.max_points = max_points
        self.window_width = window_width  # Width of the viewing window
        self.timestamps = deque(maxlen=max_points)
        self.values = deque(maxlen=max_points)
        self.start_time = time.time()
        self.running = True

    def create_chart(self):
        data_series = ft.LineChartData(
            color=ft.colors.BLUE,
            stroke_width=2,
            curved=True,
        )
        data_series.data_points = []

        return ft.LineChart(
            width=600,
            height=200,
            horizontal_grid_lines=ft.ChartGridLines(interval=10, color=ft.colors.GREY_400, width=1),
            vertical_grid_lines=ft.ChartGridLines(interval=10, color=ft.colors.GREY_400, width=1),
            left_axis=ft.ChartAxis(
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=40,
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.WHITE),
            expand=True,
            data_series=[data_series],
            min_x=0,  # Initial minimum x value
            max_x=self.window_width,  # Initial maximum x value
        )

    def update_chart(self, chart, value):
        current_time = time.time() - self.start_time
        self.timestamps.append(current_time)
        self.values.append(value)

        # Update the visible window
        if current_time > self.window_width:
            chart.min_x = current_time - self.window_width
            chart.max_x = current_time

        chart.data_series[0].data_points = [
            ft.LineChartDataPoint(x, y) 
            for x, y in zip(self.timestamps, self.values)
        ]

async def main(page: ft.Page):
    page.title = "WebSocket Activity Visualizer"
    page.theme_mode = ft.ThemeMode.DARK
    
    visualizer = WebSocketVisualizer(window_width=10)  # Set window width to 10 units
    chart = visualizer.create_chart()
    
    async def simulate_websocket_activity():
        while visualizer.running:
            try:
                value = random.uniform(0, 100)
                visualizer.update_chart(chart, value)
                page.update()
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"Error in websocket simulation: {e}")
                break

    async def cleanup():
        visualizer.running = False
        if hasattr(page, 'task'):
            page.task.cancel()
            try:
                await page.task
            except asyncio.CancelledError:
                pass

    page.on_close = cleanup
    
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("WebSocket Activity", size=20, weight=ft.FontWeight.BOLD),
                chart
            ]),
            padding=20,
        )
    )
    
    page.task = asyncio.create_task(simulate_websocket_activity())

if __name__ == "__main__":
    ft.app(target=main) 