import bpy
from bpy import context


class HOUDINI_NUMPAD_OT_editor(bpy.types.Operator):
    """Houdini-style numpad editor - middle-click on any number field"""
    bl_idname = "wm.houdini_numpad_editor"
    bl_label = "Houdini Numpad Editor"
    bl_options = {'GRAB_CURSOR', 'BLOCKING'}
    
    # State
    _steps = [1000, 100, 10, 1, 0.1, 0.01, 0.001]
    _selected_step_idx = -1
    _is_selecting_step = True
    _mouse_start_y = 0
    _mouse_start_x = 0
    _step_threshold = 15
    
    # Panel UI
    _panel_x = 0
    _panel_y = 0
    _panel_width = 50
    _panel_height = 0
    _draw_handler = None
    _timer = None
    
    # Last mouse position for debouncing
    _last_sent_value = 0
    
    def invoke(self, context, event):
        # Only work if mouse is over properties or UI
        if event.mouse_x < 0 or event.mouse_y < 0:
            return {'CANCELLED'}
        
        self._mouse_start_y = event.mouse_y
        self._mouse_start_x = event.mouse_x
        self._selected_step_idx = -1
        self._is_selecting_step = True
        self._last_sent_value = 0
        
        # Setup panel
        font_size = 11
        line_height = font_size + 4
        self._panel_height = len(self._steps) * line_height
        self._panel_x = event.mouse_x - self._panel_width // 2
        self._panel_y = event.mouse_y - self._panel_height - 10
        
        # Add modal handler
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.016, window=context.window)
        wm.modal_handler_add(self)
        
        # Add draw handler
        for area in context.screen.areas:
            if area.type == 'PROPERTIES':
                self._draw_handler = area.spaces[0].draw_handler_add(
                    self._draw_numpad_ui, (context,), 'POST_PIXEL', 'RUNNING_MODAL'
                )
                break
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            for area in context.screen.areas:
                if area.type in {'PROPERTIES', 'VIEW_3D'}:
                    area.tag_redraw()
            return {'RUNNING_MODAL'}
        
        elif event.type == 'MOUSEMOVE':
            return self._handle_mouse_move(context, event)
        
        elif event.type == 'MIDDLEMOUSE':
            if event.value == 'RELEASE':
                self._cleanup(context)
                return {'FINISHED'}
        
        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            self._cleanup(context)
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
    
    def _handle_mouse_move(self, context, event):
        current_y = event.mouse_y
        current_x = event.mouse_x
        
        if self._is_selecting_step:
            # Vertical phase - select step
            local_y = current_y - self._panel_y
            
            if 0 <= local_y <= self._panel_height:
                line_height = self._panel_height / len(self._steps)
                new_idx = int(local_y / line_height)
                new_idx = max(0, min(new_idx, len(self._steps) - 1))
                
                if new_idx != self._selected_step_idx:
                    self._selected_step_idx = new_idx
            
            # Check horizontal movement to switch to value edit
            delta_x = abs(current_x - self._mouse_start_x)
            if delta_x > self._step_threshold:
                self._is_selecting_step = False
                self._mouse_start_x = current_x
        else:
            # Horizontal phase - change value
            if self._selected_step_idx >= 0:
                delta_x = current_x - self._mouse_start_x
                step = self._steps[self._selected_step_idx]
                
                # Calculate how many wheel events to send
                # Each 2 pixels = 1 step
                wheel_count = int(delta_x / 2)
                
                if wheel_count != self._last_sent_value:
                    # Send wheel events
                    direction = 'UP' if wheel_count > self._last_sent_value else 'DOWN'
                    count = abs(wheel_count - self._last_sent_value)
                    
                    for _ in range(count):
                        # Create a synthetic wheel event
                        with context.temp_override(
                            window=context.window,
                            area=context.area,
                            region=context.region
                        ):
                            # Use operator to send wheel event
                            bpy.ops.wm.scroll_up() if direction == 'UP' else bpy.ops.wm.scroll_down()
                    
                    self._last_sent_value = wheel_count
        
        return {'RUNNING_MODAL'}
    
    def _cleanup(self, context):
        """Clean up resources"""
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)
        
        if self._draw_handler:
            for area in context.screen.areas:
                if area.type == 'PROPERTIES':
                    try:
                        area.spaces[0].draw_handler_remove(self._draw_handler, 'POST_PIXEL')
                    except:
                        pass
    
    def _draw_numpad_ui(self, context):
        """Draw the Houdini-style numpad panel"""
        import gpu
        from gpu_extras.batch import batch_for_shader
        import blf
        
        font_id = 0
        font_size = 11
        line_height = font_size + 4
        
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        
        # Panel background
        vertices_bg = [
            (self._panel_x, self._panel_y),
            (self._panel_x + self._panel_width, self._panel_y),
            (self._panel_x + self._panel_width, self._panel_y + self._panel_height),
            (self._panel_x, self._panel_y + self._panel_height),
        ]
        batch_bg = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices_bg})
        shader.bind()
        shader.uniform_float("color", (0.15, 0.15, 0.15, 0.95))
        batch_bg.draw(shader)
        
        # Draw steps
        blf.size(font_id, font_size)
        
        for i, step in enumerate(self._steps):
            y_pos = self._panel_y + self._panel_height - (i + 1) * line_height
            
            # Highlight selected step
            if i == self._selected_step_idx:
                highlight_color = (0.5, 0.7, 1.0, 0.7) if self._is_selecting_step else (0.4, 0.6, 0.8, 0.9)
                vertices_hl = [
                    (self._panel_x, y_pos),
                    (self._panel_x + self._panel_width, y_pos),
                    (self._panel_x + self._panel_width, y_pos + line_height),
                    (self._panel_x, y_pos + line_height),
                ]
                batch_hl = batch_for_shader(shader, 'TRI_FAN', {"pos": vertices_hl})
                shader.uniform_float("color", highlight_color)
                batch_hl.draw(shader)
            
            # Draw text
            step_str = f"{step:.3g}"
            blf.position(font_id, self._panel_x + 4, y_pos + 2, 0)
            blf.color(font_id, 1.0, 1.0, 1.0, 1.0)
            blf.draw(font_id, step_str)
        
        # Draw border
        vertices_border = [
            (self._panel_x, self._panel_y),
            (self._panel_x + self._panel_width, self._panel_y),
            (self._panel_x + self._panel_width, self._panel_y + self._panel_height),
            (self._panel_x, self._panel_y + self._panel_height),
            (self._panel_x, self._panel_y),
        ]
        batch_border = batch_for_shader(shader, 'LINE_STRIP', {"pos": vertices_border})
        shader.uniform_float("color", (0.5, 0.5, 0.5, 1.0))
        batch_border.draw(shader)


def register():
    bpy.utils.register_class(HOUDINI_NUMPAD_OT_editor)


def unregister():
    bpy.utils.unregister_class(HOUDINI_NUMPAD_OT_editor)
