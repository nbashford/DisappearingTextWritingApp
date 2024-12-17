from tkinter import *
from tkinter import filedialog, messagebox
import time

def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """
    Draws rounded rectangle for canvas
    """
    radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1, x2, y1 + radius,
        x2, y2 - radius, x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2, x1, y2 - radius,
        x1, y1 + radius, x1, y1
    ]
    return canvas.create_polygon(points,
                                 smooth=True, **kwargs)


def draw_rounded_background():
    """
    draws the rounded cornered frame from the canvas
    """
    global rounded_background, window_bbox, canvas_text
    canvas.delete("all")

    # draw the polygon
    rounded_background = create_rounded_rectangle(canvas,
                                                  10, 10,
                                                  canvas.winfo_width() - 10, canvas.winfo_height() - 10,
                                                  radius=50, fill="#FFA07A", outline="black", width=2)
    window_bbox = canvas.bbox(rounded_background)
    canvas_text = canvas.create_text(50, 50, anchor="nw", text="",
                                     fill='black', font=("Georgia", 20, "bold"))


def save_text():
    """
    allows users to save their text to file.
    Additional user interaction to continue adding to text or resetting text after saving
    """
    global user_string, hidden_string, countdown_active, not_started
    reset_countdown()  # stop/pauses timer

    file = filedialog.asksaveasfile(mode='w', defaultextension=".txt")  # creates file for saving/writing
    if file:  # write the full text to this file
        full_string = hidden_string + user_string
        file.write(full_string)
        file.close()

    is_ok = messagebox.askyesno(title="Write new?",  # to reset text in canvas frame
                                message="Do you want to erase all text and start fresh?")

    if is_ok:  # reset all variables and start animation
        user_string = ""
        hidden_string = ""

        countdown_active = False
        save_button.config(state='disabled')
        not_started = True
        user_string = ""
        start_animation()


def update_countdown(seconds, initial=False):
    """
    Updates countdown label and handle action when timer is zero.
    initial: flag indicating if timer running as part of initial
        user display information animation
    """
    global countdown_active, not_started, new_round, user_string
    countdown_label['text'] = f"Countdown: {seconds}"
    countdown_label['fg'] = "black"

    if seconds == 0:  # timer finished
        if initial:  # part of initial animation
            countdown_label['text'] = f"Countdown: 5"
            countdown_label['fg'] = "black"
            canvas.itemconfig(canvas_text, text=initial_text, fill="black")
            countdown_active = False
            return
        else:
            countdown_label['text'] = "Time's up! Work disappeared!"
            canvas.itemconfig(canvas_text, text="Oh no! You paused too long!")
            countdown_active = False
            save_button.config(state='disabled')  # disable save button - no text
            user_string = ""
            new_round = root.after(3000, start_animation)  # calls starting animation
            return

    elif seconds == 3 or seconds == 1:
        canvas.itemconfig(canvas_text, fill="red")  # make canvas text red (warning)
    else:
        if initial:
            canvas.itemconfig(canvas_text, fill="grey")
        else:
            canvas.itemconfig(canvas_text, fill="black")

    # recursively call the contained function with the count decremented
    countdown_active = root.after(1000, update_countdown, seconds - 1, initial)  # Schedule next countdown


def add_string_to_canvas():
    """
    handles the user input to be displayed on the canvas.
    - checks and handles action when text goes passed x and
    y axis of limit of the canvas frame
    """
    global user_string, canvas_text

    # get margins - starting text and top left coordinates of canvas frame
    text_bbox = canvas.bbox(canvas_text)
    x_margin = text_bbox[0] - window_bbox[0]  # x-axis margin
    y_margin = text_bbox[1] - window_bbox[1]  # y-axis margin

    def update_text():
        """inner function that adds user string to canvas"""
        canvas.itemconfig(canvas_text, fill='black', text=user_string)

    # if user text goes passed x-axis limit of canvas frame
    if text_bbox[2] + x_margin >= window_bbox[2]:

        last_space_index = user_string.rfind(" ")  # Find index of last whitespace

        if last_space_index != -1:
            # replace the whitespace with newline character
            user_string = user_string[:last_space_index] + "\n" + user_string[last_space_index + 1:]
            update_text()  # display new text
            text_bbox = canvas.bbox(canvas_text)  # update canvas text size for the y-axis check

    # if user text goes passed y-axis limit of canvas frame
    if text_bbox[3] + y_margin >= window_bbox[3]:

        global hidden_string

        first_new_line_index = user_string.find("\n")  # Find index of last newline
        if first_new_line_index != -1:
            # hold the hidden text
            hidden_string = hidden_string + user_string[:first_new_line_index + 1]
            # remove the top line and update the user text
            user_string = user_string[first_new_line_index + 1:]

    update_text()


def reset_countdown():
    """cancel and root after events, and reset countdown label"""
    global countdown_active, new_round, call_countdown

    # cancel each root after event
    after_events = [countdown_active, new_round, call_countdown]
    for event in after_events:
        if event:
            root.after_cancel(event)
            event = None

    # reset countdown label
    countdown_label['text'] = "Countdown: 5"
    countdown_label['fg'] = "grey"


def key_pressed(event):
    """
    :param: the key pressed.
    handles user key presses.
    Timers are reset after each key press.
    user string is updated and passed to add_string_to_canvas to handle
    """
    global user_string, not_started, call_countdown
    if not_started:
        not_started = False
        save_button.config(state='active')
    reset_countdown()  # Cancel the countdown when typing resumes

    # Append the typed character to user_string
    if event.keysym == "BackSpace":
        user_string = user_string[:-1]
    elif event.char.isprintable():  # Add character if it's printable
        if event.keysym == "Return":
            user_string += "\n"
        else:
            user_string += event.char

    add_string_to_canvas()

    # Restart countdown after typing
    call_countdown = root.after(1000, update_countdown, 5)  # Start countdown after 2s pause


def write_letter():
    """ adds next letter to the canvas text and updates the remaining text"""
    global first_text, canvas_text, start_text

    if start_text:  # Add letters only if there are characters left
        first_text = first_text + start_text[0]
        start_text = start_text[1:]  # shorten remaining text

        canvas.itemconfig(canvas_text,  # Update Canvas text
                          text=first_text, fill='black')


def start_animation():
    """
    starts the display text animation -
        loop which updates the canvas with additional character after each time interval.
    stops if any key pressed => not_started flag is set to False
    Purpose: Shows how the app works to the user.
    """
    global start_text, first_text, countdown_active, not_started, new_round
    reset_countdown() # reset any root after events

    # set up string variables for animation
    first_text = ""
    start_text = keep_text
    not_started = True

    while start_text and not_started:  # Run animation until all text is written
        time.sleep(0.05)
        write_letter()  # add next char of text to canvas
        root.update()  # Update UI

    update_countdown(5, initial=True)  # start the timer.


# Root setup
root = Tk()
root.title("Disappearing Text Writing APP")
root.geometry("800x600")
root.minsize(width=800, height=600)
root.resizable(False, False)
root.config(padx=50, pady=50, bg="AntiqueWhite1")

# Countdown label
countdown_label = Label(root, text="Countdown: 5", fg="grey", bg="AntiqueWhite1", font=("Georgia", 20, "bold"))
countdown_label.pack()

# Canvas
canvas = Canvas(root, bg="AntiqueWhite1", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# save button
save_button = Button(root, text='Save Text', bg="AntiqueWhite1", fg="black",
                     highlightcolor="blue", font=('Georgia', 15),
                     state='disabled', command=save_text)
save_button.pack()


# ---- VARIABLES ----

not_started = True  # flag for running the start_animation function
canvas_text = None  # holds the canvas create text
rounded_background = None  # holds the rounded canvas background shape
window_bbox = None  # canvas window dimensions

# root.after events
call_countdown = None  # root after event for starting the count down
countdown_active = None  # root after event for calling count down func with 1 less second
new_round = None  # root after event - calls the start_animation event

# string variables
user_string = ""  # holds what the user has types
hidden_string = ""  # holds text user has typed when text is moved out of view
initial_text = ". . . start typing to begin . . ."  # placeholder text
first_text = ""  # will hold the characters to display for the user info text
start_text = ""  # a copy of the keep_text string below
keep_text = (". . . start typing to begin . . .\n\n\nDon't pause for too long"
             " . . .\n\n. . . or your work will disappear!")  # user info text


# Key bindings
root.bind("<Key>", key_pressed)  # any key

# ---- APP starting animation -------
root.after(1, draw_rounded_background)  # Draw rounded canvas background

start_animation()  # start display helper text animation


if __name__ == "__main__":
    root.mainloop()  # loop keeping app running




"""
Todo: 

add some option for changing the setting of the app

- 1. chan



"""