The server is supposed to handle updating the results from a certain event.

It recieves an excel file, a map between the excel columns and their destined 
columns in the database tabel and the ID of the event.

The upload_excel() method recieves the data as a (binary stream?), goes through
all the sheets, and when the columns in the current sheet match the required
excel columns (recieved in the mapping sent by the client), it goes through each
row and if it finds the athlete result, it updates it, and if not it saves the
name of the missing athlete (alongside all the others) and returns a dictionary
with a relevant message and a list with the not found athletes, if any.

Right now, if in the excel file there are more athletes than in the database,
the upload_excel() method returns an error message, despite updating the
athletes that exist.