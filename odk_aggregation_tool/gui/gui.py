import tkinter
import tkinter.filedialog
import tkinter.messagebox
from functools import partial
from tkinter import ttk
from odk_aggregation_tool.gui.wrappers import aggregation_stata
from odk_aggregation_tool.gui import preferences


class ODKToolsGui:

    def __init__(self, master=None):
        """
        Set up the GUI by creating controls and adding them to the master frame.

        Controls appear in the GUI in the order they were added. Since many of
        the controls are similar, the repetitive parts of the process are
        abstracted to helper functions. The remaining functions are for input
        validation, or wrappers around commands that are run by clicking the
        button controls.
        """
        prefs = preferences.Preferences()
        master.title(prefs.app_title)
        ttk.Style().configure('.', font=prefs.font)
        ODKToolsGui.build_aggregation_stata(master=master, prefs=prefs)
        ODKToolsGui.build_output_box(master=master, prefs=prefs)

    @staticmethod
    def build_aggregation_stata(master, prefs):
        """Setup for the Aggregation to Stata task widgets."""
        master.xlsforms_path, xlsforms_path = ODKToolsGui.build_path_frame(
            master=master, label_text="* XLSForm definitions path",
            label_width=prefs.label_width,
            textbox_width=prefs.textbox_width, browser_kw=prefs.dir_browse)
        master.xforms_path, xforms_path = ODKToolsGui.build_path_frame(
            master=master, label_text="* XForm data path",
            label_width=prefs.label_width,
            textbox_width=prefs.textbox_width, browser_kw=prefs.dir_browse)
        master.output_path, output_path = ODKToolsGui.build_path_frame(
            master=master, label_text="* Output path",
            label_width=prefs.label_width,
            textbox_width=prefs.textbox_width, browser_kw=prefs.dir_browse)

        master.aggregation_to_stata_xml = ODKToolsGui.build_action_frame(
            master=master, label_text="Aggregation to Stata XML",
            label_width=prefs.label_width,
            command=lambda: ODKToolsGui.aggregation_to_stata_xml(
                master=master, xlsforms_path=xlsforms_path,
                xforms_path=xforms_path, output_path=output_path),
            pre_msg=prefs.generic_pre_msg.format("Aggregation to Stata XML"))

    @staticmethod
    def build_output_box(master, prefs):
        """Setup for the task results output box."""
        master.sep1 = ttk.Separator(master=master).grid(sticky="we")
        master.output = ttk.Frame(master=master, height=10)
        master.output.grid(sticky='w')
        master.output.rowconfigure(index=0, pad=10, weight=1)
        master.output.row_label = ttk.Label(
            master=master.output, text="Last run output",
            width=prefs.label_width)
        master.output.row_label.grid(row=0, column=0, padx=5, sticky="w")

        master.output.textbox = tkinter.Text(
            master=master.output, width=prefs.textbox_width+10,
            height=prefs.output_height)
        master.output.textbox.config(wrap='word', font=prefs.font)
        master.output.textbox.grid(row=0, column=1, padx=5, columnspan=2)
        master.output.scroll = ttk.Scrollbar(
            master=master.output, command=master.output.textbox.yview)
        master.output.scroll.grid(row=0, column=3, padx=5, pady=5, sticky='ns')
        master.output.textbox['yscrollcommand'] = master.output.scroll.set

    @staticmethod
    def textbox_pre_message(event, message):
        """Clear the output Text field and insert the provided message."""
        event.widget.master.master.output.textbox.delete("1.0", tkinter.END)
        event.widget.master.master.output.textbox.insert(tkinter.END, message)

    @staticmethod
    def build_action_frame(master, label_text, label_width, command,
                           pre_msg=None):
        """
        Generate a frame with a button for executing a command.

        The frame contains a grid row, with 3 columns: a label and a button
        labelled "Run" which executes the command on click.

        The command / function passed in should be a lambda which doesn't
        return or require any input parameters; in the above layout code the
        examples bake in a reference to the relevant variable (bound to a
        control) which is used to run the function.

        So that the user is notified that the task connected to the "Run"
        button has started, once the ButtonPress event fires, the specified
        pre_msg is displayed in the main output textbox. The button's command
        is implicitly attached to the subsequent ButtonRelease event. Refs:
        - http://tcl.tk/man/tcl8.5/TkCmd/bind.htm#M7
        - http://tcl.tk/man/tcl8.5/TkCmd/button.htm#M5

        Parameters.
        :param master: tk.Frame. The parent of the generated frame.
        :param label_text: str. The text to display next to the command button.
        :param label_width: int. How wide the label should be.
        :param command: function. What to do when the button is clicked.
        :param pre_msg: str. Message to display in textbox on button press.
        :return: path frame (tk Frame), path variable (tk StringVar)
        """
        frame = ttk.Frame(master=master)
        frame.grid(sticky='w')
        frame.rowconfigure(index=0, pad=10, weight=1)

        frame.row_label = ttk.Label(
            master=frame, text=label_text, width=label_width)
        frame.row_label.grid(row=0, column=0, padx=5, sticky="w")

        frame.button = ttk.Button(master=frame, text="Run", command=command)
        frame.button.grid(row=0, column=1, padx=5)
        if pre_msg is not None:
            frame.button.bind(
                sequence="<ButtonPress>", add='+',
                func=partial(ODKToolsGui.textbox_pre_message, message=pre_msg))
        return frame

    @staticmethod
    def build_path_frame(
            master, label_text, label_width, textbox_width, browser_kw,
            dialog_function=tkinter.filedialog.askdirectory):
        """
        Generate a frame with controls for collecting a file path.

        The frame contains a grid row, with 3 columns: a label, a text box,
        and a button which opens the file explorer which can be used to
        select the file path visually.

        Parameters.
        :param master: tk.Frame. The parent of the generated frame.
        :param label_text: str. The text to display next to the path textbox.
        :param label_width: int. How wide the label should be.
        :param textbox_width: int. How wide the text box should be.
        :param browser_kw: dict. Keyword arguments to pass to the file browser.
        :param dialog_function: File dialog generation function to use.
        :return: path frame (tk Frame), path variable (tk StringVar)
        """
        frame = ttk.Frame(master=master)
        frame.grid()
        frame.rowconfigure(index=0, pad=10, weight=1)

        frame.row_label = ttk.Label(
            master=frame, text=label_text, width=label_width)
        frame.row_label.grid(row=0, column=0, padx=5, sticky="w")

        path = tkinter.StringVar()
        frame.textbox = ttk.Entry(
            master=frame, textvariable=path, width=textbox_width)
        frame.textbox.grid(row=0, column=1, padx=5, columnspan=2)

        frame.browse = ttk.Button(
            master=frame, text="Browse...",
            command=lambda: ODKToolsGui.file_browser(
                browser_kw=browser_kw, target_variable=path,
                dialog_function=dialog_function))
        frame.browse.grid(row=0, column=3, padx=5)
        return frame, path

    @staticmethod
    def file_browser(browser_kw, target_variable, dialog_function):
        """
        Set the target_variable value using a file chooser dialog.

        Parameters.
        :param browser_kw: dict. Passed in to filedialog constructor.
        :param target_variable: tk control. Where should the value be placed.
        :param dialog_function: function to generate the file dialog control.
        """
        target_variable.set(dialog_function(**browser_kw))

    @staticmethod
    def textbox_replace(tk_end, widget, new_text):
        """
        Clear a textbox widget and insert the new text.

        Important! This is specific to "Entry" widgets, for which the start
        index is specified as 0. For "Text" widgets, the start index is instead
        in the form of "row.col" e.g. delete("1.0", END).

        :param tk_end: the tkinter.END constant meaning the final textbox char.
        :param widget: reference to the widget to work with.
        :param new_text: text to insert into the widget.
        :return: None
        """
        if len(widget.get()) != 0:
            widget.delete(0, tk_end)
        widget.insert(tk_end, new_text)

    @staticmethod
    def aggregation_to_stata_xml(
            master, xlsforms_path, xforms_path, output_path):
        """Run Aggregation to Stata XML task, put results in main textbox."""
        result = aggregation_stata.wrapper(
            xlsforms_path=xlsforms_path.get(), xforms_path=xforms_path.get(),
            output_path=output_path.get())
        master.output.textbox.insert(tkinter.END, result)


if __name__ == "__main__":
    root = tkinter.Tk()
    my_gui = ODKToolsGui(root)
    root.mainloop()
