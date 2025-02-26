import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from Datasets.COMPAS.COMPAS import COMPAS
from Datasets.Toy.Toy import Toy
from algorithms.twoDimensionalArraySweep import two_d_array_sweep
from algorithms.twoDimensionalOnline import two_d_online
from experiment import run_experiment, PLT_EXPERIMENT_NAME
from plot_satisfactory_regions import plot_satisfactory_regions

# --- UI Implementation using Tkinter ---
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fair Ranking UI")
        self.geometry("600x600")

        # Global variables to store selections and results
        self.dataset_choice = tk.StringVar()
        self.selected_dataset = None  # will hold "Toy" or "COMPAS"
        self.compas_attr1 = tk.StringVar()
        self.compas_attr2 = tk.StringVar()
        self.compas_type = tk.StringVar()
        self.compas_type_att = tk.StringVar()
        self.run_experiment_flag = tk.BooleanVar()
        self.sorted_satisfactory_regions = None
        self.optimal_weights = None

        # For Section 3 weight entry
        self.w1_var = tk.StringVar()
        self.w2_var = tk.StringVar()

        # Container frame to hold the different sections
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Configure grid so that child frames expand
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to hold the frames
        self.frames = {}
        for F in (Section1, Section2, Section3, Section4):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Section1")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def reset(self):
        # Reset variables and go back to section 1
        self.dataset_choice.set("")
        self.selected_dataset = None
        self.compas_attr1.set("")
        self.compas_attr2.set("")
        self.compas_type.set("")
        self.run_experiment_flag.set(False)
        self.sorted_satisfactory_regions = None
        self.optimal_weights = None
        self.w1_var.set("")
        self.w2_var.set("")
        self.show_frame("Section1")


# --- Section 1: Choose Dataset ---
class Section1(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Section 1: Choose Dataset", font=("Helvetica", 16))
        label.pack(pady=20)

        # Radio buttons for dataset choice
        self.choice = tk.StringVar()
        rb1 = ttk.Radiobutton(self, text="Toy", variable=self.choice, value="Toy", command=self.on_select)
        rb2 = ttk.Radiobutton(self, text="COMPAS", variable=self.choice, value="COMPAS", command=self.on_select)
        rb1.pack(pady=5)
        rb2.pack(pady=5)

        # Next button (disabled until a choice is made)
        self.next_btn = ttk.Button(self, text="Next", command=self.go_next, state="disabled")
        self.next_btn.pack(pady=20)

    def on_select(self):
        if self.choice.get():
            self.next_btn.config(state="normal")

    def go_next(self):
        selected = self.choice.get()
        self.controller.selected_dataset = selected
        if selected == "Toy":
            # For Toy, skip Section 2 and go directly to Section 3.
            # Here, we call two_d_array_sweep on a Toy dataset.
            toy_instance = Toy()
            self.controller.sorted_satisfactory_regions = two_d_array_sweep(toy_instance)
            self.controller.show_frame("Section3")
        else:
            # For COMPAS, go to Section 2.
            self.controller.show_frame("Section2")


# --- Section 2: For COMPAS: Choose attributes and type, and optionally run experiment ---
class Section2(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Section 2: Choose Attributes (COMPAS)", font=("Helvetica", 16))
        label.pack(pady=20)

        # Dropdowns for attribute1 and attribute2, using COMPAS.scoring_attr
        attr_frame = ttk.Frame(self)
        attr_frame.pack(pady=10)
        ttk.Label(attr_frame, text="Attribute 1:").grid(row=0, column=0, padx=5, pady=5)
        self.attr1_combo = ttk.Combobox(attr_frame, textvariable=controller.compas_attr1,
                                        values=COMPAS.SCORING_ATTR, state="readonly")
        self.attr1_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(attr_frame, text="Attribute 2:").grid(row=1, column=0, padx=5, pady=5)
        self.attr2_combo = ttk.Combobox(attr_frame, textvariable=controller.compas_attr2,
                                        values=COMPAS.SCORING_ATTR, state="readonly")
        self.attr2_combo.grid(row=1, column=1, padx=5, pady=5)

        # Dropdown for protected type
        type_frame = ttk.Frame(self)
        type_frame.pack(pady=10)
        ttk.Label(type_frame, text="Protected Type:").grid(row=0, column=0, padx=5, pady=5)
        self.type_combo = ttk.Combobox(type_frame, textvariable=controller.compas_type,
                                       values=list(COMPAS.TYPE_ATTS.keys()), state="readonly")
        self.type_combo.grid(row=0, column=1, padx=5, pady=5)

        type_att_frame = ttk.Frame(self)
        type_att_frame.pack(pady=10)
        ttk.Label(type_frame, text="Protected Type attribute:").grid(row=1, column=0, padx=5, pady=5)
        self.type_att_combo = ttk.Combobox(type_att_frame, textvariable=controller.compas_type_att,
                                       values=[], state="readonly")
        self.type_att_combo.grid(row=1, column=1, padx=5, pady=5)

        # Checkbox for "Run experiment"
        self.run_exp_cb = ttk.Checkbutton(self, text="Run experiment", variable=controller.run_experiment_flag)
        self.run_exp_cb.pack(pady=10)

        # Next button (enabled only when all fields are filled)
        self.next_btn = ttk.Button(self, text="Next", command=self.go_next, state="disabled")
        self.next_btn.pack(pady=20)

        # Trace variables to enable Next button when all are selected.
        controller.compas_attr1.trace("w", self.check_fields)
        controller.compas_attr2.trace("w", self.check_fields)
        controller.compas_type.trace("w", self.check_fields)
        controller.compas_type_att.trace("w", self.check_fields)

    def check_fields(self, *args):
        if self.controller.compas_type.get():
            type_att = COMPAS.TYPE_ATTS.get(self.controller.compas_type.get(), [])
            self.type_att_combo["values"] = type_att
        if (self.controller.compas_attr1.get() and
                self.controller.compas_attr2.get() and
                self.controller.compas_type.get() and
                self.controller.compas_type_att.get()
        ):
            self.next_btn.config(state="normal")
        else:
            self.next_btn.config(state="disabled")


    def go_next(self):
        # Create a COMPAS instance with selected parameters.
        attr1 = self.controller.compas_attr1.get()
        attr2 = self.controller.compas_attr2.get()
        protected_type = self.controller.compas_type.get()
        type_att = self.controller.compas_type_att.get()
        compas_dataset = COMPAS(attr1, attr2, protected_type, type_att)

        if self.controller.run_experiment_flag.get():
            # If Run experiment is checked, call run_experiment and then jump to Section 4.
            self.controller.sorted_satisfactory_regions = run_experiment(compas_dataset)
            self.controller.show_frame("Section4")
        else:
            # Otherwise, call two_d_array_sweep and then go to Section 3.
            self.controller.sorted_satisfactory_regions = two_d_array_sweep(compas_dataset)
            self.controller.show_frame("Section3")


# --- Section 3: Display plot and run online phase ---
class Section3(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Section 3: Online Phase", font=("Helvetica", 16))
        label.pack(pady=10)

        # Placeholder for the plot image
        self.plot_label = ttk.Label(self)
        self.plot_label.pack(pady=10)

        # Frame for weight entries
        weights_frame = ttk.Frame(self)
        weights_frame.pack(pady=10)
        ttk.Label(weights_frame, text="w1 (0-1):").grid(row=0, column=0, padx=5, pady=5)
        self.w1_entry = ttk.Entry(weights_frame, textvariable=controller.w1_var)
        self.w1_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(weights_frame, text="w2 (0-1):").grid(row=1, column=0, padx=5, pady=5)
        self.w2_entry = ttk.Entry(weights_frame, textvariable=controller.w2_var)
        self.w2_entry.grid(row=1, column=1, padx=5, pady=5)

        # Run online phase button (disabled until valid w1 is entered)
        self.run_online_btn = ttk.Button(self, text="Run online phase", command=self.run_online, state="disabled")
        self.run_online_btn.pack(pady=10)

        # Label to show optimized weights
        self.optimal_label = ttk.Label(self, text="")
        self.optimal_label.pack(pady=10)

        # Next button to proceed to Section 4 (initially disabled)
        self.next_btn = ttk.Button(self, text="Next", command=lambda: controller.show_frame("Section4"), state="disabled")
        self.next_btn.pack(pady=10)

        # Bind w1_var so that when w1 is entered, w2 is set automatically
        controller.w1_var.trace("w", self.on_change)
        controller.w2_var.trace("w", self.on_change)

    def on_change(self, *args):
        try:
            w1 = float(self.controller.w1_var.get())
            w2 = float(self.controller.w2_var.get())
            if 0 <= w1 <= 1 and 0 <= w2 <= 1:
                self.run_online_btn.config(state="normal")
            else:
                self.run_online_btn.config(state="disabled")
        except ValueError:
            self.run_online_btn.config(state="disabled")

    def tkraise(self, aboveThis=None):
        # When this frame is raised, update the plot image.
        filename = plot_satisfactory_regions(self.controller.sorted_satisfactory_regions)
        try:
            pil_image = Image.open(filename)
            pil_image = pil_image.resize((400, 300))
            self.image = ImageTk.PhotoImage(pil_image)
            self.plot_label.config(image=self.image)
        except Exception as e:
            self.plot_label.config(text="Could not load plot image.")
        super().tkraise(aboveThis)

    def run_online(self):
        try:
            w1 = float(self.controller.w1_var.get())
            w2 = float(self.controller.w2_var.get())
            opt_w1, opt_w2 = two_d_online(self.controller.sorted_satisfactory_regions, w1, w2)
            self.optimal_label.config(text=f"Optimized Weights: w1 = {opt_w1:.2f}, w2 = {opt_w2:.2f}")
            # Enable the Next button once the online phase has successfully run.
            self.next_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", "Invalid weights.")



# --- Section 4: Final screen with Start Over and Exit ---
class Section4(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = ttk.Label(self, text="Section 4: End", font=("Helvetica", 16))
        label.pack(pady=20)

        self.plot_label = ttk.Label(self)
        self.plot_label.pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        start_over_btn = ttk.Button(btn_frame, text="Start Over", command=self.controller.reset)
        start_over_btn.grid(row=0, column=0, padx=10)

        exit_btn = ttk.Button(btn_frame, text="Exit", command=self.controller.quit)
        exit_btn.grid(row=0, column=1, padx=10)

    def tkraise(self, aboveThis=None):
        if self.controller.run_experiment_flag:
            pil_image = Image.open(PLT_EXPERIMENT_NAME)
            pil_image = pil_image.resize((400, 300))
            self.image = ImageTk.PhotoImage(pil_image)
            self.plot_label.config(image=self.image)

        super().tkraise(aboveThis)


# --- Main execution ---
if __name__ == "__main__":
    app = Application()
    app.mainloop()

    # dataset = COMPAS()
    # print("len =", len(dataset))
    # dataset.set_portion(3000)
    #
    # import time
    #
    # start = time.perf_counter()
    # # call your function here
    # s = two_d_array_sweep(dataset)
    # end = time.perf_counter()
    #
    # elapsed_time = end - start
    # print(f"Elapsed time: {elapsed_time:.6f} seconds")
    #
    # plot_satisfactory_regions(two_d_array_sweep(dataset))

