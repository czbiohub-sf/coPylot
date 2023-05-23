# import ctypes
# import os

# from PyQt5.QtWidgets import QApplication

# from widgets.utils.update_dac import value_converter

# try:
#     from mcculw import ul
#     from mcculw.enums import Status, FunctionType, ScanOptions
#     from props.ao import AnalogOutputProps
# except ValueError:
#     print('Running in the UI demo mode. (from DACscan)')


# class DACscan:
#     def __init__(self, data_list, controlpanel, sampling_rate=int(1e5)):
#         """
#         A class object for DAC scanning a pattern on its own buffer memory.
#         :param data_list: A list of data consisting of all channels
#         :param sampling_rate: sampling rate of the DAC board
#         """
#         self.data_list = data_list
#         self.trans_obj = None  # an obj that performs affine transformation
#         self.num_points_per_ch = len(data_list[0])  # number of points per channel
#         self.controlpanel = controlpanel
#         self.ch_list = controlpanel.channel_list
#         self.num_chans = 2
#         self.total_num_points = self.num_points_per_ch * self.num_chans
#         self.board_num = controlpanel.board_num
#         self.sampling_rate = sampling_rate
#         self.input_range_list = [(0, controlpanel.window1.canvas_width), (0, controlpanel.window1.canvas_height)]
#         self.vout_range = controlpanel.galvo_x_range
#         print(f'num points per ch {self.num_points_per_ch}, total {self.total_num_points}')

#         # configure DAC board
#         self.ao_range = controlpanel.ao_range
#         # Since we are using the SCALEDATA option, the values
#         # added to data_array are the actual voltage values that the device will output
#         self.scan_options = (ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS | ScanOptions.SCALEDATA)
#         self.memhandle = ul.scaled_win_buf_alloc(self.total_num_points)
#         if not self.memhandle:
#             raise ValueError('DAC Failed to allocate memory')
#         self.data_array = None
#         self.count = 0  # the count of processed data points; for resuming from the same point

#     def transfer2dac(self, data_list=None):
#         """
#         Transfer data to DAC board
#         """
#         if data_list is not None:
#             self.data_list = data_list
#             self.num_points_per_ch = len(data_list[0])
#             self.total_num_points = self.num_points_per_ch * self.num_chans
#             self.memhandle = ul.scaled_win_buf_alloc(self.total_num_points)
#             if not self.memhandle:
#                 raise ValueError('DAC Failed to allocate memory')
#         self.data_array = self.memhandle_as_ctypes_array_scaled(self.memhandle)
#         print('starting transferring data...')
#         # apply transformation if calibration has been done.
#         data_trans = self.trans_obj.affineTrans(self.data_list)
#         self.input_range_list = [(0, self.controlpanel.window1.canvas_width), (0, self.controlpanel.window1.canvas_height)]
#         data_list_in_volt = [
#             value_converter(data, inrng, self.vout_range, invert=True) for inrng, data in zip(self.input_range_list, data_trans)
#         ]
#         # reorder along the channel number
#         if self.ch_list[0] > self.ch_list[1]:
#             data_list_in_volt = data_list_in_volt[::-1]
#         data_index = 0
#         for point_num in range(self.num_points_per_ch):
#             for channel_num in range(self.num_chans):
#                 self.data_array[data_index] = data_list_in_volt[channel_num][point_num]
#                 data_index += 1
#         print('DACscan data transfer compoleted.')

#     def start_scan(self):
#         """
#         Start scanning
#         """
#         status, curr_count, curr_index = ul.get_status(self.board_num, FunctionType.AOFUNCTION)
#         if status == Status.RUNNING:
#             raise ValueError('DAC is currently running, please stop it before start a new scan.')
#         else:
#             print('Starting scan...')
#             # Turn on laser if safe mode is True
#             if self.controlpanel.rb_safemode.isChecked():
#                 self.controlpanel.tabmanager.simple_laser.laser_switch_gp.buttons()[self.controlpanel.current_laser].setChecked(True)
#                 self.controlpanel.tabmanager.simple_laser.update_laser_onoff()
#             ul.a_out_scan(
#                 self.board_num, min(self.ch_list[:2]), max(self.ch_list[:2]), self.total_num_points,
#                 self.sampling_rate, self.ao_range, self.memhandle, self.scan_options
#             )
#             print('scan started')

#     def update_values(self, window=None, progressbar=None, laser_escape=True):
#         """
#         Get the status from DAC board
#         """
#         status, curr_count, curr_index = ul.get_status(self.board_num, FunctionType.AOFUNCTION)
#         print(f'self.count: {self.count}')
#         print(f'curr_count: {curr_count}')
#         while status == Status.RUNNING:
#             curr_count += self.count
#             # if stopflag:
#             #     self.stop_scan()
#             # elif pauseflag:
#             #     self.stop_scan()
#             #     self.count = curr_count
#             #     return curr_count, curr_index
#             # else:
#             if window is not None:
#                 window.moveMarker(self.data_list[0][curr_index // 2], self.data_list[1][curr_index // 2], window.marker)
#             if progressbar is not None:
#                 QApplication.processEvents()
#                 progressbar.setValue(curr_count // 2)
#                 if curr_count // 2 >= progressbar.maximum():
#                     self.stop_scan(laser_escape=laser_escape)
#             else:
#                 if curr_count >= self.total_num_points:
#                     self.stop_scan(laser_escape=laser_escape)
#             status, curr_count, curr_index = ul.get_status(self.board_num, FunctionType.AOFUNCTION)

#     def pause_scan(self):
#         # Turn off laser if safe mode is True
#         ul.stop_background(self.board_num, FunctionType.AOFUNCTION)
#         status, curr_count, curr_index = ul.get_status(self.board_num, FunctionType.AOFUNCTION)
#         self.count = curr_count
#         ul.win_buf_free(self.memhandle)
#         if self.controlpanel.rb_safemode.isChecked():
#             [i.setChecked(False) for i in self.controlpanel.tabmanager.simple_laser.laser_switch_gp.buttons()]
#             self.controlpanel.tabmanager.simple_laser.update_laser_onoff()
#         return curr_count, curr_index

#     def free_buffer(self):
#         ul.win_buf_free(self.memhandle)

#     def stop_scan(self, laser_escape=True):
#         ul.stop_background(self.board_num, FunctionType.AOFUNCTION)
#         ul.win_buf_free(self.memhandle)
#         self.count = 0
#         # Turn off laser if safe mode is True
#         if self.controlpanel.rb_safemode.isChecked():
#             [i.setChecked(False) for i in self.controlpanel.tabmanager.simple_laser.laser_switch_gp.buttons()]
#             self.controlpanel.tabmanager.simple_laser.update_laser_onoff(laser_escape=laser_escape)

#     def memhandle_as_ctypes_array_scaled(self, memhandle):
#         return ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_double))

