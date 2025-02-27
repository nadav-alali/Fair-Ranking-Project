import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw

from Datasets.COMPAS.COMPAS import COMPAS
from Datasets.Toy.Toy import Toy
from algorithms.twoDimensionalArraySweep import two_d_array_sweep
from algorithms.twoDimensionalOnline import two_d_online
from helpers.experiment import run_experiment, PLT_EXPERIMENT_NAME
from helpers.plot_satisfactory_regions import plot_satisfactory_regions
from PIL import ImageFilter


class CreateToolTip(object):
    """
    Create a tooltip for a given widget.
    The tooltip window is fixed to 300x200 pixels with a light green background.
    The label text will wrap within the window to prevent it from being cut off.
    """
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
        # Do nothing if tooltip is already visible or there's no text.
        if self.tipwindow or not self.text:
            return
        # Calculate position for tooltip relative to widget.
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        # Create a top-level window for the tooltip.
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)  # Remove window decorations.
        # Set fixed geometry: 300x200 pixels.
        tw.wm_geometry("300x100+%d+%d" % (x, y))
        tw.configure(background="light green")
        # Create a label inside the tooltip with a wraplength to fit text.
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="light green", relief=tk.SOLID, borderwidth=1,
                         font=("Helvetica", 12), wraplength=280)
        label.pack(fill="both", expand=True, padx=5, pady=5)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None




# Helper function to load an image, resize it to a square, add rounded corners,
# and composite it onto a white background.
def make_rounded_image(filename, size, radius):
    """
    Loads an image from filename, resizes it to `size` (tuple: (width, height)),
    applies a high-resolution rounded corner mask with the given radius,
    applies a slight Gaussian blur for smoother edges,
    and composites the image on a white background.
    Returns an ImageTk.PhotoImage.
    """
    im = Image.open(filename).convert("RGBA")
    try:
        resample_method = Image.Resampling.LANCZOS
    except AttributeError:
        resample_method = Image.ANTIALIAS
    im = im.resize(size, resample_method)

    # Increase resolution for the mask.
    scale_factor = 8  # Increase this factor for smoother edges.
    large_size = (size[0] * scale_factor, size[1] * scale_factor)
    large_radius = radius * scale_factor

    # Create the high-resolution mask.
    mask_large = Image.new("L", large_size, 0)
    draw = ImageDraw.Draw(mask_large)
    draw.rounded_rectangle((0, 0, large_size[0], large_size[1]), radius=large_radius, fill=255)

    # Downsample the mask to target size.
    mask = mask_large.resize(size, resample_method)

    # Apply a slight Gaussian blur for smoother transitions.
    mask = mask.filter(ImageFilter.GaussianBlur(1))

    # Apply the mask as an alpha channel.
    im.putalpha(mask)

    # Composite onto a white background.
    bg = Image.new("RGBA", size, (255, 255, 255, 255))
    bg.paste(im, mask=im.split()[3])
    return ImageTk.PhotoImage(bg.convert("RGB"))


# --- Application with Modern Theme and Updated Styles ---
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fair Ranking UI")
        self.geometry("600x750")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        # Define a white background style for frames.
        self.style.configure("White.TFrame", background="white")

        # Define a custom style for buttons with hover and click effects.
        self.style.configure("Hover.TButton", font=("Helvetica", 10, "bold"), background="#E0E0E0")
        self.style.map(
            "Hover.TButton",
            foreground=[("active", "white"), ("!disabled", "black")],
            background=[("active", "#0078D7"), ("!disabled", "#E0E0E0")],
        )
        self.button_style = "Hover.TButton"

        # Define a custom style for big radiobuttons.
        self.style.configure("Big.TRadiobutton", font=("Helvetica", 14), background="white")
        self.style.configure("Big.TCheckbutton", font=("Helvetica", 14), background="white")

        # Global variables to store selections and results.
        self.dataset_choice = tk.StringVar()
        self.selected_dataset = None  # "Toy" or "COMPAS"
        self.compas_attr1 = tk.StringVar()
        self.compas_attr2 = tk.StringVar()
        self.compas_type = tk.StringVar()
        self.compas_type_att = tk.StringVar()
        self.run_experiment_flag = tk.BooleanVar()
        self.sorted_satisfactory_regions = None
        self.optimal_weights = None

        # For Section 3 weight entry.
        self.w1_var = tk.StringVar()
        self.w2_var = tk.StringVar()

        # Container frame to hold the different sections.
        self.container = ttk.Frame(self, style="White.TFrame")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Create and store frames.
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
        self.dataset_choice.set("")
        self.selected_dataset = None
        self.compas_attr1.set("")
        self.compas_attr2.set("")
        self.compas_type.set("")
        self.compas_type_att.set("")
        self.run_experiment_flag.set(False)
        self.sorted_satisfactory_regions = None
        self.optimal_weights = None
        self.w1_var.set("")
        self.w2_var.set("")
        self.show_frame("Section1")


# --- Section 1: Choose Dataset with Images and Options ---
class Section1(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="White.TFrame")
        self.controller = controller

        # Title label at the top.
        title = ttk.Label(self, text="Choose Dataset", font=("Helvetica", 18, "bold"), background="white")
        title.pack(pady=40)

        # --- Toy Option ---
        toy_frame = ttk.Frame(self, style="White.TFrame")
        toy_frame.pack(pady=10)
        # Radiobutton for Toy (appearing above its image)
        toy_rb = ttk.Radiobutton(toy_frame, text="Toy", variable=controller.dataset_choice, value="Toy",
                                 command=self.on_select, style="Big.TRadiobutton")
        toy_rb.pack()
        # Add some vertical space.
        ttk.Label(toy_frame, text=" ", background="white").pack()
        # Load and display the Toy image.
        self.toy_img = make_rounded_image("Datasets/Toy/toy.png", (200, 200), radius=30)
        toy_img_label = ttk.Label(toy_frame, image=self.toy_img, background="white")
        toy_img_label.pack(pady=5)

        # --- COMPAS Option ---
        compas_frame = ttk.Frame(self, style="White.TFrame")
        compas_frame.pack(pady=10)
        # Load and display the COMPAS image.
        self.compas_img = make_rounded_image("Datasets/COMPAS/compas.png", (200, 200), radius=30)
        compas_img_label = ttk.Label(compas_frame, image=self.compas_img, background="white")
        compas_img_label.pack(pady=5)
        # Add some vertical space.
        ttk.Label(compas_frame, text=" ", background="white").pack()
        # Radiobutton for COMPAS (appearing below its image)
        compas_rb = ttk.Radiobutton(compas_frame, text="COMPAS", variable=controller.dataset_choice, value="COMPAS",
                                    command=self.on_select, style="Big.TRadiobutton")
        compas_rb.pack()

        # Next button pinned at the bottom.
        bottom_frame = ttk.Frame(self, style="White.TFrame")
        bottom_frame.pack(side="bottom", fill="x", pady=10)
        self.next_btn = ttk.Button(bottom_frame, text="Next", command=self.go_next, state="disabled",
                                   style=controller.button_style)
        self.next_btn.pack(side="right", padx=20)

    def on_select(self):
        if self.controller.dataset_choice.get():
            self.next_btn.config(state="normal")

    def go_next(self):
        selected = self.controller.dataset_choice.get()
        self.controller.selected_dataset = selected
        if selected == "Toy":
            toy_instance = Toy()
            self.controller.sorted_satisfactory_regions, _ = two_d_array_sweep(toy_instance)
            self.controller.show_frame("Section3")
        else:
            self.controller.show_frame("Section2")


# --- Section 2: For COMPAS: Choose Attributes and Type, plus FM1 explanation ---
class Section2(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="White.TFrame")
        self.controller = controller

        top_frame = ttk.Frame(self, style="White.TFrame")
        top_frame.pack(side="top", fill="x", pady=50, padx=5)
        label_title = ttk.Label(top_frame,
                                text="Choose Attributes (COMPAS)",
                                font=("Helvetica", 18, "bold"),
                                background="white")
        label_title.pack(anchor="center")

        main_frame = ttk.Frame(self, style="White.TFrame")
        main_frame.pack(side="top", fill="x", padx=120, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="Attribute 1:", font=("Helvetica", 14), background="white") \
            .grid(row=0, column=0, padx=5, pady=15, sticky="w")
        self.attr1_combo = ttk.Combobox(main_frame, textvariable=controller.compas_attr1,
                                        values=COMPAS.SCORING_ATTR, state="readonly", width=15,
                                        font=("Helvetica", 14))
        self.attr1_combo.grid(row=0, column=1, padx=5, pady=15, sticky="w")

        ttk.Label(main_frame, text="Attribute 2:", font=("Helvetica", 14), background="white") \
            .grid(row=1, column=0, padx=5, pady=15, sticky="w")
        self.attr2_combo = ttk.Combobox(main_frame, textvariable=controller.compas_attr2,
                                        values=COMPAS.SCORING_ATTR, state="readonly", width=15,
                                        font=("Helvetica", 14))
        self.attr2_combo.grid(row=1, column=1, padx=5, pady=15, sticky="w")

        ttk.Label(main_frame, text="Protected Type:", font=("Helvetica", 14), background="white") \
            .grid(row=2, column=0, padx=5, pady=15, sticky="w")
        self.type_combo = ttk.Combobox(main_frame, textvariable=controller.compas_type,
                                       values=list(COMPAS.TYPE_ATTS.keys()), state="readonly", width=15,
                                       font=("Helvetica", 14))
        self.type_combo.grid(row=2, column=1, padx=5, pady=15, sticky="w")

        ttk.Label(main_frame, text="Protected Type Att:", font=("Helvetica", 14), background="white") \
            .grid(row=3, column=0, padx=5, pady=15, sticky="w")
        self.type_att_combo = ttk.Combobox(main_frame, textvariable=controller.compas_type_att,
                                           values=[], state="disabled", width=15,
                                           font=("Helvetica", 14))
        self.type_att_combo.grid(row=3, column=1, padx=5, pady=15, sticky="w")

        lower_frame = ttk.Frame(self, style="White.TFrame")
        lower_frame.pack(pady=20)
        self.run_exp_cb = ttk.Checkbutton(lower_frame, text="Run experiment",
                                          variable=controller.run_experiment_flag,
                                          style="Big.TCheckbutton")
        self.run_exp_cb.pack(pady=5)
        # Create a tooltip for the experiment checkbox.
        tooltip_text = ("This experiment replicates the study presented in Figure 14 of the paper. "
                        "It evaluates the performance of the 2DarraySweep preprocessing algorithm as the dataset size increases "
                        "by measuring runtime (in seconds) and the number of ordering exchanges computed during preprocessing.")
        CreateToolTip(self.run_exp_cb, tooltip_text)

        fm1_explain = ttk.Label(lower_frame,
                                text=("FM1: This fairness model ensures that the top-K (30%) ranking contains "
                                      "a balanced proportion of the protected group (no more than 60% from one group). "
                                      "Adjust the attribute selections above to influence the ranking while satisfying "
                                      "the fairness constraint."),
                                foreground="green", font=("Helvetica", 14, "bold"),
                                background="white", wraplength=500, justify="center")
        fm1_explain.pack(pady=30)

        bottom_frame = ttk.Frame(self, style="White.TFrame")
        bottom_frame.pack(side="bottom", fill="x", pady=10)
        self.next_btn = ttk.Button(bottom_frame, text="Next", command=self.go_next, state="disabled",
                                     style=controller.button_style)
        self.next_btn.pack(side="right", padx=20)

        controller.compas_attr1.trace("w", self.check_fields)
        controller.compas_attr2.trace("w", self.check_fields)
        controller.compas_type.trace("w", self.check_fields)
        controller.compas_type_att.trace("w", self.check_fields)

    def check_fields(self, *args):
        if self.controller.compas_type.get():
            type_att = COMPAS.TYPE_ATTS.get(self.controller.compas_type.get(), [])
            self.type_att_combo["values"] = type_att
            self.type_att_combo["state"] = "readonly"
        if (self.controller.compas_attr1.get() and
            self.controller.compas_attr2.get() and
            self.controller.compas_type.get() and
            self.controller.compas_type_att.get()):
            self.next_btn.config(state="normal")
        else:
            self.next_btn.config(state="disabled")

    def go_next(self):
        attr1 = self.controller.compas_attr1.get()
        attr2 = self.controller.compas_attr2.get()
        protected_type = self.controller.compas_type.get()
        type_att = self.controller.compas_type_att.get()
        compas_dataset = COMPAS(attr1, attr2, protected_type, type_att)
        if self.controller.run_experiment_flag.get():
            self.controller.sorted_satisfactory_regions = run_experiment(compas_dataset)
            self.controller.show_frame("Section4")
        else:
            self.controller.sorted_satisfactory_regions, _ = two_d_array_sweep(compas_dataset)
            self.controller.show_frame("Section3")





# --- Section 3: Display plot and run online phase (unchanged) ---
class Section3(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="White.TFrame")
        self.controller = controller

        label = ttk.Label(self, text="Online Phase", font=("Helvetica", 16), background="white")
        label.pack(pady=10)

        self.plot_label = ttk.Label(self, background="white")
        self.plot_label.pack(pady=10)

        weights_frame = ttk.Frame(self, style="White.TFrame")
        weights_frame.pack(pady=10)
        ttk.Label(weights_frame, text="w1:").grid(row=0, column=0, padx=5, pady=5)
        self.w1_entry = ttk.Entry(weights_frame, textvariable=controller.w1_var)
        self.w1_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(weights_frame, text="w2:").grid(row=1, column=0, padx=5, pady=5)
        self.w2_entry = ttk.Entry(weights_frame, textvariable=controller.w2_var)
        self.w2_entry.grid(row=1, column=1, padx=5, pady=5)

        self.run_online_btn = ttk.Button(self, text="Run online phase", command=self.run_online, state="disabled",
                                         style=controller.button_style)
        self.run_online_btn.pack(pady=10)

        self.optimal_label = ttk.Label(self, text="", background="white")
        self.optimal_label.pack(pady=10)

        self.next_btn = ttk.Button(self, text="Next", command=lambda: controller.show_frame("Section4"),
                                   state="disabled", style=controller.button_style)
        self.next_btn.pack(pady=10)

        controller.w1_var.trace("w", self.on_change)
        controller.w2_var.trace("w", self.on_change)

    def on_change(self, *args):
        try:
            w1 = float(self.controller.w1_var.get())
            w2 = float(self.controller.w2_var.get())
            if w1 >= 0 and 0 <= w2:
                self.run_online_btn.config(state="normal")
            else:
                self.run_online_btn.config(state="disabled")
        except ValueError:
            self.run_online_btn.config(state="disabled")

    def tkraise(self, aboveThis=None):
        filename = plot_satisfactory_regions(self.controller.sorted_satisfactory_regions)
        try:
            pil_image = Image.open(filename)
            pil_image = pil_image.resize((600, 450))
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
            self.next_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", "Invalid weights.")


# --- Section 4: Final screen with Start Over and Exit ---
class Section4(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="White.TFrame")
        self.controller = controller
        label = ttk.Label(self, text="End", font=("Helvetica", 16), background="white")
        label.pack(pady=20)

        self.plot_label = ttk.Label(self, background="white")
        self.plot_label.pack(pady=10)

        bottom_frame = ttk.Frame(self, style="White.TFrame")
        bottom_frame.pack(side="bottom", fill="x", pady=10)
        start_over_btn = ttk.Button(bottom_frame, text="Start Over", command=self.controller.reset,
                                    style=controller.button_style)
        start_over_btn.pack(side="left", padx=10)
        exit_btn = ttk.Button(bottom_frame, text="Exit", command=self.controller.quit,
                              style=controller.button_style)
        exit_btn.pack(side="right", padx=10)

    def tkraise(self, aboveThis=None):
        is_experiment = self.controller.run_experiment_flag.get()
        image_file = PLT_EXPERIMENT_NAME if is_experiment else "helpers/section4.png"
        pil_image = Image.open(image_file).convert("RGBA")
        if is_experiment:
            pil_image = pil_image.resize((600, 450))
        self.image = ImageTk.PhotoImage(pil_image)
        self.plot_label.config(image=self.image)
        super().tkraise(aboveThis)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
