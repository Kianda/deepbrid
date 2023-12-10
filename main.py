import tkinter
import grequests
import requests
import urllib.parse
import json
from tkinter import ttk, END
from tkinter import messagebox
from tkinter import Text
import validators


def copy():
    window.clipboard_clear()
    window.clipboard_append(links_entry.get(1.0, END))


def conversion():
    links_frame.grid_forget()
    button.grid_forget()
    progressbar.pack(fill="both", padx=20, pady=10)

    # debug
    #session_id_entry.delete(1.0, END)
    #session_id_entry.insert(END, '78a7536ca1de4e12d1f7dfad1cb262f5')

    # read use input
    session_id = session_id_entry.get("1.0", END).strip()
    links = links_entry.get("1.0", END).strip().splitlines()

    # sanitize input
    for link in links.copy():
        if not validators.url(link.strip()):
            links.remove(link)

    # prepare response
    converted_links = []
    not_converted_links = []
    reqs = []
    bar_steps = round(100/max(len(links), 1))

    for link in links:
        print("Loading: "+link.strip())
        url = "https://www.deepbrid.com/backend-dl/index.php?page=api&action=generateLink"
        safe_link = urllib.parse.quote_plus(link.strip())
        payload = "link="+safe_link
        headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': 'PHPSESSID='+session_id+';'
        }
        registered_request = grequests.request("POST", url, headers=headers, data=payload)
        reqs.append(registered_request)

    print("\n")
    print("Executing requests!!")

    for response in grequests.imap(reqs, size=3):
        progressbar.step(bar_steps)
        window.update()
        status_code = response.status_code
        original_url = urllib.parse.unquote(response.request.body).replace("link=", '')

        print("Response: " + response.text)
        print("\n")

        if status_code == 200:
            response_text = response.text
            response_data = json.loads(response_text)
            if not (response_data.get('link') is None):
                converted_link = response_data["link"]
                converted_links.append(converted_link)
                continue

        not_converted_links.append(original_url)


    links_entry.delete(1.0, END)
    links_entry.insert(END, '\n'.join(converted_links)+'\n'+'\n'.join(not_converted_links))
    copy.grid(row=4, column=0, sticky="news", padx=20, pady=10)
    links_frame.grid(row=1, column=0, sticky="news", padx=20, pady=10)
    progressbar.pack_forget()


print("Deepbrid link converter ready!")
print("\n")
window = tkinter.Tk()
window.title("Deepbrid link generator")

progressbar = ttk.Progressbar(maximum=100)

frame = tkinter.Frame(window)
frame.pack()

# Cookie Info
parameters_frame = tkinter.LabelFrame(frame, text="Cookie Parameters")
parameters_frame.grid(row=0, column=0, sticky="news", padx=20, pady=10)

session_id_label = tkinter.Label(parameters_frame, text="PHPSESSID")
session_id_label.grid(row=0, column=0)

session_id_entry = Text(parameters_frame, height=1)
session_id_entry.grid(row=1, column=0)

for widget in parameters_frame.winfo_children():
    widget.grid_configure(padx=10, pady=10)


# Links
links_frame = tkinter.LabelFrame(frame, text="Data")
links_frame.grid(row=1, column=0, sticky="news", padx=20, pady=10)

links_label = tkinter.Label(links_frame, text="Links")
links_label.grid(row=1, column=0)

links_entry = Text(links_frame, height=8)
links_entry.grid(row=2, column=0)

for widget in links_frame.winfo_children():
    widget.grid_configure(padx=10, pady=10)

# Progress bar
bar_frame = tkinter.LabelFrame(frame, text="Progress")
bar_frame.grid()
progressbar.step(0)
progressbar.pack()
progressbar.pack_forget()

# Button
button = tkinter.Button(frame, text="Convert", command=conversion)
button.grid(row=3, column=0, sticky="news", padx=20, pady=10)

# Copy
copy = tkinter.Button(frame, text="Copy", command=copy)
copy.grid(row=4, column=0, sticky="news", padx=20, pady=10)
copy.grid_forget()

window.mainloop()
