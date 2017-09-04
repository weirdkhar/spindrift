'''
Code for the gui of the processing of aerosol gear

Written by Ruhi Humphries
2017

Useful documentation:
    http://www.tkdocs.com/tutorial/widgets.html
    http://pyinmyeye.blogspot.com.au/2012/08/tkinter-combobox-demo.html
    http://www.python-course.eu/tkinter_layout_management.php
'''

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import CPC_TSI
import ToolTip
from gui_base import GenericBaseGui

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import atmoscripts

class cpc_processing(GenericBaseGui):

    def loadAndProcess_Multithread(self,
                                   output_filetype,
                                   output_time_res,
                                   concat_file_freq,
                                   mask_df,
                                   flow_cal_df):

        # Call processing function
        CPC_TSI.LoadAndProcess(cn_raw_path=self.raw_path,
                               cn_output_path=self.output_path,
                               cn_output_filetype=output_filetype,
                               filename_base='CN3',
                               force_reload_from_source=self.forceReload.get(),
                               output_time_resolution=output_time_res,
                               concat_file_frequency=concat_file_freq,
                               input_filelist=list(self.files_raw),
                               NeedsTZCorrection=self.correct4TZ.get(),
                               CurrentTZ=float(self.tb_TZcurrent.get()),
                               OutputTZ=float(self.tb_TZdesired.get()),
                               mask_period_timestamp_df=mask_df,
                               flow_cal_df=flow_cal_df,
                               CN_flow_setpt=float(self.tb_flow_rate_set.get())*1000,
                               CN_flow_polyDeg=float(self.tb_flow_rate_fit.get()),
                               plot_each_step=self.plotresults.get(),
                               gui_mode=True,
                               gui_mainloop=self.w_status)

        self.finished_window()


#-----------------------------------------------------------
# GUI Functionality
#-----------------------------------------------------------
    def grey_press_input(self):
        '''
        Disables input into the pressure fields if the checkbox isn't ticked.
        '''
        self.correct4TZ
        if self.correct4TZ.get() == 0:
            self.tb_TZcurrent.configure(state='disabled')
            self.tb_TZdesired.configure(state='disabled')
        elif self.correct4TZ.get() == 1:
            self.tb_TZcurrent.configure(state='normal')
            self.tb_TZdesired.configure(state='normal')

#-----------------------------------------------------------
# GUI Widgets
#-----------------------------------------------------------
    def __init__(self, isapp=True):
        ttk.Frame.__init__(self, name='cpcprocessing')
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.master.title('TSI CPC Processing')
        self.master.geometry('1760x1160')    # original 880x560
        self.isapp = isapp
        self.build_widgets()

    def create_output_frame(self, mainFrame):
        """
        Draw the gui frame for data output options
        KJ - new version using grid
        """
        # create output path dialog
        self.f2 = tk.LabelFrame(mainFrame, text='Output data')
        self.b_output = tk.Button(self.f2,
                                  text='Change output directory',
                                  command=self.output_path_dialog)
        self.t_outputPath = tk.Entry(self.f2)

         # Create output filetype combobox
        filetypes = ['netcdf', 'hdf', 'csv']
        self.lb1 = tk.Label(self.f2, text='Select output filetype')
        self.cb_output_filetype = ttk.Combobox(self.f2,
                                               values=filetypes,
                                               state='readonly',
                                               width=10)
        self.cb_output_filetype.current(1)  # set selection
        self.cb_output_filetype.bind('<<ComboboxSelected>>', self.launch_netcdf_input)

        file_freq=['Single file', 'Daily files', 'Weekly files', 'Monthly files']
        self.lb2 = tk.Label(self.f2, text='Select output frequency')
        self.cb_file_freq = ttk.Combobox(self.f2,
                                         values=file_freq,
                                         state='readonly',
                                         width=15)
        self.cb_file_freq.current(2)  # set selection

        self.f21 = tk.LabelFrame(self.f2, text='Output time resolution')

         # Declare checkbox variables - KJ - Change this to combo box
        self.output_1s = tk.IntVar()
        self.output_5s = tk.IntVar()
        self.output_10s = tk.IntVar()
        self.output_15s = tk.IntVar()
        self.output_30s = tk.IntVar()
        self.output_1m = tk.IntVar()
        self.output_5m = tk.IntVar()
        self.output_10m = tk.IntVar()
        self.output_15m = tk.IntVar()
        self.output_30m = tk.IntVar()
        self.output_1h = tk.IntVar()
        self.output_3h = tk.IntVar()
        self.output_6h = tk.IntVar()
        self.output_12h = tk.IntVar()
        self.output_1d = tk.IntVar()

        # Create checkboxes
        self.cb_1s = tk.Checkbutton(self.f21, text='1 second', variable=self.output_1s)
        self.cb_5s = tk.Checkbutton(self.f21, text='5 seconds', variable=self.output_5s)
        self.cb_10s = tk.Checkbutton(self.f21, text='10 seconds', variable=self.output_10s)
        self.cb_15s = tk.Checkbutton(self.f21, text='15 seconds', variable=self.output_15s)
        self.cb_30s = tk.Checkbutton(self.f21, text='30 seconds', variable=self.output_30s)
        self.cb_1m = tk.Checkbutton(self.f21, text='1 minute', variable=self.output_1m)
        self.cb_5m = tk.Checkbutton(self.f21, text='5 minutes', variable=self.output_5m)
        self.cb_10m = tk.Checkbutton(self.f21, text='10 minutes', variable=self.output_10m)
        self.cb_15m = tk.Checkbutton(self.f21, text='15 minutes', variable=self.output_15m)
        self.cb_30m = tk.Checkbutton(self.f21, text='30 minutes', variable=self.output_30m)
        self.cb_1h = tk.Checkbutton(self.f21, text='1 hour', variable=self.output_1h)
        self.cb_3h = tk.Checkbutton(self.f21, text='3 hours', variable=self.output_3h)
        self.cb_6h = tk.Checkbutton(self.f21, text='6 hours', variable=self.output_6h)
        self.cb_12h = tk.Checkbutton(self.f21, text='12 hours', variable=self.output_12h)
        self.cb_1d = tk.Checkbutton(self.f21, text='1 day', variable=self.output_1d)

        self.cb_1s.select() # set selection

        # place all Output Frame elements using grid
        self.f2.grid(row=2, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5)
        self.b_output.grid(column=1, row=1, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.t_outputPath.grid(column=2, row=1, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.lb1.grid(column=1, row=2, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_output_filetype.grid(column=2, row=2, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.lb2.grid(column=1, row=3, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_file_freq.grid(column=2, row=3, columnspan=1, rowspan=1, sticky=tk.NE, padx=5, pady=5)
        self.f21.grid(column=1, row=5, columnspan=3, rowspan=5, sticky=tk.NW, padx=5, pady=5)

        self.cb_1s.grid(column=1, row=5, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_5s.grid(column=1, row=6, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_10s.grid(column=1, row=7, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_15s.grid(column=1, row=8, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_30s.grid(column=1, row=9, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)

        self.cb_1m.grid(column=2, row=5, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_5m.grid(column=2, row=6, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_10m.grid(column=2, row=7, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_15m.grid(column=2, row=8, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_30m.grid(column=2, row=9, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)

        self.cb_1h.grid(column=3, row=5, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_3h.grid(column=3, row=6, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_6h.grid(column=3, row=7, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_12h.grid(column=3, row=8, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)
        self.cb_1d.grid(column=3, row=9, columnspan=1, rowspan=1, sticky=tk.NW, padx=5, pady=5)

    def create_processing_frame(self, mainFrame):
        """
        Draw the gui frame for data processing options
        KJ - new version using grid
        """
        self.f3 = tk.LabelFrame(mainFrame, text='Processing options')
        self.f31 = tk.LabelFrame(self.f3, text='Data masking/removal')
        self.f311 = tk.LabelFrame(self.f31, text='Select file with mask events (optional)')
        self.tb2 = tk.Entry(self.f311, width=40)
        self.b311 = tk.Button(self.f311,
                              text='Browse',
                              command=self.ask_mask_file)

        # help tooltip
        self.l311 = tk.Label(self.f311, text=u'\u2754')
        ToolTip.ToolTip(self.l311,
                        'Choose an ASCII file where the 1st and 2nd columns \
                        are the start and end timestamps of the period to be \
                        removed. Any additional columns (such as description \
                        columns) will be ignored.')

        self.f32 = tk.LabelFrame(self.f3, text='Flow calibration')
        self.f321 = tk.LabelFrame(self.f32, text='Select file with flow calibration data (optional)')
        self.tb3 = tk.Entry(self.f321, width=40)
        self.b321 = tk.Button(self.f321,
                              text='Browse',
                              command=self.ask_flowcal_file)
         # help tooltip
        self.l321 = tk.Label(self.f321, text=u'\u2754')
        ToolTip.ToolTip(self.l321,
                        'Choose an ASCII file where the 1st column is the  \
                        timestamp of the flow measurement, and the second \
                        column is the measured flow rate in units of \
                        L/min or LPM')

        self.lb_flow_rate_set = tk.Label(self.f32, text='Set flow rate (LPM)')
        self.tb_flow_rate_set = tk.Entry(self.f32, width=10)
        self.tb_flow_rate_set.insert(tk.END, 1.0)
        self.lb_flow_rate_fit = tk.Label(self.f32, text='Polynomial degree for flow rate fit')
        self.tb_flow_rate_fit = tk.Entry(self.f32, width=10)
        self.tb_flow_rate_fit.insert(tk.END, 2.0)

        self.lb_flow_rate_set.grid(row=16, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.tb_flow_rate_set.grid(row=16, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.lb_flow_rate_fit.grid(row=17, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.tb_flow_rate_fit.grid(row=17, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.f322 = tk.LabelFrame(self.f3, text='Time Zone Correction')
        self.lb322 = tk.Label(self.f322, text = '''Corrects timestamp for offset created by AIM \
outputting the timestamps based on the export computer's settings, rather \
than the measurement computer's time zone settings.''', wraplength=350)

        self.correct4TZ = tk.IntVar()
        self.cb_TZcorrection = tk.Checkbutton(self.f322,
                                           text='Correct Time Zone',
                                           variable=self.correct4TZ,
                                           onvalue=1, offvalue=0,
                                           command=self.grey_press_input)

        self.lb_TZcurrent = tk.Label(self.f322, text='Export PCs TZ (current)')
        self.tb_TZcurrent = tk.Entry(self.f322, width=5)
        self.tb_TZcurrent.insert(tk.END,0)
        self.lb_units1 = tk.Label(self.f322, text='hrs from UTC')

        self.lb_TZdesired = tk.Label(self.f322, text='Meas. PCs TZ (desired)')
        self.tb_TZdesired = tk.Entry(self.f322, width=5)
        self.tb_TZdesired.insert(tk.END, 0)
        self.lb_units2 = tk.Label(self.f322, text='hrs from UTC')


         # place all Processing Frame elements using grid
        self.f3.grid(row=10, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5)
        self.f31.grid(row=10, column=0, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.f311.grid(row=2, column=0, rowspan=1, columnspan=3, sticky=tk.NW, padx=5, pady=5)
        self.tb2.grid(row=3, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.b311.grid(row=3, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.l311.grid(row=3, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.f32.grid(row=14, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.f321.grid(row=14, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.tb3.grid(row=1, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.b321.grid(row=1, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.l321.grid(row=1, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.f322.grid(row=18, column=1, rowspan=2, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)
        self.lb322.grid(row=20, column=1, rowspan=3, columnspan=3, sticky=tk.NW, padx=5, pady=5)
        self.cb_TZcorrection.grid(row=25, column=1, rowspan=2, columnspan=3, sticky=tk.N, padx=5, pady=5)

        self.lb_TZcurrent.grid(row=28, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.tb_TZcurrent.grid(row=28, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.lb_units1.grid(row=28, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)

        self.lb_TZdesired.grid(row=29, column=1, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.tb_TZdesired.grid(row=29, column=2, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)
        self.lb_units2.grid(row=29, column=3, rowspan=1, columnspan=1, sticky=tk.NW, padx=5, pady=5)


    def _create_processing_frame(self, mainFrame):



        # Create go button!
        self.bt_go = tk.Button(self.f3,
                       text='GO!',
                       command=self.load_and_process,
                       background='forest green',
                       foreground='white',
                       font='Times 18 bold',
                       width=15)
        self.bt_go.pack(side=tk.BOTTOM)
        self.bt_go.place(rely=0.89, relx=0.25)

        self.f31.place(relx=0.01, rely=0.04, relheight=0.15, relwidth=0.98)
        self.f32.place(relx=0.01, rely=0.2, relheight=0.26, relwidth=0.98)
        self.f322.place(relx=0.01, rely=0.47, relheight=0.33, relwidth=0.98)
        self.cb_plot.place(relx=0.3, rely=0.83)

if __name__ == '__main__':
    cpc_processing().mainloop()
