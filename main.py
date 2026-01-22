from yapper import setUpChannel, tearDownChannel, sendParameterChange, requestParameterValue
from canlib import canlib
import dearpygui.dearpygui as dpg
import struct
import time, apps, bse

#from canlib import canlib, Frame

def save_callback():
    #send all changed can parameters to the vcu, then initiate a flash write
    pass

def process_control_vector_message(display_item, frame_data):
    vector_vals = struct.unpack("<4H", frame_data)
    
    flags = ""
    if((vector_vals[0] & 0x1) > 0):
        flags+= "Negative Torque Request,"
    
    if((vector_vals[0] & (0x1 << 12)) > 0):
        flags+="Brake Sensor Encoder Error,"

    if((vector_vals[0] & (0x1 << 13))> 0):
        flags+="APPS/BSE Plausibility,"

    if((vector_vals[0] & (0x1 << 14) )> 0):
        flags+="APPS Delta,"
        
    if((vector_vals[0] & (0x1 << 15) )> 0):
        flags+="APPS Bounds,"

    control_vector_display_string = "Flags: " + flags + "\nTorque Request: " + str(vector_vals[1]) + "\nRear Brake Pressure: " + str(vector_vals[2]) + "\nFront Brake Pressure: " + str(vector_vals[3])
    dpg.set_value(display_item, control_vector_display_string)

def process_vcu_state_message(display_item, frame_data):
    state_vals = struct.unpack("<BBH", frame_data)
    active_state = state_vals[0]
    fault_counter = state_vals[1] & 0x7F
    APPS_BSE_plaus_latch = state_vals[1] & 0x80
    last_valid_torque_request = state_vals[2]

    states = ["Idle", "Init", "Ready to Drive", "Reset"]
    APPS_BSE_plaus_latch_string = str(APPS_BSE_plaus_latch >0)

    vcu_state_display_string = "Active State: " + states[active_state] + "\nFault Counter: " + str(fault_counter ) + " \nAPPS/BSE Plaus Latch: " + APPS_BSE_plaus_latch_string + " \nLast Valid Torque Request: " + str(last_valid_torque_request)
    dpg.set_value(display_item, vcu_state_display_string)

if __name__ == '__main__':
    dpg.create_context()
    ch = setUpChannel()
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
                with dpg.group():
                    param_id = dpg.add_input_int(label="Parameter ID\nDecimal", min_value=0, max_value=14)
                    param_value = dpg.add_input_int(label="Parameter Value\nDecimal")
                    do_write = dpg.add_checkbox(label="Write to Flash?")
                    param_send_button = dpg.add_button(label="SEND", 
                                                       callback=lambda : sendParameterChange(
                                                           ch, 
                                                           dpg.get_value(param_id),
                                                           dpg.get_value(param_value),
                                                           dpg.get_value(do_write)
                                                       ))
                    value_set_on_vcu = dpg.add_text("Not yet requested", label="Value On VCU")
                    param_request_button = dpg.add_button(label="Request Current Value",
                                                          callback=lambda : requestParameterValue(
                                                              ch,
                                                              dpg.get_value(param_id)
                                                          ))
            with dpg.group():
                dpg.bind_item_font(dpg.add_text("Sensors"), header_font)

                cb = dpg.add_checkbox(label="Calibration")
                vcu_state = dpg.add_text("Not yet recieved", label="VCU State")
                control_vector = dpg.add_text("Not yet recieved", label="Control Vector")

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

        try:
            frame = ch.read()

            match frame.id:
                case 0x101:
                    apps_vals = struct.unpack("<4H", frame.data)
                    APPS1.update_vals(new_val=apps_vals[0])
                    APPS2.update_vals(new_val=apps_vals[1])
                    APPS3.update_vals(new_val=apps_vals[2])
                    APPS4.update_vals(new_val=apps_vals[3])
                case 0x102:
                    bse_vals = struct.unpack("<2H", frame.data)
                    FBSE.update_vals(new_val=bse_vals[0])
                    RBSE.update_vals(new_val=bse_vals[1])
                case 0x103:
                    process_control_vector_message(control_vector, frame.data)
                case 0x104:
                    process_vcu_state_message(vcu_state, frame.data)
                case 0x105:
                    recieved_data = struct.unpack(">IH", frame.data)
                    dpg.set_value(value_set_on_vcu, str(recieved_data[0]) + ", id: " + str(recieved_data[1]))
                case _:
                    pass

        except canlib.CanNoMsg:
            pass 
        except struct.error:
            print("Message Data is the wrong size: " + str(frame.id))

        APPS1.update_vals(dpg.get_value(cb)) 
        APPS2.update_vals(dpg.get_value(cb))
        APPS3.update_vals(dpg.get_value(cb))
        APPS4.update_vals(dpg.get_value(cb))
    
    dpg.destroy_context()   

