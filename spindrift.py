'''
Spindrift
Author: Kristina Johnson, Ruhi Humphries
'''

from tkinter import *
from tkinter import ttk

from Instruments.gui_ccnc import ccn_processing
from Instruments.gui_cpc import cpc_processing

class App(ccn_processing, cpc_processing):
    '''
    Spindrift main application class
    '''
    def __init__(self, master):
        '''
        Draw the main application frame.
        Add one tab per instrument.
        Uses Grid layout.
        '''
        # define main frame for application window
        frame = Frame(master)

        # define tabs
        self.notebook = ttk.Notebook(frame)
        tab_ccnc = Frame(self.notebook)
        tab_cpc = Frame(self.notebook)
        self.notebook.add(tab_ccnc, text='DMT CCN')
        self.notebook.add(tab_cpc, text='TSI CPC')

        # place notebook with tabs using grid
        frame.grid(row=0, column=0, sticky=NSEW)
        self.notebook.grid(sticky=NSEW, padx=5)

        # from gui_base
        self.create_input_frame(tab_ccnc)
        # from Instruments.gui_ccnc
        self.create_output_frame_ccn(tab_ccnc)
        self.create_processing_frame_ccn(tab_ccnc)

        # from gui_base
        # self.create_input_frame(tab_cpc)  # >>> conflict!!
        # from Instruments.gui_cpc
        # self.create_output_frame_cpc(tab_cpc)
        # self.create_processing_frame_cpc(tab_cpc)
        # self.create_plot_cpc(tab_cpc)

# Run the application
APP_WINDOW = Tk()
APP_WINDOW.title('Spindrift atmospheric data processing')
APP_WINDOW.geometry('1760x1160')
APP = App(APP_WINDOW)
APP_WINDOW.mainloop()
