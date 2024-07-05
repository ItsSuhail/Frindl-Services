import pyrebase
from tkinter import filedialog
import datetime
import time

email = "<auth_email>"
password = "<auth_password>"

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://databaseName.firebaseio.com",
  "storageBucket": "projectId.appspot.com",
  "serviceAccount": "path/to/serviceAccountCredentials.json"
}

firebase = pyrebase.initialize_app(config)

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()
auth = firebase.auth()

def open_file_dialog():
    file_path = filedialog.askopenfilename(title="Select a File", filetypes=[("pdf", "*.pdf"), ("msword", "*.docs"), ("vnd.openxmlformats-officedocument.wordprocessingml.document", "*.docx")])
    if(file_path):
        return file_path
    
    return None

def upload_file(file_path):
    book_id = "B" + (datetime.datetime.now().strftime("%Y%m%d") + str(time.time_ns()))[:-4]
    storage.child("docs/"+book_id).put(file_path)
    print("\n** Uploaded file to the storage **\n")

    user = auth.sign_in_with_email_and_password(email, password)
    user = auth.refresh(user['refreshToken'])
    
    return [storage.child("docs/"+book_id).get_url(user['idToken']), book_id]

def retrieve_libraries():
    db_libs = db.child("libraries").get().each()
    lib_names = []
    lib_ids = []
    for lib in db_libs:
        lib_names.append(lib.val()['libName'])
        lib_ids.append(lib.val()['libId'])

    return lib_names, lib_ids

if __name__ == '__main__':
    while(True):
        inp = input("\n\nUpload books/documents: ")
        if(inp == "-1" or "exit" in inp):
            exit(0)

        file_path = open_file_dialog()
        if(not file_path):
            continue # next cycle of while loop
        
        info = upload_file(file_path)

        title = input("Book title: ")
        description = input("Book description: ")
        category = input("Category: ")
        in_library = input("In library (0/1): ")
        library_id = None
        if(in_library == "0" or not in_library):
            library_id = -1
        else:
            print("\n\n [LIBRARIES] \n\n")
            lib_names, lib_ids = retrieve_libraries()
            for name, identity in zip(lib_names, lib_ids):
                print("\n"+str(lib_ids.index(identity) + 1), name, identity+"\n")

            library_id = int(input(f"Library ID (select 1-{len(lib_names)}): "))
            library_id = lib_ids[library_id-1]
        
        public = input("Public (0/1): ")
        access_url = info[0]
        book_id = info[1]
        
        data = {"accessUrl" : access_url, "bookDescription" : description,
                "bookId" : book_id, "bookTitle" : title, "category" : category,
                "inLibrary" : bool(in_library), "libraryId" : library_id, "public" : bool(public)}

        db.child("docs").child(book_id).set(data) # Appending into the docs db

        if(bool(in_library)):
            books = db.child("libraries").child(library_id).child("bookIds").get().val()
            if(not books):
                books = []
            books.append(book_id)
            book_dict = dict()
            for book in books:
                book_dict.update({books.index(book):book})

            db.child("libraries").child(library_id).child("bookIds").update(book_dict)

        print("\n\n** Appended into the Database **")
        print("DONE\n\n\n")
