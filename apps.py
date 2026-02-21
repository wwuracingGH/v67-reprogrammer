# APPS library - renders a single APPS pedal
# Broken out to make it much more user friendly to work with

import math
import dearpygui.dearpygui as dpg

DEADBAND = 10

def quick_remap(a1,a2,b1,b2,t):
    if (t is None): return 0
    if a1 == a2: return 0
    if a1 == None or a2 == None: return 0
    return ((t - a1) / (a2 - a1)) * (b2 - b1) + b1     

class APPS_Display():
    def update_slider(self):
        self.val = dpg.get_value(self.slider)
        
    def update_min(self, newval=None):
        if (newval is None):
            newval = dpg.get_value(self.min_tb)
        else:
            dpg.set_value(self.min_tb, newval)

        self.min = newval
        self.recalc_render()

    def update_max(self, newval=None):
        if (newval is None):
            newval = dpg.get_value(self.max_tb)
        else:
            dpg.set_value(self.max_tb, newval)
        print(newval)
        self.max = newval
        self.recalc_render()
        
    def recalc_render(self):
        new_maxy = quick_remap( 0, 4092, 300, 0, self.max)
        new_miny = quick_remap( 0, 4092, 300, 0, self.min)

        dpg.configure_item(self.min_line, p1=(0, new_miny), p2=(20, new_miny))
        dpg.configure_item(self.max_line, p1=(0, new_maxy), p2=(20, new_maxy))
        
        percentage = math.floor(quick_remap(self.min, self.max, 0, 1000, self.val)) / 10
        if (percentage > 100): percentage = 100.0
        if (percentage < 0): percentage = 0.0
        
        dpg.set_value(self.val_text, str(percentage) + "%")
        
    def update_vals(self, calibrating = False, new_val = None):
        if new_val is not None:
            self.val = new_val
            
        if calibrating:
            self.min = min(self.min, self.val + DEADBAND)
            self.max = max(self.max, self.val - DEADBAND)
            
            dpg.set_value(self.min_tb, self.min)
            dpg.set_value(self.max_tb, self.max)
            
        dpg.set_value(self.slider, self.val)
        self.recalc_render()
   
    def reset_bounds(self):
        self.min = 4096
        self.max = 0 
    
    def get_max(self):
        if dpg.get_value(self.swap_check):
            return self.min
        else:
            return self.max
        
    def get_min(self):
        if dpg.get_value(self.swap_check):
            return self.max
        else:
            return self.min
    
    def __init__(self, name):
        self.min = 0
        self.max = 4096
        self.val = 0
        
        with dpg.group(horizontal=True):
            with dpg.group():
                self.name_text = dpg.add_text(name)
                self.val_text = dpg.add_text("0%")
                self.swap_check = dpg.add_checkbox(label="Reverse Min/Max")
                
                with dpg.group(horizontal=True):
                    self.slider = dpg.add_slider_int(vertical=True, max_value=4092, height=300, width=50, callback = self.update_slider)
                    with dpg.drawlist(pos = [0, 0], width = 70, height = 300):
                        self.min_line = dpg.draw_line((0,300), (30,300), thickness=4)
                        self.max_line = dpg.draw_line((0, 0), (30, 0), thickness=4)
                
                self.max_tb = dpg.add_drag_int(label="MAX", width=60, max_value=4092, callback=self.update_min)
                self.min_tb = dpg.add_drag_int(label="MIN", width=60, max_value=4092, callback=self.update_max) 
