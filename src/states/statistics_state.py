"""
Statistics viewing state with detailed run history and all-time stats.
"""
import pygame
import math
from datetime import datetime
from src.states.base_state import BaseState
from src.graphics.background import Background
from src.utils.constants import *
from src.utils.analytics import (
    RunStatistics, AllTimeStatistics, format_time, format_number,
    format_distance, get_platform_display_name, get_collectible_display_name,
    get_platform_color, get_collectible_color
)


class StatisticsState(BaseState):
    """
    Statistics viewing state with tabs for:
    - All-time statistics
    - Run history with detailed view
    """
    
    def __init__(self, game):
        """
        Initialize statistics state.
        
        Args:
            game: Reference to main Game instance
        """
        super().__init__(game)
        background_colors = game.customization.get_background_colors()
        self.background = Background(SCREEN_WIDTH, SCREEN_HEIGHT, background_colors)
        self.save_system = game.save_system
        
        # UI state
        self.current_tab = 0  # 0 = All-Time, 1 = Run History
        self.tabs = ["ALL-TIME STATS", "RUN HISTORY"]
        self.tab_rects = []
        
        # Run history state
        self.selected_run_index = -1  # -1 = no run selected (show list)
        self.run_history_scroll = 0
        self.max_visible_runs = 6  # Reduced to prevent overlap with back button
        
        # Button rects
        self.back_button_rect = None
        self.run_item_rects = []
        self.back_to_list_rect = None
        
        # Animation
        self.animation_time = 0.0
        self.mouse_pos = (0, 0)
        
        # Load statistics
        self.all_time_stats = None
        self.run_history = []
    
    def enter(self):
        """Called when entering this state."""
        self.animation_time = 0.0
        self.current_tab = 0
        self.selected_run_index = -1
        self.run_history_scroll = 0
        
        # Load statistics from save system
        self._load_statistics()
        
        print("Statistics screen loaded")
    
    def _load_statistics(self):
        """Load statistics from save system."""
        # Get all-time stats
        all_time_data = self.save_system.get_all_time_stats()
        if all_time_data:
            self.all_time_stats = AllTimeStatistics.from_dict(all_time_data)
        else:
            self.all_time_stats = AllTimeStatistics()
        
        # Get run history
        run_history_data = self.save_system.get_run_history()
        self.run_history = []
        for run_data in run_history_data:
            self.run_history.append(RunStatistics.from_dict(run_data))
    
    def exit(self):
        """Called when exiting this state."""
        pass
    
    def update(self, dt):
        """Update state."""
        self.animation_time += dt
        self.background.update(dt)
        self.mouse_pos = pygame.mouse.get_pos()
    
    def render(self, screen):
        """Render statistics screen."""
        # Use gradient background for run detail view, regular background for other views
        if self.current_tab == 1 and self.selected_run_index >= 0:
            # Gradient background for run detail (matches game over screen)
            self._render_gradient_background(screen)
        else:
            # Regular background for list views
            class SimpleCamera:
                def __init__(self):
                    self.position = pygame.math.Vector2(0, 0)
            
            camera = SimpleCamera()
            self.background.render(screen, camera)
            
            # Semi-transparent overlay for readability
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
        
        # Render title
        self._render_title(screen)
        
        # Render tabs
        self._render_tabs(screen)
        
        # Render content based on current tab
        if self.current_tab == 0:
            self._render_all_time_stats(screen)
        else:
            if self.selected_run_index >= 0:
                self._render_run_detail(screen)
            else:
                self._render_run_history(screen)
        
        # Render back button
        self._render_back_button(screen)
    
    def _render_gradient_background(self, screen):
        """Render a faded gradient background matching game over and title screens."""
        # Create gradient from dark purple at top to dark blue at bottom
        for y in range(SCREEN_HEIGHT):
            # Calculate gradient progress (0 at top, 1 at bottom)
            progress = y / SCREEN_HEIGHT
            
            # Interpolate between colors
            # Top color: dark purple (40, 20, 60)
            # Bottom color: dark blue (20, 30, 80)
            r = int(40 + (20 - 40) * progress)
            g = int(20 + (30 - 20) * progress)
            b = int(60 + (80 - 60) * progress)
            
            # Draw horizontal line
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Add subtle vignette effect (darker at edges)
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Draw radial gradient for vignette
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
        
        for y in range(0, SCREEN_HEIGHT, 4):  # Step by 4 for performance
            for x in range(0, SCREEN_WIDTH, 4):
                dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                alpha = int((dist / max_dist) * 100)  # Max alpha of 100
                pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, 4, 4))
        
        screen.blit(vignette, (0, 0))
    
    def _render_title(self, screen):
        """Render screen title."""
        font = pygame.font.Font(None, 64)
        title = "STATISTICS"
        
        # Shadow
        shadow = font.render(title, True, UI_TEXT_SHADOW)
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 50 + 3))
        screen.blit(shadow, shadow_rect)
        
        # Main text
        text = font.render(title, True, UI_ACCENT)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(text, text_rect)
    
    def _render_tabs(self, screen):
        """Render tab buttons."""
        self.tab_rects = []
        tab_width = 200
        tab_height = 40
        tab_y = 100
        total_width = len(self.tabs) * tab_width + (len(self.tabs) - 1) * 10
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, tab_name in enumerate(self.tabs):
            tab_x = start_x + i * (tab_width + 10)
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, tab_height)
            self.tab_rects.append(tab_rect)
            
            is_selected = (i == self.current_tab)
            is_hovered = tab_rect.collidepoint(self.mouse_pos)
            
            # Draw tab background
            if is_selected:
                color = UI_ACCENT
            elif is_hovered:
                color = (100, 100, 150)
            else:
                color = (60, 60, 80)
            
            pygame.draw.rect(screen, color, tab_rect, border_radius=8)
            pygame.draw.rect(screen, UI_TEXT, tab_rect, 2, border_radius=8)
            
            # Draw tab text
            font = pygame.font.Font(None, 24)
            text_color = (0, 0, 0) if is_selected else UI_TEXT
            text = font.render(tab_name, True, text_color)
            text_rect = text.get_rect(center=tab_rect.center)
            screen.blit(text, text_rect)
    
    def _render_all_time_stats(self, screen):
        """Render all-time statistics."""
        if not self.all_time_stats:
            self._render_no_stats(screen)
            return
        
        stats = self.all_time_stats
        
        # Content area - two column layout
        content_y = 160
        content_x = 50
        col_width = (SCREEN_WIDTH - 100) // 2
        
        # Left Column: General Stats
        self._render_stat_column(screen, content_x, content_y, "GENERAL", [
            ("Total Runs", format_number(stats.total_runs)),
            ("Total Score", format_number(stats.total_score)),
            ("Best Score", format_number(stats.best_score)),
            ("Avg Score", format_number(int(stats.avg_score))),
            ("Total Play Time", format_time(stats.total_play_time)),
            ("Longest Run", format_time(stats.longest_run_time)),
            ("Total Distance", format_distance(stats.total_distance)),
            ("Furthest Run", format_distance(stats.furthest_distance)),
        ])
        
        # Right Column: Jumps & Combos
        self._render_stat_column(screen, content_x + col_width, content_y, "JUMPS & COMBOS", [
            ("Total Jumps", format_number(stats.total_jumps)),
            ("Single Jumps", format_number(stats.total_single_jumps)),
            ("Double Jumps", format_number(stats.total_double_jumps)),
            ("Triple Jumps", format_number(stats.total_triple_jumps)),
            ("Helicopter Uses", format_number(stats.total_helicopter_uses)),
            ("Best Combo", format_number(stats.best_combo)),
            ("Best Multiplier", f"x{stats.best_multiplier}"),
            ("Shields Used", format_number(stats.total_shields_used)),
        ])
        
        # Platform breakdown (below General stats, left side)
        platform_y = content_y + 250  # Below the stat columns
        self._render_breakdown(screen, content_x, platform_y, "PLATFORMS BY TYPE",
                              stats.total_platforms_by_type, get_platform_display_name, get_platform_color)
        
        # Collectible breakdown (below Jumps & Combos, right side)
        self._render_breakdown(screen, content_x + col_width, platform_y, "COLLECTIBLES BY TYPE",
                              stats.total_collectibles_by_type, get_collectible_display_name, get_collectible_color)
    
    def _render_stat_column(self, screen, x, y, title, stats_list):
        """Render a column of statistics."""
        # Title
        title_font = pygame.font.Font(None, 28)
        title_text = title_font.render(title, True, UI_ACCENT)
        screen.blit(title_text, (x, y))
        
        # Stats
        stat_font = pygame.font.Font(None, 22)
        y_offset = y + 35
        
        for label, value in stats_list:
            # Label
            label_text = stat_font.render(f"{label}:", True, (180, 180, 180))
            screen.blit(label_text, (x, y_offset))
            
            # Value
            value_text = stat_font.render(str(value), True, UI_TEXT)
            screen.blit(value_text, (x + 150, y_offset))
            
            y_offset += 26
    
    def _render_breakdown(self, screen, x, y, title, data_dict, name_func, color_func):
        """Render a breakdown of stats by type with colored bars."""
        # Title
        title_font = pygame.font.Font(None, 24)
        title_text = title_font.render(title, True, UI_ACCENT)
        screen.blit(title_text, (x, y))
        
        # Calculate max value for bar scaling
        max_val = max(data_dict.values()) if data_dict.values() else 1
        if max_val == 0:
            max_val = 1
        
        # Render each type
        stat_font = pygame.font.Font(None, 18)
        y_offset = y + 30
        bar_width = 150
        bar_height = 14
        
        for type_name, count in data_dict.items():
            display_name = name_func(type_name)
            color = color_func(type_name)
            
            # Name
            name_text = stat_font.render(display_name, True, UI_TEXT)
            screen.blit(name_text, (x, y_offset))
            
            # Bar background
            bar_x = x + 100
            pygame.draw.rect(screen, (40, 40, 50), (bar_x, y_offset, bar_width, bar_height), border_radius=3)
            
            # Bar fill
            fill_width = int((count / max_val) * bar_width)
            if fill_width > 0:
                pygame.draw.rect(screen, color, (bar_x, y_offset, fill_width, bar_height), border_radius=3)
            
            # Count
            count_text = stat_font.render(format_number(count), True, UI_TEXT)
            screen.blit(count_text, (bar_x + bar_width + 10, y_offset))
            
            y_offset += 20
    
    def _render_run_history(self, screen):
        """Render run history list."""
        if not self.run_history:
            self._render_no_stats(screen, "No runs recorded yet!")
            return
        
        content_y = 160
        content_x = 50
        item_height = 60
        item_width = SCREEN_WIDTH - 100
        item_spacing = 10
        
        # Calculate max visible runs based on available space (stop before back button area)
        back_button_area_top = SCREEN_HEIGHT - 100  # Leave space for back button
        available_height = back_button_area_top - content_y - 30  # 30px buffer for scroll indicator
        self.max_visible_runs = min(6, available_height // (item_height + item_spacing))
        
        self.run_item_rects = []
        
        # Render visible runs
        visible_runs = self.run_history[self.run_history_scroll:self.run_history_scroll + self.max_visible_runs]
        
        for i, run in enumerate(visible_runs):
            actual_index = self.run_history_scroll + i
            item_y = content_y + i * (item_height + item_spacing)
            item_rect = pygame.Rect(content_x, item_y, item_width, item_height)
            self.run_item_rects.append((item_rect, actual_index))
            
            is_hovered = item_rect.collidepoint(self.mouse_pos)
            
            # Background
            bg_color = (80, 80, 100) if is_hovered else (50, 50, 70)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=8)
            pygame.draw.rect(screen, UI_ACCENT if is_hovered else (100, 100, 120), item_rect, 2, border_radius=8)
            
            # Run number
            num_font = pygame.font.Font(None, 32)
            num_text = num_font.render(f"#{actual_index + 1}", True, UI_ACCENT)
            screen.blit(num_text, (content_x + 15, item_y + 15))
            
            # Score
            score_font = pygame.font.Font(None, 36)
            score_text = score_font.render(f"Score: {format_number(run.score)}", True, UI_TEXT)
            screen.blit(score_text, (content_x + 80, item_y + 12))
            
            # Date
            try:
                date_obj = datetime.fromisoformat(run.timestamp)
                date_str = date_obj.strftime("%b %d, %Y %H:%M")
            except (ValueError, AttributeError):
                date_str = "Unknown date"
            
            date_font = pygame.font.Font(None, 20)
            date_text = date_font.render(date_str, True, (150, 150, 150))
            screen.blit(date_text, (content_x + 80, item_y + 40))
            
            # Quick stats
            stats_font = pygame.font.Font(None, 22)
            quick_stats = f"Time: {format_time(run.play_time)} | Platforms: {run.total_platforms_landed} | Combo: {run.max_combo}"
            stats_text = stats_font.render(quick_stats, True, (180, 180, 180))
            screen.blit(stats_text, (content_x + 300, item_y + 20))
            
            # Click hint
            if is_hovered:
                hint_text = stats_font.render("Click for details →", True, UI_ACCENT)
                screen.blit(hint_text, (item_rect.right - 150, item_y + 20))
        
        # Scroll indicators - positioned above back button area
        if self.run_history_scroll > 0:
            self._render_scroll_indicator(screen, content_y - 20, "▲ More above")
        
        if self.run_history_scroll + self.max_visible_runs < len(self.run_history):
            # Position scroll indicator just below the last visible item
            last_item_bottom = content_y + self.max_visible_runs * (item_height + item_spacing)
            self._render_scroll_indicator(screen, last_item_bottom, "▼ More below")
    
    def _render_scroll_indicator(self, screen, y, text):
        """Render scroll indicator."""
        font = pygame.font.Font(None, 20)
        indicator = font.render(text, True, (150, 150, 150))
        indicator_rect = indicator.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(indicator, indicator_rect)
    
    def _render_run_detail(self, screen):
        """Render detailed view of a single run with clean 2-column layout."""
        if self.selected_run_index < 0 or self.selected_run_index >= len(self.run_history):
            return
        
        run = self.run_history[self.selected_run_index]
        
        # Run header with score - centered at top
        header_y = 155
        header_font = pygame.font.Font(None, 36)
        header_text = header_font.render(f"Run #{self.selected_run_index + 1}", True, UI_ACCENT)
        header_rect = header_text.get_rect(centerx=SCREEN_WIDTH // 2)
        screen.blit(header_text, (header_rect.x, header_y))
        
        # Score below header
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Score: {format_number(run.score)}", True, UI_TEXT)
        score_rect = score_text.get_rect(centerx=SCREEN_WIDTH // 2)
        screen.blit(score_text, (score_rect.x, header_y + 35))
        
        # Date below score
        try:
            date_obj = datetime.fromisoformat(run.timestamp)
            date_str = date_obj.strftime("%B %d, %Y at %H:%M")
        except (ValueError, AttributeError):
            date_str = "Unknown date"
        
        date_font = pygame.font.Font(None, 22)
        date_text = date_font.render(date_str, True, (150, 150, 150))
        date_rect = date_text.get_rect(centerx=SCREEN_WIDTH // 2)
        screen.blit(date_text, (date_rect.x, header_y + 75))
        
        # Divider line
        divider_y = header_y + 100
        pygame.draw.line(screen, (100, 100, 120), (80, divider_y), (SCREEN_WIDTH - 80, divider_y), 2)
        
        # Content area - 2 column layout
        content_y = divider_y + 15
        content_x = 60
        col_width = (SCREEN_WIDTH - 120) // 2
        
        # Left Column: General + Platforms
        self._render_run_stat_section(screen, content_x, content_y, "GENERAL", [
            ("Play Time", format_time(run.play_time)),
            ("Distance", format_distance(run.distance_traveled)),
            ("Max Combo", format_number(run.max_combo)),
            ("Max Multiplier", f"x{run.max_multiplier}"),
        ])
        
        # Right Column: Jumps
        self._render_run_stat_section(screen, content_x + col_width, content_y, "JUMPS", [
            ("Total Jumps", format_number(run.total_jumps)),
            ("Single", format_number(run.single_jumps)),
            ("Double", format_number(run.double_jumps)),
            ("Triple", format_number(run.triple_jumps)),
            ("Helicopter", format_number(run.helicopter_uses)),
        ])
        
        # Second row - Platforms and Collectibles breakdowns
        breakdown_y = content_y + 150
        
        # Left: Platforms breakdown
        self._render_compact_breakdown(screen, content_x, breakdown_y, "PLATFORMS",
                                       run.platforms_landed, get_platform_display_name, get_platform_color)
        
        # Right: Collectibles breakdown
        self._render_compact_breakdown(screen, content_x + col_width, breakdown_y, "COLLECTIBLES",
                                       run.collectibles_gathered, get_collectible_display_name, get_collectible_color)
        
        # Back to list button - centered above main back button
        back_width = 180
        back_height = 40
        back_x = SCREEN_WIDTH // 2 - back_width // 2
        back_y = SCREEN_HEIGHT - 140
        self.back_to_list_rect = pygame.Rect(back_x, back_y, back_width, back_height)
        is_back_hovered = self.back_to_list_rect.collidepoint(self.mouse_pos)
        
        self.game.ui_renderer.render_button(
            screen, "← BACK TO LIST",
            back_x, back_y, back_width, back_height,
            is_back_hovered
        )
    
    def _render_run_stat_section(self, screen, x, y, title, stats_list):
        """Render a compact stat section for run detail view."""
        # Title
        title_font = pygame.font.Font(None, 26)
        title_text = title_font.render(title, True, UI_ACCENT)
        screen.blit(title_text, (x, y))
        
        # Stats
        stat_font = pygame.font.Font(None, 20)
        y_offset = y + 28
        
        for label, value in stats_list:
            # Label
            label_text = stat_font.render(f"{label}:", True, (180, 180, 180))
            screen.blit(label_text, (x, y_offset))
            
            # Value
            value_text = stat_font.render(str(value), True, UI_TEXT)
            screen.blit(value_text, (x + 100, y_offset))
            
            y_offset += 22
    
    def _render_compact_breakdown(self, screen, x, y, title, data_dict, name_func, color_func):
        """Render a compact breakdown with small bars for run detail view."""
        # Title with total count
        total = sum(data_dict.values())
        title_font = pygame.font.Font(None, 24)
        title_text = title_font.render(f"{title}: {total}", True, UI_ACCENT)
        screen.blit(title_text, (x, y))
        
        # Calculate max value for bar scaling
        max_val = max(data_dict.values()) if data_dict.values() else 1
        if max_val == 0:
            max_val = 1
        
        # Render each type in a compact list
        stat_font = pygame.font.Font(None, 18)
        y_offset = y + 26
        bar_width = 80
        bar_height = 12
        
        for type_name, count in data_dict.items():
            display_name = name_func(type_name)
            color = color_func(type_name)
            
            # Name
            name_text = stat_font.render(display_name, True, UI_TEXT)
            screen.blit(name_text, (x, y_offset))
            
            # Bar background
            bar_x = x + 85
            pygame.draw.rect(screen, (40, 40, 50), (bar_x, y_offset, bar_width, bar_height), border_radius=2)
            
            # Bar fill
            fill_width = int((count / max_val) * bar_width)
            if fill_width > 0:
                pygame.draw.rect(screen, color, (bar_x, y_offset, fill_width, bar_height), border_radius=2)
            
            # Count
            count_text = stat_font.render(str(count), True, UI_TEXT)
            screen.blit(count_text, (bar_x + bar_width + 5, y_offset))
            
            y_offset += 18
    
    def _render_no_stats(self, screen, message="No statistics available yet!"):
        """Render message when no stats are available."""
        font = pygame.font.Font(None, 32)
        text = font.render(message, True, (150, 150, 150))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
        
        hint_font = pygame.font.Font(None, 24)
        hint = hint_font.render("Play some games to see your statistics!", True, (100, 100, 100))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        screen.blit(hint, hint_rect)
    
    def _render_back_button(self, screen):
        """Render back button."""
        button_width = 150
        button_height = 45
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = SCREEN_HEIGHT - 80
        
        self.back_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        is_hovered = self.back_button_rect.collidepoint(self.mouse_pos)
        
        # Pulse animation when hovered
        pulse = 1.0 + math.sin(self.animation_time * 4) * 0.05 if is_hovered else 1.0
        
        if pulse != 1.0:
            scaled_width = int(button_width * pulse)
            scaled_height = int(button_height * pulse)
            button_x = SCREEN_WIDTH // 2 - scaled_width // 2
            button_y_adjusted = button_y + (button_height - scaled_height) // 2
            self.back_button_rect = pygame.Rect(button_x, button_y_adjusted, scaled_width, scaled_height)
        
        self.game.ui_renderer.render_button(
            screen, "BACK",
            self.back_button_rect.x, self.back_button_rect.y,
            self.back_button_rect.width, self.back_button_rect.height,
            is_hovered
        )
    
    def handle_event(self, event):
        """Handle pygame events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check back button
                if self.back_button_rect and self.back_button_rect.collidepoint(event.pos):
                    self._go_back()
                    return
                
                # Check tabs
                for i, tab_rect in enumerate(self.tab_rects):
                    if tab_rect.collidepoint(event.pos):
                        self.current_tab = i
                        self.selected_run_index = -1
                        self.run_history_scroll = 0
                        return
                
                # Check run history items
                if self.current_tab == 1 and self.selected_run_index < 0:
                    for item_rect, run_index in self.run_item_rects:
                        if item_rect.collidepoint(event.pos):
                            self.selected_run_index = run_index
                            return
                
                # Check back to list button
                if self.back_to_list_rect and self.back_to_list_rect.collidepoint(event.pos):
                    self.selected_run_index = -1
                    return
            
            # Scroll handling
            elif event.button == 4:  # Scroll up
                if self.current_tab == 1 and self.selected_run_index < 0:
                    self.run_history_scroll = max(0, self.run_history_scroll - 1)
            elif event.button == 5:  # Scroll down
                if self.current_tab == 1 and self.selected_run_index < 0:
                    max_scroll = max(0, len(self.run_history) - self.max_visible_runs)
                    self.run_history_scroll = min(max_scroll, self.run_history_scroll + 1)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.selected_run_index >= 0:
                    self.selected_run_index = -1
                else:
                    self._go_back()
            elif event.key == pygame.K_LEFT:
                self.current_tab = max(0, self.current_tab - 1)
                self.selected_run_index = -1
            elif event.key == pygame.K_RIGHT:
                self.current_tab = min(len(self.tabs) - 1, self.current_tab + 1)
                self.selected_run_index = -1
    
    def _go_back(self):
        """Return to title screen."""
        print("Returning to title screen...")
        self.exit()
        
        from src.states.title_state import TitleState
        if not hasattr(self.game, 'title_state'):
            self.game.title_state = TitleState(self.game)
        self.game.current_state = self.game.title_state
        self.game.current_state.enter()