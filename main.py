#from yapper import setUpChannel, tearDownChannel
import dearpygui.dearpygui as dpg
import time, apps, bse

#from canlib import canlib, Frame

def save_callback():
    #send all changed can parameters to the vcu, then initiate a flash write
    pass

if __name__ == '__main__':
    dpg.create_context()

    with dpg.font_registry():
        default_font = dpg.add_font("ComicMono-Bold.ttf", 20)
        header_font = dpg.add_font("ComicMono-Bold.ttf", 30)
        title_font = dpg.add_font("ComicMono-Bold.ttf", 45)

    with dpg.window(label="MainWindow") as main_window:
        dpg.bind_font(default_font)
        dpg.bind_item_font(dpg.add_text("V67 VCU Reprogrammer"), title_font)
        dpg.add_separator()
        with dpg.group(horizontal=True):
            with dpg.group(width=200):
                dpg.add_button()
            with dpg.group():
                dpg.bind_item_font(dpg.add_text("Sensors"), header_font)

                cb = dpg.add_checkbox(label="Calibration")

                with dpg.group(horizontal=True):
                    APPS1 = apps.APPS_Display("APPS 1")
                    APPS2 = apps.APPS_Display("APPS 2")
                    APPS3 = apps.APPS_Display("APPS 3")
                    APPS4 = apps.APPS_Display("APPS 4")
                    FBSE  = bse.BSE_Display("FBSE")
                    RBSE  = bse.BSE_Display("RBSE")

                def callback():
                    if not dpg.get_value(cb): return
                    APPS1.reset_bounds()
                    APPS2.reset_bounds()
                    APPS3.reset_bounds()
                    APPS4.reset_bounds()

                dpg.set_item_callback(cb, callback=callback)

    dpg.create_viewport(title='Hello', min_width=1000, min_height=700)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    
    dpg.set_primary_window(main_window, True)
    
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        # TODO: get vals from can
        APPS1.update_vals(dpg.get_value(cb)) 
        APPS2.update_vals(dpg.get_value(cb))
        APPS3.update_vals(dpg.get_value(cb))
        APPS4.update_vals(dpg.get_value(cb))
    
    dpg.destroy_context()   

