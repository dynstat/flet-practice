import flet as ft
import asyncio
import time
import random
from collections import deque

class WebSocketVisualizer:
    def __init__(self, max_points=50, window_width=10):
        self.max_points = max_points
        self.window_width = window_width
        self.timestamps = deque(maxlen=max_points)
        self.values = deque(maxlen=max_points)
        self.start_time = time.time()
        self.running = True
        self.points_per_window = 50  # Number of points to show in the window

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
            left_axis=ft.ChartAxis(
                labels_size=40,
                labels_interval=20,
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=40,
                labels_interval=2,
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.WHITE),
            expand=True,
            data_series=[data_series],
            min_x=0,
            max_x=self.window_width,
            border=None,
            bgcolor=ft.colors.TRANSPARENT,
            animate=0,
        )

    def update_chart(self, chart, value):
        current_time = time.time() - self.start_time
        
        # Calculate time step to maintain consistent point density
        if len(self.timestamps) > 0:
            last_time = self.timestamps[-1]
            if current_time - last_time < self.window_width / self.points_per_window:
                return  # Skip update if points would be too dense
        
        self.timestamps.append(current_time)
        self.values.append(value)

        # Update the visible window
        if current_time > self.window_width:
            window_start = current_time - self.window_width
            chart.min_x = window_start
            chart.max_x = current_time
            
            # Filter points to maintain consistent density
            visible_points = [
                (t, v) for t, v in zip(self.timestamps, self.values)
                if t >= window_start
            ]
            
            # Ensure we don't have too many points in the window
            if len(visible_points) > self.points_per_window:
                step = len(visible_points) // self.points_per_window
                visible_points = visible_points[::step]
            
            if visible_points:
                timestamps, values = zip(*visible_points)
                chart.data_series[0].data_points = [
                    ft.LineChartDataPoint(x, y) 
                    for x, y in zip(timestamps, values)
                ]
        else:
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
                await asyncio.sleep(0.01)
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