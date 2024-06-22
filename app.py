from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector

class DatabaseApp:
    def __init__(self):
        self.cursor = None
        self.cnx = None

        img = Image.open("img.png")
        img.thumbnail((300, 300)) # resize image 
        img_tk = ImageTk.PhotoImage(img) 

        self.canvas = Canvas(width=300, height=300)
        self.canvas.grid(column=0, row=0, columnspan=2, pady=20)
        self.canvas.create_image(img.width / 2 +2, img.height / 2 +2, image=img_tk)
        self.canvas.image = img_tk

        self.create_widgets()
        window.protocol("WM_DELETE_WINDOW", self.on_closing) # window closing protocol

    def create_widgets(self):
        self.label1 = Label(text="Select User:")
        self.label1.grid(column=0, row=1, sticky="w")
        self.label2 = Label(text="Password:")
        self.label2.grid(column=0, row=2, sticky="w")
        self.label3 = Label(text="Select Database:")
        self.label3.grid(column=0, row=3, sticky="w")

        self.user = Entry(width=50)
        self.user.grid(column=1, row=1, padx=10)
        self.user.focus()
        self.password = Entry(width=50)
        self.password.grid(column=1, row=2, padx=10)
        self.database = Entry(width=50)
        self.database.grid(column=1, row=3, padx=10)

        self.log = Button(text="Login", padx=10, pady=10, command=self.login)
        self.log.grid(column=0, row=4, columnspan=2)

        self.widgets = [self.label1, self.label2, self.label3, self.user, self.password, self.database, self.log]

    def login(self):
        try: 
            self.cnx = mysql.connector.connect(user=self.user.get(), 
                                    password=self.password.get(),
                                    database=self.database.get())
        except:
            messagebox.showerror("Error", message="Cannot connect to MySQL server!\nPlease check back your DBMS or your input.")
        else:
            self.canvas.destroy()
            for widget in self.widgets:
                widget.grid_forget()

            self.syntax_label = Label(text="Syntax :")
            self.syntax_label.grid(column=0, row=0, padx=10, sticky="n")
        
            self.query_input = Text(width=70, height=10)
            self.query_input.grid(column=1, row=0)
            self.query_input.focus()

            self.exe = Button(text="Execute", padx=10, pady=10, command=self.execute)
            self.exe.grid(column=0, row=1, columnspan=2)
    
    def execute(self):
        self.cursor = self.cnx.cursor()
        query_syntax = " ".join(self.query_input.get("1.0", END).split("\n")) # delete '\n' from text box

        try:
            self.cursor.execute(query_syntax)
        
        except mysql.connector.errors.ProgrammingError as err:
            messagebox.showwarning(title="Syntax error", message=f"Error: {err}")

        else:
            if "select" in query_syntax or "SELECT" in query_syntax:
                self.query_input.delete("1.0", END)

                values = [x for x in self.cursor]
                tuple_len = len(values[0])

                with open("result.txt", "w") as file: # tkinter output by .txt 
                    for value in values:
                        for idx in range(tuple_len):
                            file.write(str(value[idx])+"  ")
                        file.write("\n")
            
                self.show_to_gui()

            else: # insert, delete, and update
                self.query_input.delete("1.0", END)
                messagebox.showinfo(title="Info", message="Database has been modified!")
                
                self.cnx.commit()

    def show_to_gui(self):
        with open("result.txt", "r") as file:
            result = file.read()
            self.query_input.insert(END, result) #show to the text box 

    def on_closing(self):
        if messagebox.askokcancel(title="Keluar", message="Anda yakin ingin keluar?"):
            if self.cursor:  # close cursor and connection
                self.cursor.close()
            if self.cnx:
                self.cnx.close()
            
            window.destroy() # exit from tkinter
        

if __name__ == "__main__":
    window = Tk()
    window.config(padx=50, pady=50)
    window.title("Database Handling")
    
    app = DatabaseApp()
    window.mainloop()