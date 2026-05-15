from yapper import setUpChannel, tearDownChannel, sendParameterChange, requestParameterValue
from canlib import canlib
import dearpygui.dearpygui as dpg
import struct
import time, apps, bse

#from canlib import canlib, Frame

def req_all_values(ch):
    requestParameterValue(ch, 0)
    time.sleep(0.01)
    requestParameterValue(ch, 1)
    time.sleep(0.01)
    requestParameterValue(ch, 2)
    time.sleep(0.01)
    requestParameterValue(ch, 3)
    time.sleep(0.01)
    requestParameterValue(ch, 4)
    time.sleep(0.01)
    requestParameterValue(ch, 5)
    time.sleep(0.01)
    requestParameterValue(ch, 6)
    time.sleep(0.01)
    requestParameterValue(ch, 7)
    time.sleep(0.01)
    requestParameterValue(ch, 8)
    time.sleep(0.01)
    requestParameterValue(ch, 9)
    time.sleep(0.01)
    requestParameterValue(ch, 10)
    time.sleep(0.01)
    requestParameterValue(ch, 12)
    time.sleep(0.01)
    requestParameterValue(ch, 13)
    time.sleep(0.01)
    requestParameterValue(ch, 14)
    time.sleep(0.01)

def save_callback(ch, parameters:dict):
    for it, (id, value) in enumerate(parameters.items()):
        if (it == len(parameters.items()) - 1):
            print("sending write command.")
            sendParameterChange(ch, id, value, True)
            time.sleep(0.01)
        else:
            sendParameterChange(ch, id, value)
    req_all_values(ch)

def process_control_vector_message(display_item, frame_data):
    vector_vals = struct.unpack("<4H", frame_data)
    
    flags = ""
    if((vector_vals[0] & 0x1) > 0):
        flags+= "Negative Torque Request,"
    
    if((vector_vals[0] & (0x1 << 12)) > 0):
        flags+="Brake Sensor Encoder Error,"

    if((vector_vals[0] & (0x1 << 13)) > 0):
        flags+="APPS/BSE Plausibility,"

    if((vector_vals[0] & (0x1 << 14) ) > 0):
        flags+="APPS Delta,"
        
    if((vector_vals[0] & (0x1 << 15) ) > 0):
        flags+="APPS Bounds,"

    control_vector_display_string = "Flags: " + flags + "\nTorque Request: " + str(vector_vals[1]) + "\nRear Brake Pressure: " + str(float(int(10 * vector_vals[2] * (brake_bias / 65535))) / 10) + "\nFront Brake Pressure: " + str(float(int(10 * vector_vals[2] * ((65535 - brake_bias) / 65535))) / 10)
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


class get_vals:
    def __init__(self, mt, hbt):
        self.mt = mt
        self.hbt = hbt

    def get_mt(self) -> int:
        return dpg.get_value(self.mt)

    def get_hbt(self) -> int:
        return dpg.get_value(self.hbt)


if __name__ == '__main__':
    debugging = False
    dpg.create_context()
    ch = None if debugging else setUpChannel()
    with dpg.font_registry():
        default_font = dpg.add_font("ComicMono-Bold.ttf", 20)
        header_font = dpg.add_font("ComicMono-Bold.ttf", 30)
        title_font = dpg.add_font("ComicMono-Bold.ttf", 45)

    brake_bias = 0
    prog_tabs = []
    
    with dpg.window(label="MainWindow") as main_window:
        dpg.bind_font(default_font)
        title = dpg.add_text("V67 VCU Reprogrammer")
        dpg.bind_item_font(title, title_font)
        dpg.add_separator()
        
        param_send_button = dpg.add_button(label="Write to VCU Flash", 
                                           callback=lambda: save_callback(ch,{
                                                0:APPS1.get_min(),
                                                1:APPS1.get_max(),
                                                2:APPS2.get_min(),
                                                3:APPS2.get_max(),
                                                4:APPS3.get_min(),
                                                5:APPS3.get_max(),
                                                6:APPS4.get_min(),
                                                7:APPS4.get_max(),
                                                #8:FBSE.get_min(),
                                                #9:FBSE.get_max(),
                                                #10:brake_bias,
                                                12:vals_getter.get_mt(),
                                                13:vals_getter.get_hbt(),
                                            }))
        with dpg.group(horizontal=True):
            with dpg.group(width=200):
                with dpg.group():
                    prog_tabs = [
                        dpg.add_button(label="Sensors"), 
                        dpg.add_button(label="CM200"),
                        dpg.add_button(label="BMS") 
                    ]
            with dpg.group():
                dpg.bind_item_font(dpg.add_text("Sensors"), header_font)

                cb = dpg.add_checkbox(label="Calibration")
                vcu_state = dpg.add_text("Not yet recieved", label="VCU State")
                control_vector = dpg.add_text("Not yet recieved", label="Control Vector")

                brake_bias_txt = dpg.add_text("Brake Bias: ")
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

                with dpg.group(horizontal=True):                 
                    max_torque = dpg.add_drag_int(label="Max Torque", min_value=0, max_value=2300, width=80)
                    current_max_torque_on_vcu = dpg.add_text("Not yet recieved")
                with dpg.group(horizontal=True):
                    hard_braking_threshold = dpg.add_drag_int(label="Hard Braking Threshold", min_value=1, max_value=300, width=80)
                    current_hard_braking_threshold_on_vcu = dpg.add_text("Not yet recieved")
                    vals_getter = get_vals(max_torque, hard_braking_threshold)

    dpg.create_viewport(title='V67-reprogrammer', min_width=1000, min_height=700)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    if not debugging:
        req_all_values(ch)

    dpg.set_primary_window(main_window, True)

    last_render_time = time.time()
    while dpg.is_dearpygui_running():
        if time.time() > last_render_time + 0.008:
            dpg.render_dearpygui_frame()
            last_render_time = time.time()
        try:
            if debugging: continue
            frame = ch.read()

            if frame.id <= 0x107 or frame.id >= 0x101:
                match frame.id:
                    case 0x101:
                        apps_vals = struct.unpack("<4H", frame.data)
                        APPS1.update_vals(new_val=apps_vals[0])
                        APPS2.update_vals(new_val=apps_vals[1])
                        APPS3.update_vals(new_val=apps_vals[2])
                        APPS4.update_vals(new_val=apps_vals[3])
                        print(apps_vals)
                    case 0x102:
                        bse_vals = struct.unpack("<2H", frame.data)
                        FBSE.update_vals(new_val=bse_vals[0])
                        RBSE.update_vals(new_val=bse_vals[1])
                        #if (dpg.get_value(cb)):
                        #    fbse_fr = (bse_vals[0] - FBSE.min) / ((FBSE.max - FBSE.min) + 1)
                        #    rbse_fr = (bse_vals[0] - RBSE.min) / ((FBSE.max - FBSE.min) + 1)
                        #    brake_bias_fr = fbse_fr / (rbse_fr + fbse_fr)
                        #    brake_bias = brake_bias_fr * 65536
                        #    dpg.set_value(brake_bias_txt, "Brake Bias: " + str(round((brake_bias*1000)/65536)/10) + "%")
                    case 0x103:
                        process_control_vector_message(control_vector, frame.data)
                    case 0x104:
                        process_vcu_state_message(vcu_state, frame.data)
                    case 0x105:
                        recieved_data = struct.unpack("<IH", frame.data)
                        match recieved_data[1]:
                            case 8:
                                FBSE.update_min(recieved_data[0])
                                RBSE.update_min(recieved_data[0])
                            case 9:
                                FBSE.update_max(recieved_data[0])
                                RBSE.update_max(recieved_data[0])
                            case 10:
                                brake_bias = recieved_data[0]
                                dpg.set_value(brake_bias_txt, "Brake Bias: " + str(round((brake_bias*1000)/65536)/10) + "%")
                            case 12:
                                dpg.set_value(max_torque, recieved_data[0])
                                dpg.set_value(current_max_torque_on_vcu, recieved_data[0])
                            case 13:
                                dpg.set_value(current_hard_braking_threshold_on_vcu, recieved_data[0])
                                dpg.set_value(hard_braking_threshold, recieved_data[0])
                            case 11:
                                dpg.set_value(title, "Nicole sent me parameter 11 which does not exist.")
                            case 0: 
                                APPS1.update_min(recieved_data[0])
                            case 1: 
                                APPS1.update_max(recieved_data[0])
                                if APPS1.get_min() < APPS1.get_max(): 
                                    APPS1.reversed = True
                            case 2: 
                                APPS2.update_min(recieved_data[0])
                            case 3: 
                                APPS2.update_max(recieved_data[0])
                                if APPS2.get_min() < APPS2.get_max(): 
                                    APPS1.reversed = True
                            case 4: 
                                APPS3.update_min(recieved_data[0])
                            case 5: 
                                APPS3.update_max(recieved_data[0])
                                if APPS3.get_min() < APPS3.get_max(): 
                                    APPS1.reversed = True
                            case 6: 
                                APPS4.update_min(recieved_data[0])
                            case 7: 
                                APPS4.update_max(recieved_data[0])
                                if APPS4.get_min() < APPS4.get_max(): 
                                    APPS1.reversed = True
                            case _:
                                pass
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

