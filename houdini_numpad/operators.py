import bpy
from bpy import context


class HOUDINI_NUMPAD_OT_editor(bpy.types.Operator):
    """Houdini-style numpad editor - Alt+Middle-click on any number field"""
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
    
    # Last mouse position for debouncing
    _last_sent_value = 0
    _timer = None
    _field_activated = False
    
    def invoke(self, context, event):
        # Only work if mouse is over properties or UI
        if event.mouse_x < 0 or event.mouse_y < 0:
            return {'CANCELLED'}
        
        self._mouse_start_y = event.mouse_y
        self._mouse_start_x = event.mouse_x
        self._selected_step_idx = -1
        self._is_selecting_step = True
        self._last_sent_value = 0
        self._field_activated = False
        
        print("\n=== Houdini Numpad Editor Started ===")
        print("Move MOUSE UP/DOWN to select step size")
        print("Move MOUSE LEFT/RIGHT to change value")
        print("Release MMB to confirm, ESC/RMB to cancel")
        
        # Add modal handler
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.016, window=context.window)
        wm.modal_handler_add(self)
        
        # Simulate LMB click to activate field editing
        try:
            with context.temp_override(
                window=context.window,
                area=context.area,
                region=context.region
            ):
                bpy.ops.ui.copy_data_path_button(full_path=False)
        except:
            pass
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            return {'RUNNING_MODAL'}
        
        elif event.type == 'MOUSEMOVE':
            return self._handle_mouse_move(context, event)
        
        elif event.type == 'MIDDLEMOUSE':
            if event.value == 'RELEASE':
                self._cleanup(context)
                print("=== Numpad Editor Finished ===\n")
                return {'FINISHED'}
        
        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            self._cleanup(context)
            print("=== Numpad Editor Cancelled ===\n")
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}
    
    def _handle_mouse_move(self, context, event):
        current_y = event.mouse_y
        current_x = event.mouse_x
        
        if self._is_selecting_step:
            # Vertical phase - select step
            delta_y = current_y - self._mouse_start_y
            
            # Calculate which step based on vertical movement
            # Positive = down (lower steps), Negative = up (higher steps)
            step_range = len(self._steps)
            # Each step ~30 pixels
            step_pixels = 30
            new_idx = int(delta_y / step_pixels)
            new_idx = max(-step_range//2, min(new_idx, step_range//2))
            
            # Map to actual step index (0-6)
            mapped_idx = (step_range // 2) - new_idx
            mapped_idx = max(0, min(mapped_idx, step_range - 1))
            
            if mapped_idx != self._selected_step_idx:
                self._selected_step_idx = mapped_idx
                step = self._steps[self._selected_step_idx]
                print(f"Step selected: {step:.3g}")
            
            # Check horizontal movement to switch to value edit
            delta_x = abs(current_x - self._mouse_start_x)
            if delta_x > self._step_threshold:
                self._is_selecting_step = False
                self._mouse_start_x = current_x
                print(f"Entering value edit mode with step: {self._steps[self._selected_step_idx]:.3g}")
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
                        try:
                            with context.temp_override(
                                window=context.window,
                                area=context.area,
                                region=context.region
                            ):
                                if direction == 'UP':
                                    bpy.ops.ui.button_increment(mode='UP')
                                else:
                                    bpy.ops.ui.button_increment(mode='DOWN')
                        except:
                            pass
                    
                    self._last_sent_value = wheel_count
                    value_change = wheel_count * step
                    print(f"Value change: {value_change:+.4g} (step: {step:.3g})")
        
        return {'RUNNING_MODAL'}
    
    def _cleanup(self, context):
        """Clean up resources"""
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)


def register():
    bpy.utils.register_class(HOUDINI_NUMPAD_OT_editor)


def unregister():
    bpy.utils.unregister_class(HOUDINI_NUMPAD_OT_editor)
