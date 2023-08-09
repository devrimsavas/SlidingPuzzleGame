from tkinter import *
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk,ImageFilter

import os
import random

# tile dimensions
CARD_WIDTH = 160
CARD_HEIGHT = 160

class Card:
    def __init__(self, name, image_slice, canvas):
        self.canvas = canvas
        self.name = name
        self.image_tk = ImageTk.PhotoImage(image_slice)
        all_images.append(self.image_tk)
        self.shape = None
        self.image_item = None

    def place_tile(self, xpos, ypos):
        # Create the rectangle
        self.shape = self.canvas.create_rectangle(xpos, ypos, xpos+CARD_WIDTH, 
                                                  ypos+CARD_HEIGHT, fill="white", width=4, outline="gray")
        # Create the image after the rectangle to ensure it's on top
        self.image_item = self.canvas.create_image(xpos, ypos, image=self.image_tk, anchor=NW)

empty_slot = (9, 9)  # position of the empty slot /choosen last one as original but can be changed 



def animate_movement(card, x_move, y_move, steps=10):
    x_step = x_move / steps
    y_step = y_move / steps

    for i in range(steps):
        root.after(10 * (i+1), canvas.move, card.shape, x_step, y_step)
        root.after(10 * (i+1), canvas.move, card.image_item, x_step, y_step)

def swap_tile(event):
    global empty_slot
    clicked_column = event.x // CARD_WIDTH
    clicked_row = event.y // CARD_HEIGHT

    if ((abs(empty_slot[0] - clicked_column) == 1 and empty_slot[1] == clicked_row) or 
        (empty_slot[0] == clicked_column and abs(empty_slot[1] - clicked_row) == 1)):
        
        clicked_items = canvas.find_closest(event.x, event.y)
        clicked_card = None
        
        # Identify which card is clicked
        for card in all_cards:
            if card.image_item in clicked_items:
                clicked_card = card
                break

        if clicked_card:
            x_move = (empty_slot[0] - clicked_column) * CARD_WIDTH
            y_move = (empty_slot[1] - clicked_row) * CARD_HEIGHT

            # Animate the tile movement
            animate_movement(clicked_card, x_move, y_move)
            
            # Update the empty slot position
            empty_slot = (clicked_column, clicked_row)

all_cards = []
all_images=[]

#need to check if it is solvable or not
#since not all random allocation allow a solvable solution need count inversion 

def count_inversions(sequence):
    #inversion count in random sequence
    inv_count=0
    seq_len=len(sequence)
    for i in range(seq_len):
        for j in range(i+1,seq_len):
            if (sequence[i]>sequence[j]) and sequence[i] != 0 and sequence[j] != 0:
                inv_count += 1
    return inv_count



def create_cards(main_image_path):
    main_image = Image.open(main_image_path)
    main_image = main_image.resize((800, 800), Image.Resampling.LANCZOS)
    #optional image effect
    #main_image=main_image.filter(ImageFilter.EMBOSS)
    slice_width = main_image.width // 5
    slice_height = main_image.height // 5

    # Prepare all image slices
    for y in range(5):
        for x in range(5):
            if x == 4 and y == 4:  # Skip the last tile (empty slot)
                continue
            image_slice = main_image.crop((x * slice_width, y * slice_height, (x+1) * slice_width, (y+1) * slice_height))
            card = Card("card" + str(y * 5 + x), image_slice, canvas)
            all_cards.append(card)

    # Shuffle the cards and check solvability
    is_solvable = False
    while not is_solvable:
        random.shuffle(all_cards)
        # Convert the 2D board to a linear sequence for checking solvability
        linear_board = [int(card.name.replace("card", "")) for card in all_cards]
        linear_board.append(0)  # for the empty slot
        #finally compare list.. for inversion 
        inv_count = count_inversions(linear_board)
        if ((5 - empty_slot[1]) % 2 == 0 and inv_count % 2 == 1) or ((5 - empty_slot[1]) % 2 == 1 and inv_count % 2 == 0):
            is_solvable = True

    # Place shuffled tiles
    index = 0
    for y in range(5):
        for x in range(5):
            if x == 4 and y == 4:  # Skip the last tile (empty slot)
                continue
            card = all_cards[index]
            card.place_tile(x * CARD_WIDTH, y * CARD_HEIGHT)
            index += 1


#show reference image

def show_reference():
    global show_original, original_img_tk, main_image_path
    show_original=1-show_original
    print(show_original)
    if show_original:
        root.geometry("1700x950")
        button_expends.config(text="Hide Original Image")
        update_reference_image()
    else:
        root.geometry("850x950")
        button_expends.config(text="Show Original Image")

def update_reference_image():
    global original_img_tk, main_image_path
    original_img = Image.open(main_image_path).resize((800, 800), Image.Resampling.LANCZOS)

    
    
    original_img_tk = ImageTk.PhotoImage(original_img)
    canvas_or.create_image(0, 0, image=original_img_tk, anchor="nw")

def reset_game():
    global empty_slot
    global all_cards
    canvas.delete("all")
    canvas_or.delete("all")
    all_cards=[]
    all_images.clear()
    empty_slot=(4,4) # need to restart empty slot
    canvas.create_image(0,0,anchor=NW,image=bg)
    

def start_game():
    
    global main_image_path
    global timer_running,elapsed_time
    reset_game()
    timer_running=True
    elapsed_time=0
    update_timer()
    main_image_path = filedialog.askopenfilename(title="Select main image")
    if main_image_path:
        create_cards(main_image_path)
        button_expends.place(x=300, y=870)  # Move the Show Original Image button after starting the game
        if show_original:
            update_reference_image()


def stop_game():
    global timer_running
    timer_running=False 



def update_timer():
    global elapsed_time
    if timer_running:
        elapsed_time += 1
        mins, secs = divmod(elapsed_time, 60)
        time_str = "Time: {:02d}:{:02d}".format(mins, secs)
        timer_label.config(text=time_str)
        root.after(1000, update_timer)




    
global show_original,original_img_tk
original_img_tk=None

root = Tk()
root.geometry("850x950")
root.title("Madman Puzzle")
root.config(bg="#361c7e")




canvas_frame = LabelFrame(root, width=840, height=840, borderwidth=5, relief="sunken")
canvas_frame.place(x=5, y=5)

canvas = Canvas(canvas_frame, width=802, height=802 ,bg="orange")  #529feb"
canvas.place(x=5, y=0)
canvas.bind("<Button-1>", swap_tile)

#reference image canvas
canvas_or=Canvas(root,width=800,height=800,bg="#529feb")
canvas_or.place(x=860,y=5)

#canvas background
bg=Image.open("background.png")
bg=bg.resize((840,840),Image.Resampling.LANCZOS)

#emboss
#bg=bg.filter(ImageFilter.EMBOSS)
bg=ImageTk.PhotoImage(bg)

#canvas.create_image(0,0,anchor=NW,image=bg)
#canvas.bg_image=bg











#see original image

global show_original
show_original=False 
button_expends=Button(root,text="Show Original Image",width=23,height=1,font=("Arial",16),command=lambda:show_reference(),bg="beige")
button_expends.place(x=300,y=870)


# Add Start Game button
start_button = Button(root, text="Start Game", width=15, height=1, font=("Arial", 16), command=start_game,bg="beige")
start_button.place(x=50, y=870)


#timer
#init timer
elapsed_time=0
timer_running=False

#timer label
timer_label=Label(root,text="Time: 0",font=("Arial",16), bg="#361c7e", fg="white")
timer_label.place(x=650,y=870)




root.mainloop()
